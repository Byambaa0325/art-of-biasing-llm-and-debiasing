"""
Unit tests for the API helpers module.

Tests cover:
- JSON sanitization
- Node building
- Edge building
- Response formatting
"""

import pytest
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from api_helpers import (
    sanitize_for_json,
    build_node_from_detection,
    build_potential_paths,
    build_connecting_edge,
    generate_node_id,
    APIResponse
)


class TestSanitizeForJson:
    """Test JSON sanitization."""

    def test_sanitize_none(self):
        """Should handle None."""
        assert sanitize_for_json(None) is None

    def test_sanitize_primitives(self):
        """Should handle primitive types."""
        assert sanitize_for_json(True) is True
        assert sanitize_for_json(42) == 42
        assert sanitize_for_json(3.14) == 3.14
        assert sanitize_for_json("hello") == "hello"

    def test_sanitize_list(self):
        """Should handle lists."""
        result = sanitize_for_json([1, 2, 3])
        assert result == [1, 2, 3]

    def test_sanitize_tuple(self):
        """Should convert tuples to lists."""
        result = sanitize_for_json((1, 2, 3))
        assert result == [1, 2, 3]

    def test_sanitize_dict(self):
        """Should handle dictionaries."""
        result = sanitize_for_json({'a': 1, 'b': 2})
        assert result == {'a': 1, 'b': 2}

    def test_sanitize_set(self):
        """Should convert sets to lists."""
        result = sanitize_for_json({1, 2, 3})
        assert set(result) == {1, 2, 3}

    def test_sanitize_nested(self):
        """Should handle nested structures."""
        data = {
            'list': [1, 2, {'nested': True}],
            'tuple': (4, 5),
            'set': {6, 7}
        }
        result = sanitize_for_json(data)
        assert result['list'] == [1, 2, {'nested': True}]
        assert result['tuple'] == [4, 5]
        assert set(result['set']) == {6, 7}

    def test_sanitize_object_with_dict(self):
        """Should convert objects with __dict__."""
        class TestObj:
            def __init__(self):
                self.value = 42

        obj = TestObj()
        result = sanitize_for_json(obj)
        assert result['value'] == 42

    def test_sanitize_unknown_type(self):
        """Should convert unknown types to string or dict."""
        class CustomClass:
            def __str__(self):
                return "custom"

        result = sanitize_for_json(CustomClass())
        # Objects with __dict__ are converted to dicts, others to strings
        assert isinstance(result, (str, dict))


class TestBuildNodeFromDetection:
    """Test node building."""

    @pytest.fixture
    def sample_detection(self):
        return {
            'overall_bias_score': 0.5,
            'confidence': 0.8,
            'source_agreement': 0.9,
            'layers_used': ['rule-based'],
            'detection_sources': ['Rule-based'],
            'hearts': {},
            'gemini_validation': {},
            'explanations': {},
            'bias_metrics': [{'judge': 'Test', 'score': 0.5}],
            'judge_count': 1,
            'judges_used': ['Test']
        }

    def test_builds_node_with_required_fields(self, sample_detection):
        """Node should have required fields."""
        node = build_node_from_detection(
            node_id='test-123',
            prompt='Test prompt',
            llm_answer='Test answer',
            detected_biases=sample_detection
        )

        assert node['id'] == 'test-123'
        assert node['prompt'] == 'Test prompt'
        assert node['llm_answer'] == 'Test answer'
        assert node['type'] == 'original'

    def test_builds_node_with_evaluations(self, sample_detection):
        """Node should have evaluation sections."""
        node = build_node_from_detection(
            node_id='test-123',
            prompt='Test prompt',
            llm_answer='Test answer',
            detected_biases=sample_detection
        )

        assert 'hearts_evaluation' in node
        assert 'gemini_evaluation' in node
        assert 'bias_metrics' in node

    def test_builds_child_node(self, sample_detection):
        """Should build child node with parent info."""
        node = build_node_from_detection(
            node_id='child-456',
            prompt='Modified prompt',
            llm_answer='Answer',
            detected_biases=sample_detection,
            node_type='biased',
            parent_id='parent-123',
            transformation='confirmation_bias'
        )

        assert node['type'] == 'biased'
        assert node['parent_id'] == 'parent-123'
        assert node['transformation'] == 'confirmation_bias'


class TestBuildPotentialPaths:
    """Test potential path building."""

    def test_builds_bias_paths(self):
        """Should build bias path edges."""
        biases = [
            {'bias_type': 'confirmation', 'label': 'Confirmation', 'description': 'Test'}
        ]
        paths = build_potential_paths('node-123', biases, [])

        assert len(paths) == 1
        assert paths[0]['type'] == 'bias'
        assert paths[0]['source'] == 'node-123'
        assert 'target' not in paths[0]  # Potential path has no target

    def test_builds_debias_paths(self):
        """Should build debias path edges."""
        debiases = [
            {'method': 'self_help', 'label': 'Self Help', 'description': 'Test'}
        ]
        paths = build_potential_paths('node-123', [], debiases)

        assert len(paths) == 1
        assert paths[0]['type'] == 'debias'
        assert paths[0]['source'] == 'node-123'

    def test_builds_combined_paths(self):
        """Should build both bias and debias paths."""
        biases = [{'bias_type': 'confirmation', 'label': 'Confirmation', 'description': 'Test'}]
        debiases = [{'method': 'self_help', 'label': 'Self Help', 'description': 'Test'}]

        paths = build_potential_paths('node-123', biases, debiases)

        assert len(paths) == 2
        bias_paths = [p for p in paths if p['type'] == 'bias']
        debias_paths = [p for p in paths if p['type'] == 'debias']
        assert len(bias_paths) == 1
        assert len(debias_paths) == 1


class TestBuildConnectingEdge:
    """Test connecting edge building."""

    def test_builds_edge_with_target(self):
        """Connecting edge should have target."""
        edge = build_connecting_edge('parent-123', 'child-456', 'bias', 'Test Label')

        assert edge['source'] == 'parent-123'
        assert edge['target'] == 'child-456'
        assert edge['type'] == 'bias'
        assert edge['label'] == 'Test Label'


class TestGenerateNodeId:
    """Test node ID generation."""

    def test_generates_string(self):
        """Should generate string ID."""
        node_id = generate_node_id()
        assert isinstance(node_id, str)

    def test_generates_unique_ids(self):
        """Should generate unique IDs."""
        ids = [generate_node_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestAPIResponse:
    """Test APIResponse helper."""

    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        from flask import Flask
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_success_returns_200(self, app):
        """Success should return 200 status."""
        with app.app_context():
            response, status = APIResponse.success({'data': 'test'})
            assert status == 200

    def test_error_returns_custom_status(self, app):
        """Error should return custom status."""
        with app.app_context():
            response, status = APIResponse.error('Test error', 404)
            assert status == 404

    def test_not_available_returns_503(self, app):
        """Not available should return 503."""
        with app.app_context():
            response, status = APIResponse.not_available('TestService')
            assert status == 503
