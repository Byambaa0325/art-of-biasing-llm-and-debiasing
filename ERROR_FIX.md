# JSON Serialization Error - Root Cause Analysis & Fix

## Problem Summary

**Error**: `TypeError: Object of type BiasAggregator is not JSON serializable`

**Location**: `backend/api.py` in both `/api/graph/expand` and `/api/graph/expand-node` endpoints

## Root Cause

The issue was NOT in individual fields being non-serializable. The root cause was:

**Complex nested dictionaries from detection methods contained non-serializable objects deep in their structure.**

### Why It Kept Happening

1. `bias_aggregator.detect_all_layers()` returns a complex nested dictionary
2. This dictionary contains results from:
   - `rule_detector.detect_biases()`
   - `hearts_detector.detect_stereotypes()`
   - `llm_service.evaluate_bias()`
3. These methods return dictionaries that may contain:
   - Custom Python objects
   - References to detector instances
   - NumPy arrays
   - Other non-serializable types

4. When we extracted fields like `detected_biases.get('hearts')`, we were still getting nested dictionaries that contained non-serializable objects

5. **Manually converting individual fields (e.g., `float(...)`, `str(...)`) was treating symptoms, not the root cause**

## The Fix

### Created `sanitize_for_json()` Helper Function

```python
def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert any object to JSON-serializable primitives.
    This prevents 'Object of type X is not JSON serializable' errors.
    """
    # Handle None
    if obj is None:
        return None

    # Handle primitives
    if isinstance(obj, (bool, int, float, str)):
        return obj

    # Handle lists/tuples
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]

    # Handle dicts
    if isinstance(obj, dict):
        return {str(key): sanitize_for_json(value) for key, value in obj.items()}

    # Handle sets
    if isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]

    # Handle objects with __dict__ (convert to dict)
    if hasattr(obj, '__dict__'):
        return sanitize_for_json(obj.__dict__)

    # Fallback: convert to string
    return str(obj)
```

### Applied to Both Endpoints

**Before** (treating symptoms):
```python
return jsonify({
    'nodes': [node],
    'edges': edges
})
# Error: BiasAggregator not serializable
```

**After** (fixing root cause):
```python
response = sanitize_for_json({
    'nodes': [node],
    'edges': edges
})
return jsonify(response)
# Now ANY non-serializable object is converted automatically
```

## Why This Solution Works

1. **Comprehensive**: Handles ANY type of object, not just specific cases
2. **Recursive**: Catches non-serializable objects at ANY nesting level
3. **Safe Fallback**: Converts unknown types to strings instead of crashing
4. **Future-Proof**: Will handle new detection methods or data structures without modification
5. **Centralized**: One function fixes the issue everywhere it's applied

## What Was Wrong With Previous Approach

❌ **Symptom Treatment**:
```python
# Manually converting each field
'confidence': float(hearts_data.get('confidence', 0))
'token': str(token.get('token', ''))
```

Problems:
- Only fixes known fields
- Misses deeply nested objects
- Needs updating every time detection methods change
- Still allows non-serializable objects to slip through

✅ **Root Cause Fix**:
```python
# Recursively sanitize entire structure
response = sanitize_for_json(entire_response)
```

Benefits:
- Catches everything automatically
- No manual field conversion needed
- Works for any future changes
- Guaranteed JSON-serializable output

## Files Modified

1. **backend/api.py** (Lines 77-113): Added `sanitize_for_json()` function
2. **backend/api.py** (Line 580-587): Applied sanitization in `/api/graph/expand`
3. **backend/api.py** (Line 825-832): Applied sanitization in `/api/graph/expand-node`

## Testing

To verify the fix:

```bash
# Start backend
python backend/api.py

# Test initial expand
curl -X POST http://localhost:5000/api/graph/expand \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Why are women always so emotional?"}'

# Should return JSON without errors
```

## Key Takeaway

**Always fix root causes, not symptoms.**

When encountering serialization errors:
1. ❌ Don't manually convert individual fields
2. ✅ Create a recursive sanitizer for the entire data structure
3. ✅ Apply it once at the API boundary
4. ✅ Future changes are automatically handled

This approach prevents the whack-a-mole problem of fixing one field only to discover another non-serializable object later.

---

## Additional Fix: Missing Import Error

**Error**: `NameError: name 'BIAS_INSTRUCTIONS' is not defined`

**Location**: `backend/vertex_llm_service.py` line 248

**Cause**: The code referenced `BIAS_INSTRUCTIONS.keys()` in an error message but didn't import `BIAS_INSTRUCTIONS`.

**Fix**: Added `BIAS_INSTRUCTIONS` to the import statement:

```python
# Before
from bias_instructions import get_bias_instruction

# After
from bias_instructions import get_bias_instruction, BIAS_INSTRUCTIONS
```

**Files Modified**: `backend/vertex_llm_service.py` (line 237 and 240)
