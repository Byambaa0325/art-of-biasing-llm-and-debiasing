"""
Test script for HEARTS integration

Tests:
1. HEARTS detector standalone
2. Bias aggregator multi-layer detection
3. Comparison of rule-based vs HEARTS detection

Run with: python -m backend.test_hearts_integration
or from backend/: python test_hearts_integration.py
"""

import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from hearts_detector import HEARTSDetector, is_hearts_available
from bias_aggregator import BiasAggregator
from bias_detection import BiasDetector


def test_hearts_detector():
    """Test HEARTS detector standalone"""
    print("\n" + "=" * 70)
    print("TEST 1: HEARTS Detector Standalone")
    print("=" * 70)

    if not is_hearts_available():
        print("❌ HEARTS not available. Install: pip install transformers torch")
        return False

    try:
        detector = HEARTSDetector()
        print("✓ HEARTS detector loaded successfully\n")

        # Test prompts
        test_cases = [
            ("Neutral", "What are the benefits of regular exercise?"),
            ("Stereotype", "Why are women always so emotional?"),
            ("Neutral", "How does photosynthesis work in plants?"),
            ("Stereotype", "All teenagers are irresponsible with money."),
            ("Neutral", "What is the capital of France?"),
            ("Stereotype", "Old people can't use technology properly.")
        ]

        correct_predictions = 0
        total_cases = len(test_cases)

        for expected, prompt in test_cases:
            result = detector.detect_stereotypes(prompt, explain=True)

            is_correct = (
                (expected == "Stereotype" and result['is_stereotype']) or
                (expected == "Neutral" and not result['is_stereotype'])
            )
            correct_predictions += is_correct

            status = "✓" if is_correct else "✗"
            print(f"{status} Expected: {expected:12} | Predicted: {result['prediction']:15} | Confidence: {result['confidence']:.2%}")
            print(f"   Prompt: {prompt[:60]}...")

            # Show top biased tokens for stereotypes
            if result.get('explanations', {}).get('token_importance'):
                top_tokens = result['explanations']['token_importance'][:3]
                print(f"   Top tokens: {', '.join([t['token'] for t in top_tokens])}")

            print()

        accuracy = correct_predictions / total_cases
        print(f"Accuracy: {accuracy:.1%} ({correct_predictions}/{total_cases})")
        print("✓ HEARTS detector test completed\n")
        return True

    except Exception as e:
        print(f"❌ HEARTS detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bias_aggregator():
    """Test multi-layer bias aggregator"""
    print("\n" + "=" * 70)
    print("TEST 2: Multi-Layer Bias Aggregator")
    print("=" * 70)

    try:
        aggregator = BiasAggregator()
        print("✓ Bias aggregator initialized\n")

        test_prompts = [
            "What are effective teaching strategies?",
            "Why are all millennials lazy and entitled?",
            "Explain the theory of relativity.",
            "Women are naturally better at multitasking than men."
        ]

        for prompt in test_prompts:
            print(f"\nPrompt: {prompt}")
            print("-" * 70)

            result = aggregator.detect_all_layers(
                prompt=prompt,
                use_hearts=is_hearts_available(),
                use_gemini=False,
                explain=True
            )

            print(f"Overall Bias Score: {result['overall_bias_score']:.2%}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Detection Sources: {', '.join(result['detection_sources'])}")
            print(f"Layers Used: {', '.join(result['layers_used'])}")

            # Show detected biases
            detected = result['detected_biases']
            if detected.get('stereotypes'):
                print(f"\nStereotype Detection:")
                for stereo in detected['stereotypes']:
                    print(f"  - Detected: {stereo['detected']}")
                    print(f"  - Confidence: {stereo['confidence']:.2%}")
                    if stereo.get('most_biased_tokens'):
                        tokens = ', '.join([t['token'] for t in stereo['most_biased_tokens']])
                        print(f"  - Key tokens: {tokens}")

            if detected.get('cognitive_biases'):
                print(f"\nCognitive Biases: {len(detected['cognitive_biases'])} detected")
                for bias in detected['cognitive_biases'][:2]:
                    print(f"  - {bias['type']}")

            # Show token explanations if available
            explanations = result.get('explanations', {})
            if explanations.get('most_biased_tokens'):
                print(f"\nMost Biased Tokens (SHAP):")
                for token in explanations['most_biased_tokens'][:5]:
                    print(f"  - {token['token']:15} importance: {token['importance']:.3f}")

        print("\n✓ Bias aggregator test completed\n")
        return True

    except Exception as e:
        print(f"❌ Bias aggregator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Compare rule-based vs HEARTS detection"""
    print("\n" + "=" * 70)
    print("TEST 3: Rule-Based vs HEARTS Comparison")
    print("=" * 70)

    if not is_hearts_available():
        print("⚠ HEARTS not available, skipping comparison test")
        return True

    try:
        rule_detector = BiasDetector()
        hearts_detector = HEARTSDetector()

        test_prompts = [
            "Why are women always so emotional?",
            "All teenagers are irresponsible with money.",
            "What is the best way to learn programming?"
        ]

        for prompt in test_prompts:
            print(f"\nPrompt: {prompt}")
            print("-" * 70)

            # Rule-based detection
            rule_result = rule_detector.detect_biases(prompt)
            rule_score = rule_result.get('overall_bias_score', 0)

            # HEARTS detection
            hearts_result = hearts_detector.detect_stereotypes(prompt, explain=False)
            hearts_score = hearts_result['probabilities']['Stereotype']

            print(f"Rule-based Score:  {rule_score:.2%}")
            print(f"HEARTS Score:      {hearts_score:.2%}")
            print(f"HEARTS Prediction: {hearts_result['prediction']}")

            # Show what rule-based detected
            if rule_result.get('cognitive_biases'):
                print(f"Rule-based detected: {len(rule_result['cognitive_biases'])} cognitive biases")
            if rule_result.get('demographic_biases'):
                print(f"Rule-based detected: {len(rule_result['demographic_biases'])} demographic biases")

        print("\n✓ Comparison test completed\n")
        return True

    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HEARTS Integration Test Suite")
    print("=" * 70)

    # Check HEARTS availability
    print(f"\nHEARTS Available: {is_hearts_available()}")
    if not is_hearts_available():
        print("\n⚠ WARNING: HEARTS not available")
        print("Install with: pip install transformers torch shap lime")
        print("Tests will run in limited mode\n")

    # Run tests
    results = []
    results.append(("HEARTS Detector", test_hearts_detector()))
    results.append(("Bias Aggregator", test_bias_aggregator()))
    results.append(("Comparison", test_comparison()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20} {status}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
