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
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using Llama 3.3 via REST API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # Build messages array
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": self.llama_model_name,
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
            raise Exception(f"Llama 3.3 API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def inject_bias_llm(self, prompt: str, bias_type: str) -> Dict[str, Any]:
        """
        Use Llama 3.3 to inject bias into a prompt.
        
        Args:
            prompt: Original prompt
            bias_type: Type of bias to inject
            
        Returns:
            Dictionary with biased prompt and explanation
        """
        system_prompt = f"""You are an expert in cognitive bias and language analysis. 
Your task is to modify a user's prompt to introduce {bias_type} bias, while keeping the core question intact.
Make the modification subtle but effective - the bias should influence how an LLM would respond.
Return only the modified prompt, without explanation."""
        
        biased_prompt = self.generate(
            f"Original prompt: {prompt}\n\nCreate a biased version that introduces {bias_type} bias:",
            system_prompt=system_prompt,
            temperature=0.8
        )
        
        return {
            'type': f'{bias_type}_bias_llm',
            'biased_prompt': biased_prompt,
            'bias_added': f'{bias_type.capitalize()} Bias (LLM-generated)',
            'explanation': f'Llama 3.3-generated version introducing {bias_type} bias.',
            'how_it_works': f'Llama 3.3 analyzed the original prompt and generated a version that introduces {bias_type} bias.',
            'source': 'Vertex AI (Llama 3.3)'
        }
    
    def debias_self_help(self, prompt: str) -> Dict[str, Any]:
        """
        Use Llama 3.3 for self-help debiasing (BiasBuster method).
        
        Args:
            prompt: Potentially biased prompt
            
        Returns:
            Dictionary with debiased prompt and explanation
        """
        system_prompt = """You are an expert in fair and unbiased communication. 
Your task is to rewrite a user's prompt to remove any potential biases while preserving the core question.
Remove leading questions, stereotypes, assumptions, and any language that might introduce bias.
Make the prompt neutral, fair, and clear."""
        
        debiased_prompt = self.generate(
            f"Rewrite this prompt to be neutral and unbiased:\n\n{prompt}",
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        return {
            'method': 'Self-Help Debiasing (LLM)',
            'debiased_prompt': debiased_prompt,
            'explanation': 'Llama 3.3-based self-help debiasing (BiasBuster method).',
            'how_it_works': 'Llama 3.3 analyzes the prompt and rewrites it to be neutral and unbiased.',
            'framework': 'BiasBuster (Echterhoff et al., 2024)',
            'source': 'Vertex AI (Llama 3.3)'
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

