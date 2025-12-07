"""
Flask API for the Bias Analysis Tool

Provides endpoints for:
- Graph-based bias analysis (React frontend)
- Bias detection
- LLM-based bias injection (Vertex AI Llama 3.3)
- LLM-based debiasing (Vertex AI Llama 3.3)
- Bias evaluation (Gemini 2.5 Flash)

Designed for Google Cloud Run deployment.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import uuid
import json
import gc
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

# Handle imports for both local development and production (gunicorn)
# When running locally: direct imports work
# When running with gunicorn (backend.api:app): need relative or absolute imports
try:
    # Try relative imports first (works when backend is a package)
    from .bias_detection import BiasDetector
    from .bias_injection import BiasInjector
    from .debiasing import PromptDebiaser
except ImportError:
    # Fallback to absolute imports (works in local development)
    try:
        from bias_detection import BiasDetector
        from bias_injection import BiasInjector
        from debiasing import PromptDebiaser
    except ImportError:
        # Last resort: add backend to path and import
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from bias_detection import BiasDetector
        from bias_injection import BiasInjector
        from debiasing import PromptDebiaser

# Import HEARTS bias aggregator (optional - requires transformers + torch)
try:
    from .bias_aggregator import BiasAggregator, is_aggregator_available
    HEARTS_AGGREGATOR_AVAILABLE = is_aggregator_available()
except ImportError:
    try:
        from bias_aggregator import BiasAggregator, is_aggregator_available
        HEARTS_AGGREGATOR_AVAILABLE = is_aggregator_available()
    except ImportError:
        HEARTS_AGGREGATOR_AVAILABLE = False
        BiasAggregator = None
        print("HEARTS bias aggregator not available. Install: pip install transformers torch shap lime")

# Import security and rate limiting
try:
    from .security import require_api_key, rate_limit, admin_only, usage_tracker, SecurityConfig
except ImportError:
    try:
        from security import require_api_key, rate_limit, admin_only, usage_tracker, SecurityConfig
    except ImportError:
        print("Warning: Security module not available. API will be unprotected!")
        # Provide no-op decorators if security module not available
        def require_api_key(f): return f
        def rate_limit(**kwargs): return lambda f: f
        def admin_only(f): return f
        usage_tracker = None
        SecurityConfig = None

# Load environment variables from .env file
load_dotenv()

# Vertex AI LLM service (for Google Cloud)
try:
    # Try relative import first (for gunicorn)
    from .vertex_llm_service import get_vertex_llm_service
    VERTEX_LLM_AVAILABLE = True
except ImportError:
    try:
        # Fallback to absolute import (for local development)
        from vertex_llm_service import get_vertex_llm_service
        VERTEX_LLM_AVAILABLE = True
    except Exception as e:
        VERTEX_LLM_AVAILABLE = False
        print(f"Vertex AI LLM service not available: {e}")
        print("To enable LLM features, set GOOGLE_CLOUD_PROJECT")

# Bedrock LLM service (for AWS Bedrock)
try:
    # Try relative import first (for gunicorn)
    from .bedrock_llm_service import get_bedrock_llm_service
    BEDROCK_LLM_AVAILABLE = True
except ImportError:
    try:
        # Fallback to absolute import (for local development)
        from bedrock_llm_service import get_bedrock_llm_service
        BEDROCK_LLM_AVAILABLE = True
    except Exception as e:
        BEDROCK_LLM_AVAILABLE = False
        print(f"Bedrock LLM service not available: {e}")
        print("To enable Bedrock features, configure .env.bedrock")

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert any object to JSON-serializable primitives.
    This prevents 'Object of type X is not JSON serializable' errors.

    Args:
        obj: Any Python object

    Returns:
        JSON-serializable version of the object
    """
    # Handle None
    if obj is None:
        return None

    # Handle primitives
    if isinstance(obj, (bool, int, float, str)):
        return obj

    # Handle lists/tuples
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]

    # Handle dicts
    if isinstance(obj, dict):
        return {str(key): sanitize_for_json(value) for key, value in obj.items()}

    # Handle sets
    if isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]

    # Handle objects with __dict__ (convert to dict)
    if hasattr(obj, '__dict__'):
        return sanitize_for_json(obj.__dict__)

    # Fallback: convert to string
    return str(obj)

# Determine frontend build directory
FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "frontend-react" / "build"
if not FRONTEND_BUILD_DIR.exists():
    FRONTEND_BUILD_DIR = Path("/app/frontend-react/build")  # Docker path

app = Flask(__name__, static_folder=str(FRONTEND_BUILD_DIR), static_url_path='')
# Allow all origins for Cloud Run deployment
CORS(app, resources={r"/api/*": {"origins": "*"}})

bias_detector = BiasDetector()
bias_injector = BiasInjector()
debiaser = PromptDebiaser()

# Initialize HEARTS bias aggregator (optional, lazy-loaded)
# Use lazy initialization to avoid blocking startup in production
bias_aggregator = None
if HEARTS_AGGREGATOR_AVAILABLE and BiasAggregator:
    try:
        # Lazy initialization: HEARTS model will load on first use, not at startup
        # This prevents startup failures in production if model download fails
        enable_hearts = os.getenv('ENABLE_HEARTS', 'true').lower() == 'true'
        lazy_hearts = os.getenv('HEARTS_LAZY_LOAD', 'true').lower() == 'true'
        
        bias_aggregator = BiasAggregator(
            use_hearts=enable_hearts,
            lazy_hearts=lazy_hearts
        )
        if lazy_hearts:
            print("✓ HEARTS bias aggregator ready (lazy-loaded)")
        else:
            print("✓ HEARTS bias aggregator initialized")
    except Exception as e:
        print(f"Warning: Could not create HEARTS aggregator: {e}")
        import traceback
        traceback.print_exc()
        HEARTS_AGGREGATOR_AVAILABLE = False
        bias_aggregator = None

def get_bias_aggregator():
    """
    Get the bias aggregator instance, ensuring it's available.
    
    Returns:
        BiasAggregator instance or None if not available
    """
    return bias_aggregator

# Set LLM_AVAILABLE based on available services
LLM_AVAILABLE = VERTEX_LLM_AVAILABLE or BEDROCK_LLM_AVAILABLE

def get_llm_service(model_id: Optional[str] = None):
    """
    Get appropriate LLM service based on model_id.
    
    Args:
        model_id: Optional model ID to determine which service to use
        
    Returns:
        LLM service instance (Vertex or Bedrock)
    """
    # If model_id is provided, check if it's a Bedrock model
    if model_id:
        try:
            from model_config import get_model_info
            model_info = get_model_info(model_id)
            if model_info and model_info.get('endpoint_type') == 'bedrock':
                if not BEDROCK_LLM_AVAILABLE:
                    raise Exception("Bedrock LLM service not available. Configure .env.bedrock")
                return get_bedrock_llm_service(default_model=model_id)
        except Exception as e:
            print(f"Warning: Could not determine model type: {e}")
    
    # Default to Vertex AI if available, otherwise Bedrock
    if VERTEX_LLM_AVAILABLE:
        return get_vertex_llm_service()
    elif BEDROCK_LLM_AVAILABLE:
        return get_bedrock_llm_service()
    else:
        raise Exception("No LLM service available. Configure Vertex AI or Bedrock.")


# Memory management: Force garbage collection after every request
@app.after_request
def cleanup_memory(response):
    """
    Run garbage collection after each request to prevent memory leaks.
    Critical for ML models (HEARTS, torch tensors, SHAP/LIME objects).
    """
    gc.collect()
    
    # If torch is available, clear CUDA cache too
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
    
    return response


@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    """
    Comprehensive analysis endpoint that returns:
    - Detected biases
    - Biased versions (rule-based and optionally LLM-based)
    - Debiased versions (rule-based and optionally LLM-based)
    - LLM answers comparison (if LLM is available)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        prompt = data.get('prompt', '')
        use_llm = data.get('use_llm', False) and LLM_AVAILABLE
        generate_answers = data.get('generate_answers', False) and LLM_AVAILABLE
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        result = {
            'original_prompt': prompt,
            'detected_biases': None,
            'biased_versions': [],
            'debiased_versions': [],
            'llm_available': LLM_AVAILABLE,
            'answers_comparison': None
        }
        
        # Detect biases
        try:
            result['detected_biases'] = bias_detector.detect_biases(prompt)
        except Exception as e:
            print(f"Error in bias detection: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Bias detection failed: {str(e)}'}), 500
        
        # Generate biased versions (rule-based)
        try:
            result['biased_versions'] = bias_injector.inject_biases(prompt)
        except Exception as e:
            print(f"Error in bias injection: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Bias injection failed: {str(e)}'}), 500
        
        # Generate LLM-based biased versions if requested
        if use_llm:
            try:
                llm = get_llm_service()
                llm_biased = llm.inject_bias_llm(prompt, "confirmation")
                result['biased_versions'].append(llm_biased)
            except Exception as e:
                result['llm_error'] = str(e)
        
        # Generate debiased versions (rule-based)
        try:
            result['debiased_versions'] = debiaser.get_all_debiasing_methods(prompt)
        except Exception as e:
            print(f"Error in debiasing: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Debiasing failed: {str(e)}'}), 500
        
        # Generate LLM-based debiased version if requested
        if use_llm:
            try:
                llm = get_llm_service()
                llm_debiased = llm.debias_self_help(prompt)
                result['debiased_versions'].append(llm_debiased)
            except Exception as e:
                if 'llm_error' not in result:
                    result['llm_error'] = str(e)
        
        # Generate and compare answers if requested
        if generate_answers:
            try:
                llm = get_llm_service()
                original_answer = llm.generate_answer(prompt)
                
                answers_comparison = {
                    'original_prompt': prompt,
                    'original_answer': original_answer,
                    'modified_versions': []
                }
                
                # Compare with first biased version if available
                if result['biased_versions']:
                    biased_prompt = result['biased_versions'][0].get('biased_prompt', '')
                    if biased_prompt:
                        biased_answer = llm.generate_answer(biased_prompt)
                        answers_comparison['modified_versions'].append({
                            'type': 'biased',
                            'prompt': biased_prompt,
                            'answer': biased_answer,
                            'bias_type': result['biased_versions'][0].get('bias_added', 'Unknown')
                        })
                
                # Compare with first debiased version if available
                if result['debiased_versions']:
                    debiased_prompt = result['debiased_versions'][0].get('debiased_prompt', '')
                    if debiased_prompt:
                        debiased_answer = llm.generate_answer(debiased_prompt)
                        answers_comparison['modified_versions'].append({
                            'type': 'debiased',
                            'prompt': debiased_prompt,
                            'answer': debiased_answer,
                            'method': result['debiased_versions'][0].get('method', 'Unknown')
                        })
                
                result['answers_comparison'] = answers_comparison
            except Exception as e:
                result['answers_error'] = str(e)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Unexpected error in analyze_prompt: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/detect', methods=['POST'])
def detect_biases():
    """Detect biases in a prompt"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    biases = bias_detector.detect_biases(prompt)
    return jsonify(biases)


@app.route('/api/inject', methods=['POST'])
def inject_biases():
    """Generate biased versions of a prompt"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    biased_versions = bias_injector.inject_biases(prompt)
    return jsonify({
        'original_prompt': prompt,
        'biased_versions': biased_versions
    })


@app.route('/api/debias', methods=['POST'])
def debias_prompt():
    """Generate debiased versions of a prompt"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    method = data.get('method', 'comprehensive')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    if method == 'all':
        debiased_versions = debiaser.get_all_debiasing_methods(prompt)
        return jsonify({
            'original_prompt': prompt,
            'debiased_versions': debiased_versions
        })
    else:
        result = debiaser.debias_prompt(prompt, method)
        return jsonify({
            'original_prompt': prompt,
            'debiased_prompt': result
        })


@app.route('/api/llm/debias', methods=['POST'])
def llm_debias():
    """Use LLM for self-help debiasing (BiasBuster method)"""
    if not LLM_AVAILABLE:
        return jsonify({'error': 'LLM service not available. Set OPENAI_API_KEY or configure Ollama.'}), 503
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        llm = get_llm_service()
        result = llm.debias_self_help(prompt)
        return jsonify({
            'original_prompt': prompt,
            'debiased_result': result
        })
    except Exception as e:
        return jsonify({'error': f'LLM debiasing failed: {str(e)}'}), 500


@app.route('/api/llm/inject', methods=['POST'])
def llm_inject():
    """Use LLM to inject bias into a prompt"""
    if not LLM_AVAILABLE:
        return jsonify({'error': 'LLM service not available. Set OPENAI_API_KEY or configure Ollama.'}), 503
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    bias_type = data.get('bias_type', 'confirmation')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        llm = get_llm_service()
        result = llm.inject_bias_llm(prompt, bias_type)
        return jsonify({
            'original_prompt': prompt,
            'biased_result': result
        })
    except Exception as e:
        return jsonify({'error': f'LLM bias injection failed: {str(e)}'}), 500


@app.route('/api/llm/compare', methods=['POST'])
def llm_compare():
    """Generate LLM answers for original and modified prompts and compare"""
    if not LLM_AVAILABLE:
        return jsonify({'error': 'LLM service not available. Set OPENAI_API_KEY or configure Ollama.'}), 503
    
    data = request.get_json()
    original_prompt = data.get('original_prompt', '')
    modified_prompts = data.get('modified_prompts', [])  # List of {'prompt': str, 'type': str, 'label': str}
    
    if not original_prompt:
        return jsonify({'error': 'No original prompt provided'}), 400
    
    try:
        llm = get_llm_service()
        original_answer = llm.generate_answer(original_prompt)
        
        comparison = {
            'original_prompt': original_prompt,
            'original_answer': original_answer,
            'modified_comparisons': []
        }
        
        for mod in modified_prompts:
            mod_prompt = mod.get('prompt', '')
            if mod_prompt:
                mod_answer = llm.generate_answer(mod_prompt)
                comparison['modified_comparisons'].append({
                    'prompt': mod_prompt,
                    'answer': mod_answer,
                    'type': mod.get('type', 'unknown'),
                    'label': mod.get('label', 'Modified')
                })
        
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': f'LLM comparison failed: {str(e)}'}), 500


@app.route('/api/admin/usage', methods=['GET'])
@admin_only
def admin_usage():
    """
    Admin endpoint to monitor API usage and costs.
    Requires admin API key.
    """
    if not usage_tracker:
        return jsonify({'error': 'Usage tracking not available'}), 500

    try:
        # Get all API keys' stats
        all_stats = []
        for api_key in usage_tracker.usage.keys():
            all_stats.append(usage_tracker.get_stats(api_key))

        return jsonify({
            'config': SecurityConfig.get_config_summary() if SecurityConfig else {},
            'usage_by_key': all_stats,
            'total_requests_today': sum(
                stats['today']['count'] for stats in all_stats
            ),
            'total_cost_today': sum(
                stats['today']['cost'] for stats in all_stats
            ),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get usage stats: {str(e)}'}), 500


@app.route('/api/admin/config', methods=['GET'])
@admin_only
def admin_config():
    """
    Admin endpoint to view security configuration.
    Requires admin API key.
    """
    if not SecurityConfig:
        return jsonify({'error': 'Security configuration not available'}), 500

    return jsonify(SecurityConfig.get_config_summary())


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (no auth required).
    """
    # Check HEARTS initialization status
    hearts_status = {
        'available': HEARTS_AGGREGATOR_AVAILABLE,
        'initialized': False,
        'lazy_loaded': False,
        'error': None,
        'status': 'unknown'
    }
    
    if bias_aggregator:
        try:
            hearts_status['initialized'] = getattr(bias_aggregator, '_hearts_initialized', False)
            hearts_status['lazy_loaded'] = getattr(bias_aggregator, 'use_hearts', False) and not hearts_status['initialized']
            
            if hasattr(bias_aggregator, '_hearts_init_error') and bias_aggregator._hearts_init_error:
                hearts_status['error'] = bias_aggregator._hearts_init_error
                hearts_status['status'] = 'error'
            elif hearts_status['initialized']:
                hearts_status['status'] = 'ready'
            elif hearts_status['lazy_loaded']:
                hearts_status['status'] = 'lazy_loaded'  # Available but will initialize on first use
            elif HEARTS_AGGREGATOR_AVAILABLE:
                hearts_status['status'] = 'available'  # Available but not enabled
            else:
                hearts_status['status'] = 'unavailable'
        except Exception:
            pass  # Ignore errors when checking status
    elif HEARTS_AGGREGATOR_AVAILABLE:
        hearts_status['status'] = 'available'
    else:
        hearts_status['status'] = 'unavailable'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'hearts': hearts_status,
            'vertex_ai_available': VERTEX_LLM_AVAILABLE,
            'security_enabled': SecurityConfig.REQUIRE_API_KEY if SecurityConfig else False
        }
    })


@app.route('/api/models', methods=['GET'])
@rate_limit('get_models', cost_estimate=0.0)  # Free endpoint, just rate limited
def get_models():
    """
    Get list of available models for generation.

    Returns:
        JSON with generation and evaluation models
    """
    try:
        from model_config import get_generation_models, get_evaluation_models
    except ImportError:
        try:
            from .model_config import get_generation_models, get_evaluation_models
        except ImportError:
            return jsonify({'error': 'Model configuration not available'}), 500

    try:
        return jsonify({
            'generation_models': get_generation_models(),
            'evaluation_models': get_evaluation_models()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get models: {str(e)}'}), 500


@app.route('/api/graph/expand', methods=['POST'])
@rate_limit('graph_expand', cost_estimate=0.02)  # ~$0.02 per initial graph, IP-based limits
def graph_expand():
    """
    Initial graph expansion - creates the first node with evaluations and potential paths.

    Returns:
    - Single node with: prompt, LLM answer, HEARTS evaluation, Gemini evaluation
    - Potential paths (edges without targets) for bias/debias options

    Does NOT create child nodes - those are created when user clicks a path.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        prompt = data.get('prompt', '')
        model_id = data.get('model_id')  # Get selected model
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        # Generate unique ID for this node
        node_id = str(uuid.uuid4())

        # Step 1: Generate LLM answer for the prompt using selected model
        llm_answer = None
        if LLM_AVAILABLE:
            try:
                llm = get_llm_service(model_id=model_id)
                llm_answer = llm.generate_answer(prompt, model_id=model_id)
                print(f"✓ Generated LLM answer ({len(llm_answer)} chars)")
            except Exception as e:
                print(f"Warning: Could not generate LLM answer: {e}")
                llm_answer = f"[Error generating answer: {str(e)}]"
        else:
            llm_answer = "[LLM not available - configure Vertex AI or Bedrock]"

        # Step 2: Multi-layer bias detection (HEARTS + Gemini/Claude)
        # HEARTS analyzes the LLM answer, not the original prompt
        use_hearts = HEARTS_AGGREGATOR_AVAILABLE and bias_aggregator
        use_gemini = VERTEX_LLM_AVAILABLE
        use_claude = BEDROCK_LLM_AVAILABLE

        if use_hearts and llm_answer:
            try:
                detected_biases = bias_aggregator.detect_all_layers(
                    prompt=llm_answer,  # Analyze the LLM answer, not the original prompt
                    use_hearts=True,
                    use_gemini=use_gemini,  # Enable Gemini evaluation
                    explain=True
                )
                print(f"✓ Multi-layer detection complete (HEARTS + Gemini on answer)")
            except Exception as e:
                print(f"Warning: HEARTS detection failed: {e}")
                # Fallback to rule-based
                detected_biases = bias_detector.detect_biases(llm_answer)
                use_hearts = False
        else:
            # Rule-based only (analyze answer if available, otherwise prompt)
            detected_biases = bias_detector.detect_biases(llm_answer if llm_answer else prompt)

        # Step 2.5: Add Claude bias evaluation on the LLM answer if available
        claude_evaluation = None
        if use_claude and llm_answer:
            try:
                llm = get_llm_service(model_id=model_id)
                if hasattr(llm, 'evaluate_bias'):
                    claude_evaluation = llm.evaluate_bias(llm_answer)
                    print(f"✓ Claude bias evaluation complete (evaluated answer)")
            except Exception as e:
                print(f"Warning: Claude evaluation failed: {e}")

        # Step 3: Build node with structured evaluations
        hearts_data = detected_biases.get('hearts', {}) if isinstance(detected_biases.get('hearts'), dict) else {}
        gemini_data = detected_biases.get('gemini_validation', {}) if isinstance(detected_biases.get('gemini_validation'), dict) else {}
        explanations = detected_biases.get('explanations', {}) if isinstance(detected_biases.get('explanations'), dict) else {}

        # Check if HEARTS actually returned valid results
        # If hearts_data is empty or missing key fields, HEARTS didn't work properly
        hearts_actually_worked = use_hearts and hearts_data and (
            'is_stereotype' in hearts_data or 
            'confidence' in hearts_data or 
            'prediction' in hearts_data
        )
        
        # Only warn if HEARTS was attempted but didn't return valid results
        # Don't warn if HEARTS failed to initialize (that's already logged)
        if use_hearts and not hearts_actually_worked:
            hearts_error = detected_biases.get('hearts_error', '')
            if hearts_error:
                # HEARTS failed to initialize - already logged, don't duplicate warning
                pass
            else:
                # HEARTS ran but returned empty results - this is unusual
                print(f"Warning: HEARTS evaluation returned empty results. Check if HEARTS is properly initialized.")

        # Safely extract token importance (ensure it's serializable)
        token_importance = []
        if hearts_actually_worked and explanations.get('most_biased_tokens'):
            raw_tokens = explanations.get('most_biased_tokens', [])[:10]
            for token in raw_tokens:
                if isinstance(token, dict):
                    token_importance.append({
                        'token': str(token.get('token', '')),
                        'importance': float(token.get('importance', 0)),
                        'contribution': str(token.get('contribution', 'unknown')),
                        'source': str(token.get('source', 'HEARTS-SHAP'))
                    })

        node = {
            'id': node_id,
            'prompt': prompt,
            'llm_answer': llm_answer,
            'type': 'original',

            # HEARTS ML evaluation
            'hearts_evaluation': {
                'available': hearts_actually_worked,
                'is_stereotype': bool(hearts_data.get('is_stereotype', False)) if hearts_actually_worked else None,
                'confidence': float(hearts_data.get('confidence', 0)) if hearts_actually_worked else None,
                'probabilities': dict(hearts_data.get('probabilities', {})) if hearts_actually_worked else {},
                'prediction': str(hearts_data.get('prediction', 'Unknown')) if hearts_actually_worked else None,
                'token_importance': token_importance,
                'model': 'HEARTS ALBERT-v2' if hearts_actually_worked else None,
                'error': detected_biases.get('hearts_error') if use_hearts and not hearts_actually_worked else None
            },

            # Gemini LLM evaluation
            'gemini_evaluation': {
                'available': bool(use_gemini and gemini_data),
                'bias_score': float(gemini_data.get('evaluation', {}).get('bias_score', 0)) if gemini_data else None,
                'severity': str(gemini_data.get('evaluation', {}).get('severity', 'unknown')) if gemini_data else None,
                'bias_types': list(gemini_data.get('evaluation', {}).get('bias_types', [])) if gemini_data else [],
                'explanation': str(gemini_data.get('evaluation', {}).get('explanation', '')) if gemini_data else None,
                'recommendations': str(gemini_data.get('evaluation', {}).get('recommendations', '')) if gemini_data else None,
                'model': 'Gemini 2.5 Flash' if gemini_data else None
            },

            # Claude LLM evaluation (zero-shot)
            'claude_evaluation': {
                'available': bool(claude_evaluation),
                'bias_score': float(claude_evaluation.get('evaluation', {}).get('overall_bias_score', 0)) if claude_evaluation else None,
                'severity': str(claude_evaluation.get('evaluation', {}).get('severity', 'unknown')) if claude_evaluation else None,
                'bias_types': list(claude_evaluation.get('evaluation', {}).get('detected_bias_types', [])) if claude_evaluation else [],
                'bias_scores': dict(claude_evaluation.get('evaluation', {}).get('bias_scores', {})) if claude_evaluation else {},
                'explanation': str(claude_evaluation.get('evaluation', {}).get('explanation', '')) if claude_evaluation else None,
                'recommendations': str(claude_evaluation.get('evaluation', {}).get('recommendations', '')) if claude_evaluation else None,
                'model': claude_evaluation.get('model', 'Claude') if claude_evaluation else None,
                'method': claude_evaluation.get('method', 'Zero-shot') if claude_evaluation else None
            },

            # Bias metrics from individual judges (not aggregated)
            'bias_metrics': detected_biases.get('bias_metrics', []),
            'judge_count': detected_biases.get('judge_count', 0),
            'judges_used': detected_biases.get('judges_used', []),
            
            # Overall metrics (for backward compatibility)
            'bias_score': float(detected_biases.get('overall_bias_score', 0)),
            'confidence': float(detected_biases.get('confidence', 0)),
            'source_agreement': float(detected_biases.get('source_agreement', 1.0)),

            # Metadata
            'detection_sources': list(detected_biases.get('detection_sources', ['Rule-based'])),
            'layers_used': list(detected_biases.get('layers_used', ['rule-based'])),
            'frameworks': list(explanations.get('frameworks', []))
        }

        # Step 4: Determine available bias/debias paths
        # Import bias instructions
        try:
            from bias_instructions import get_available_bias_types, get_available_debias_methods
        except ImportError:
            from .bias_instructions import get_available_bias_types, get_available_debias_methods

        available_biases = get_available_bias_types(detected_biases)
        available_debiases = get_available_debias_methods(detected_biases)

        # Create potential path edges (NO target nodes yet)
        edges = []

        # Add bias paths
        for bias_option in available_biases:
            edges.append({
                'id': f"{node_id}-bias-{bias_option['bias_type']}",
                'source': node_id,
                # NO 'target' field = potential path, not actual edge
                'type': 'bias',
                'bias_type': bias_option['bias_type'],
                'label': bias_option['label'],
                'description': bias_option['description'],
                'severity': bias_option.get('severity', 'medium'),
                'action_required': 'click_to_generate'
            })

        # Add debias paths
        for debias_option in available_debiases:
            edges.append({
                'id': f"{node_id}-debias-{debias_option['method']}",
                'source': node_id,
                # NO 'target' field = potential path, not actual edge
                'type': 'debias',
                'method': debias_option['method'],
                'label': debias_option['label'],
                'description': debias_option['description'],
                'effectiveness': debias_option.get('effectiveness', 'high'),
                'action_required': 'click_to_generate'
            })

        print(f"✓ Created node with {len(edges)} potential paths ({len(available_biases)} bias, {len(available_debiases)} debias)")

        # Sanitize entire response to ensure JSON serializability
        response = sanitize_for_json({
            'nodes': [node],  # Only 1 node
            'edges': edges,    # Potential paths (no targets)
            'root_id': node_id
        })

        return jsonify(response)

    except Exception as e:
        print(f"Error in graph_expand: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Graph expansion failed: {str(e)}'}), 500


@app.route('/api/graph/evaluate', methods=['POST'])
def graph_evaluate():
    """
    Evaluate bias using Gemini 2.5 Flash for a specific node.
    """
    if not VERTEX_LLM_AVAILABLE:
        return jsonify({'error': 'Vertex AI not available'}), 503
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    node_id = data.get('node_id', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        llm = get_vertex_llm_service()
        evaluation = llm.evaluate_bias(prompt)
        
        return jsonify({
            'node_id': node_id,
            'evaluation': evaluation,
            'model': 'Gemini 2.5 Flash'
        })
    except Exception as e:
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500


@app.route('/api/graph/expand-node', methods=['POST'])
@rate_limit('graph_expand_node', cost_estimate=0.01)  # ~$0.01 per node expansion, IP-based limits
def graph_expand_node():
    """
    Expand a node - creates new child node when user clicks a potential path.

    Process:
    1. Transform prompt using LLM (bias or debias)
    2. Generate LLM answer for new prompt
    3. Evaluate new prompt with HEARTS
    4. Evaluate new prompt with Gemini
    5. Determine new potential paths
    6. Return new node + connecting edge + new potential paths
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        parent_id = data.get('node_id', '')
        parent_prompt = data.get('prompt', '')
        action = data.get('action', 'debias')  # 'bias' or 'debias'
        bias_type = data.get('bias_type')  # For bias actions
        debias_method = data.get('method')  # For debias actions
        model_id = data.get('model_id')  # Optional model ID
        # Get existing conversation history from parent node (for nested bias injection)
        parent_conversation = data.get('parent_conversation')  # Optional: existing conversation from parent

        if not parent_prompt or not parent_id:
            return jsonify({'error': 'Missing node_id or prompt'}), 400

        if not LLM_AVAILABLE:
            return jsonify({'error': 'LLM service not available. Configure Vertex AI or Bedrock.'}), 503

        llm = get_llm_service(model_id=model_id)

        # Step 1: Transform prompt using LLM with instructions
        if action == 'bias':
            if not bias_type:
                return jsonify({'error': 'Missing bias_type for bias action'}), 400

            print(f"Injecting {bias_type} into prompt{' using ' + model_id if model_id else ''}...")
            # Pass existing conversation to prepend new bias injection turns (for nested bias injection)
            transformation = llm.inject_bias_llm(
                parent_prompt, 
                bias_type, 
                model_id=model_id,
                existing_conversation=parent_conversation  # Prepend parent conversation for nested injections
            )
            
            # Handle multi-turn format: biased_prompt is the original prompt, conversation has the history
            if transformation.get('multi_turn'):
                # For multi-turn, the "biased prompt" is the original prompt (asked after priming)
                new_prompt = transformation['biased_prompt']  # This is the original prompt
                conversation = transformation.get('conversation', {})
                # The LLM answer will be generated from the original prompt after priming
                transformation_label = f"{transformation['bias_added']} (Multi-turn)"
            else:
                # Legacy single-turn format
                new_prompt = transformation['biased_prompt']
                transformation_label = transformation['bias_added']
                conversation = None
            
            node_type = 'biased'

        else:  # action == 'debias'
            if not debias_method:
                debias_method = 'auto'  # Auto-detect method

            print(f"Debiasing prompt with method: {debias_method}{' using ' + model_id if model_id else ''}...")
            transformation = llm.debias_self_help(parent_prompt, method=debias_method, model_id=model_id)
            new_prompt = transformation['debiased_prompt']
            transformation_label = transformation['method']
            node_type = 'debiased'

        print(f"✓ Transformed prompt ({len(new_prompt)} chars)")

        # Step 2: Generate LLM answer for the NEW prompt using selected model
        # For multi-turn bias injection, use the conversation response
        if action == 'bias' and conversation and transformation.get('multi_turn'):
            # Use the Turn 2 response from the multi-turn conversation
            llm_answer = conversation.get('turn2_response', '')
            if not llm_answer:
                # Fallback: generate new answer
                try:
                    llm_answer = llm.generate_answer(new_prompt, model_id=model_id)
                except Exception as e:
                    llm_answer = f"[Error generating answer: {str(e)}]"
            print(f"✓ Using multi-turn conversation response ({len(llm_answer)} chars)")
        else:
            # Standard single-turn: generate answer
            try:
                llm_answer = llm.generate_answer(new_prompt, model_id=model_id)
                print(f"✓ Generated LLM answer ({len(llm_answer)} chars)")
            except Exception as e:
                print(f"Warning: Could not generate LLM answer: {e}")
                llm_answer = f"[Error generating answer: {str(e)}]"

        # Step 3 & 4: Evaluate with HEARTS + Gemini/Claude
        # HEARTS analyzes the LLM answer, not the prompt
        use_hearts = HEARTS_AGGREGATOR_AVAILABLE and bias_aggregator
        use_claude = BEDROCK_LLM_AVAILABLE

        if use_hearts and llm_answer:
            try:
                detected_biases = bias_aggregator.detect_all_layers(
                    prompt=llm_answer,  # Analyze the LLM answer, not the prompt
                    use_hearts=True,
                    use_gemini=True,  # Enable Gemini
                    explain=True
                )
                print(f"✓ Multi-layer evaluation complete (HEARTS + Gemini on answer)")
            except Exception as e:
                print(f"Warning: Multi-layer evaluation failed: {e}")
                detected_biases = bias_detector.detect_biases(llm_answer)
                use_hearts = False
        else:
            detected_biases = bias_detector.detect_biases(llm_answer if llm_answer else new_prompt)

        # Add Claude bias evaluation on the LLM answer if available
        claude_evaluation = None
        if use_claude and llm_answer:
            try:
                if hasattr(llm, 'evaluate_bias'):
                    claude_evaluation = llm.evaluate_bias(llm_answer)
                    print(f"✓ Claude bias evaluation complete (evaluated answer)")
            except Exception as e:
                print(f"Warning: Claude evaluation failed: {e}")

        # Build new node with structured evaluations
        new_id = str(uuid.uuid4())
        hearts_data = detected_biases.get('hearts', {}) if isinstance(detected_biases.get('hearts'), dict) else {}
        gemini_data = detected_biases.get('gemini_validation', {}) if isinstance(detected_biases.get('gemini_validation'), dict) else {}
        explanations = detected_biases.get('explanations', {}) if isinstance(detected_biases.get('explanations'), dict) else {}

        # Check if HEARTS actually returned valid results
        # If hearts_data is empty or missing key fields, HEARTS didn't work properly
        hearts_actually_worked = use_hearts and hearts_data and (
            'is_stereotype' in hearts_data or 
            'confidence' in hearts_data or 
            'prediction' in hearts_data
        )
        
        # Only warn if HEARTS was attempted but didn't return valid results
        # Don't warn if HEARTS failed to initialize (that's already logged)
        if use_hearts and not hearts_actually_worked:
            hearts_error = detected_biases.get('hearts_error', '')
            if hearts_error:
                # HEARTS failed to initialize - already logged, don't duplicate warning
                pass
            else:
                # HEARTS ran but returned empty results - this is unusual
                print(f"Warning: HEARTS evaluation returned empty results. Check if HEARTS is properly initialized.")

        # Safely extract token importance
        token_importance = []
        if hearts_actually_worked and explanations.get('most_biased_tokens'):
            raw_tokens = explanations.get('most_biased_tokens', [])[:10]
            for token in raw_tokens:
                if isinstance(token, dict):
                    token_importance.append({
                        'token': str(token.get('token', '')),
                        'importance': float(token.get('importance', 0)),
                        'contribution': str(token.get('contribution', 'unknown')),
                        'source': str(token.get('source', 'HEARTS-SHAP'))
                    })

        new_node = {
            'id': new_id,
            'prompt': new_prompt,
            'llm_answer': llm_answer,
            'type': node_type,
            'parent_id': parent_id,
            'transformation': transformation_label,
            'transformation_details': {
                'action': str(action),
                'bias_type': str(bias_type) if action == 'bias' and bias_type else None,
                'method': str(debias_method) if action == 'debias' and debias_method else None,
                'explanation': str(transformation.get('explanation', '')),
                'framework': str(transformation.get('framework', '')),
                'multi_turn': transformation.get('multi_turn', False),
                'conversation': conversation if conversation else None
            },

            # HEARTS ML evaluation
            'hearts_evaluation': {
                'available': hearts_actually_worked,
                'is_stereotype': bool(hearts_data.get('is_stereotype', False)) if hearts_actually_worked else None,
                'confidence': float(hearts_data.get('confidence', 0)) if hearts_actually_worked else None,
                'probabilities': dict(hearts_data.get('probabilities', {})) if hearts_actually_worked else {},
                'prediction': str(hearts_data.get('prediction', 'Unknown')) if hearts_actually_worked else None,
                'token_importance': token_importance,
                'model': 'HEARTS ALBERT-v2' if hearts_actually_worked else None,
                'error': detected_biases.get('hearts_error') if use_hearts and not hearts_actually_worked else None
            },

            # Gemini LLM evaluation
            'gemini_evaluation': {
                'available': bool(gemini_data),
                'bias_score': float(gemini_data.get('evaluation', {}).get('bias_score', 0)) if gemini_data else None,
                'severity': str(gemini_data.get('evaluation', {}).get('severity', 'unknown')) if gemini_data else None,
                'bias_types': list(gemini_data.get('evaluation', {}).get('bias_types', [])) if gemini_data else [],
                'explanation': str(gemini_data.get('evaluation', {}).get('explanation', '')) if gemini_data else None,
                'recommendations': str(gemini_data.get('evaluation', {}).get('recommendations', '')) if gemini_data else None,
                'model': 'Gemini 2.5 Flash' if gemini_data else None
            },

            # Claude LLM evaluation (zero-shot)
            'claude_evaluation': {
                'available': bool(claude_evaluation),
                'bias_score': float(claude_evaluation.get('evaluation', {}).get('overall_bias_score', 0)) if claude_evaluation else None,
                'severity': str(claude_evaluation.get('evaluation', {}).get('severity', 'unknown')) if claude_evaluation else None,
                'bias_types': list(claude_evaluation.get('evaluation', {}).get('detected_bias_types', [])) if claude_evaluation else [],
                'bias_scores': dict(claude_evaluation.get('evaluation', {}).get('bias_scores', {})) if claude_evaluation else {},
                'explanation': str(claude_evaluation.get('evaluation', {}).get('explanation', '')) if claude_evaluation else None,
                'recommendations': str(claude_evaluation.get('evaluation', {}).get('recommendations', '')) if claude_evaluation else None,
                'model': claude_evaluation.get('model', 'Claude') if claude_evaluation else None,
                'method': claude_evaluation.get('method', 'Zero-shot') if claude_evaluation else None
            },

            # Bias metrics from individual judges (not aggregated)
            'bias_metrics': detected_biases.get('bias_metrics', []),
            'judge_count': detected_biases.get('judge_count', 0),
            'judges_used': detected_biases.get('judges_used', []),
            
            # Overall metrics (for backward compatibility)
            'bias_score': float(detected_biases.get('overall_bias_score', 0)),
            'confidence': float(detected_biases.get('confidence', 0)),
            'source_agreement': float(detected_biases.get('source_agreement', 1.0)),

            # Metadata
            'detection_sources': list(detected_biases.get('detection_sources', ['Rule-based'])),
            'layers_used': list(detected_biases.get('layers_used', ['rule-based'])),
            'frameworks': list(explanations.get('frameworks', []))
        }

        # Step 5: Create connecting edge
        connecting_edge = {
            'id': f"{parent_id}-{new_id}",
            'source': parent_id,
            'target': new_id,  # This edge HAS a target
            'type': action,
            'label': transformation_label,
            'transformation': action
        }

        # Step 6: Determine new potential paths from this node
        try:
            from bias_instructions import get_available_bias_types, get_available_debias_methods
        except ImportError:
            from .bias_instructions import get_available_bias_types, get_available_debias_methods

        available_biases = get_available_bias_types(detected_biases)
        available_debiases = get_available_debias_methods(detected_biases)

        # Create potential paths from new node (NO targets)
        potential_paths = []

        # Add bias paths
        for bias_option in available_biases:
            potential_paths.append({
                'id': f"{new_id}-bias-{bias_option['bias_type']}",
                'source': new_id,
                # NO 'target' field = potential path
                'type': 'bias',
                'bias_type': bias_option['bias_type'],
                'label': bias_option['label'],
                'description': bias_option['description'],
                'severity': bias_option.get('severity', 'medium'),
                'action_required': 'click_to_generate'
            })

        # Add debias paths
        for debias_option in available_debiases:
            potential_paths.append({
                'id': f"{new_id}-debias-{debias_option['method']}",
                'source': new_id,
                # NO 'target' field = potential path
                'type': 'debias',
                'method': debias_option['method'],
                'label': debias_option['label'],
                'description': debias_option['description'],
                'effectiveness': debias_option.get('effectiveness', 'high'),
                'action_required': 'click_to_generate'
            })

        print(f"✓ Created node with {len(potential_paths)} new potential paths")

        # Sanitize entire response to ensure JSON serializability
        response = sanitize_for_json({
            'nodes': [new_node],
            'edges': [connecting_edge] + potential_paths,  # 1 real edge + potential paths
            'new_node_id': new_id
        })

        return jsonify(response)

    except Exception as e:
        print(f"Error in graph_expand_node: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Node expansion failed: {str(e)}'}), 500


@app.route('/api/explain', methods=['POST'])
def explain_bias():
    """
    Get detailed SHAP explanations for a prompt using HEARTS.

    Requires HEARTS model to be available.
    Returns token-level importance scores and visualization data.
    """
    if not HEARTS_AGGREGATOR_AVAILABLE or not bias_aggregator:
        return jsonify({
            'error': 'HEARTS not available. Install: pip install transformers torch shap lime'
        }), 503

    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    try:
        # Get detailed explanation
        result = bias_aggregator.detect_all_layers(
            prompt=prompt,
            use_hearts=True,
            use_gemini=False,
            explain=True
        )

        # Extract explanation data
        explanations = result.get('explanations', {})
        hearts_data = result.get('hearts', {})

        return jsonify({
            'prompt': prompt,
            'is_stereotype': hearts_data.get('is_stereotype', False),
            'confidence': hearts_data.get('confidence', 0),
            'probabilities': hearts_data.get('probabilities', {}),
            'token_importance': explanations.get('most_biased_tokens', []),
            'frameworks': explanations.get('frameworks', []),
            'detected_bias_types': explanations.get('detected_bias_types', []),
            'model': 'HEARTS ALBERT-v2'
        })
    except Exception as e:
        return jsonify({'error': f'Explanation failed: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve React frontend index.html"""
    if FRONTEND_BUILD_DIR.exists():
        index_path = FRONTEND_BUILD_DIR / 'index.html'
        if index_path.exists():
            return send_file(str(index_path))
    
    # Fallback: API info if frontend not available
    return jsonify({
        'message': 'Bias Analysis API',
        'version': '2.1',
        'note': 'Frontend not available. Use /api endpoints.',
        'vertex_llm_available': VERTEX_LLM_AVAILABLE,
        'hearts_available': HEARTS_AGGREGATOR_AVAILABLE,
        'features': {
            'rule_based_detection': True,
            'ml_stereotype_detection': HEARTS_AGGREGATOR_AVAILABLE,
            'shap_explanations': HEARTS_AGGREGATOR_AVAILABLE,
            'llm_generation': VERTEX_LLM_AVAILABLE,
            'llm_evaluation': VERTEX_LLM_AVAILABLE
        },
        'endpoints': {
            'POST /api/graph/expand': 'Expand graph from starter prompt (multi-layer detection)',
            'POST /api/graph/evaluate': 'Evaluate bias using Gemini 2.5 Flash',
            'POST /api/graph/expand-node': 'Expand specific node (bias/debias)',
            'POST /api/explain': 'Get SHAP token-level explanations (HEARTS)',
            'POST /api/analyze': 'Full analysis (legacy)',
            'GET /api/health': 'Health check'
        }
    })


@app.route('/<path:path>', methods=['GET'])
def serve_frontend_routes(path):
    """
    Serve React frontend files and handle client-side routing.
    All non-API routes serve the React app (for client-side routing).
    """
    # Don't interfere with API routes
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    # Serve static files if they exist
    if FRONTEND_BUILD_DIR.exists():
        file_path = FRONTEND_BUILD_DIR / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(FRONTEND_BUILD_DIR), path)
        
        # For client-side routing, serve index.html for all routes
        index_path = FRONTEND_BUILD_DIR / 'index.html'
        if index_path.exists():
            return send_file(str(index_path))
    
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    # Get port from environment variable (Cloud Run uses PORT, local uses 5000)
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    env = os.getenv('FLASK_ENV', 'development')
    
    print("Starting Bias Analysis API server...")
    print(f"Environment: {env}")
    print(f"Debug mode: {debug}")
    print("\nAPI endpoints:")
    print("  POST /api/graph/expand - Expand graph from starter prompt (multi-layer)")
    print("  POST /api/graph/evaluate - Evaluate bias using Gemini 2.5 Flash")
    print("  POST /api/graph/expand-node - Expand specific node")
    print("  POST /api/explain - Get SHAP explanations (HEARTS)")
    print("  GET  /api/health - Health check")
    print(f"\nServer running on port {port}")
    print(f"\nFeatures:")
    print(f"  Vertex AI (Llama + Gemini): {VERTEX_LLM_AVAILABLE}")
    print(f"  HEARTS ML Detection: {HEARTS_AGGREGATOR_AVAILABLE}")
    if HEARTS_AGGREGATOR_AVAILABLE:
        print(f"  - ALBERT-v2 stereotype detection")
        print(f"  - SHAP token-level explanations")
        print(f"  - Multi-layer ensemble scoring")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

