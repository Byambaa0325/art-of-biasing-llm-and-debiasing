"""
Test Amazon Nova Pro with Persona-Based Bias Injection

This script demonstrates the new default configuration:
- Persona-based bias injection (only option)
- Amazon Nova Pro for generating bias questions
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from bedrock_client import BedrockModels
from bias_instructions import get_sentence_generation_guide

# Try to import service (may fail if credentials not configured)
try:
    from bedrock_llm_service import BedrockLLMService
    SERVICE_AVAILABLE = True
except Exception as e:
    SERVICE_AVAILABLE = False
    SERVICE_ERROR = str(e)

def test_configuration():
    """Test that the configuration is correctly set"""
    print("=" * 80)
    print("TESTING AMAZON NOVA PRO + PERSONA-BASED CONFIGURATION")
    print("=" * 80)

    # Test 1: Verify Amazon Nova Pro model ID
    print("\n1. Amazon Nova Pro Model ID:")
    print(f"   {BedrockModels.NOVA_PRO}")

    # Test 2: Verify persona templates are available
    print("\n2. Available Persona Templates:")
    bias_types = [
        'confirmation_bias',
        'availability_bias',
        'anchoring_bias',
        'framing_bias',
        'leading_question',
        'demographic_bias',
        'negativity_bias',
        'stereotypical_assumption'
    ]

    for bias_type in bias_types:
        template = get_sentence_generation_guide(bias_type)
        status = "[OK]" if template else "[MISSING]"
        print(f"   {status} {bias_type}")

    # Test 3: Initialize service and verify default model
    print("\n3. Bedrock LLM Service Initialization:")
    if not SERVICE_AVAILABLE:
        print(f"   [SKIP] Service not available (credentials needed)")
        print(f"   Reason: {SERVICE_ERROR}")
        service = None
    else:
        try:
            service = BedrockLLMService()
            print(f"   [OK] Service initialized")
            print(f"   Default model: {service.default_model}")
            print(f"   Evaluation model: {service.evaluation_model}")
        except Exception as e:
            print(f"   [ERROR] {e}")
            service = None

    # Test 4: Show example persona template
    print("\n4. Example Persona Template (Confirmation Bias - 'The Validator'):")
    print("-" * 80)
    template = get_sentence_generation_guide('confirmation_bias')
    if template:
        formatted = template.format(
            sentence="The software developer is ===nerdy===",
            trait="nerdy"
        )
        print(formatted[:400] + "...")

    print("\n" + "=" * 80)
    print("CONFIGURATION SUMMARY")
    print("=" * 80)
    print("- Bias Injection Method: PERSONA-BASED (only option)")
    print(f"- Bias Generator Model: Amazon Nova Pro ({BedrockModels.NOVA_PRO})")
    print("- Target Model: Configurable (defaults to Claude 3.5 Sonnet V2)")
    print("- Available Personas: 8 bias types")
    print("\nThe system will ALWAYS use:")
    print("1. Persona-based templates (psycholinguistic approach removed)")
    print("2. Amazon Nova Pro for generating priming questions")
    print("3. Specified target model for evaluating bias susceptibility")
    print("=" * 80)

    # Test 5: Verify inject_bias_llm signature
    print("\n5. Method Signature Check:")
    print("-" * 80)
    if service and SERVICE_AVAILABLE:
        import inspect
        sig = inspect.signature(service.inject_bias_llm)
        print(f"   inject_bias_llm{sig}")
        print("\n   Parameters:")
        for param_name, param in sig.parameters.items():
            default = f" = {param.default}" if param.default != inspect.Parameter.empty else ""
            print(f"   - {param_name}: {param.annotation.__name__ if hasattr(param.annotation, '__name__') else param.annotation}{default}")

        print("\n   Note: 'use_persona' parameter has been removed")
        print("   Note: 'bias_generator_model_id' defaults to Amazon Nova Pro")
    else:
        print("   [SKIP] Service not available (see above)")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nTo test with live API call (requires Bedrock credentials):")
    print("  from backend.bedrock_llm_service import BedrockLLMService")
    print("  service = BedrockLLMService()")
    print("  result = service.inject_bias_llm(")
    print("      prompt='The software developer is ===nerdy===',")
    print("      bias_type='confirmation_bias',")
    print("      model_id='us.anthropic.claude-3-5-sonnet-20241022-v2:0'")
    print("  )")
    print("  print(result['conversation']['turn1_question'])")


if __name__ == "__main__":
    test_configuration()
