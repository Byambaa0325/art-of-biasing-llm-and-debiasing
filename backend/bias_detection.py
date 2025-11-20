"""
Bias Detection Module

Based on established research frameworks:
- Representational vs. Allocative Bias (Neumann et al., FAccT 2025)
- BEATS Framework (29 metrics)
- Cognitive Bias Taxonomy (Sun & Kok, 2025)
- FairMonitor Framework

Detects various types of biases in user prompts including:
- Demographic biases (representational & allocative)
- Cognitive biases (confirmation, availability, anchoring, framing, etc.)
- Stereotypical language
- Leading questions
- Assumption-laden phrasing
- Structural biases (template, positional)
"""

import re
from typing import List, Dict, Any
from enum import Enum


class BiasType(Enum):
    """Bias type classification"""
    REPRESENTATIONAL = "representational"  # How groups are portrayed
    ALLOCATIVE = "allocative"  # How resources/outcomes are distributed
    COGNITIVE = "cognitive"  # Cognitive biases
    LANGUAGE = "language"  # Language-level biases
    STRUCTURAL = "structural"  # Structural/template biases


class BiasDetector:
    """
    Detects biases in prompts using research-backed frameworks.
    
    Aligned with:
    - Neumann et al. (FAccT 2025): Representational vs. Allocative bias
    - BEATS Framework: 29 comprehensive metrics
    - Sun & Kok (2025): Cognitive bias taxonomy
    """
    
    # Demographic indicators (aligned with BEATS framework)
    DEMOGRAPHIC_KEYWORDS = {
        'race': ['race', 'ethnicity', 'racial', 'black', 'white', 'asian', 'hispanic', 'latino', 
                 'african', 'european', 'caucasian', 'indigenous', 'native'],
        'gender': ['gender', 'male', 'female', 'man', 'woman', 'men', 'women', 'masculine', 
                   'feminine', 'transgender', 'non-binary', 'cisgender'],
        'age': ['age', 'young', 'old', 'elderly', 'teenager', 'senior', 'millennial', 'gen z', 
                'boomer', 'youth', 'adolescent', 'geriatric'],
        'religion': ['religion', 'religious', 'christian', 'muslim', 'islam', 'jewish', 'judaism', 
                     'hindu', 'hinduism', 'buddhist', 'buddhism', 'atheist', 'atheism', 'sikh'],
        'nationality': ['nationality', 'national', 'american', 'british', 'chinese', 'indian', 
                        'mexican', 'country', 'citizen', 'immigrant', 'refugee'],
        'socioeconomic': ['poor', 'rich', 'wealthy', 'poverty', 'income', 'class', 'affluent', 
                          'disadvantaged', 'socioeconomic', 'economic status', 'wealth'],
        'sexual_orientation': ['gay', 'lesbian', 'bisexual', 'straight', 'heterosexual', 
                               'homosexual', 'lgbtq', 'queer', 'sexual orientation'],
        'disability': ['disabled', 'disability', 'handicapped', 'impairment', 'autism', 
                       'deaf', 'blind', 'wheelchair']
    }
    
    # Cognitive bias patterns (aligned with Sun & Kok, 2025 and BEATS framework)
    COGNITIVE_BIAS_PATTERNS = {
        'confirmation_bias': [
            r'isn\'?t it true that',
            r'doesn\'?t.*prove',
            r'clearly.*shows',
            r'obviously',
            r'everyone knows',
            r'it\'?s clear that',
            r'undoubtedly',
            r'certainly.*demonstrates'
        ],
        'availability_bias': [
            r'recent.*shows',
            r'you\'?ve probably heard',
            r'common knowledge',
            r'widely known',
            r'everyone has seen',
            r'frequently.*mentioned',
            r'often.*discussed'
        ],
        'anchoring_bias': [
            r'compared to',
            r'relative to',
            r'as much as',
            r'more than',
            r'less than',
            r'compared with',
            r'in contrast to',
            r'unlike.*which'
        ],
        'framing_bias': [
            r'loss.*of',
            r'gain.*of',
            r'risk.*of',
            r'benefit.*of',
            r'cost.*of',
            r'advantage.*of',
            r'disadvantage.*of'
        ],
        'leading_question': [
            r'why.*so.*bad',
            r'why.*so.*good',
            r'isn\'?t.*better',
            r'wouldn\'?t.*agree',
            r'don\'?t.*think',
            r'why.*always',
            r'why.*never',
            r'how.*could.*possibly'
        ],
        'stereotypical_assumption': [
            r'typically.*are',
            r'usually.*do',
            r'always.*like',
            r'never.*want',
            r'traditionally.*believe',
            r'all.*are',
            r'every.*is',
            r'none.*can'
        ],
        'halo_effect': [
            r'because.*is.*good',
            r'since.*is.*excellent',
            r'given.*is.*superior',
            r'as.*is.*better'
        ],
        'negativity_bias': [
            r'problem.*with',
            r'issue.*with',
            r'negative.*aspect',
            r'worst.*thing',
            r'bad.*about',
            r'fail.*to',
            r'cannot.*do'
        ]
    }
    
    # Structural bias patterns (Xu et al., LREC 2024)
    STRUCTURAL_BIAS_PATTERNS = {
        'template_bias': [
            r'^the.*of.*is',
            r'^what.*is.*the',
            r'^why.*is.*the',
            r'^how.*is.*the'
        ],
        'positional_bias': [
            r'^first.*consider',
            r'^primarily.*focus',
            r'^most.*important.*is'
        ]
    }
    
    def detect_biases(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze a prompt for various types of biases using research-backed frameworks.
        
        Based on:
        - Neumann et al. (FAccT 2025): Representational vs. Allocative bias
        - BEATS Framework: 29 comprehensive metrics
        - Sun & Kok (2025): Cognitive bias taxonomy
        - Xu et al. (LREC 2024): Structural/template bias
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            Dictionary containing detected biases with explanations and classifications
        """
        prompt_lower = prompt.lower()
        biases = {
            'demographic_biases': [],
            'representational_biases': [],  # How groups are portrayed
            'allocative_biases': [],  # Resource/outcome distribution
            'cognitive_biases': [],
            'stereotypical_language': [],
            'leading_questions': [],
            'assumption_laden': [],
            'structural_biases': [],
            'bias_classification': {
                'representational': False,
                'allocative': False,
                'cognitive': False,
                'structural': False
            },
            'overall_bias_score': 0.0,
            'framework_alignments': []
        }
        
        # Check for demographic references (can lead to both representational and allocative bias)
        for category, keywords in self.DEMOGRAPHIC_KEYWORDS.items():
            found_keywords = [kw for kw in keywords if kw in prompt_lower]
            if found_keywords:
                # Determine if this is representational or allocative
                is_allocative = any(word in prompt_lower for word in 
                                   ['should', 'recommend', 'hire', 'loan', 'admit', 'select', 
                                    'choose', 'prefer', 'better', 'best', 'qualify'])
                is_representational = any(word in prompt_lower for word in 
                                        ['are', 'is', 'like', 'characteristic', 'trait', 'portray'])
                
                bias_info = {
                    'category': category,
                    'keywords': found_keywords,
                    'bias_type': [],
                    'explanation': f"Prompt contains references to {category}, which may introduce demographic bias."
                }
                
                if is_allocative:
                    bias_info['bias_type'].append('allocative')
                    bias_info['explanation'] += " This could affect resource allocation or decision-making outcomes."
                    biases['allocative_biases'].append(bias_info)
                    biases['bias_classification']['allocative'] = True
                
                if is_representational or not is_allocative:
                    bias_info['bias_type'].append('representational')
                    bias_info['explanation'] += " This could affect how groups are portrayed or represented."
                    biases['representational_biases'].append(bias_info)
                    biases['bias_classification']['representational'] = True
                
                biases['demographic_biases'].append(bias_info)
        
        # Check for cognitive biases
        for bias_type, patterns in self.COGNITIVE_BIAS_PATTERNS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    matches.append(pattern)
            
            if matches:
                explanation = self._get_bias_explanation(bias_type)
                biases['cognitive_biases'].append({
                    'type': bias_type,
                    'patterns_found': matches,
                    'explanation': explanation,
                    'framework': 'BEATS & Sun & Kok (2025)'
                })
                biases['bias_classification']['cognitive'] = True
        
        # Check for structural biases (Xu et al., LREC 2024)
        for struct_type, patterns in self.STRUCTURAL_BIAS_PATTERNS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    matches.append(pattern)
            
            if matches:
                biases['structural_biases'].append({
                    'type': struct_type,
                    'patterns_found': matches,
                    'explanation': self._get_structural_bias_explanation(struct_type),
                    'framework': 'Xu et al. (LREC 2024)'
                })
                biases['bias_classification']['structural'] = True
        
        # Check for leading questions
        if any(re.search(pattern, prompt_lower) for pattern in self.COGNITIVE_BIAS_PATTERNS['leading_question']):
            biases['leading_questions'].append({
                'explanation': "Prompt contains leading questions that suggest a particular answer (Sun & Kok, 2025)."
            })
        
        # Check for stereotypical assumptions
        if any(re.search(pattern, prompt_lower) for pattern in self.COGNITIVE_BIAS_PATTERNS['stereotypical_assumption']):
            biases['assumption_laden'].append({
                'explanation': "Prompt contains language that makes broad assumptions or generalizations, which can lead to stereotyping."
            })
        
        # Framework alignments
        if biases['bias_classification']['representational'] or biases['bias_classification']['allocative']:
            biases['framework_alignments'].append('Neumann et al. (FAccT 2025)')
        if biases['cognitive_biases']:
            biases['framework_alignments'].append('BEATS Framework')
            biases['framework_alignments'].append('Sun & Kok (2025)')
        if biases['structural_biases']:
            biases['framework_alignments'].append('Xu et al. (LREC 2024)')
        
        # Calculate overall bias score (weighted approach)
        bias_weights = {
            'demographic': 0.3,
            'cognitive': 0.25,
            'structural': 0.2,
            'leading_questions': 0.15,
            'assumption_laden': 0.1
        }
        
        weighted_score = (
            len(biases['demographic_biases']) * bias_weights['demographic'] +
            len(biases['cognitive_biases']) * bias_weights['cognitive'] +
            len(biases['structural_biases']) * bias_weights['structural'] +
            len(biases['leading_questions']) * bias_weights['leading_questions'] +
            len(biases['assumption_laden']) * bias_weights['assumption_laden']
        )
        
        # Normalize to 0-1 scale (max expected: ~10 bias indicators)
        biases['overall_bias_score'] = min(1.0, weighted_score / 3.0)
        
        return biases
    
    def _get_bias_explanation(self, bias_type: str) -> str:
        """Get educational explanation for each bias type based on research"""
        explanations = {
            'confirmation_bias': "Confirmation bias (Sun & Kok, 2025): The prompt suggests a particular conclusion, making the LLM more likely to confirm rather than question the premise. This can lead to one-sided responses.",
            'availability_bias': "Availability bias (Sun & Kok, 2025): The prompt relies on easily recalled examples rather than comprehensive evidence, which can skew responses toward memorable but potentially unrepresentative information.",
            'anchoring_bias': "Anchoring bias (Sun & Kok, 2025): The prompt provides a reference point that may unduly influence the LLM's response, causing it to anchor judgments around the initial information.",
            'framing_bias': "Framing bias: The prompt presents information in a way that emphasizes gains/losses or positive/negative aspects, which can influence how the LLM evaluates the situation.",
            'leading_question': "Leading question (Sun & Kok, 2025): The prompt is phrased in a way that suggests a particular answer, reducing critical evaluation and biasing the response.",
            'stereotypical_assumption': "Stereotypical assumption (BEATS Framework): The prompt makes broad generalizations that may not apply to individuals, potentially reinforcing stereotypes.",
            'halo_effect': "Halo effect: The prompt encourages generalizing from one positive trait to overall assessment, which can lead to biased evaluations.",
            'negativity_bias': "Negativity bias: The prompt emphasizes negative aspects, which can cause the LLM to give disproportionate weight to negative information."
        }
        return explanations.get(bias_type, "Potential bias detected in prompt phrasing.")
    
    def _get_structural_bias_explanation(self, struct_type: str) -> str:
        """Get explanation for structural biases (Xu et al., LREC 2024)"""
        explanations = {
            'template_bias': "Template bias (Xu et al., LREC 2024): The prompt structure systematically skews responses toward particular labels or conclusions due to its template format.",
            'positional_bias': "Positional bias (Xu et al., LREC 2024): Information placement in the prompt may cause the LLM to give undue weight to early-mentioned information."
        }
        return explanations.get(struct_type, "Structural bias detected in prompt format.")


if __name__ == "__main__":
    # Example usage
    detector = BiasDetector()
    test_prompt = "Why are teenagers so bad at making decisions compared to adults?"
    result = detector.detect_biases(test_prompt)
    print("Detected biases:", result)

