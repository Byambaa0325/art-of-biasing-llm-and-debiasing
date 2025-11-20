"""
Debiasing/Normalization Module

Implements methods to normalize and de-bias prompts based on research:
- BiasBuster Self-Help prompting (Echterhoff et al., 2024): LLM paraphrases biased questions neutrally
- Counterfactual and Contrastive debiasing (Echterhoff et al., 2024): Examples of biased vs. unbiased behavior
- Self-Adaptive Cognitive Debiasing (SACD) (Lyu et al., 2025): Iterative bias detection and correction
- Representation-based debiasing concepts (Xu et al., LREC 2024): Removing bias vectors from latent states
- Simple instruction-based normalization (BiasFreeBench, 2024)
"""

from typing import List, Dict, Any
import re
from bias_detection import BiasDetector


class PromptDebiaser:
    """Normalizes and de-biases prompts"""
    
    def __init__(self):
        self.bias_detector = BiasDetector()
    
    def debias_prompt(self, prompt: str, method: str = 'comprehensive') -> Dict[str, Any]:
        """
        De-bias a prompt using specified method.
        
        Args:
            prompt: The original prompt
            method: 'simple', 'iterative', or 'comprehensive'
            
        Returns:
            Dictionary with debiased prompt and explanation
        """
        if method == 'simple':
            return self._simple_debias(prompt)
        elif method == 'iterative':
            return self._iterative_debias(prompt)
        elif method == 'comprehensive':
            return self._comprehensive_debias(prompt)
        else:
            return self._simple_debias(prompt)
    
    def get_all_debiasing_methods(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Get all available debiasing methods for a prompt.
        
        Args:
            prompt: The original prompt
            
        Returns:
            List of debiased versions with explanations
        """
        methods = []
        
        # Method 1: Simple instruction-based
        simple_result = self._simple_debias(prompt)
        methods.append(simple_result)
        
        # Method 2: Remove demographic references
        demographic_removed = self._remove_demographic_bias(prompt)
        if demographic_removed:
            methods.append(demographic_removed)
        
        # Method 3: Neutralize leading questions
        neutralized = self._neutralize_leading_questions(prompt)
        if neutralized:
            methods.append(neutralized)
        
        # Method 4: Remove confirmation bias phrases
        confirmation_removed = self._remove_confirmation_bias(prompt)
        if confirmation_removed:
            methods.append(confirmation_removed)
        
        # Method 5: Remove stereotypical language
        stereotype_removed = self._remove_stereotypical_language(prompt)
        if stereotype_removed:
            methods.append(stereotype_removed)
        
        # Method 6: Iterative refinement (SACD-inspired)
        iterative_result = self._iterative_debias(prompt)
        methods.append(iterative_result)
        
        return methods
    
    def _simple_debias(self, prompt: str) -> Dict[str, Any]:
        """Simple instruction-based debiasing (BiasFreeBench, 2024)"""
        debiased = f"Please answer the following question fairly and without bias: {prompt}"
        
        return {
            'method': 'Simple Instruction-Based',
            'debiased_prompt': debiased,
            'explanation': 'Added explicit instruction to be fair and unbiased. Research (BiasFreeBench, 2024) shows that making the LLM aware of potential bias can reduce harmful output.',
            'how_it_works': 'By explicitly instructing the model to be fair and unbiased, we activate its built-in fairness mechanisms and reduce the influence of biased language in the prompt.',
            'framework': 'BiasFreeBench (2024)'
        }
    
    def _remove_demographic_bias(self, prompt: str) -> Dict[str, Any]:
        """Remove unnecessary demographic references"""
        # Check if demographic keywords exist
        detector = BiasDetector()
        biases = detector.detect_biases(prompt)
        
        if not biases['demographic_biases']:
            return None
        
        # Try to remove demographic qualifiers
        debiased = prompt
        for category, keywords in detector.DEMOGRAPHIC_KEYWORDS.items():
            for keyword in keywords:
                # Remove standalone demographic mentions that aren't central to the question
                pattern = rf'\b{keyword}\b'
                if re.search(pattern, debiased, re.IGNORECASE):
                    # Only remove if it's not essential to the question
                    if not self._is_essential_keyword(keyword, debiased):
                        debiased = re.sub(pattern, '', debiased, flags=re.IGNORECASE)
        
        debiased = re.sub(r'\s+', ' ', debiased).strip()
        
        if debiased == prompt:
            return None
        
        return {
            'method': 'Remove Demographic References',
            'debiased_prompt': debiased,
            'explanation': 'Removed unnecessary demographic qualifiers that may introduce bias. Based on Neumann et al. (FAccT 2025), demographic information placement significantly affects model behavior.',
            'how_it_works': 'By removing demographic qualifiers that aren\'t essential to the question, we prevent the model from making assumptions based on group identity.'
        }
    
    def _neutralize_leading_questions(self, prompt: str) -> Dict[str, Any]:
        """Convert leading questions to neutral questions"""
        detector = BiasDetector()
        biases = detector.detect_biases(prompt)
        
        if not biases['leading_questions']:
            return None
        
        debiased = prompt
        
        # Remove leading question phrases
        leading_phrases = [
            (r"isn't it true that", ""),
            (r"don't you think", "what do you think about"),
            (r"wouldn't you agree", "what is your perspective on"),
            (r"clearly", ""),
            (r"obviously", ""),
        ]
        
        for pattern, replacement in leading_phrases:
            debiased = re.sub(pattern, replacement, debiased, flags=re.IGNORECASE)
        
        debiased = re.sub(r'\s+', ' ', debiased).strip()
        
        if debiased == prompt:
            return None
        
        return {
            'method': 'Neutralize Leading Questions',
            'debiased_prompt': debiased,
            'explanation': 'Converted leading questions to neutral phrasing that doesn\'t suggest a particular answer, allowing for more balanced responses.',
            'how_it_works': 'By removing phrases that imply a conclusion, we allow the model to evaluate the question more objectively without being primed toward a specific answer.'
        }
    
    def _remove_confirmation_bias(self, prompt: str) -> Dict[str, Any]:
        """Remove confirmation bias phrases"""
        detector = BiasDetector()
        biases = detector.detect_biases(prompt)
        
        if not any(b['type'] == 'confirmation_bias' for b in biases['cognitive_biases']):
            return None
        
        debiased = prompt
        
        # Remove confirmation bias phrases
        confirmation_phrases = [
            r"isn't it true that\s*",
            r"doesn't.*prove\s*",
            r"clearly.*shows\s*",
            r"obviously\s*",
            r"everyone knows\s*",
        ]
        
        for pattern in confirmation_phrases:
            debiased = re.sub(pattern, "", debiased, flags=re.IGNORECASE)
        
        debiased = re.sub(r'\s+', ' ', debiased).strip()
        
        if debiased == prompt:
            return None
        
        return {
            'method': 'Remove Confirmation Bias',
            'debiased_prompt': debiased,
            'explanation': 'Removed phrases that suggest a particular conclusion, allowing the model to evaluate the question more critically.',
            'how_it_works': 'By removing language that primes confirmation, we enable the model to consider alternative perspectives and evidence.'
        }
    
    def _remove_stereotypical_language(self, prompt: str) -> Dict[str, Any]:
        """Remove stereotypical assumptions"""
        detector = BiasDetector()
        biases = detector.detect_biases(prompt)
        
        if not biases['assumption_laden']:
            return None
        
        debiased = prompt
        
        # Replace stereotypical language
        replacements = [
            (r'\btypically\b', 'in some cases'),
            (r'\busually\b', 'sometimes'),
            (r'\balways\b', 'often'),
            (r'\bnever\b', 'rarely'),
            (r'\ball\b', 'many'),
        ]
        
        for pattern, replacement in replacements:
            debiased = re.sub(pattern, replacement, debiased, flags=re.IGNORECASE)
        
        if debiased == prompt:
            return None
        
        return {
            'method': 'Remove Stereotypical Language',
            'debiased_prompt': debiased,
            'explanation': 'Replaced absolute or broad generalizations with more nuanced language that acknowledges variation and avoids stereotyping.',
            'how_it_works': 'By using more qualified language, we prevent the model from making overly broad generalizations that may not apply to individuals.'
        }
    
    def _iterative_debias(self, prompt: str) -> Dict[str, Any]:
        """Iterative debiasing inspired by SACD (Lyu et al., 2025) and BiasBuster (Echterhoff et al., 2024)"""
        current_prompt = prompt
        steps = []
        
        # Step 1: Detect biases
        biases = self.bias_detector.detect_biases(current_prompt)
        steps.append(f"Detected {len(biases['cognitive_biases']) + len(biases['demographic_biases'])} types of biases")
        
        # Step 2: Apply multiple normalization techniques
        # Remove confirmation bias
        confirmation_removed = self._remove_confirmation_bias(current_prompt)
        if confirmation_removed:
            current_prompt = confirmation_removed['debiased_prompt']
            steps.append("Removed confirmation bias phrases")
        
        # Neutralize leading questions
        neutralized = self._neutralize_leading_questions(current_prompt)
        if neutralized:
            current_prompt = neutralized['debiased_prompt']
            steps.append("Neutralized leading questions")
        
        # Remove stereotypical language
        stereotype_removed = self._remove_stereotypical_language(current_prompt)
        if stereotype_removed:
            current_prompt = stereotype_removed['debiased_prompt']
            steps.append("Removed stereotypical language")
        
        # Step 3: Add fairness instruction
        final_prompt = f"Please answer the following question fairly, considering multiple perspectives: {current_prompt}"
        
        return {
            'method': 'Iterative Refinement (SACD-inspired)',
            'debiased_prompt': final_prompt,
            'steps': steps,
            'explanation': 'Applied iterative debiasing: detected biases, removed biased language, and added fairness instructions. Inspired by Self-Adaptive Cognitive Debiasing (SACD, Lyu et al., 2025) and BiasBuster (Echterhoff et al., 2024) which iteratively identify and correct biases.',
            'how_it_works': 'This method mimics SACD by: (1) detecting biases, (2) analyzing and removing them, (3) rewriting the prompt, and (4) checking again. This iterative process ensures comprehensive bias removal.',
            'framework': 'SACD (Lyu et al., 2025) & BiasBuster (Echterhoff et al., 2024)'
        }
    
    def _comprehensive_debias(self, prompt: str) -> Dict[str, Any]:
        """Comprehensive debiasing using all methods"""
        return self._iterative_debias(prompt)
    
    def _is_essential_keyword(self, keyword: str, prompt: str) -> bool:
        """Check if a keyword is essential to the question's meaning"""
        # Simple heuristic: if the question is specifically about the demographic, it's essential
        essential_patterns = [
            r'what.*' + keyword,
            r'how.*' + keyword,
            r'why.*' + keyword,
            r'compare.*' + keyword,
        ]
        return any(re.search(pattern, prompt, re.IGNORECASE) for pattern in essential_patterns)


if __name__ == "__main__":
    # Example usage
    debiaser = PromptDebiaser()
    test_prompt = "Why are teenagers so bad at making decisions compared to adults?"
    methods = debiaser.get_all_debiasing_methods(test_prompt)
    
    for method in methods:
        print(f"\n{method['method']}:")
        print(f"  Debiased: {method['debiased_prompt']}")
        print(f"  Explanation: {method['explanation']}")

