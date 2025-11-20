"""
Bias Aggregator

Combines multiple bias detection layers:
- Layer 1: Rule-based detection (fast, deterministic)
- Layer 2: HEARTS ML detection (accurate, explainable)
- Layer 3: LLM validation (optional, expensive)

Provides ensemble scoring and confidence metrics.
"""

from typing import Dict, Any, List, Optional
import numpy as np

# Import existing detectors
try:
    from .bias_detection import BiasDetector
except ImportError:
    from bias_detection import BiasDetector

# Import HEARTS detector
try:
    from .hearts_detector import HEARTSDetector, is_hearts_available
    HEARTS_AVAILABLE = is_hearts_available()
except ImportError:
    HEARTS_AVAILABLE = False
    print("Warning: HEARTS detector not available")

# Import Vertex LLM service (optional)
try:
    from .vertex_llm_service import VertexLLMService
except ImportError:
    VertexLLMService = None


class BiasAggregator:
    """
    Multi-layer bias detection with ensemble scoring.

    Combines:
    - Rule-based detection (cognitive, structural biases)
    - HEARTS ML detection (stereotype detection)
    - Optional LLM validation (Gemini 2.5 Flash)

    Provides:
    - Unified bias reporting
    - Ensemble confidence scoring
    - Token-level explainability
    - Source attribution
    """

    def __init__(
        self,
        use_hearts: bool = True,
        llm_service: Optional[VertexLLMService] = None,
        lazy_hearts: bool = True
    ):
        """
        Initialize bias aggregator.

        Args:
            use_hearts: Enable HEARTS ML detection (default: True if available)
            llm_service: Optional Vertex AI LLM service for validation
            lazy_hearts: If True, initialize HEARTS only when first needed (default: True)
                         Set to False to initialize immediately (may block startup)
        """
        # Layer 1: Rule-based detector (always available)
        self.rule_detector = BiasDetector()

        # Layer 2: HEARTS detector (optional, lazy-loaded by default)
        self.hearts_detector = None
        self._hearts_initialized = False
        self._hearts_init_error = None
        self.use_hearts = use_hearts and HEARTS_AVAILABLE
        
        if use_hearts and HEARTS_AVAILABLE and not lazy_hearts:
            # Eager initialization (for backward compatibility)
            self._initialize_hearts()

        # Layer 3: LLM validation (optional)
        self.llm_service = llm_service

        # Configuration
        self.hearts_enabled = self.use_hearts
        self.llm_enabled = self.llm_service is not None
    
    def _initialize_hearts(self):
        """Lazy initialization of HEARTS detector"""
        if self._hearts_initialized:
            return
        
        if not self.use_hearts:
            return
        
        if self._hearts_init_error:
            # Don't retry if we already failed
            return
        
        try:
            print("Initializing HEARTS detector (lazy load)...")
            self.hearts_detector = HEARTSDetector()
            self._hearts_initialized = True
            print("✓ HEARTS detector initialized successfully")
        except Exception as e:
            error_msg = str(e)
            self._hearts_init_error = error_msg
            print(f"Warning: Could not initialize HEARTS: {error_msg}")
            print(f"  HEARTS will be disabled. Error details: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.hearts_detector = None
            self.hearts_enabled = False

    def detect_all_layers(
        self,
        prompt: str,
        use_hearts: bool = True,
        use_gemini: bool = False,
        explain: bool = True,
        gemini_confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Multi-layer bias detection with ensemble scoring.

        Args:
            prompt: Text to analyze
            use_hearts: Use HEARTS ML detection (default: True)
            use_gemini: Use Gemini validation (default: False, expensive)
            explain: Generate token-level explanations (default: True)
            gemini_confidence_threshold: Only use Gemini if HEARTS confidence < threshold

        Returns:
            Aggregated bias detection results with confidence scoring
        """
        result = {
            'prompt': prompt,
            'layers_used': [],
            'detection_sources': []
        }

        # Layer 1: Rule-based detection (always run - fast)
        rule_result = self.rule_detector.detect_biases(prompt)
        result['rule_based'] = rule_result
        result['layers_used'].append('rule-based')
        result['detection_sources'].append('Rule-based (BEATS, Neumann et al.)')

        # Layer 2: HEARTS ML detection (lazy initialization)
        hearts_result = None
        if use_hearts and self.use_hearts:
            # Lazy initialize HEARTS if not already done
            if not self._hearts_initialized:
                self._initialize_hearts()
            
            if self.hearts_detector is not None:
                try:
                    hearts_result = self.hearts_detector.detect_stereotypes(
                        prompt,
                        explain=explain
                    )
                    result['hearts'] = hearts_result
                    result['layers_used'].append('HEARTS')
                    result['detection_sources'].append('HEARTS ALBERT-v2 (King et al., 2024)')
                except Exception as e:
                    print(f"Warning: HEARTS detection failed: {e}")
                    import traceback
                    traceback.print_exc()
            elif self._hearts_init_error:
                # Log that HEARTS is unavailable due to initialization error
                result['hearts_error'] = f"HEARTS unavailable: {self._hearts_init_error}"

        # Layer 3: Gemini validation (optional - expensive)
        gemini_result = None
        if use_gemini and self.llm_enabled:
            # Only validate if HEARTS confidence is low
            should_validate = True
            if hearts_result:
                hearts_confidence = hearts_result.get('confidence', 1.0)
                should_validate = hearts_confidence < gemini_confidence_threshold

            if should_validate:
                try:
                    gemini_result = self.llm_service.evaluate_bias(prompt)
                    result['gemini_validation'] = gemini_result
                    result['layers_used'].append('Gemini')
                    result['detection_sources'].append('Gemini 2.5 Flash')
                except Exception as e:
                    print(f"Warning: Gemini validation failed: {e}")

        # Aggregate results
        result['detected_biases'] = self._merge_detections(
            rule_result,
            hearts_result,
            gemini_result
        )

        # Calculate ensemble scores
        result['overall_bias_score'] = self._calculate_ensemble_score(
            rule_result,
            hearts_result,
            gemini_result
        )

        result['confidence'] = self._calculate_confidence(
            rule_result,
            hearts_result,
            gemini_result
        )

        # Source agreement
        result['source_agreement'] = self._calculate_source_agreement(
            rule_result,
            hearts_result
        )

        # Generate explanations
        if explain and hearts_result:
            result['explanations'] = self._generate_explanations(
                rule_result,
                hearts_result
            )

        return result

    def _merge_detections(
        self,
        rule_result: Dict[str, Any],
        hearts_result: Optional[Dict[str, Any]],
        gemini_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge detections from all layers into unified report.

        Args:
            rule_result: Rule-based detection results
            hearts_result: HEARTS ML detection results
            gemini_result: Gemini validation results

        Returns:
            Merged bias detection report
        """
        merged = {
            'demographic_biases': rule_result.get('demographic_biases', []),
            'cognitive_biases': rule_result.get('cognitive_biases', []),
            'structural_biases': rule_result.get('structural_biases', []),
            'stereotypes': [],
            'frameworks_used': []
        }

        # Add HEARTS stereotype detection
        if hearts_result and hearts_result.get('is_stereotype'):
            stereotype_info = {
                'detected': True,
                'confidence': hearts_result.get('confidence', 0),
                'probability': hearts_result['probabilities']['Stereotype'],
                'source': 'HEARTS ALBERT-v2',
                'framework': hearts_result.get('framework', 'HEARTS (King et al., 2024)')
            }

            # Add token importance if available
            if hearts_result.get('explanations', {}).get('token_importance'):
                stereotype_info['most_biased_tokens'] = [
                    {
                        'token': t['token'],
                        'importance': t['importance']
                    }
                    for t in hearts_result['explanations']['token_importance'][:5]
                ]

            merged['stereotypes'].append(stereotype_info)

        # Add framework alignments
        merged['frameworks_used'] = rule_result.get('framework_alignments', [])
        if hearts_result:
            merged['frameworks_used'].append('HEARTS (King et al., 2024)')

        # Add Gemini insights if available
        if gemini_result:
            evaluation = gemini_result.get('evaluation', {})
            merged['gemini_severity'] = evaluation.get('severity', 'unknown')
            merged['gemini_bias_types'] = evaluation.get('bias_types', [])

        return merged

    def _calculate_ensemble_score(
        self,
        rule_result: Dict[str, Any],
        hearts_result: Optional[Dict[str, Any]],
        gemini_result: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate weighted ensemble bias score.

        Weights:
        - Rule-based: 0.3 (good for cognitive/structural biases)
        - HEARTS: 0.5 (best for stereotype detection)
        - Gemini: 0.2 (validation layer)

        Args:
            rule_result: Rule-based detection results
            hearts_result: HEARTS ML detection results
            gemini_result: Gemini validation results

        Returns:
            Ensemble bias score (0-1)
        """
        scores = []
        weights = []

        # Rule-based score
        rule_score = rule_result.get('overall_bias_score', 0)
        scores.append(rule_score)
        weights.append(0.3)

        # HEARTS score
        if hearts_result:
            hearts_score = hearts_result['probabilities']['Stereotype']
            scores.append(hearts_score)
            weights.append(0.5)
        else:
            # Adjust weights if HEARTS not available
            weights[0] = 0.6  # Increase rule-based weight

        # Gemini score
        if gemini_result:
            evaluation = gemini_result.get('evaluation', {})
            gemini_score = evaluation.get('bias_score', 0.5)
            scores.append(gemini_score)
            weights.append(0.2)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Calculate weighted average
        ensemble_score = sum(s * w for s, w in zip(scores, weights))

        return min(1.0, max(0.0, ensemble_score))

    def _calculate_confidence(
        self,
        rule_result: Dict[str, Any],
        hearts_result: Optional[Dict[str, Any]],
        gemini_result: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate detection confidence.

        Based on:
        - HEARTS model confidence
        - SHAP-LIME similarity (if available)
        - Source agreement between rule-based and ML

        Args:
            rule_result: Rule-based detection results
            hearts_result: HEARTS ML detection results
            gemini_result: Gemini validation results

        Returns:
            Confidence score (0-1)
        """
        confidence_scores = []

        # HEARTS confidence
        if hearts_result:
            hearts_conf = hearts_result.get('confidence', 0.5)
            confidence_scores.append(hearts_conf)

            # Explanation confidence (SHAP-LIME similarity)
            if hearts_result.get('explanation_confidence'):
                confidence_scores.append(hearts_result['explanation_confidence'])

        # Source agreement confidence
        agreement = self._calculate_source_agreement(rule_result, hearts_result)
        confidence_scores.append(agreement)

        # Average confidence
        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)

        return 0.5  # Default moderate confidence

    def _calculate_source_agreement(
        self,
        rule_result: Dict[str, Any],
        hearts_result: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate agreement between rule-based and HEARTS detection.

        Args:
            rule_result: Rule-based detection results
            hearts_result: HEARTS ML detection results

        Returns:
            Agreement score (0-1)
        """
        if not hearts_result:
            return 1.0  # Perfect agreement if only one source

        # Check if both detect bias
        rule_detects_bias = rule_result.get('overall_bias_score', 0) > 0.3
        hearts_detects_bias = hearts_result.get('is_stereotype', False)

        # Both agree on presence/absence
        if rule_detects_bias == hearts_detects_bias:
            return 0.9  # High agreement

        # Disagreement - check if it's marginal
        rule_score = rule_result.get('overall_bias_score', 0)
        hearts_score = hearts_result['probabilities']['Stereotype']

        # Calculate score difference
        score_diff = abs(rule_score - hearts_score)

        # Agreement decreases with score difference
        agreement = max(0.3, 1.0 - score_diff)

        return agreement

    def _generate_explanations(
        self,
        rule_result: Dict[str, Any],
        hearts_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate unified explanations from all sources.

        Args:
            rule_result: Rule-based detection results
            hearts_result: HEARTS ML detection results

        Returns:
            Unified explanation report
        """
        explanations = {
            'frameworks': [],
            'most_biased_tokens': [],
            'detected_bias_types': []
        }

        # Add framework references
        explanations['frameworks'] = rule_result.get('framework_alignments', [])
        if hearts_result:
            explanations['frameworks'].append('HEARTS (King et al., 2024)')

        # Add token-level importance from HEARTS
        if hearts_result.get('explanations', {}).get('token_importance'):
            explanations['most_biased_tokens'] = [
                {
                    'token': t['token'],
                    'importance': t['importance'],
                    'contribution': t.get('contribution', 'unknown'),
                    'source': 'HEARTS-SHAP'
                }
                for t in hearts_result['explanations']['token_importance'][:10]
            ]

        # Combine bias types
        bias_types = set()

        # From rule-based
        for bias in rule_result.get('cognitive_biases', []):
            bias_types.add(bias['type'])

        # From HEARTS
        if hearts_result.get('is_stereotype'):
            bias_types.add('stereotype')

        explanations['detected_bias_types'] = list(bias_types)

        return explanations


def is_aggregator_available() -> bool:
    """Check if bias aggregator can be initialized"""
    return True  # Rule-based detector always available


if __name__ == "__main__":
    # Example usage
    aggregator = BiasAggregator()

    test_prompts = [
        "What are the benefits of regular exercise?",
        "Why are women always so emotional?",
        "How does photosynthesis work?",
        "All teenagers are irresponsible with money."
    ]

    print("\n" + "="*60)
    print("Multi-Layer Bias Detection Test")
    print("="*60 + "\n")

    for prompt in test_prompts:
        result = aggregator.detect_all_layers(
            prompt=prompt,
            use_hearts=True,
            use_gemini=False,
            explain=True
        )

        print(f"Prompt: {prompt}")
        print(f"Overall Bias Score: {result['overall_bias_score']:.2%}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Detection Sources: {', '.join(result['detection_sources'])}")

        if result.get('explanations', {}).get('most_biased_tokens'):
            print("Most Biased Tokens:")
            for token in result['explanations']['most_biased_tokens'][:3]:
                print(f"  - {token['token']}: {token['importance']:.3f}")

        print("-" * 60 + "\n")
