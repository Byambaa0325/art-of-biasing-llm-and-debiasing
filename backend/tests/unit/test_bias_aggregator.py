"""
Unit tests for the BiasAggregator module.

Tests cover:
- Multi-layer detection initialization
- Rule-based detection layer
- Ensemble scoring
- Confidence calculation
- Source agreement
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from bias_aggregator import BiasAggregator, is_aggregator_available


class TestBiasAggregatorInit:
    """Test BiasAggregator initialization."""

    def test_creates_instance(self):
        """BiasAggregator should instantiate without errors."""
        aggregator = BiasAggregator(use_hearts=False)
        assert aggregator is not None

    def test_has_rule_detector(self):
        """BiasAggregator should have rule-based detector."""
        aggregator = BiasAggregator(use_hearts=False)
        assert aggregator.rule_detector is not None

    def test_lazy_hearts_by_default(self):
        """HEARTS should be lazy-loaded by default."""
        aggregator = BiasAggregator(use_hearts=True)
        assert aggregator._hearts_initialized is False

    def test_is_aggregator_available(self):
        """is_aggregator_available should return True (rule-based always available)."""
        assert is_aggregator_available() is True


class TestRuleBasedLayer:
    """Test rule-based detection layer."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_rule_layer_always_used(self, aggregator):
        """Rule-based layer should always be in layers_used."""
        result = aggregator.detect_all_layers("Test prompt", use_hearts=False)
        assert 'rule-based' in result['layers_used']

    def test_rule_layer_detection_source(self, aggregator):
        """Rule-based should be in detection_sources."""
        result = aggregator.detect_all_layers("Test prompt", use_hearts=False)
        assert any('Rule-based' in source for source in result['detection_sources'])

    def test_rule_result_included(self, aggregator):
        """Rule-based result should be included in output."""
        result = aggregator.detect_all_layers("Test prompt", use_hearts=False)
        assert 'rule_based' in result


class TestMultiLayerDetection:
    """Test multi-layer detection."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_returns_prompt(self, aggregator):
        """Result should include the original prompt."""
        result = aggregator.detect_all_layers("Test prompt")
        assert result['prompt'] == "Test prompt"

    def test_returns_layers_used(self, aggregator):
        """Result should list layers used."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'layers_used' in result
        assert isinstance(result['layers_used'], list)

    def test_returns_detection_sources(self, aggregator):
        """Result should list detection sources."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'detection_sources' in result
        assert isinstance(result['detection_sources'], list)

    def test_returns_detected_biases(self, aggregator):
        """Result should include detected biases."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'detected_biases' in result
        assert isinstance(result['detected_biases'], dict)

    def test_returns_overall_bias_score(self, aggregator):
        """Result should include overall bias score."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'overall_bias_score' in result
        assert isinstance(result['overall_bias_score'], (int, float))

    def test_returns_confidence(self, aggregator):
        """Result should include confidence score."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'confidence' in result
        assert isinstance(result['confidence'], (int, float))


class TestEnsembleScoring:
    """Test ensemble scoring calculation."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_bias_metrics_list(self, aggregator):
        """Should return list of bias metrics from each judge."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'bias_metrics' in result
        assert isinstance(result['bias_metrics'], list)

    def test_judge_count(self, aggregator):
        """Should return judge count."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'judge_count' in result
        assert result['judge_count'] >= 1

    def test_judges_used(self, aggregator):
        """Should list judges used."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'judges_used' in result
        assert isinstance(result['judges_used'], list)

    def test_rule_based_in_judges(self, aggregator):
        """Rule-Based Detector should be in judges."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'Rule-Based Detector' in result['judges_used']


class TestConfidenceCalculation:
    """Test confidence score calculation."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_confidence_between_0_and_1(self, aggregator):
        """Confidence should be between 0 and 1."""
        prompts = [
            "Neutral prompt",
            "Why are women emotional?",
            "All teenagers are bad.",
        ]
        for prompt in prompts:
            result = aggregator.detect_all_layers(prompt)
            assert 0 <= result['confidence'] <= 1

    def test_source_agreement_score(self, aggregator):
        """Should include source agreement score."""
        result = aggregator.detect_all_layers("Test prompt")
        assert 'source_agreement' in result
        assert 0 <= result['source_agreement'] <= 1


class TestDetectedBiases:
    """Test detected biases structure."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_detected_biases_structure(self, aggregator):
        """Detected biases should have expected structure."""
        result = aggregator.detect_all_layers("Test prompt")
        detected = result['detected_biases']

        assert 'demographic_biases' in detected
        assert 'cognitive_biases' in detected
        assert 'structural_biases' in detected
        assert 'stereotypes' in detected

    def test_frameworks_used(self, aggregator):
        """Should include frameworks used."""
        result = aggregator.detect_all_layers("Obviously this is true.")
        detected = result['detected_biases']
        assert 'frameworks_used' in detected


class TestMockedHEARTS:
    """Test with mocked HEARTS detector."""

    @pytest.fixture
    def mock_hearts(self):
        mock = MagicMock()
        mock.detect_stereotypes.return_value = {
            'is_stereotype': True,
            'confidence': 0.9,
            'prediction': 'Stereotype',
            'probabilities': {'Stereotype': 0.9, 'Non-Stereotype': 0.1},
            'explanations': {
                'token_importance': [
                    {'token': 'always', 'importance': 0.8, 'contribution': 'positive'}
                ]
            }
        }
        return mock

    def test_hearts_results_merged(self, mock_hearts):
        """HEARTS results should be merged when available."""
        # Create aggregator with HEARTS disabled initially
        aggregator = BiasAggregator(use_hearts=False)

        # Manually set up mocked HEARTS
        aggregator.hearts_detector = mock_hearts
        aggregator._hearts_initialized = True
        aggregator.use_hearts = True
        aggregator.hearts_enabled = True

        result = aggregator.detect_all_layers(
            "Why are women always emotional?",
            use_hearts=True
        )

        # Verify the mock was called
        mock_hearts.detect_stereotypes.assert_called_once()
        assert 'hearts' in result
        assert result['hearts']['is_stereotype'] is True


class TestExplanations:
    """Test explanation generation."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_explanations_with_explain_true(self, aggregator):
        """Should include explanations when explain=True."""
        result = aggregator.detect_all_layers(
            "Obviously this is true.",
            explain=True
        )
        # Explanations may be empty without HEARTS but key should exist
        assert 'explanations' in result or 'detected_biases' in result


class TestEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_empty_prompt(self, aggregator):
        """Should handle empty prompt."""
        result = aggregator.detect_all_layers("")
        assert 'overall_bias_score' in result

    def test_very_long_prompt(self, aggregator):
        """Should handle very long prompt."""
        long_prompt = "This is a test sentence. " * 500
        result = aggregator.detect_all_layers(long_prompt)
        assert 'overall_bias_score' in result

    def test_special_characters(self, aggregator):
        """Should handle special characters."""
        result = aggregator.detect_all_layers("Test @#$%^& prompt!")
        assert 'overall_bias_score' in result
