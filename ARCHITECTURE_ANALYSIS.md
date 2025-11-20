# Architecture Analysis - Technical Problems

## Current vs Intended Flow

### ❌ **Current Implementation (INCORRECT)**

```
User inputs prompt
    ↓
/api/graph/expand
    ↓
1. Detect biases with HEARTS ✓
2. Generate ALL biased nodes immediately ❌
3. Generate ALL debiased nodes immediately ❌
4. Return ALL nodes at once ❌
5. NO LLM answer for original prompt ❌
6. NO Gemini evaluation ❌
    ↓
Returns: Original node + 10+ child nodes (pre-generated)
```

### ✓ **Intended Implementation (CORRECT)**

```
User inputs prompt
    ↓
/api/graph/expand
    ↓
1. Create node for original prompt
2. Generate LLM ANSWER for this prompt ← MISSING
3. Evaluate with HEARTS ✓
4. Evaluate with GEMINI ← MISSING
5. Return ONLY:
   - Original node (with answer + evaluations)
   - Potential PATHS (edges only, no destination nodes)
    ↓
Returns: 1 node + potential paths (no actual child nodes)

────────────────────────────────────────────

User clicks "Bias" button on a path
    ↓
/api/graph/expand-node
    ↓
1. Transform prompt using LLM with bias instructions
2. Create new node with transformed prompt
3. Generate LLM ANSWER for new prompt ← MISSING
4. Evaluate with HEARTS ← MISSING
5. Evaluate with GEMINI ✓ (partial)
6. Create new potential paths from this node ← MISSING
    ↓
Returns: New node (with answer + evaluations) + new paths
```

## Technical Problems Identified

### Problem 1: Premature Node Generation

**File:** `backend/api.py` lines 452-530

**Current Code:**
```python
# Generate biased versions (rule-based)
biased_versions = bias_injector.inject_biases(prompt)
for i, biased in enumerate(biased_versions):
    bias_id = str(uuid.uuid4())
    nodes.append({
        'id': bias_id,
        'label': f"Biased: {biased.get('bias_added', 'Bias')}",
        'prompt': biased.get('biased_prompt', ''),  # ❌ Creating actual nodes
        'type': 'biased',
        ...
    })
```

**Problem:** Creating 10+ nodes immediately on initial expand

**Solution:** Only return potential PATHS (edges), not actual nodes

```python
# ✓ CORRECT: Return only potential paths
potential_paths = [
    {
        'id': f"{root_id}-bias-confirmation",
        'source': root_id,
        'type': 'bias',
        'bias_type': 'confirmation',
        'label': 'Add Confirmation Bias',
        'description': 'Makes the prompt more leading and confirmatory'
    },
    {
        'id': f"{root_id}-bias-anchoring",
        'source': root_id,
        'type': 'bias',
        'bias_type': 'anchoring',
        'label': 'Add Anchoring Bias',
        'description': 'Introduces reference points that influence judgment'
    },
    {
        'id': f"{root_id}-debias-remove-demographic",
        'source': root_id,
        'type': 'debias',
        'method': 'remove_demographic',
        'label': 'Remove Demographic References',
        'description': 'Strips demographic qualifiers from the prompt'
    }
]

return jsonify({
    'nodes': [root_node],  # Only the original node
    'edges': potential_paths  # No 'target' field = potential paths
})
```

---

### Problem 2: Missing LLM Answer Generation

**File:** `backend/api.py` lines 420-450

**Current Code:**
```python
root_node = {
    'id': root_id,
    'prompt': prompt,
    'bias_score': detected_biases.get('overall_bias_score', 0),
    'biases': detected_biases
    # ❌ NO 'llm_answer' field
}
```

**Problem:** User can't see the LLM's response to the prompt

**Solution:** Generate answer using Llama

```python
# ✓ CORRECT: Generate LLM answer
llm_answer = None
if VERTEX_LLM_AVAILABLE:
    try:
        llm = get_vertex_llm_service()
        llm_answer = llm.generate_answer(prompt)
    except Exception as e:
        print(f"Warning: Could not generate LLM answer: {e}")

root_node = {
    'id': root_id,
    'prompt': prompt,
    'llm_answer': llm_answer,  # ✓ Include answer
    'bias_score': detected_biases.get('overall_bias_score', 0),
    'biases': detected_biases
}
```

---

### Problem 3: Missing Gemini Evaluation

**File:** `backend/api.py` lines 400-414

**Current Code:**
```python
detected_biases = bias_aggregator.detect_all_layers(
    prompt=prompt,
    use_hearts=True,
    use_gemini=False,  # ❌ Disabled
    explain=True
)
```

**Problem:** No Gemini evaluation on initial expand

**Solution:** Enable Gemini evaluation

```python
# ✓ CORRECT: Evaluate with both HEARTS and Gemini
detected_biases = bias_aggregator.detect_all_layers(
    prompt=prompt,
    use_hearts=True,
    use_gemini=True,  # ✓ Enable Gemini
    explain=True
)

# Separate evaluations for clarity
root_node = {
    'id': root_id,
    'prompt': prompt,
    'llm_answer': llm_answer,

    # HEARTS evaluation
    'hearts_evaluation': {
        'is_stereotype': detected_biases.get('hearts', {}).get('is_stereotype'),
        'confidence': detected_biases.get('hearts', {}).get('confidence'),
        'probabilities': detected_biases.get('hearts', {}).get('probabilities'),
        'token_importance': detected_biases.get('explanations', {}).get('most_biased_tokens')
    },

    # Gemini evaluation
    'gemini_evaluation': detected_biases.get('gemini_validation', {}).get('evaluation'),

    # Overall metrics
    'bias_score': detected_biases.get('overall_bias_score', 0),
    'confidence': detected_biases.get('confidence', 0)
}
```

---

### Problem 4: Expand-Node Missing Features

**File:** `backend/api.py` lines 586-715

**Issues:**
1. ❌ No HEARTS evaluation for expanded nodes
2. ❌ No LLM answer generation for expanded nodes
3. ❌ No new potential paths created from expanded nodes

**Current Code:**
```python
node_data = {
    'id': new_id,
    'prompt': debiased_prompt,
    'evaluation': evaluation  # Only Gemini, no HEARTS
    # ❌ No 'llm_answer'
    # ❌ No 'hearts_evaluation'
}

nodes.append(node_data)
edges.append({...})  # Only edge back to parent
# ❌ No new potential paths from this node

return jsonify({'nodes': nodes, 'edges': edges})
```

**Solution:**
```python
# ✓ CORRECT: Complete node expansion
llm = get_vertex_llm_service()

# 1. Transform prompt
if action == 'bias':
    transformed = llm.inject_bias_llm(prompt, bias_type)
    new_prompt = transformed.get('biased_prompt')
else:
    transformed = llm.debias_self_help(prompt)
    new_prompt = transformed.get('debiased_prompt')

# 2. Generate answer for new prompt
llm_answer = llm.generate_answer(new_prompt)

# 3. Evaluate with HEARTS
hearts_result = None
if HEARTS_AGGREGATOR_AVAILABLE and bias_aggregator:
    evaluation_result = bias_aggregator.detect_all_layers(
        prompt=new_prompt,
        use_hearts=True,
        use_gemini=True,
        explain=True
    )
    hearts_result = evaluation_result.get('hearts')
    gemini_result = evaluation_result.get('gemini_validation')

# 4. Build new node
new_id = str(uuid.uuid4())
node_data = {
    'id': new_id,
    'prompt': new_prompt,
    'llm_answer': llm_answer,  # ✓ Include answer
    'type': 'biased' if action == 'bias' else 'debiased',

    # HEARTS evaluation
    'hearts_evaluation': {
        'is_stereotype': hearts_result.get('is_stereotype') if hearts_result else None,
        'confidence': hearts_result.get('confidence') if hearts_result else None,
        'probabilities': hearts_result.get('probabilities') if hearts_result else None,
        'token_importance': evaluation_result.get('explanations', {}).get('most_biased_tokens')
    },

    # Gemini evaluation
    'gemini_evaluation': gemini_result.get('evaluation') if gemini_result else None,

    # Overall metrics
    'bias_score': evaluation_result.get('overall_bias_score', 0),
    'confidence': evaluation_result.get('confidence', 0)
}

# 5. Create potential paths from this new node
potential_paths = [
    {
        'id': f"{new_id}-bias-{bias_type}",
        'source': new_id,
        'type': 'bias',
        'bias_type': bias_type,
        'label': f'Further Bias: {bias_type}',
    },
    {
        'id': f"{new_id}-debias-{method}",
        'source': new_id,
        'type': 'debias',
        'method': method,
        'label': f'Debias: {method}',
    }
]

return jsonify({
    'nodes': [node_data],
    'edges': [
        {
            'id': f"{node_id}-{new_id}",
            'source': node_id,
            'target': new_id,
            'type': action,
            'label': transformed.get('bias_added') or transformed.get('method')
        }
    ] + potential_paths  # ✓ Include new potential paths
})
```

---

## Correct Data Flow

### Initial Expand Flow

```
POST /api/graph/expand
{
  "prompt": "Why are women always so emotional?"
}

↓

Backend Processing:
1. Generate LLM answer using Llama
2. Evaluate with HEARTS (stereotype detection)
3. Evaluate with Gemini (bias assessment)
4. Identify potential bias/debias paths

↓

Response:
{
  "nodes": [
    {
      "id": "node-123",
      "prompt": "Why are women always so emotional?",
      "llm_answer": "Women are not inherently more emotional...",

      "hearts_evaluation": {
        "is_stereotype": true,
        "confidence": 0.85,
        "probabilities": {
          "Stereotype": 0.853,
          "Non-Stereotype": 0.147
        },
        "token_importance": [
          {"token": "women", "importance": 0.42},
          {"token": "always", "importance": 0.38},
          {"token": "emotional", "importance": 0.31}
        ]
      },

      "gemini_evaluation": {
        "bias_score": 0.78,
        "severity": "high",
        "bias_types": ["gender", "stereotypical_assumption"],
        "explanation": "This prompt contains gender stereotypes..."
      },

      "bias_score": 0.81,
      "confidence": 0.87
    }
  ],

  "edges": [
    // Potential BIAS paths (no target nodes yet)
    {
      "id": "edge-bias-confirmation",
      "source": "node-123",
      "type": "bias",
      "bias_type": "confirmation",
      "label": "Add Confirmation Bias"
    },
    {
      "id": "edge-bias-anchoring",
      "source": "node-123",
      "type": "bias",
      "bias_type": "anchoring",
      "label": "Add Anchoring Bias"
    },

    // Potential DEBIAS paths (no target nodes yet)
    {
      "id": "edge-debias-remove-demographic",
      "source": "node-123",
      "type": "debias",
      "method": "remove_demographic",
      "label": "Remove Demographic References"
    },
    {
      "id": "edge-debias-neutralize",
      "source": "node-123",
      "type": "debias",
      "method": "neutralize_language",
      "label": "Neutralize Language"
    }
  ]
}
```

### Node Expansion Flow

```
User clicks "Add Confirmation Bias" button

↓

POST /api/graph/expand-node
{
  "node_id": "node-123",
  "prompt": "Why are women always so emotional?",
  "action": "bias",
  "bias_type": "confirmation"
}

↓

Backend Processing:
1. Transform prompt using Llama with bias instructions
2. Generate LLM answer for the NEW prompt
3. Evaluate NEW prompt with HEARTS
4. Evaluate NEW prompt with Gemini
5. Create new potential paths from the NEW node

↓

Response:
{
  "nodes": [
    {
      "id": "node-456",
      "prompt": "Isn't it true that women are always more emotional than men?",
      "llm_answer": "Research shows that emotional expression varies...",
      "type": "biased",

      "hearts_evaluation": {
        "is_stereotype": true,
        "confidence": 0.92,
        "probabilities": {
          "Stereotype": 0.923,
          "Non-Stereotype": 0.077
        },
        "token_importance": [
          {"token": "isn't", "importance": 0.45},
          {"token": "true", "importance": 0.43},
          {"token": "always", "importance": 0.41}
        ]
      },

      "gemini_evaluation": {
        "bias_score": 0.89,
        "severity": "high",
        "bias_types": ["confirmation_bias", "gender", "leading_question"],
        "explanation": "This is a leading question that assumes..."
      },

      "bias_score": 0.88,
      "confidence": 0.91
    }
  ],

  "edges": [
    // Edge connecting parent to this new node
    {
      "id": "edge-123-456",
      "source": "node-123",
      "target": "node-456",
      "type": "bias",
      "label": "Confirmation Bias Added"
    },

    // NEW potential paths from this node
    {
      "id": "edge-456-bias-anchoring",
      "source": "node-456",
      "type": "bias",
      "bias_type": "anchoring",
      "label": "Further Bias: Anchoring"
    },
    {
      "id": "edge-456-debias-remove",
      "source": "node-456",
      "type": "debias",
      "method": "remove_confirmation",
      "label": "Remove Confirmation Bias"
    }
  ]
}
```

---

## Required Changes Summary

### 1. `/api/graph/expand` Endpoint

**Changes needed:**
- ✓ Keep HEARTS evaluation
- ✅ **ADD:** Generate LLM answer for original prompt
- ✅ **ADD:** Enable Gemini evaluation
- ✅ **CHANGE:** Return only potential paths, not actual child nodes
- ✅ **CHANGE:** Structure evaluations clearly (separate hearts_evaluation, gemini_evaluation)

### 2. `/api/graph/expand-node` Endpoint

**Changes needed:**
- ✓ Keep LLM transformation
- ✅ **ADD:** Generate LLM answer for transformed prompt
- ✅ **ADD:** HEARTS evaluation for transformed prompt
- ✓ Keep Gemini evaluation
- ✅ **ADD:** Create new potential paths from the expanded node
- ✅ **CHANGE:** Structure evaluations clearly

### 3. Bias Aggregator

**Changes needed:**
- ✅ **ENSURE:** `use_gemini=True` works correctly
- ✅ **ENSURE:** Returns both hearts and gemini results separately

### 4. Frontend (React)

**Changes needed:**
- ✅ Display `llm_answer` in node details
- ✅ Display both `hearts_evaluation` and `gemini_evaluation`
- ✅ Show potential paths as buttons (not pre-rendered nodes)
- ✅ On click, call `/api/graph/expand-node` to create actual node
- ✅ Render token importance visualization

---

## Node Structure Definition

```typescript
interface Node {
  id: string;
  prompt: string;
  llm_answer: string;  // LLM's response to this prompt
  type: 'original' | 'biased' | 'debiased';

  // HEARTS ML evaluation
  hearts_evaluation: {
    is_stereotype: boolean;
    confidence: number;
    probabilities: {
      'Stereotype': number;
      'Non-Stereotype': number;
    };
    token_importance: Array<{
      token: string;
      importance: number;
      contribution: 'positive' | 'negative';
    }>;
  };

  // Gemini LLM evaluation
  gemini_evaluation: {
    bias_score: number;  // 0-1
    severity: 'low' | 'moderate' | 'high';
    bias_types: string[];
    explanation: string;
    recommendations: string;
  };

  // Overall metrics
  bias_score: number;  // Ensemble score 0-1
  confidence: number;  // Detection confidence 0-1

  // Metadata
  detection_sources: string[];
  layers_used: string[];
}

interface Edge {
  id: string;
  source: string;
  target?: string;  // Undefined for potential paths
  type: 'bias' | 'debias';
  label: string;

  // For bias paths
  bias_type?: 'confirmation' | 'anchoring' | 'availability' | 'framing';

  // For debias paths
  method?: 'remove_demographic' | 'neutralize_language' | 'remove_confirmation';

  // Description shown in UI
  description?: string;
}
```

---

## Implementation Priority

### Phase 1: Fix Core Flow (Critical)
1. ✅ Fix `/api/graph/expand` to NOT generate child nodes
2. ✅ Add LLM answer generation in `/api/graph/expand`
3. ✅ Enable Gemini evaluation in `/api/graph/expand`
4. ✅ Return potential paths only

### Phase 2: Fix Node Expansion (Critical)
1. ✅ Add LLM answer generation in `/api/graph/expand-node`
2. ✅ Add HEARTS evaluation in `/api/graph/expand-node`
3. ✅ Create new potential paths from expanded nodes

### Phase 3: Enhance Data Structure (Important)
1. ✅ Separate hearts_evaluation and gemini_evaluation
2. ✅ Include token_importance in node data
3. ✅ Add clear metadata fields

### Phase 4: Frontend Integration (Important)
1. Display LLM answers
2. Show HEARTS + Gemini metrics side-by-side
3. Render potential paths as interactive buttons
4. Token importance visualization
