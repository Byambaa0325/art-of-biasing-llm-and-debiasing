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

from flask import Flask, request, jsonify
from flask_cors import CORS
from bias_detection import BiasDetector
from bias_injection import BiasInjector
from debiasing import PromptDebiaser
from dotenv import load_dotenv
import os
import uuid

# Load environment variables from .env file
load_dotenv()

# Vertex AI LLM service (for Google Cloud)
try:
    from vertex_llm_service import get_vertex_llm_service
    VERTEX_LLM_AVAILABLE = True
except Exception as e:
    VERTEX_LLM_AVAILABLE = False
    print(f"Vertex AI LLM service not available: {e}")
    print("To enable LLM features, set GOOGLE_CLOUD_PROJECT")

app = Flask(__name__)
# Allow all origins for Cloud Run deployment
CORS(app, resources={r"/api/*": {"origins": "*"}})

bias_detector = BiasDetector()
bias_injector = BiasInjector()
debiaser = PromptDebiaser()


@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    """
    Comprehensive analysis endpoint that returns:
    - Detected biases
    - Biased versions (rule-based and optionally LLM-based)
    - Debiased versions (rule-based and optionally LLM-based)
    - LLM answers comparison (if LLM is available)
    """
    data = request.get_json()
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
    result['detected_biases'] = bias_detector.detect_biases(prompt)
    
    # Generate biased versions (rule-based)
    result['biased_versions'] = bias_injector.inject_biases(prompt)
    
    # Generate LLM-based biased versions if requested
    if use_llm:
        try:
            llm = get_llm_service()
            llm_biased = llm.inject_bias_llm(prompt, "confirmation")
            result['biased_versions'].append(llm_biased)
        except Exception as e:
            result['llm_error'] = str(e)
    
    # Generate debiased versions (rule-based)
    result['debiased_versions'] = debiaser.get_all_debiasing_methods(prompt)
    
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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


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


@app.route('/api/graph/expand', methods=['POST'])
def graph_expand():
    """
    Graph-based expansion endpoint for React frontend.
    Creates a graph structure showing bias pathways from a starter prompt.
    """
    data = request.get_json()
    prompt = data.get('prompt', '')
    node_id = data.get('node_id')  # If expanding from existing node
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Detect biases
    detected_biases = bias_detector.detect_biases(prompt)
    
    # Generate nodes and edges for the graph
    nodes = []
    edges = []
    
    # Root node (original prompt)
    root_id = node_id or str(uuid.uuid4())
    nodes.append({
        'id': root_id,
        'label': prompt[:50] + '...' if len(prompt) > 50 else prompt,
        'prompt': prompt,
        'type': 'original',
        'bias_score': detected_biases.get('overall_bias_score', 0),
        'biases': detected_biases
    })
    
    # Generate biased versions (rule-based)
    biased_versions = bias_injector.inject_biases(prompt)
    for i, biased in enumerate(biased_versions):
        bias_id = str(uuid.uuid4())
        nodes.append({
            'id': bias_id,
            'label': f"Biased: {biased.get('bias_added', 'Bias')}",
            'prompt': biased.get('biased_prompt', ''),
            'type': 'biased',
            'bias_type': biased.get('bias_added', ''),
            'explanation': biased.get('explanation', ''),
            'how_it_works': biased.get('how_it_works', ''),
            'source': 'Rule-based'
        })
        edges.append({
            'id': f"{root_id}-{bias_id}",
            'source': root_id,
            'target': bias_id,
            'type': 'bias',
            'label': biased.get('bias_added', 'Bias')
        })
    
    # Generate LLM-based biased versions if available
    if VERTEX_LLM_AVAILABLE:
        try:
            llm = get_vertex_llm_service()
            llm_biased = llm.inject_bias_llm(prompt, "confirmation")
            llm_bias_id = str(uuid.uuid4())
            nodes.append({
                'id': llm_bias_id,
                'label': f"Biased (LLM): {llm_biased.get('bias_added', 'Bias')}",
                'prompt': llm_biased.get('biased_prompt', ''),
                'type': 'biased',
                'bias_type': llm_biased.get('bias_added', ''),
                'explanation': llm_biased.get('explanation', ''),
                'source': 'Vertex AI (Llama 3.3)'
            })
            edges.append({
                'id': f"{root_id}-{llm_bias_id}",
                'source': root_id,
                'target': llm_bias_id,
                'type': 'bias',
                'label': 'LLM Bias',
                'highlight': False
            })
        except Exception as e:
            print(f"LLM bias injection error: {e}")
    
    # Generate debiased versions (rule-based)
    debiased_versions = debiaser.get_all_debiasing_methods(prompt)
    for i, debiased in enumerate(debiased_versions):
        debias_id = str(uuid.uuid4())
        nodes.append({
            'id': debias_id,
            'label': f"Debiased: {debiased.get('method', 'Debias')}",
            'prompt': debiased.get('debiased_prompt', ''),
            'type': 'debiased',
            'method': debiased.get('method', ''),
            'explanation': debiased.get('explanation', ''),
            'how_it_works': debiased.get('how_it_works', ''),
            'framework': debiased.get('framework', ''),
            'source': 'Rule-based'
        })
        edges.append({
            'id': f"{root_id}-{debias_id}",
            'source': root_id,
            'target': debias_id,
            'type': 'debias',
            'label': debiased.get('method', 'Debias'),
            'highlight': True  # Always highlight debias edges
        })
    
    # Generate LLM-based debiased version if available
    if VERTEX_LLM_AVAILABLE:
        try:
            llm = get_vertex_llm_service()
            llm_debiased = llm.debias_self_help(prompt)
            llm_debias_id = str(uuid.uuid4())
            nodes.append({
                'id': llm_debias_id,
                'label': f"Debiased (LLM): {llm_debiased.get('method', 'Debias')}",
                'prompt': llm_debiased.get('debiased_prompt', ''),
                'type': 'debiased',
                'method': llm_debiased.get('method', ''),
                'explanation': llm_debiased.get('explanation', ''),
                'framework': llm_debiased.get('framework', ''),
                'source': 'Vertex AI (Llama 3.3)'
            })
            edges.append({
                'id': f"{root_id}-{llm_debias_id}",
                'source': root_id,
                'target': llm_debias_id,
                'type': 'debias',
                'label': 'LLM Debias',
                'highlight': True
            })
        except Exception as e:
            print(f"LLM debiasing error: {e}")
    
    return jsonify({
        'nodes': nodes,
        'edges': edges,
        'root_id': root_id
    })


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
def graph_expand_node():
    """
    Expand a specific node in the graph (further bias or debias).
    """
    data = request.get_json()
    node_id = data.get('node_id', '')
    prompt = data.get('prompt', '')
    action = data.get('action', 'debias')  # 'bias' or 'debias'
    bias_type = data.get('bias_type', 'confirmation')
    
    if not prompt or not node_id:
        return jsonify({'error': 'Missing node_id or prompt'}), 400
    
    nodes = []
    edges = []
    
    if action == 'debias':
        # Generate debiased version
        if VERTEX_LLM_AVAILABLE:
            try:
                llm = get_vertex_llm_service()
                debiased = llm.debias_self_help(prompt)
                new_id = str(uuid.uuid4())
                nodes.append({
                    'id': new_id,
                    'label': f"Debiased: {debiased.get('method', 'Debias')}",
                    'prompt': debiased.get('debiased_prompt', ''),
                    'type': 'debiased',
                    'method': debiased.get('method', ''),
                    'source': 'Vertex AI (Llama 3.3)'
                })
                edges.append({
                    'id': f"{node_id}-{new_id}",
                    'source': node_id,
                    'target': new_id,
                    'type': 'debias',
                    'highlight': True
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            # Fallback to rule-based
            debiased = debiaser.debias_prompt(prompt, 'comprehensive')
            new_id = str(uuid.uuid4())
            nodes.append({
                'id': new_id,
                'label': f"Debiased: {debiased.get('method', 'Debias')}",
                'prompt': debiased.get('debiased_prompt', ''),
                'type': 'debiased',
                'method': debiased.get('method', ''),
                'source': 'Rule-based'
            })
            edges.append({
                'id': f"{node_id}-{new_id}",
                'source': node_id,
                'target': new_id,
                'type': 'debias',
                'highlight': True
            })
    else:  # bias
        # Generate biased version
        if VERTEX_LLM_AVAILABLE:
            try:
                llm = get_vertex_llm_service()
                biased = llm.inject_bias_llm(prompt, bias_type)
                new_id = str(uuid.uuid4())
                nodes.append({
                    'id': new_id,
                    'label': f"Biased: {biased.get('bias_added', 'Bias')}",
                    'prompt': biased.get('biased_prompt', ''),
                    'type': 'biased',
                    'bias_type': biased.get('bias_added', ''),
                    'source': 'Vertex AI (Llama 3.3)'
                })
                edges.append({
                    'id': f"{node_id}-{new_id}",
                    'source': node_id,
                    'target': new_id,
                    'type': 'bias',
                    'highlight': False
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            # Fallback to rule-based
            biased_versions = bias_injector.inject_biases(prompt)
            if biased_versions:
                biased = biased_versions[0]
                new_id = str(uuid.uuid4())
                nodes.append({
                    'id': new_id,
                    'label': f"Biased: {biased.get('bias_added', 'Bias')}",
                    'prompt': biased.get('biased_prompt', ''),
                    'type': 'biased',
                    'bias_type': biased.get('bias_added', ''),
                    'source': 'Rule-based'
                })
                edges.append({
                    'id': f"{node_id}-{new_id}",
                    'source': node_id,
                    'target': new_id,
                    'type': 'bias',
                    'highlight': False
                })
    
    return jsonify({
        'nodes': nodes,
        'edges': edges
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Bias Analysis API',
        'version': '2.0',
        'vertex_llm_available': VERTEX_LLM_AVAILABLE,
        'endpoints': {
            'POST /api/graph/expand': 'Expand graph from starter prompt',
            'POST /api/graph/evaluate': 'Evaluate bias using Gemini 2.5 Flash',
            'POST /api/graph/expand-node': 'Expand specific node (bias/debias)',
            'POST /api/analyze': 'Full analysis (legacy)',
            'GET /api/health': 'Health check'
        }
    })


if __name__ == '__main__':
    # Get port from environment variable (Cloud Run uses PORT, local uses 5000)
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    env = os.getenv('FLASK_ENV', 'development')
    
    print("Starting Bias Analysis API server...")
    print(f"Environment: {env}")
    print(f"Debug mode: {debug}")
    print("\nAPI endpoints:")
    print("  POST /api/graph/expand - Expand graph from starter prompt")
    print("  POST /api/graph/evaluate - Evaluate bias using Gemini 2.5 Flash")
    print("  POST /api/graph/expand-node - Expand specific node")
    print("  GET  /api/health - Health check")
    print(f"\nServer running on port {port}")
    print(f"Vertex AI available: {VERTEX_LLM_AVAILABLE}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

