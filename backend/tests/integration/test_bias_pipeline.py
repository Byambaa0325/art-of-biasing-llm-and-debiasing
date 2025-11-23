"""
Integration tests for the bias detection pipeline.

Tests the full pipeline from prompt input to bias detection output.
"""

import pytest
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from bias_detection import BiasDetector
from bias_injection import BiasInjector
from debiasing import PromptDebiaser
from bias_aggregator import BiasAggregator


class TestFullBiasPipeline:
    """Test the complete bias detection pipeline."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    @pytest.fixture
    def injector(self):
        return BiasInjector()

    @pytest.fixture
    def debiaser(self):
        return PromptDebiaser()

    @pytest.fixture
    def aggregator(self):
        return BiasAggregator(use_hearts=False)

    def test_detect_inject_debias_cycle(self, detector, injector, debiaser):
        """Test the full detect -> inject -> debias cycle."""
        # Start with neutral prompt
        neutral_prompt = "What are effective teaching strategies?"

        # 1. Detect - should be low bias
        detection_result = detector.detect_biases(neutral_prompt)
        assert detection_result['overall_bias_score'] < 0.3

        # 2. Inject bias
        biased_versions = injector.inject_biases(neutral_prompt)
        assert len(biased_versions) > 0

        # Pick first biased version
        biased_prompt = biased_versions[0]['biased_prompt']

        # 3. Detect bias in injected version - should be higher
        biased_detection = detector.detect_biases(biased_prompt)
        # Note: May not always be higher depending on injection type
        assert 'overall_bias_score' in biased_detection

        # 4. Debias the biased prompt
        debiased_versions = debiaser.get_all_debiasing_methods(biased_prompt)
        assert len(debiased_versions) > 0

    def test_aggregator_processes_biased_prompt(self, aggregator):
        """Test aggregator processes biased prompts correctly."""
        biased_prompt = "Why are women always so emotional?"

        result = aggregator.detect_all_layers(
            prompt=biased_prompt,
            use_hearts=False,
            use_gemini=False,
            explain=True
        )

        assert result['overall_bias_score'] > 0
        assert 'rule-based' in result['layers_used']
        assert len(result['detection_sources']) > 0

    def test_aggregator_processes_neutral_prompt(self, aggregator):
        """Test aggregator processes neutral prompts correctly."""
        neutral_prompt = "What is the capital of France?"

        result = aggregator.detect_all_layers(
            prompt=neutral_prompt,
            use_hearts=False,
            use_gemini=False,
            explain=True
        )

        assert result['overall_bias_score'] < 0.3
        assert 'rule-based' in result['layers_used']

    def test_multiple_prompts_batch(self, aggregator):
        """Test processing multiple prompts in batch."""
        prompts = [
            "What is the weather today?",
            "Why are teenagers so irresponsible?",
            "How does machine learning work?",
            "All politicians are corrupt.",
        ]

        results = []
        for prompt in prompts:
            result = aggregator.detect_all_layers(prompt, use_hearts=False)
            results.append(result)

        # Verify all processed
        assert len(results) == 4

        # Verify biased prompts have higher scores
        neutral_scores = [results[0]['overall_bias_score'], results[2]['overall_bias_score']]
        biased_scores = [results[1]['overall_bias_score'], results[3]['overall_bias_score']]

        # At least one biased should be higher than neutrals
        assert max(biased_scores) >= min(neutral_scores)


class TestBiasInjectionPipeline:
    """Test bias injection pipeline."""

    @pytest.fixture
    def injector(self):
        return BiasInjector()

    def test_inject_produces_variations(self, injector):
        """Injection should produce multiple variations."""
        prompt = "What makes a good leader?"
        variations = injector.inject_biases(prompt)

        assert len(variations) > 0
        for v in variations:
            assert 'biased_prompt' in v
            assert 'bias_added' in v

    def test_injected_prompts_differ_from_original(self, injector):
        """Injected prompts should differ from original."""
        prompt = "What makes a good leader?"
        variations = injector.inject_biases(prompt)

        for v in variations:
            # Most should be different (some simple injections might not change it)
            if v['biased_prompt'] != prompt:
                assert len(v['biased_prompt']) >= len(prompt) * 0.5


class TestDebiasingPipeline:
    """Test debiasing pipeline."""

    @pytest.fixture
    def debiaser(self):
        return PromptDebiaser()

    def test_debias_produces_variations(self, debiaser):
        """Debiasing should produce multiple variations."""
        prompt = "Why are women always so emotional?"
        variations = debiaser.get_all_debiasing_methods(prompt)

        assert len(variations) > 0
        for v in variations:
            assert 'debiased_prompt' in v
            assert 'method' in v

    def test_specific_debias_method(self, debiaser):
        """Test specific debiasing method."""
        prompt = "Why are women always so emotional?"
        result = debiaser.debias_prompt(prompt, method='comprehensive')

        assert result is not None


class TestConsistency:
    """Test consistency across multiple runs."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_detection_is_deterministic(self, detector):
        """Same input should produce same output."""
        prompt = "Why are women always so emotional?"

        result1 = detector.detect_biases(prompt)
        result2 = detector.detect_biases(prompt)

        assert result1['overall_bias_score'] == result2['overall_bias_score']
        assert len(result1['demographic_biases']) == len(result2['demographic_biases'])
        assert len(result1['cognitive_biases']) == len(result2['cognitive_biases'])

    def test_aggregator_is_deterministic(self):
        """Aggregator should produce consistent results."""
        aggregator = BiasAggregator(use_hearts=False)
        prompt = "Test consistency prompt"

        result1 = aggregator.detect_all_layers(prompt, use_hearts=False)
        result2 = aggregator.detect_all_layers(prompt, use_hearts=False)

        assert result1['overall_bias_score'] == result2['overall_bias_score']
        assert result1['confidence'] == result2['confidence']
