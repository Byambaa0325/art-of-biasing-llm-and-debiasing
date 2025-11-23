"""
Model Configuration for Vertex AI

Defines available models from different providers accessible through Vertex AI:
- Meta (Llama models)
- Anthropic (Claude models)
- Mistral AI
- OpenAI (via Vertex AI)
- Qwen (Alibaba)
"""

from typing import Dict, List, Any

# Model categories
MODEL_CATEGORIES = {
    'generation': 'Text Generation',
    'evaluation': 'Bias Evaluation',
    'both': 'Generation & Evaluation'
}

# Available models through Vertex AI
AVAILABLE_MODELS = {
    # Meta Llama 3.3 Models
    'meta/llama-3.3-70b-instruct-maas': {
        'name': 'Llama 3.3 70B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Latest Llama 3.3, excellent for reasoning and instruction following',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },

    # Meta Llama 3.1 Models
    'meta/llama-3.1-405b-instruct-maas': {
        'name': 'Llama 3.1 405B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Largest Llama 3.1 model, exceptional performance',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },
    'meta/llama-3.1-70b-instruct-maas': {
        'name': 'Llama 3.1 70B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Balanced Llama 3.1, good performance and speed',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },

    # Google Gemini Models (for comparison)
    'gemini-2.0-flash-exp': {
        'name': 'Gemini 2.0 Flash',
        'provider': 'Google',
        'category': 'both',
        'description': 'Latest Gemini flash model, fast and capable',
        'context_window': 1000000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },
    'gemini-1.5-pro-002': {
        'name': 'Gemini 1.5 Pro',
        'provider': 'Google',
        'category': 'both',
        'description': 'Google\'s Pro model with extended context',
        'context_window': 2000000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },
    'gemini-1.5-flash-002': {
        'name': 'Gemini 1.5 Flash',
        'provider': 'Google',
        'category': 'both',
        'description': 'Fast Gemini model for quick tasks',
        'context_window': 1000000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },
}

# Default models for each purpose
DEFAULT_MODELS = {
    'generation': 'meta/llama-3.3-70b-instruct-maas',
    'evaluation': 'gemini-2.0-flash-exp'
}


def get_available_models(category: str = None) -> Dict[str, Any]:
    """
    Get available models, optionally filtered by category.

    Args:
        category: Optional category filter ('generation', 'evaluation', 'both')

    Returns:
        Dictionary of available models
    """
    if category:
        return {
            model_id: config
            for model_id, config in AVAILABLE_MODELS.items()
            if category in config['recommended_for'] or config['category'] == 'both'
        }
    return AVAILABLE_MODELS


def get_models_by_provider(provider: str) -> Dict[str, Any]:
    """
    Get models from a specific provider.

    Args:
        provider: Provider name (e.g., 'Meta', 'Anthropic', 'Mistral AI', 'Google')

    Returns:
        Dictionary of models from the provider
    """
    return {
        model_id: config
        for model_id, config in AVAILABLE_MODELS.items()
        if config['provider'] == provider
    }


def get_model_info(model_id: str) -> Dict[str, Any]:
    """
    Get information about a specific model.

    Args:
        model_id: Model identifier

    Returns:
        Model configuration dictionary or None if not found
    """
    return AVAILABLE_MODELS.get(model_id)


def is_valid_model(model_id: str) -> bool:
    """
    Check if a model ID is valid.

    Args:
        model_id: Model identifier

    Returns:
        True if model exists, False otherwise
    """
    return model_id in AVAILABLE_MODELS


def get_model_for_ui() -> List[Dict[str, Any]]:
    """
    Get models formatted for UI display (grouped by provider).

    Returns:
        List of model groups with provider and models
    """
    providers = {}

    for model_id, config in AVAILABLE_MODELS.items():
        provider = config['provider']
        if provider not in providers:
            providers[provider] = []

        providers[provider].append({
            'id': model_id,
            'name': config['name'],
            'description': config['description'],
            'category': config['category'],
            'recommended_for': config['recommended_for']
        })

    # Convert to list format
    result = []
    for provider, models in providers.items():
        result.append({
            'provider': provider,
            'models': models
        })

    return result


def get_generation_models() -> List[Dict[str, str]]:
    """Get list of models suitable for generation (bias injection, debiasing)."""
    models = []
    for model_id, config in AVAILABLE_MODELS.items():
        if 'generation' in config['recommended_for']:
            models.append({
                'id': model_id,
                'name': config['name'],
                'provider': config['provider'],
                'description': config['description']
            })
    return models


def get_evaluation_models() -> List[Dict[str, str]]:
    """Get list of models suitable for evaluation."""
    models = []
    for model_id, config in AVAILABLE_MODELS.items():
        if 'evaluation' in config['recommended_for']:
            models.append({
                'id': model_id,
                'name': config['name'],
                'provider': config['provider'],
                'description': config['description']
            })
    return models
