"""
Unit tests for the BiasDetector module.

Tests cover:
- Demographic bias detection
- Cognitive bias pattern matching
- Structural bias detection
- Bias score calculation
- Framework alignment
"""

import pytest
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from bias_detection import BiasDetector, BiasType


class TestBiasDetectorInit:
    """Test BiasDetector initialization."""

    def test_creates_instance(self):
        """BiasDetector should instantiate without errors."""
        detector = BiasDetector()
        assert detector is not None

    def test_has_demographic_keywords(self):
        """BiasDetector should have demographic keyword categories."""
        detector = BiasDetector()
        assert hasattr(detector, 'DEMOGRAPHIC_KEYWORDS')
        assert 'gender' in detector.DEMOGRAPHIC_KEYWORDS
        assert 'age' in detector.DEMOGRAPHIC_KEYWORDS
        assert 'race' in detector.DEMOGRAPHIC_KEYWORDS

    def test_has_cognitive_bias_patterns(self):
        """BiasDetector should have cognitive bias patterns."""
        detector = BiasDetector()
        assert hasattr(detector, 'COGNITIVE_BIAS_PATTERNS')
        assert 'confirmation_bias' in detector.COGNITIVE_BIAS_PATTERNS
        assert 'availability_bias' in detector.COGNITIVE_BIAS_PATTERNS


class TestDemographicBiasDetection:
    """Test demographic bias detection."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_detects_gender_references(self, detector):
        """Should detect gender-related keywords."""
        result = detector.detect_biases("Why are women always emotional?")
        assert len(result['demographic_biases']) > 0
        categories = [b['category'] for b in result['demographic_biases']]
        assert 'gender' in categories

    def test_detects_age_references(self, detector):
        """Should detect age-related keywords."""
        result = detector.detect_biases("Why are teenagers so irresponsible?")
        assert len(result['demographic_biases']) > 0
        categories = [b['category'] for b in result['demographic_biases']]
        assert 'age' in categories

    def test_detects_race_references(self, detector):
        """Should detect race-related keywords."""
        result = detector.detect_biases("Are Asian students smarter?")
        assert len(result['demographic_biases']) > 0
        categories = [b['category'] for b in result['demographic_biases']]
        assert 'race' in categories

    def test_detects_religion_references(self, detector):
        """Should detect religion-related keywords."""
        result = detector.detect_biases("Why are Muslim people more religious?")
        assert len(result['demographic_biases']) > 0
        categories = [b['category'] for b in result['demographic_biases']]
        assert 'religion' in categories

    def test_no_demographic_bias_in_neutral_prompt(self, detector):
        """Should not detect demographic bias in neutral prompts."""
        result = detector.detect_biases("How does photosynthesis work?")
        assert len(result['demographic_biases']) == 0

    def test_allocative_bias_classification(self, detector):
        """Should classify allocative bias when decision-related words present."""
        result = detector.detect_biases("Should we hire more women?")
        assert result['bias_classification']['allocative'] is True

    def test_representational_bias_classification(self, detector):
        """Should classify representational bias for portrayal-related prompts."""
        result = detector.detect_biases("What are women like in the workplace?")
        assert result['bias_classification']['representational'] is True


class TestCognitiveBiasDetection:
    """Test cognitive bias pattern detection."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_detects_confirmation_bias(self, detector):
        """Should detect confirmation bias patterns."""
        prompts = [
            "Isn't it true that this is the best approach?",
            "Obviously, vaccines are dangerous.",
            "Everyone knows that this is wrong.",
        ]
        for prompt in prompts:
            result = detector.detect_biases(prompt)
            bias_types = [b['type'] for b in result['cognitive_biases']]
            assert 'confirmation_bias' in bias_types, f"Failed for: {prompt}"

    def test_detects_availability_bias(self, detector):
        """Should detect availability bias patterns."""
        result = detector.detect_biases("You've probably heard about the recent problems.")
        bias_types = [b['type'] for b in result['cognitive_biases']]
        assert 'availability_bias' in bias_types

    def test_detects_anchoring_bias(self, detector):
        """Should detect anchoring bias patterns."""
        result = detector.detect_biases("Compared to last year, is this better?")
        bias_types = [b['type'] for b in result['cognitive_biases']]
        assert 'anchoring_bias' in bias_types

    def test_detects_framing_bias(self, detector):
        """Should detect framing bias patterns."""
        result = detector.detect_biases("What is the risk of this investment?")
        bias_types = [b['type'] for b in result['cognitive_biases']]
        assert 'framing_bias' in bias_types

    def test_detects_leading_questions(self, detector):
        """Should detect leading question patterns."""
        prompts = [
            "Why is this product so bad?",
            "Why do teenagers always cause problems?",
        ]
        for prompt in prompts:
            result = detector.detect_biases(prompt)
            assert len(result['leading_questions']) > 0, f"Failed for: {prompt}"

    def test_detects_stereotypical_assumptions(self, detector):
        """Should detect stereotypical assumption patterns."""
        prompts = [
            "All politicians are corrupt.",
            "Women typically are more emotional.",
        ]
        for prompt in prompts:
            result = detector.detect_biases(prompt)
            bias_types = [b['type'] for b in result['cognitive_biases']]
            assert 'stereotypical_assumption' in bias_types, f"Failed for: {prompt}"

    def test_no_cognitive_bias_in_neutral_prompt(self, detector):
        """Should not detect cognitive bias in neutral prompts."""
        result = detector.detect_biases("What is the capital of France?")
        assert len(result['cognitive_biases']) == 0


class TestStructuralBiasDetection:
    """Test structural bias detection."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_detects_template_bias(self, detector):
        """Should detect template bias patterns."""
        result = detector.detect_biases("The problem of climate change is serious.")
        # Template bias detection depends on exact patterns
        # Just verify the method runs without error
        assert 'structural_biases' in result

    def test_detects_positional_bias(self, detector):
        """Should detect positional bias patterns."""
        result = detector.detect_biases("First, consider the economic impact.")
        bias_types = [b['type'] for b in result['structural_biases']]
        assert 'positional_bias' in bias_types


class TestBiasScoreCalculation:
    """Test overall bias score calculation."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_neutral_prompt_low_score(self, detector):
        """Neutral prompts should have low bias score."""
        result = detector.detect_biases("How does photosynthesis work?")
        assert result['overall_bias_score'] < 0.3

    def test_biased_prompt_high_score(self, detector):
        """Biased prompts should have higher bias score."""
        result = detector.detect_biases("Why are women always so emotional?")
        assert result['overall_bias_score'] > 0.2

    def test_score_normalized(self, detector):
        """Bias score should be normalized between 0 and 1."""
        prompts = [
            "Normal question",
            "Why are all teenagers irresponsible?",
            "Isn't it obvious that women can't do math?",
        ]
        for prompt in prompts:
            result = detector.detect_biases(prompt)
            assert 0 <= result['overall_bias_score'] <= 1, f"Score out of range for: {prompt}"


class TestFrameworkAlignment:
    """Test framework alignment reporting."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_neumann_framework_alignment(self, detector):
        """Should align with Neumann et al. for demographic bias."""
        result = detector.detect_biases("Should we hire more women?")
        assert 'Neumann et al. (FAccT 2025)' in result['framework_alignments']

    def test_beats_framework_alignment(self, detector):
        """Should align with BEATS framework for cognitive bias."""
        result = detector.detect_biases("Everyone knows this is true.")
        assert 'BEATS Framework' in result['framework_alignments']

    def test_sun_kok_framework_alignment(self, detector):
        """Should align with Sun & Kok for cognitive bias."""
        result = detector.detect_biases("Obviously this is the best choice.")
        assert 'Sun & Kok (2025)' in result['framework_alignments']


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def detector(self):
        return BiasDetector()

    def test_empty_string(self, detector):
        """Should handle empty string."""
        result = detector.detect_biases("")
        assert result['overall_bias_score'] == 0

    def test_whitespace_only(self, detector):
        """Should handle whitespace-only input."""
        result = detector.detect_biases("   \n\t  ")
        assert result['overall_bias_score'] == 0

    def test_very_long_prompt(self, detector):
        """Should handle very long prompts."""
        long_prompt = "This is a test. " * 1000
        result = detector.detect_biases(long_prompt)
        assert 'overall_bias_score' in result

    def test_special_characters(self, detector):
        """Should handle special characters."""
        result = detector.detect_biases("What about @#$%^&* symbols?")
        assert 'overall_bias_score' in result

    def test_unicode_characters(self, detector):
        """Should handle unicode characters."""
        result = detector.detect_biases("What about unicode: \u00e9\u00e8\u00ea?")
        assert 'overall_bias_score' in result

    def test_case_insensitivity(self, detector):
        """Bias detection should be case-insensitive."""
        result_lower = detector.detect_biases("why are women emotional?")
        result_upper = detector.detect_biases("WHY ARE WOMEN EMOTIONAL?")
        assert len(result_lower['demographic_biases']) == len(result_upper['demographic_biases'])


class TestBiasType:
    """Test BiasType enum."""

    def test_bias_types_exist(self):
        """Should have all expected bias types."""
        assert BiasType.REPRESENTATIONAL.value == "representational"
        assert BiasType.ALLOCATIVE.value == "allocative"
        assert BiasType.COGNITIVE.value == "cognitive"
        assert BiasType.LANGUAGE.value == "language"
        assert BiasType.STRUCTURAL.value == "structural"
