"""
LLM Service Module

Provides LLM integration for:
- Bias injection (LLM-generated biased prompts)
- Debiasing (LLM-based self-help debiasing, inspired by BiasBuster)
- Answer generation (comparing original vs modified prompts)

Supports multiple LLM providers:
- OpenAI API (recommended for public demo)
- Local models via Ollama (cost-effective alternative)
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import requests for Ollama
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class LLMService:
    """
    LLM service for bias injection, debiasing, and answer generation.
    
    Supports:
    - OpenAI API (GPT-3.5, GPT-4, etc.)
    - Local models via Ollama (Llama, Mistral, etc.)
    """
    
    def __init__(self, provider: str = "openai", model: str = None):
        """
        Initialize LLM service.
        
        Args:
            provider: "openai" or "ollama"
            model: Model name (e.g., "gpt-3.5-turbo", "llama2", "mistral")
        """
        self.provider = provider.lower()
        self.model = model or self._get_default_model()
        self.client = None
        
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        if self.provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        elif self.provider == "ollama":
            return os.getenv("OLLAMA_MODEL", "llama2")
        return "gpt-3.5-turbo"
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.base_url = None
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package not installed. Install with: pip install requests")
        
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.client = None  # Ollama uses HTTP requests
        
        # Test connection
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self.ollama_url}. Make sure Ollama is running.")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-2)
            
        Returns:
            Generated text
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, temperature)
        elif self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt, temperature)
    
    def _generate_openai(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Generate using OpenAI API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Generate using Ollama API"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def inject_bias_llm(self, prompt: str, bias_type: str) -> Dict[str, Any]:
        """
        Use LLM to inject bias into a prompt (inspired by research on cognitive bias injection).
        
        Args:
            prompt: Original prompt
            bias_type: Type of bias to inject (e.g., "confirmation", "demographic", "anchoring")
            
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
            'explanation': f'LLM-generated version introducing {bias_type} bias. This demonstrates how AI can be used to create biased prompts.',
            'how_it_works': f'An LLM analyzed the original prompt and generated a version that introduces {bias_type} bias, showing how language models can be used to create biased content.'
        }
    
    def debias_self_help(self, prompt: str) -> Dict[str, Any]:
        """
        Use LLM for self-help debiasing (BiasBuster method).
        The LLM paraphrases the biased question neutrally.
        
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
            temperature=0.3  # Lower temperature for more consistent debiasing
        )
        
        return {
            'method': 'Self-Help Debiasing (LLM)',
            'debiased_prompt': debiased_prompt,
            'explanation': 'LLM-based self-help debiasing (BiasBuster method). The model automatically identifies and removes bias-inducing language from the prompt.',
            'how_it_works': 'The LLM analyzes the prompt and rewrites it to be neutral and unbiased, removing leading questions, stereotypes, and assumptions. This is inspired by BiasBuster (Echterhoff et al., 2024).',
            'framework': 'BiasBuster (Echterhoff et al., 2024)'
        }
    
    def generate_answer(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate an answer to a prompt using the LLM.
        Used to compare responses from original vs. modified prompts.
        
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


# Global LLM service instance (lazy initialization)
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.
    
    Environment variables:
    - LLM_PROVIDER: "openai" or "ollama" (default: "openai")
    - LLM_MODEL: Model name (default: "gpt-3.5-turbo" for OpenAI, "llama2" for Ollama)
    - OPENAI_API_KEY: Required for OpenAI provider
    - OLLAMA_URL: Ollama server URL (default: "http://localhost:11434")
    """
    global _llm_service
    
    if _llm_service is None:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        model = os.getenv("LLM_MODEL")
        _llm_service = LLMService(provider=provider, model=model)
    
    return _llm_service


if __name__ == "__main__":
    # Example usage
    service = get_llm_service()
    
    # Test debiasing
    biased_prompt = "Why are teenagers so bad at making decisions?"
    debiased = service.debias_self_help(biased_prompt)
    print("Debiased:", debiased['debiased_prompt'])
    
    # Test answer generation
    answer = service.generate_answer(biased_prompt)
    print("Answer:", answer)

