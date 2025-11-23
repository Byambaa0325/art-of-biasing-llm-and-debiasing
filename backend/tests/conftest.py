"""
Pytest configuration and shared fixtures.

This module provides:
- Test fixtures for common test objects
- Mock factories for external services
- Configuration for test isolation
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from typing import Dict, Any, Generator

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def neutral_prompts() -> list[str]:
    """Prompts that should not trigger bias detection."""
    return [
        "What are the benefits of regular exercise?",
        "How does photosynthesis work in plants?",
        "What is the capital of France?",
        "Explain the theory of relativity.",
        "What is the best way to learn programming?",
    ]


@pytest.fixture
def biased_prompts() -> list[str]:
    """Prompts that should trigger bias detection."""
    return [
        "Why are women always so emotional?",
        "All teenagers are irresponsible with money.",
        "Old people can't use technology properly.",
        "Why are millennials so lazy and entitled?",
        "Women are naturally better at multitasking than men.",
        "Isn't it true that immigrants take all the jobs?",
    ]


@pytest.fixture
def cognitive_bias_prompts() -> Dict[str, list[str]]:
    """Prompts categorized by cognitive bias type."""
    return {
        'confirmation_bias': [
            "Isn't it true that climate change is a hoax?",
            "Obviously, this approach is the best one.",
            "Everyone knows that vaccines are dangerous.",
        ],
        'availability_bias': [
            "You've probably heard about the recent crime wave.",
            "Common knowledge suggests this is bad.",
        ],
        'anchoring_bias': [
            "Compared to the $1000 original price, is $500 a good deal?",
            "This is more than twice as expensive as last year.",
        ],
        'leading_questions': [
            "Why is this product so bad?",
            "Don't you think we should fire him?",
            "Why do teenagers always cause problems?",
        ],
    }


@pytest.fixture
def demographic_prompts() -> Dict[str, list[str]]:
    """Prompts containing demographic references."""
    return {
        'gender': [
            "Should we hire more women in tech?",
            "Why are men better at math?",
        ],
        'age': [
            "Why are elderly people so slow with technology?",
            "Should teenagers be allowed to vote?",
        ],
        'race': [
            "Are certain races more athletic?",
            "Why do Asian students perform better?",
        ],
    }


# =============================================================================
# Service Mocks
# =============================================================================

@pytest.fixture
def mock_vertex_llm_service():
    """Mock Vertex AI LLM service."""
    mock = MagicMock()

    # Mock generate_answer
    mock.generate_answer.return_value = "This is a mock LLM response."

    # Mock inject_bias_llm
    mock.inject_bias_llm.return_value = {
        'biased_prompt': 'This is a biased version of the prompt.',
        'bias_added': 'confirmation_bias',
        'explanation': 'Added confirmation bias language.',
        'framework': 'Sun & Kok (2025)'
    }

    # Mock debias_self_help
    mock.debias_self_help.return_value = {
        'debiased_prompt': 'This is a debiased version of the prompt.',
        'method': 'self_help',
        'explanation': 'Removed biased language.',
        'framework': 'BiasBuster'
    }

    # Mock evaluate_bias
    mock.evaluate_bias.return_value = {
        'evaluation': {
            'bias_score': 0.7,
            'severity': 'medium',
            'bias_types': ['stereotyping'],
            'explanation': 'The prompt contains stereotypical language.',
            'recommendations': 'Consider rephrasing to be more neutral.'
        }
    }

    return mock


@pytest.fixture
def mock_hearts_detector():
    """Mock HEARTS detector for stereotype detection."""
    mock = MagicMock()

    def detect_stereotypes(prompt: str, explain: bool = False) -> Dict[str, Any]:
        # Simple keyword-based mock logic
        stereotype_keywords = ['always', 'never', 'all', 'every', 'none']
        is_stereotype = any(kw in prompt.lower() for kw in stereotype_keywords)

        result = {
            'is_stereotype': is_stereotype,
            'confidence': 0.85 if is_stereotype else 0.9,
            'prediction': 'Stereotype' if is_stereotype else 'Non-Stereotype',
            'probabilities': {
                'Stereotype': 0.85 if is_stereotype else 0.15,
                'Non-Stereotype': 0.15 if is_stereotype else 0.85
            },
            'framework': 'HEARTS (King et al., 2024)'
        }

        if explain:
            result['explanations'] = {
                'token_importance': [
                    {'token': 'always', 'importance': 0.8, 'contribution': 'positive'}
                ] if is_stereotype else []
            }

        return result

    mock.detect_stereotypes.side_effect = detect_stereotypes
    return mock


@pytest.fixture
def mock_bias_aggregator(mock_hearts_detector):
    """Mock bias aggregator with all layers."""
    mock = MagicMock()

    def detect_all_layers(prompt: str, **kwargs) -> Dict[str, Any]:
        return {
            'prompt': prompt,
            'overall_bias_score': 0.5,
            'confidence': 0.8,
            'source_agreement': 0.85,
            'layers_used': ['rule-based', 'HEARTS'],
            'detection_sources': ['Rule-based', 'HEARTS ALBERT-v2'],
            'detected_biases': {
                'demographic_biases': [],
                'cognitive_biases': [],
                'structural_biases': [],
                'stereotypes': []
            },
            'bias_metrics': [
                {'judge': 'Rule-Based Detector', 'score': 0.3, 'confidence': 1.0},
                {'judge': 'HEARTS ALBERT-v2', 'score': 0.7, 'confidence': 0.85}
            ],
            'judge_count': 2,
            'judges_used': ['Rule-Based Detector', 'HEARTS ALBERT-v2'],
            'explanations': {
                'frameworks': ['BEATS Framework', 'HEARTS'],
                'most_biased_tokens': [],
                'detected_bias_types': []
            }
        }

    mock.detect_all_layers.side_effect = detect_all_layers
    return mock


# =============================================================================
# Flask App Fixtures
# =============================================================================

@pytest.fixture
def app(mock_vertex_llm_service, mock_bias_aggregator):
    """Create Flask app for testing with mocked services."""
    # Patch services before importing app
    with patch.dict('sys.modules', {
        'vertex_llm_service': MagicMock(),
    }):
        with patch('api.VERTEX_LLM_AVAILABLE', True):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', True):
                with patch('api.get_vertex_llm_service', return_value=mock_vertex_llm_service):
                    with patch('api.bias_aggregator', mock_bias_aggregator):
                        from api import app as flask_app
                        flask_app.config['TESTING'] = True
                        yield flask_app


@pytest.fixture
def client(app):
    """Create test client for API testing."""
    return app.test_client()


# =============================================================================
# Detector Fixtures
# =============================================================================

@pytest.fixture
def bias_detector():
    """Create real BiasDetector instance."""
    from bias_detection import BiasDetector
    return BiasDetector()


@pytest.fixture
def bias_injector():
    """Create real BiasInjector instance."""
    from bias_injection import BiasInjector
    return BiasInjector()


@pytest.fixture
def debiaser():
    """Create real PromptDebiaser instance."""
    from debiasing import PromptDebiaser
    return PromptDebiaser()


# =============================================================================
# Helper Functions
# =============================================================================

def assert_bias_detected(result: Dict[str, Any], min_score: float = 0.1) -> None:
    """Assert that bias was detected in the result."""
    assert result.get('overall_bias_score', 0) >= min_score, \
        f"Expected bias score >= {min_score}, got {result.get('overall_bias_score', 0)}"


def assert_no_bias(result: Dict[str, Any], max_score: float = 0.1) -> None:
    """Assert that no significant bias was detected."""
    assert result.get('overall_bias_score', 0) <= max_score, \
        f"Expected bias score <= {max_score}, got {result.get('overall_bias_score', 0)}"


def assert_bias_type_detected(result: Dict[str, Any], bias_type: str) -> None:
    """Assert that a specific bias type was detected."""
    cognitive_biases = result.get('cognitive_biases', [])
    bias_types = [b['type'] for b in cognitive_biases]
    assert bias_type in bias_types, \
        f"Expected {bias_type} to be detected, found: {bias_types}"
