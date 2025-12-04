"""
Bedrock LLM Service Module

Provides LLM integration using AWS Bedrock Proxy API:
- Claude models for prompt generation (bias injection, debiasing) and evaluation
- All Bedrock models for answer generation

Supports all Bedrock models including Claude, Llama, Nova, Mistral, and DeepSeek.
"""

import os
import json
import re
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Bedrock client
try:
    from bedrock_client import BedrockClient, BedrockModels, load_env_file
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: bedrock_client not available. Install dependencies.")

# Load Bedrock credentials
try:
    # Try to load from parent directory or current directory
    import sys
    from pathlib import Path
    parent_env = Path(__file__).parent.parent / ".env.bedrock"
    current_env = Path(__file__).parent / ".env.bedrock"
    
    if parent_env.exists():
        load_env_file(str(parent_env))
    elif current_env.exists():
        load_env_file(str(current_env))
    else:
        load_env_file(".env.bedrock")
except Exception as e:
    print(f"Warning: Could not load Bedrock credentials: {e}")


class BedrockLLMService:
    """
    LLM service using AWS Bedrock Proxy API.
    
    Uses:
    - Claude models for prompt generation (bias injection, debiasing) and evaluation
    - All Bedrock models for answer generation
    """
    
    def __init__(
        self,
        default_model: Optional[str] = None,
        evaluation_model: Optional[str] = None
    ):
        """
        Initialize Bedrock service.
        
        Args:
            default_model: Default model for generation (defaults to Claude 3.5 Sonnet)
            evaluation_model: Model for bias evaluation (defaults to Claude 3.5 Sonnet)
        """
        if not BEDROCK_AVAILABLE:
            raise ImportError(
                "Bedrock client not available. Make sure bedrock_client.py is available."
            )
        
        try:
            self.client = BedrockClient()
        except Exception as e:
            raise ValueError(
                f"Could not initialize Bedrock client: {e}. "
                "Make sure BEDROCK_TEAM_ID and BEDROCK_API_TOKEN are set."
            )
        
        # Default to Claude 3.5 Sonnet for generation and evaluation
        self.default_model = default_model or os.getenv(
            "BEDROCK_DEFAULT_MODEL",
            BedrockModels.CLAUDE_3_5_SONNET_V2
        )
        self.evaluation_model = evaluation_model or os.getenv(
            "BEDROCK_EVALUATION_MODEL",
            BedrockModels.CLAUDE_3_5_SONNET_V2
        )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        model_override: Optional[str] = None
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            model_override: Override default model
            
        Returns:
            Generated text
        """
        model = model_override or self.default_model
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.invoke(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract text from response
            # Bedrock response format: {"content": [{"text": "..."}], "metadata": {...}}
            # Use the same pattern as bedrock_client.chat() method: response["content"][0]["text"]
            if isinstance(response, dict):
                try:
                    # Direct extraction like chat() method
                    text = response["content"][0]["text"]
                    if text:
                        return text
                except (KeyError, IndexError, TypeError) as e:
                    # If direct extraction fails, try fallback methods
                    content = response.get("content", [])
                    if isinstance(content, list) and len(content) > 0:
                        first_item = content[0]
                        if isinstance(first_item, dict):
                            text = first_item.get("text", "")
                            if text:
                                return text
                        elif isinstance(first_item, str):
                            return first_item
                    # Last resort: return error message
                    raise Exception(f"Could not extract text from response. Response structure: {response}")
            else:
                raise Exception(f"Unexpected response type: {type(response)}, value: {response}")
        except Exception as e:
            raise Exception(f"Bedrock generation failed: {str(e)}")
    
    def generate_answer(self, prompt: str, model_id: Optional[str] = None) -> str:
        """
        Generate an answer for a prompt.
        
        Args:
            prompt: The prompt to answer
            model_id: Optional model ID to use
            
        Returns:
            Generated answer
        """
        model = model_id or self.default_model
        
        system_prompt = "You are a helpful assistant. Provide clear, accurate, and concise answers."
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1024,
            model_override=model
        )
    
    def inject_bias_llm(
        self,
        prompt: str,
        bias_type: str,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use LLM to inject bias into a prompt.
        
        Args:
            prompt: Original prompt
            bias_type: Type of bias to inject (e.g., 'confirmation', 'anchoring')
            model_id: Optional model ID to use
            
        Returns:
            Dictionary with biased prompt and metadata
        """
        # Import bias instructions
        try:
            from bias_instructions import get_bias_instruction
        except ImportError:
            from .bias_instructions import get_bias_instruction
        
        instruction = get_bias_instruction(bias_type)
        if not instruction:
            # Fallback to generic bias injection
            instruction = {
                'name': bias_type,
                'description': f'Introduce {bias_type} bias',
                'techniques': ['Use leading questions', 'Add assumptions', 'Include loaded language'],
                'examples': [],
                'framework': 'Generic bias injection'
            }
        
        examples_text = "\n\n".join([
            f"Example {i+1}:\nOriginal: {ex['original']}\nBiased: {ex['biased']}"
            for i, ex in enumerate(instruction['examples'])
        ]) if instruction.get('examples') else "No examples provided."
        
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
            
            # Clean up the response
            biased_prompt = biased_prompt.strip()
            
            # Remove common prefixes if LLM added them
            for prefix in ["Biased prompt:", "Biased version:", "Here is", "Here's"]:
                if biased_prompt.lower().startswith(prefix.lower()):
                    biased_prompt = biased_prompt[len(prefix):].strip()
                    # Remove colon if present
                    if biased_prompt.startswith(":"):
                        biased_prompt = biased_prompt[1:].strip()
            
            # Get model name for display
            try:
                from model_config import get_model_info
                model_info = get_model_info(model_id or self.default_model)
                model_display = model_info['name'] if model_info else (model_id or 'Claude 3.5 Sonnet')
            except:
                model_display = model_id or 'Claude 3.5 Sonnet'
            
            return {
                'biased_prompt': biased_prompt,
                'bias_added': instruction['name'],
                'bias_type': bias_type,
                'explanation': f'LLM-based bias injection using {instruction["framework"]}',
                'framework': instruction['framework'],
                'source': f'Bedrock ({model_display})',
                'model_id': model_id or self.default_model,
                'instruction_based': True
            }
        except Exception as e:
            raise Exception(f"Bias injection failed: {str(e)}")
    
    def debias_self_help(
        self,
        prompt: str,
        method: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use LLM for self-help debiasing (BiasBuster method).
        
        Args:
            prompt: Original prompt
            method: Optional debiasing method (currently not used, kept for compatibility)
            model_id: Optional model ID to use
            
        Returns:
            Dictionary with debiased prompt and metadata
        """
        system_prompt = """You are an expert in bias detection and prompt normalization.

Your task is to rewrite a prompt to remove bias and make it neutral, fair, and objective.

CRITICAL REQUIREMENTS:
1. Preserve the core intent and question
2. Remove loaded language, assumptions, and leading questions
3. Make the prompt neutral and balanced
4. Maintain grammatical correctness and fluency
5. Return ONLY the debiased prompt - no explanation, no preamble, no extra text

Your response must be ONLY the debiased prompt."""
        
        user_prompt = f"Original prompt: {prompt}\n\nCreate a neutral, unbiased version:"
        
        try:
            debiased_prompt = self.generate(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500,
                model_override=model_id
            )
            
            # Clean up the response
            debiased_prompt = debiased_prompt.strip()
            
            # Remove common prefixes if LLM added them
            for prefix in ["Debiased prompt:", "Neutral version:", "Here is", "Here's"]:
                if debiased_prompt.lower().startswith(prefix.lower()):
                    debiased_prompt = debiased_prompt[len(prefix):].strip()
                    if debiased_prompt.startswith(":"):
                        debiased_prompt = debiased_prompt[1:].strip()
            
            # Get model name for display
            try:
                from model_config import get_model_info
                model_info = get_model_info(model_id or self.default_model)
                model_display = model_info['name'] if model_info else (model_id or 'Claude 3.5 Sonnet')
            except:
                model_display = model_id or 'Claude 3.5 Sonnet'
            
            return {
                'debiased_prompt': debiased_prompt,
                'method': 'Self-Help Debiasing',
                'debias_method': 'comprehensive',
                'explanation': 'LLM-based debiasing to remove bias and make prompt neutral.',
                'framework': 'BiasBuster (Echterhoff et al., 2024)',
                'source': f'Bedrock ({model_display})',
                'model_id': model_id or self.default_model,
                'instruction_based': False
            }
        except Exception as e:
            raise Exception(f"Debiasing failed: {str(e)}")
    
    def evaluate_bias(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Claude to evaluate bias in a prompt with zero-shot prompting.
        
        Args:
            prompt: Prompt to evaluate
            context: Optional context about the prompt
            
        Returns:
            Dictionary with bias evaluation results including scores and bias types
        """
        evaluation_prompt = f"""You are an expert in bias detection and analysis. Evaluate the following prompt for various types of bias.

PROMPT TO EVALUATE:
{prompt}

{f"CONTEXT: {context}" if context else ""}

Evaluate this prompt across the following bias categories:
1. Confirmation Bias - Does it lead toward a specific answer?
2. Anchoring Bias - Does it anchor to specific information?
3. Framing Bias - Is the question framed in a biased way?
4. Availability Bias - Does it rely on easily recalled examples?
5. Stereotyping - Does it contain stereotypes?
6. Cultural Bias - Does it assume cultural norms?
7. Gender Bias - Does it contain gender assumptions?
8. Racial/Ethnic Bias - Does it contain racial/ethnic assumptions?
9. Socioeconomic Bias - Does it assume socioeconomic status?
10. Cognitive Bias - General cognitive biases

For each category, provide:
- A score from 0.0 (no bias) to 1.0 (high bias)
- A brief explanation (1-2 sentences)
- Whether the bias is present (true/false)

Also provide:
- Overall bias score (0.0 to 1.0)
- Severity level (none, low, medium, high, severe)
- List of detected bias types
- Overall explanation
- Recommendations for improvement

Return your response as a JSON object with this structure:
{{
    "bias_scores": {{
        "confirmation_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "anchoring_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "framing_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "availability_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "stereotyping": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "cultural_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "gender_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "racial_ethnic_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "socioeconomic_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}},
        "cognitive_bias": {{"score": 0.0-1.0, "present": true/false, "explanation": "..."}}
    }},
    "overall_bias_score": 0.0-1.0,
    "severity": "none|low|medium|high|severe",
    "detected_bias_types": ["type1", "type2", ...],
    "explanation": "Overall explanation of bias in the prompt",
    "recommendations": "Recommendations for reducing bias"
}}"""
        
        try:
            response_text = self.generate(
                evaluation_prompt,
                system_prompt="You are an expert bias analyst. Provide detailed, accurate bias evaluations in JSON format.",
                temperature=0.3,  # Lower temperature for more consistent evaluation
                max_tokens=2000,
                model_override=self.evaluation_model
            )
            
            # Try to extract JSON from response
            # Look for JSON object in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    evaluation_data = json.loads(json_str)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a structured response from text
                    evaluation_data = self._parse_evaluation_text(response_text)
            else:
                evaluation_data = self._parse_evaluation_text(response_text)
            
            # Ensure all required fields exist
            if 'bias_scores' not in evaluation_data:
                evaluation_data['bias_scores'] = {}
            
            if 'overall_bias_score' not in evaluation_data:
                # Calculate from individual scores
                scores = [v.get('score', 0) for v in evaluation_data['bias_scores'].values() if isinstance(v, dict)]
                evaluation_data['overall_bias_score'] = sum(scores) / len(scores) if scores else 0.0
            
            if 'severity' not in evaluation_data:
                score = evaluation_data.get('overall_bias_score', 0.0)
                if score < 0.2:
                    evaluation_data['severity'] = 'none'
                elif score < 0.4:
                    evaluation_data['severity'] = 'low'
                elif score < 0.6:
                    evaluation_data['severity'] = 'medium'
                elif score < 0.8:
                    evaluation_data['severity'] = 'high'
                else:
                    evaluation_data['severity'] = 'severe'
            
            if 'detected_bias_types' not in evaluation_data:
                detected = []
                for bias_type, data in evaluation_data.get('bias_scores', {}).items():
                    if isinstance(data, dict) and data.get('present', False):
                        detected.append(bias_type.replace('_', ' ').title())
                evaluation_data['detected_bias_types'] = detected
            
            # Get model name for display
            try:
                from model_config import get_model_info
                model_info = get_model_info(self.evaluation_model)
                model_display = model_info['name'] if model_info else 'Claude 3.5 Sonnet'
            except:
                model_display = 'Claude 3.5 Sonnet'
            
            return {
                'evaluation': evaluation_data,
                'model': model_display,
                'source': 'Bedrock (Claude)',
                'method': 'Zero-shot prompting'
            }
        except Exception as e:
            raise Exception(f"Bias evaluation failed: {str(e)}")
    
    def _parse_evaluation_text(self, text: str) -> Dict[str, Any]:
        """
        Parse evaluation text into structured format if JSON parsing fails.
        
        Args:
            text: Evaluation text
            
        Returns:
            Structured evaluation dictionary
        """
        # This is a fallback parser - try to extract information from text
        evaluation_data = {
            'bias_scores': {},
            'overall_bias_score': 0.0,
            'severity': 'unknown',
            'detected_bias_types': [],
            'explanation': text[:500],  # Use first 500 chars as explanation
            'recommendations': ''
        }
        
        # Try to extract scores from text
        score_pattern = r'(\w+\s*bias)[:\s]+([0-9.]+)'
        matches = re.findall(score_pattern, text, re.IGNORECASE)
        for bias_type, score_str in matches:
            try:
                score = float(score_str)
                bias_key = bias_type.lower().replace(' ', '_')
                evaluation_data['bias_scores'][bias_key] = {
                    'score': min(1.0, max(0.0, score)),
                    'present': score > 0.3,
                    'explanation': f'Detected {bias_type}'
                }
            except ValueError:
                pass
        
        return evaluation_data


def get_bedrock_llm_service(
    default_model: Optional[str] = None,
    evaluation_model: Optional[str] = None
) -> BedrockLLMService:
    """
    Get or create Bedrock LLM service instance.
    
    Args:
        default_model: Default model for generation
        evaluation_model: Model for evaluation
        
    Returns:
        BedrockLLMService instance
    """
    return BedrockLLMService(
        default_model=default_model,
        evaluation_model=evaluation_model
    )


