"""
API endpoint tests.

Tests cover:
- Health check endpoint
- Graph expansion endpoints
- Bias detection endpoints
- Error handling
- Input validation
"""

import pytest
import json
import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


class TestHealthEndpoint:
    """Test /api/health endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked services."""
        with patch.dict(os.environ, {'ENABLE_HEARTS': 'false'}):
            with patch('api.VERTEX_LLM_AVAILABLE', False):
                with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                    from api import app
                    app.config['TESTING'] = True
                    with app.test_client() as client:
                        yield client

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint should return JSON."""
        response = client.get('/api/health')
        assert response.content_type == 'application/json'

    def test_health_has_status(self, client):
        """Health response should have status field."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_health_has_features(self, client):
        """Health response should have features field."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'features' in data


class TestDetectEndpoint:
    """Test /api/detect endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_detect_requires_json(self, client):
        """Detect endpoint should require JSON body."""
        response = client.post('/api/detect')
        # 400 (no data) or 415 (unsupported media type) are both acceptable
        assert response.status_code in [400, 415]

    def test_detect_requires_prompt(self, client):
        """Detect endpoint should require prompt field."""
        response = client.post(
            '/api/detect',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_detect_with_valid_prompt(self, client):
        """Detect endpoint should work with valid prompt."""
        response = client.post(
            '/api/detect',
            data=json.dumps({'prompt': 'Why are women emotional?'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'demographic_biases' in data

    def test_detect_returns_bias_score(self, client):
        """Detect endpoint should return bias score."""
        response = client.post(
            '/api/detect',
            data=json.dumps({'prompt': 'Test prompt'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        assert 'overall_bias_score' in data


class TestInjectEndpoint:
    """Test /api/inject endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_inject_requires_prompt(self, client):
        """Inject endpoint should require prompt."""
        response = client.post(
            '/api/inject',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_inject_returns_biased_versions(self, client):
        """Inject endpoint should return biased versions."""
        response = client.post(
            '/api/inject',
            data=json.dumps({'prompt': 'What is the weather?'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'biased_versions' in data
        assert 'original_prompt' in data


class TestDebiasEndpoint:
    """Test /api/debias endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_debias_requires_prompt(self, client):
        """Debias endpoint should require prompt."""
        response = client.post(
            '/api/debias',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_debias_returns_debiased_prompt(self, client):
        """Debias endpoint should return debiased prompt."""
        response = client.post(
            '/api/debias',
            data=json.dumps({'prompt': 'Why are women emotional?'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'original_prompt' in data

    def test_debias_all_methods(self, client):
        """Debias endpoint should support all methods."""
        response = client.post(
            '/api/debias',
            data=json.dumps({'prompt': 'Test prompt', 'method': 'all'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'debiased_versions' in data


class TestGraphExpandEndpoint:
    """Test /api/graph/expand endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client without LLM (simpler test)."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_graph_expand_requires_prompt(self, client):
        """Graph expand should require prompt."""
        response = client.post(
            '/api/graph/expand',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_graph_expand_returns_nodes_and_edges(self, client):
        """Graph expand should return nodes and edges (without LLM)."""
        response = client.post(
            '/api/graph/expand',
            data=json.dumps({'prompt': 'Test prompt'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'nodes' in data
        assert 'edges' in data

    def test_graph_expand_returns_root_id(self, client):
        """Graph expand should return root_id."""
        response = client.post(
            '/api/graph/expand',
            data=json.dumps({'prompt': 'Test prompt'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        assert 'root_id' in data


class TestModelsEndpoint:
    """Test /api/models endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_models_returns_200(self, client):
        """Models endpoint should return 200."""
        response = client.get('/api/models')
        assert response.status_code == 200

    def test_models_returns_generation_models(self, client):
        """Models endpoint should return generation models."""
        response = client.get('/api/models')
        data = json.loads(response.data)
        assert 'generation_models' in data

    def test_models_returns_evaluation_models(self, client):
        """Models endpoint should return evaluation models."""
        response = client.get('/api/models')
        data = json.loads(response.data)
        assert 'evaluation_models' in data


class TestErrorHandling:
    """Test error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.HEARTS_AGGREGATOR_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_404_for_unknown_endpoint(self, client):
        """Should return 404 for unknown API endpoints."""
        response = client.get('/api/unknown')
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Should handle invalid JSON gracefully."""
        response = client.post(
            '/api/detect',
            data='not valid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 415, 500]


class TestLLMEndpoints:
    """Test LLM-dependent endpoints."""

    @pytest.fixture
    def client_no_llm(self):
        """Create test client without LLM."""
        with patch('api.VERTEX_LLM_AVAILABLE', False):
            with patch('api.LLM_AVAILABLE', False):
                from api import app
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client

    def test_llm_debias_unavailable(self, client_no_llm):
        """LLM debias should return 503 when LLM unavailable."""
        response = client_no_llm.post(
            '/api/llm/debias',
            data=json.dumps({'prompt': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code == 503

    def test_llm_inject_unavailable(self, client_no_llm):
        """LLM inject should return 503 when LLM unavailable."""
        response = client_no_llm.post(
            '/api/llm/inject',
            data=json.dumps({'prompt': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code == 503
