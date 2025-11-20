"""
Vertex AI LLM Service Module

Provides LLM integration using Google Cloud Vertex AI:
- Llama 3.3 for prompt generation (bias injection, debiasing)
- Gemini 2.5 Flash for bias evaluation

Designed for Google Cloud Run deployment.
"""

import os
import json
import re
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import requests for REST API calls
try:
    import requests
    import subprocess
    import json
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

# Try to import Vertex AI (for Gemini, optional)
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_SDK_AVAILABLE = True
except ImportError:
    VERTEX_AI_SDK_AVAILABLE = False

# Try to import Gemini API (for evaluation, optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class VertexLLMService:
    """
    LLM service using Google Cloud Vertex AI.
    
    Uses:
    - Llama 3.3 for prompt generation (bias injection, debiasing)
    - Gemini 2.5 Flash for bias evaluation
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        llama_model: str = "meta/llama-3.3-70b-instruct-maas",
        gemini_model: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize Vertex AI service using REST API.
        
        Args:
            project_id: GCP project ID (from env if not provided)
            location: GCP region
            llama_model: Llama model name for generation (default: meta/llama-3.3-70b-instruct-maas)
            gemini_model: Gemini model name for evaluation
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests library not available. Install with: pip install requests"
            )
        
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT or GCP_PROJECT_ID must be set. "
                "Set it in .env file or as environment variable."
            )
        
        self.location = location or os.getenv("GCP_LOCATION", "us-central1")
        self.llama_model_name = llama_model or os.getenv("LLAMA_MODEL", "meta/llama-3.3-70b-instruct-maas")
        self.gemini_model_name = gemini_model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        # Set up REST API endpoint
        self.endpoint = f"{self.location}-aiplatform.googleapis.com"
        self.llama_api_url = (
            f"https://{self.endpoint}/v1/projects/{self.project_id}/locations/{self.location}/"
            f"endpoints/openapi/chat/completions"
        )
        
        # Initialize Gemini for evaluation (try Vertex AI SDK first, then REST API)
        self.gemini_model = None
        if VERTEX_AI_SDK_AVAILABLE:
            try:
                vertexai.init(project=self.project_id, location=self.location)
                gemini_path = f"publishers/google/models/{self.gemini_model_name}"
                self.gemini_model = GenerativeModel(gemini_path)
            except Exception as e:
                print(f"Warning: Could not initialize Gemini via Vertex AI SDK: {e}")
        
        # Fallback to Gemini API if SDK not available
        if not self.gemini_model and GEMINI_AVAILABLE:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                try:
                    genai.configure(api_key=gemini_api_key)
                    self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
                except Exception as e:
                    print(f"Warning: Could not initialize Gemini API: {e}")
    
    def _get_access_token(self) -> str:
        """
        Get Google Cloud access token.
        
        Tries multiple methods:
        1. gcloud CLI (for local development)
        2. Application Default Credentials (for Cloud Run)
        
        Returns:
            Access token string
        """
        # Try gcloud CLI first (for local development)
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback to Application Default Credentials (for Cloud Run)
            try:
                from google.auth import default
                from google.auth.transport.requests import Request
                
                credentials, project = default()
                if credentials.requires_scopes:
                    credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
                
                # Refresh credentials if needed
                if not credentials.valid:
                    credentials.refresh(Request())
                
                return credentials.token
            except Exception as e:
                raise Exception(
                    f"Failed to get access token. "
                    f"For local: run 'gcloud auth application-default login'. "
                    f"For Cloud Run: ensure service account has proper permissions. "
                    f"Error: {str(e)}"
                )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        model_override: Optional[str] = None
    ) -> str:
        """
        Generate text using specified model (default: Llama 3.3).
        Supports both OpenAPI endpoint models and Vertex AI SDK models.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            model_override: Optional model ID to use instead of default

        Returns:
            Generated text
        """
        # Import model config
        try:
            from model_config import get_model_info, is_valid_model
        except ImportError:
            from .model_config import get_model_info, is_valid_model

        # Determine which model to use
        model_id = model_override or self.llama_model_name

        # Validate model
        if not is_valid_model(model_id):
            raise ValueError(f"Invalid model ID: {model_id}")

        model_info = get_model_info(model_id)
        endpoint_type = model_info.get('endpoint_type', 'openapi')

        # Route to appropriate generation method
        if endpoint_type == 'openapi':
            return self._generate_openapi(model_id, prompt, system_prompt, temperature, max_tokens)
        elif endpoint_type == 'vertex_sdk':
            return self._generate_vertex_sdk(model_id, prompt, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported endpoint type: {endpoint_type}")

    def _generate_openapi(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAPI endpoint (for Llama models)."""
        # Build messages array
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare request payload
        payload = {
            "model": model_id,
            "stream": False,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Get access token
        access_token = self._get_access_token()

        # Make API request
        try:
            response = requests.post(
                self.llama_api_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Extract content from response
            # Response format: {"choices": [{"message": {"content": "..."}}]}
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                return content.strip()
            else:
                raise Exception(f"Unexpected response format: {result}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenAPI request failed for {model_id}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")

    def _generate_vertex_sdk(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Vertex AI SDK (for Claude, Mistral, Gemini models)."""
        if not VERTEX_AI_SDK_AVAILABLE:
            raise Exception("Vertex AI SDK not available. Install with: pip install google-cloud-aiplatform")

        try:
            # Initialize model
            if not hasattr(vertexai, '_initialized') or not vertexai._initialized:
                vertexai.init(project=self.project_id, location=self.location)
                vertexai._initialized = True

            # Determine model path
            if 'mistral' in model_id:
                model_path = f"publishers/mistralai/models/{model_id}"
            elif 'gemini' in model_id:
                model_path = f"publishers/google/models/{model_id}"
            else:
                model_path = model_id

            model = GenerativeModel(model_path)

            # Build prompt with system instructions if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Generate content
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )

            return response.text.strip()

        except Exception as e:
            raise Exception(f"Vertex SDK generation failed for {model_id}: {str(e)}")
    
    def inject_bias_llm(self, prompt: str, bias_type: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Use LLM to inject bias into a prompt using instruction-based approach.

        Args:
            prompt: Original prompt
            bias_type: Type of bias to inject (e.g., 'confirmation_bias', 'anchoring_bias')
            model_id: Optional model ID to use (default: Llama 3.3)

        Returns:
            Dictionary with biased prompt and metadata
        """
        # Import here to avoid circular dependencies
        try:
            from bias_instructions import get_bias_instruction, BIAS_INSTRUCTIONS
        except ImportError:
            try:
                from .bias_instructions import get_bias_instruction, BIAS_INSTRUCTIONS
            except ImportError:
                # Fallback to simple approach if instructions not available
                return self._inject_bias_simple(prompt, bias_type, model_id)

        # Get instruction guide
        instruction = get_bias_instruction(bias_type)
        if not instruction:
            raise ValueError(f"Unknown bias type: {bias_type}. Available types: {list(BIAS_INSTRUCTIONS.keys())}")

        # Build comprehensive system prompt with instructions
        examples_text = "\n\n".join([
            f"Example {i+1}:\nOriginal: {ex['original']}\nBiased: {ex['biased']}"
            for i, ex in enumerate(instruction['examples'])
        ])

        techniques_text = "\n".join([f"  • {technique}" for technique in instruction['techniques']])

        system_prompt = f"""You are an expert in bias analysis and prompt engineering.

Your task is to modify a prompt to introduce {instruction['name']}.

DESCRIPTION:
{instruction['description']}

TECHNIQUES TO USE:
{techniques_text}

EXAMPLES:
{examples_text}

RESEARCH FRAMEWORK:
{instruction['framework']}

CRITICAL REQUIREMENTS:
1. Make the biased version sound NATURAL and grammatically correct
2. Don't use obvious templates - be creative and subtle
3. The bias should be effective but not crude or forced
4. Preserve the core intent and question while introducing the bias
5. Maintain fluency - it should read like a naturally written prompt
6. Return ONLY the biased prompt - no explanation, no preamble, no extra text

Your response must be ONLY the biased prompt."""

        user_prompt = f"Original prompt: {prompt}\n\nCreate a naturally biased version with {instruction['name']}:"

        try:
            biased_prompt = self.generate(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,  # Higher for creativity
                max_tokens=500,
                model_override=model_id
            )

            # Clean up the response (remove any explanation if LLM added it)
            biased_prompt = biased_prompt.strip()

            # Remove common prefixes if LLM added them
            for prefix in ["Biased prompt:", "Biased version:", "Here is", "Here's"]:
                if biased_prompt.lower().startswith(prefix.lower()):
                    biased_prompt = biased_prompt[len(prefix):].strip().lstrip(':').strip()

            # Get model name for display
            try:
                from model_config import get_model_info
                model_info = get_model_info(model_id or self.llama_model_name)
                model_display = model_info['name'] if model_info else (model_id or 'Llama 3.3')
            except:
                model_display = model_id or 'Llama 3.3'

            return {
                'biased_prompt': biased_prompt,
                'bias_added': instruction['name'],
                'bias_type': bias_type,
                'explanation': instruction['description'],
                'framework': instruction['framework'],
                'severity': instruction.get('severity', 'medium'),
                'source': f'LLM-based ({model_display})',
                'model_id': model_id or self.llama_model_name,
                'instruction_based': True
            }

        except Exception as e:
            raise Exception(f"Bias injection failed: {str(e)}")

    def _inject_bias_simple(self, prompt: str, bias_type: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Fallback simple bias injection if instructions not available"""
        system_prompt = f"""You are an expert in cognitive bias and language analysis.
Your task is to modify a user's prompt to introduce {bias_type}, while keeping the core question intact.
Make the modification subtle but effective.
Return only the modified prompt, without explanation."""

        biased_prompt = self.generate(
            f"Original prompt: {prompt}\n\nCreate a biased version that introduces {bias_type}:",
            system_prompt=system_prompt,
            temperature=0.8,
            model_override=model_id
        )

        # Get model name for display
        try:
            from model_config import get_model_info
            model_info = get_model_info(model_id or self.llama_model_name)
            model_display = model_info['name'] if model_info else (model_id or 'Llama 3.3')
        except:
            model_display = model_id or 'Llama 3.3'

        return {
            'biased_prompt': biased_prompt.strip(),
            'bias_added': f'{bias_type.replace("_", " ").title()}',
            'bias_type': bias_type,
            'explanation': f'LLM-generated version introducing {bias_type}.',
            'source': f'Vertex AI ({model_display})',
            'model_id': model_id or self.llama_model_name,
            'instruction_based': False
        }
    
    def debias_self_help(self, prompt: str, method: str = 'auto', model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Use LLM for debiasing using instruction-based approach.

        Args:
            prompt: Potentially biased prompt
            method: Debiasing method or 'auto' to auto-detect (default: 'auto')
            model_id: Optional model ID to use (default: Llama 3.3)

        Returns:
            Dictionary with debiased prompt and metadata
        """
        # Import here to avoid circular dependencies
        try:
            from bias_instructions import get_debias_instruction, get_available_debias_methods
            from bias_detection import BiasDetector
        except ImportError:
            try:
                from .bias_instructions import get_debias_instruction, get_available_debias_methods
                from .bias_detection import BiasDetector
            except ImportError:
                # Fallback to simple approach
                return self._debias_simple(prompt, model_id)

        # Auto-detect method if needed
        if method == 'auto':
            try:
                detector = BiasDetector()
                detected = detector.detect_biases(prompt)
                methods = get_available_debias_methods(detected)
                method = methods[0]['method'] if methods else 'neutralize_language'
            except Exception:
                method = 'comprehensive'  # Default to comprehensive

        # Get instruction guide
        instruction = get_debias_instruction(method)
        if not instruction:
            # Fallback to comprehensive if method not found
            instruction = get_debias_instruction('comprehensive')
            if not instruction:
                return self._debias_simple(prompt, model_id)

        # Build comprehensive system prompt with instructions
        examples_text = "\n\n".join([
            f"Example {i+1}:\nBiased: {ex['biased']}\nDebiased: {ex['debiased']}"
            for i, ex in enumerate(instruction['examples'])
        ])

        techniques_text = "\n".join([f"  • {technique}" for technique in instruction['techniques']])

        system_prompt = f"""You are an expert in fair and unbiased communication.

Your task is to remove bias from a prompt using the {instruction['name']} approach.

DESCRIPTION:
{instruction['description']}

TECHNIQUES TO USE:
{techniques_text}

EXAMPLES:
{examples_text}

RESEARCH FRAMEWORK:
{instruction['framework']}

CRITICAL REQUIREMENTS:
1. Make the debiased version sound natural and fluent
2. Preserve the core question and intent
3. Remove ALL bias indicators identified in the techniques
4. Keep the prompt clear, concise, and useful
5. Maintain grammatical correctness
6. Return ONLY the debiased prompt - no explanation, no preamble

Your response must be ONLY the debiased prompt."""

        user_prompt = f"Biased prompt: {prompt}\n\nCreate a debiased version using {instruction['name']}:"

        try:
            debiased_prompt = self.generate(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower for consistency
                max_tokens=500,
                model_override=model_id
            )

            # Clean up the response
            debiased_prompt = debiased_prompt.strip()

            # Remove common prefixes if LLM added them
            for prefix in ["Debiased prompt:", "Debiased version:", "Here is", "Here's", "Neutral prompt:"]:
                if debiased_prompt.lower().startswith(prefix.lower()):
                    debiased_prompt = debiased_prompt[len(prefix):].strip().lstrip(':').strip()

            # Get model name for display
            try:
                from model_config import get_model_info
                model_info = get_model_info(model_id or self.llama_model_name)
                model_display = model_info['name'] if model_info else (model_id or 'Llama 3.3')
            except:
                model_display = model_id or 'Llama 3.3'

            return {
                'debiased_prompt': debiased_prompt,
                'method': instruction['name'],
                'debias_method': method,
                'explanation': instruction['description'],
                'framework': instruction['framework'],
                'effectiveness': instruction.get('effectiveness', 'high'),
                'source': f'LLM-based ({model_display})',
                'model_id': model_id or self.llama_model_name,
                'instruction_based': True
            }

        except Exception as e:
            raise Exception(f"Debiasing failed: {str(e)}")

    def _debias_simple(self, prompt: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Fallback simple debiasing if instructions not available"""
        system_prompt = """You are an expert in fair and unbiased communication.
Your task is to rewrite a user's prompt to remove any potential biases while preserving the core question.
Remove leading questions, stereotypes, assumptions, and any language that might introduce bias.
Make the prompt neutral, fair, and clear.
Return only the debiased prompt, without explanation."""

        debiased_prompt = self.generate(
            f"Rewrite this prompt to be neutral and unbiased:\n\n{prompt}",
            system_prompt=system_prompt,
            temperature=0.3,
            model_override=model_id
        )

        # Get model name for display
        try:
            from model_config import get_model_info
            model_info = get_model_info(model_id or self.llama_model_name)
            model_display = model_info['name'] if model_info else (model_id or 'Llama 3.3')
        except:
            model_display = model_id or 'Llama 3.3'

        return {
            'debiased_prompt': debiased_prompt.strip(),
            'method': 'General Debiasing',
            'debias_method': 'comprehensive',
            'explanation': 'LLM-based debiasing to remove bias and make prompt neutral.',
            'framework': 'BiasBuster (Echterhoff et al., 2024)',
            'source': f'Vertex AI ({model_display})',
            'model_id': model_id or self.llama_model_name,
            'instruction_based': False
        }
    
    def evaluate_bias(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Use Gemini 2.5 Flash to evaluate bias in a prompt.
        
        Args:
            prompt: Prompt to evaluate
            context: Optional context about the prompt
            
        Returns:
            Dictionary with bias evaluation results
        """
        if not self.gemini_model:
            raise ValueError("Gemini model not available for evaluation")
        
        evaluation_prompt = f"""Evaluate the following prompt for potential biases. Consider:
1. Demographic biases (race, gender, age, religion, etc.)
2. Cognitive biases (confirmation, anchoring, framing, etc.)
3. Language-level biases (stereotypes, assumptions, leading questions)

Prompt to evaluate: "{prompt}"

{f'Context: {context}' if context else ''}

Provide a JSON response with:
- bias_score: 0-1 (0 = no bias, 1 = high bias)
- bias_types: list of detected bias types
- severity: "low", "moderate", or "high"
- explanation: brief explanation
- recommendations: suggestions for debiasing"""
        
        try:
            response = self.gemini_model.generate_content(
                evaluation_prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                }
            )
            
            # Parse response (Gemini may return JSON or text)
            result_text = response.text.strip()
            
            # Try to extract JSON if present
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except:
                    result = self._parse_text_evaluation(result_text)
            else:
                result = self._parse_text_evaluation(result_text)
            
            return {
                'prompt': prompt,
                'evaluation': result,
                'model': 'Gemini 2.5 Flash',
                'source': 'Vertex AI (Gemini 2.5 Flash)'
            }
        except Exception as e:
            raise Exception(f"Gemini evaluation error: {str(e)}")
    
    def _parse_text_evaluation(self, text: str) -> Dict[str, Any]:
        """Parse text evaluation response into structured format"""
        # Simple parsing - can be improved
        bias_score = 0.5  # Default
        bias_types = []
        severity = "moderate"
        
        # Try to extract score
        import re
        score_match = re.search(r'(?:bias[_\s]*score|score)[:\s]*([0-9.]+)', text, re.IGNORECASE)
        if score_match:
            bias_score = float(score_match.group(1))
        
        # Extract severity
        if 'high' in text.lower():
            severity = "high"
            bias_score = max(bias_score, 0.7)
        elif 'low' in text.lower():
            severity = "low"
            bias_score = min(bias_score, 0.3)
        
        return {
            'bias_score': bias_score,
            'bias_types': bias_types,
            'severity': severity,
            'explanation': text,
            'recommendations': 'Review the prompt for potential biases.'
        }
    
    def generate_answer(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate an answer to a prompt using Llama 3.3.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            
        Returns:
            LLM-generated answer
        """
        default_system = "You are a helpful assistant. Provide clear, informative answers."
        return self.generate(
            prompt,
            system_prompt=system_prompt or default_system,
            temperature=0.7
        )


# Global service instance
_vertex_llm_service: Optional[VertexLLMService] = None


def get_vertex_llm_service() -> VertexLLMService:
    """
    Get or create the global Vertex AI LLM service instance.
    
    Environment variables (loaded from .env file):
    - GOOGLE_CLOUD_PROJECT or GCP_PROJECT_ID: GCP project ID (required)
    - GCP_LOCATION: GCP region (default: "us-central1")
    - LLAMA_MODEL: Llama model name (default: "meta/llama-3.3-70b-instruct-maas")
    - GEMINI_MODEL: Gemini model name (default: "gemini-2.0-flash-exp")
    - GEMINI_API_KEY: Optional, for Gemini API (if not using Vertex AI endpoint)
    """
    global _vertex_llm_service
    
    if _vertex_llm_service is None:
        location = os.getenv("GCP_LOCATION", "us-central1")
        llama_model = os.getenv("LLAMA_MODEL", "meta/llama-3.3-70b-instruct-maas")
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        _vertex_llm_service = VertexLLMService(
            location=location,
            llama_model=llama_model,
            gemini_model=gemini_model
        )
    
    return _vertex_llm_service

