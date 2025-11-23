"""
Import Helper Module

Provides clean, centralized imports for all backend modules.
Eliminates the triple try/except import pattern used throughout the codebase.

Usage:
    from imports import (
        BiasDetector,
        BiasInjector,
        PromptDebiaser,
        BiasAggregator,
        get_vertex_llm_service,
        VERTEX_LLM_AVAILABLE,
        HEARTS_AVAILABLE,
    )
"""

import os
import sys
from typing import Optional, Any

# Ensure backend directory is in path
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


def _import_module(module_name: str, class_names: list[str]) -> dict:
    """
    Safely import a module and extract specified classes/functions.

    Args:
        module_name: Name of the module to import
        class_names: List of class/function names to extract

    Returns:
        Dictionary mapping names to imported objects
    """
    result = {}

    try:
        # Try relative import first (for package context)
        module = __import__(f'.{module_name}', globals(), locals(), class_names, 1)
    except ImportError:
        try:
            # Fall back to direct import
            module = __import__(module_name, globals(), locals(), class_names, 0)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
            return {name: None for name in class_names}

    for name in class_names:
        result[name] = getattr(module, name, None)

    return result


# =============================================================================
# Core Detector Imports
# =============================================================================

_bias_detection = _import_module('bias_detection', ['BiasDetector', 'BiasType'])
BiasDetector = _bias_detection['BiasDetector']
BiasType = _bias_detection['BiasType']

_bias_injection = _import_module('bias_injection', ['BiasInjector'])
BiasInjector = _bias_injection['BiasInjector']

_debiasing = _import_module('debiasing', ['PromptDebiaser'])
PromptDebiaser = _debiasing['PromptDebiaser']


# =============================================================================
# HEARTS / ML Imports
# =============================================================================

HEARTS_AVAILABLE = False
HEARTSDetector = None
is_hearts_available = lambda: False

try:
    from hearts_detector import HEARTSDetector as _HEARTSDetector, is_hearts_available as _is_hearts_available
    HEARTSDetector = _HEARTSDetector
    is_hearts_available = _is_hearts_available
    HEARTS_AVAILABLE = _is_hearts_available()
except ImportError:
    try:
        from .hearts_detector import HEARTSDetector as _HEARTSDetector, is_hearts_available as _is_hearts_available
        HEARTSDetector = _HEARTSDetector
        is_hearts_available = _is_hearts_available
        HEARTS_AVAILABLE = _is_hearts_available()
    except ImportError:
        pass


# =============================================================================
# Bias Aggregator Import
# =============================================================================

BiasAggregator = None
is_aggregator_available = lambda: False

try:
    from bias_aggregator import BiasAggregator as _BiasAggregator, is_aggregator_available as _is_aggregator_available
    BiasAggregator = _BiasAggregator
    is_aggregator_available = _is_aggregator_available
except ImportError:
    try:
        from .bias_aggregator import BiasAggregator as _BiasAggregator, is_aggregator_available as _is_aggregator_available
        BiasAggregator = _BiasAggregator
        is_aggregator_available = _is_aggregator_available
    except ImportError:
        pass


# =============================================================================
# Vertex AI LLM Service Import
# =============================================================================

VERTEX_LLM_AVAILABLE = False
VertexLLMService = None
get_vertex_llm_service = None

try:
    from vertex_llm_service import VertexLLMService as _VertexLLMService, get_vertex_llm_service as _get_vertex_llm_service
    VertexLLMService = _VertexLLMService
    get_vertex_llm_service = _get_vertex_llm_service
    VERTEX_LLM_AVAILABLE = True
except ImportError:
    try:
        from .vertex_llm_service import VertexLLMService as _VertexLLMService, get_vertex_llm_service as _get_vertex_llm_service
        VertexLLMService = _VertexLLMService
        get_vertex_llm_service = _get_vertex_llm_service
        VERTEX_LLM_AVAILABLE = True
    except ImportError:
        pass
except Exception as e:
    print(f"Warning: Vertex AI LLM service not available: {e}")


# =============================================================================
# Security Module Import
# =============================================================================

SecurityConfig = None
require_api_key = lambda f: f
rate_limit = lambda *args, **kwargs: lambda f: f
admin_only = lambda f: f
usage_tracker = None

try:
    from security import require_api_key as _require_api_key, rate_limit as _rate_limit, admin_only as _admin_only, usage_tracker as _usage_tracker, SecurityConfig as _SecurityConfig
    require_api_key = _require_api_key
    rate_limit = _rate_limit
    admin_only = _admin_only
    usage_tracker = _usage_tracker
    SecurityConfig = _SecurityConfig
except ImportError:
    try:
        from .security import require_api_key as _require_api_key, rate_limit as _rate_limit, admin_only as _admin_only, usage_tracker as _usage_tracker, SecurityConfig as _SecurityConfig
        require_api_key = _require_api_key
        rate_limit = _rate_limit
        admin_only = _admin_only
        usage_tracker = _usage_tracker
        SecurityConfig = _SecurityConfig
    except ImportError:
        print("Warning: Security module not available. API will be unprotected!")


# =============================================================================
# Model Config Import
# =============================================================================

get_generation_models = None
get_evaluation_models = None

try:
    from model_config import get_generation_models as _get_gen, get_evaluation_models as _get_eval
    get_generation_models = _get_gen
    get_evaluation_models = _get_eval
except ImportError:
    try:
        from .model_config import get_generation_models as _get_gen, get_evaluation_models as _get_eval
        get_generation_models = _get_gen
        get_evaluation_models = _get_eval
    except ImportError:
        pass


# =============================================================================
# Bias Instructions Import
# =============================================================================

get_available_bias_types = None
get_available_debias_methods = None

try:
    from bias_instructions import get_available_bias_types as _get_bias, get_available_debias_methods as _get_debias
    get_available_bias_types = _get_bias
    get_available_debias_methods = _get_debias
except ImportError:
    try:
        from .bias_instructions import get_available_bias_types as _get_bias, get_available_debias_methods as _get_debias
        get_available_bias_types = _get_bias
        get_available_debias_methods = _get_debias
    except ImportError:
        pass


# =============================================================================
# Export All
# =============================================================================

__all__ = [
    # Core detectors
    'BiasDetector',
    'BiasType',
    'BiasInjector',
    'PromptDebiaser',

    # HEARTS / ML
    'HEARTSDetector',
    'is_hearts_available',
    'HEARTS_AVAILABLE',

    # Aggregator
    'BiasAggregator',
    'is_aggregator_available',

    # Vertex AI
    'VertexLLMService',
    'get_vertex_llm_service',
    'VERTEX_LLM_AVAILABLE',

    # Security
    'SecurityConfig',
    'require_api_key',
    'rate_limit',
    'admin_only',
    'usage_tracker',

    # Model config
    'get_generation_models',
    'get_evaluation_models',

    # Bias instructions
    'get_available_bias_types',
    'get_available_debias_methods',
]
