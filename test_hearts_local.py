#!/usr/bin/env python
"""Test script to verify HEARTS is working locally"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("="*60)
print("HEARTS Local Setup Verification")
print("="*60)
print()

# Check imports
print("1. Checking dependencies...")
try:
    import transformers
    print(f"   ✓ transformers {transformers.__version__}")
except ImportError as e:
    print(f"   ✗ transformers not found: {e}")
    print("   Install with: pip install transformers")
    sys.exit(1)

try:
    import torch
    print(f"   ✓ torch {torch.__version__}")
    print(f"   ✓ CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"   ✗ torch not found: {e}")
    print("   Install with: pip install torch")
    sys.exit(1)

try:
    import shap
    print(f"   ✓ shap available")
except ImportError:
    print(f"   ⚠ shap not available (optional, for explanations)")
    print("   Install with: pip install shap")

try:
    import lime
    print(f"   ✓ lime available")
except ImportError:
    print(f"   ⚠ lime not available (optional, for explanations)")
    print("   Install with: pip install lime")

print()

# Check HEARTS detector
print("2. Checking HEARTS detector...")
try:
    from hearts_detector import is_hearts_available, HEARTSDetector
    if is_hearts_available():
        print("   ✓ HEARTS detector is available")
    else:
        print("   ✗ HEARTS detector not available")
        sys.exit(1)
except ImportError as e:
    print(f"   ✗ Failed to import HEARTS detector: {e}")
    sys.exit(1)

print()

# Test initialization (lazy load test - this will download model on first run)
print("3. Testing HEARTS initialization...")
print("   (This may download the model on first run - ~500MB)")
try:
    detector = HEARTSDetector(enable_shap=False, enable_lime=False)
    print("   ✓ HEARTS detector initialized successfully")
    print(f"   ✓ Model device: {detector.device}")
except Exception as e:
    print(f"   ✗ Failed to initialize HEARTS: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test detection
print("4. Testing HEARTS detection...")
try:
    test_prompt = "What are the benefits of regular exercise?"
    result = detector.detect_stereotypes(test_prompt, explain=False)
    print(f"   ✓ Detection successful")
    print(f"   ✓ Prompt: {test_prompt}")
    print(f"   ✓ Prediction: {result['prediction']}")
    print(f"   ✓ Confidence: {result['confidence']:.2%}")
except Exception as e:
    print(f"   ✗ Detection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*60)
print("✓ All tests passed! HEARTS is ready to use locally.")
print("="*60)
print()
print("Environment variables you can set:")
print("  ENABLE_HEARTS=true (default: true)")
print("  HEARTS_LAZY_LOAD=true (default: true - loads on first use)")
print("  HEARTS_LOCAL_FILES_ONLY=false (default: false - download if needed)")
print("  HF_HOME=<path> (optional: set HuggingFace cache directory)")

