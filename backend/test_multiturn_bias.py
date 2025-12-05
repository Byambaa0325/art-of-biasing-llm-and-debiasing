"""
Test script for multi-turn bias injection
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

# Try to load Bedrock credentials
try:
    from bedrock_client import load_env_file
    parent_env = Path(__file__).parent.parent / ".env.bedrock"
    if parent_env.exists():
        load_env_file(str(parent_env))
    else:
        load_env_file(".env.bedrock")
except Exception as e:
    print(f"Warning: Could not load Bedrock credentials: {e}")

def test_bedrock_multiturn():
    """Test multi-turn bias injection with Bedrock"""
    print("=" * 60)
    print("Testing Multi-Turn Bias Injection (Bedrock)")
    print("=" * 60)
    
    try:
        from bedrock_llm_service import get_bedrock_llm_service
    except ImportError:
        print("✗ Bedrock LLM service not available")
        return False
    
    try:
        llm = get_bedrock_llm_service()
        print("✓ Bedrock LLM service initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Bedrock service: {e}")
        return False
    
    # Test prompt
    test_prompt = "What are the best programming languages to learn?"
    bias_type = "confirmation_bias"
    
    print(f"\nTest Prompt: {test_prompt}")
    print(f"Bias Type: {bias_type}")
    print("\nGenerating multi-turn bias injection...")
    
    try:
        result = llm.inject_bias_llm(test_prompt, bias_type)
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"\n✓ Bias Added: {result.get('bias_added')}")
        print(f"✓ Framework: {result.get('framework')}")
        print(f"✓ Multi-turn: {result.get('multi_turn')}")
        print(f"✓ Target Group: {result.get('target_group')}")
        
        if result.get('conversation'):
            conv = result['conversation']
            print("\n" + "-" * 60)
            print("CONVERSATION HISTORY")
            print("-" * 60)
            
            print("\n[Turn 1 - Priming Question]")
            print(f"User: {conv.get('turn1_question', 'N/A')}")
            print(f"\nAssistant: {conv.get('turn1_response', 'N/A')[:200]}...")
            
            print("\n[Turn 2 - Original Prompt]")
            print(f"User: {conv.get('original_prompt', 'N/A')}")
            print(f"\nAssistant: {conv.get('turn2_response', 'N/A')[:200]}...")
        
        print("\n" + "=" * 60)
        print("✓ Test PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vertex_multiturn():
    """Test multi-turn bias injection with Vertex AI"""
    print("\n" + "=" * 60)
    print("Testing Multi-Turn Bias Injection (Vertex AI)")
    print("=" * 60)
    
    try:
        from vertex_llm_service import get_vertex_llm_service
    except ImportError:
        print("✗ Vertex AI LLM service not available")
        return False
    
    try:
        llm = get_vertex_llm_service()
        print("✓ Vertex AI LLM service initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Vertex service: {e}")
        return False
    
    # Test prompt
    test_prompt = "What makes a good leader?"
    bias_type = "anchoring_bias"
    
    print(f"\nTest Prompt: {test_prompt}")
    print(f"Bias Type: {bias_type}")
    print("\nGenerating multi-turn bias injection...")
    
    try:
        result = llm.inject_bias_llm(test_prompt, bias_type)
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"\n✓ Bias Added: {result.get('bias_added')}")
        print(f"✓ Framework: {result.get('framework')}")
        print(f"✓ Multi-turn: {result.get('multi_turn')}")
        print(f"✓ Target Group: {result.get('target_group')}")
        
        if result.get('conversation'):
            conv = result['conversation']
            print("\n" + "-" * 60)
            print("CONVERSATION HISTORY")
            print("-" * 60)
            
            print("\n[Turn 1 - Priming Question]")
            print(f"User: {conv.get('turn1_question', 'N/A')}")
            print(f"\nAssistant: {conv.get('turn1_response', 'N/A')[:200]}...")
            
            print("\n[Turn 2 - Original Prompt]")
            print(f"User: {conv.get('original_prompt', 'N/A')}")
            print(f"\nAssistant: {conv.get('turn2_response', 'N/A')[:200]}...")
        
        print("\n" + "=" * 60)
        print("✓ Test PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Multi-Turn Bias Injection Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test Bedrock
    results.append(("Bedrock", test_bedrock_multiturn()))
    
    # Test Vertex AI (if available)
    results.append(("Vertex AI", test_vertex_multiturn()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for service, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{service:20s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


