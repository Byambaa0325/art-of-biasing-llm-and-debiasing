# Corrected Architecture - Rule-Based vs LLM-Based

## Critical Misunderstanding: Rule-Based Usage

### ❌ **WRONG: Using Rules as Literal Transformations**

**Current Code (`bias_injection.py`):**
```python
def _inject_confirmation_bias(self, prompt: str) -> Dict[str, Any]:
    # ❌ LITERAL string template
    biased_prompt = f"Isn't it true that {prompt.lower()}? This clearly shows the pattern."

    return {
        'biased_prompt': biased_prompt,  # ❌ Returns literal transformation
        'bias_added': 'Confirmation Bias'
    }
```

**Problem:** This creates crude, templated prompts like:
```
Original: "What are the benefits of exercise?"
Biased:   "Isn't it true that what are the benefits of exercise?? This clearly shows the pattern."
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Grammatically broken, unnatural
```

### ✓ **CORRECT: Using Rules as LLM Instructions**

**Rules should be GUIDES for the LLM:**
```python
BIAS_INSTRUCTIONS = {
    'confirmation_bias': {
        'description': 'Confirmation bias makes the prompt suggest a particular conclusion',
        'techniques': [
            'Add leading phrases like "Isn\'t it true that..."',
            'Use words that presuppose an answer: "clearly", "obviously"',
            'Frame as rhetorical question that assumes agreement',
            'Add phrases like "this proves" or "everyone knows"'
        ],
        'examples': [
            {
                'original': 'What impact does social media have on mental health?',
                'biased': 'Isn\'t it obvious that social media is destroying our mental health? Everyone can see the clear negative effects.'
            },
            {
                'original': 'How effective are remote work policies?',
                'biased': 'Given that remote work clearly reduces productivity, how can companies justify these policies?'
            }
        ],
        'framework': 'Sun & Kok (2025) - Cognitive Bias Taxonomy'
    },

    'anchoring_bias': {
        'description': 'Anchoring bias introduces reference points that unduly influence judgment',
        'techniques': [
            'Provide a specific number or comparison point',
            'Use phrases like "compared to", "more than", "less than"',
            'Establish a baseline that influences the response',
            'Reference extreme cases as anchors'
        ],
        'examples': [
            {
                'original': 'What is a reasonable salary for this role?',
                'biased': 'Considering similar roles pay $150,000+, what is a reasonable salary for this role?'
            }
        ],
        'framework': 'Sun & Kok (2025) - Cognitive Bias Taxonomy'
    },

    'demographic_bias': {
        'description': 'Introduces demographic qualifiers that may trigger stereotypes',
        'techniques': [
            'Add demographic qualifiers (age, gender, race, religion)',
            'Use group identifiers instead of individual characteristics',
            'Make assumptions based on demographic membership',
            'Prime the model with demographic context'
        ],
        'examples': [
            {
                'original': 'What makes a good leader?',
                'biased': 'What makes a good male leader in tech companies?'
            }
        ],
        'framework': 'Neumann et al. (FAccT 2025) - Representational Bias'
    }
}
```

**Then use with LLM:**
```python
def inject_bias_with_llm(prompt: str, bias_type: str) -> str:
    """Use LLM to inject bias based on rules as instructions"""

    bias_guide = BIAS_INSTRUCTIONS[bias_type]

    system_prompt = f"""You are an expert in bias analysis. Your task is to modify a prompt to introduce {bias_type}.

{bias_guide['description']}

Techniques to use:
{chr(10).join('- ' + t for t in bias_guide['techniques'])}

Examples:
{chr(10).join(f"Original: {ex['original']}\nBiased: {ex['biased']}\n" for ex in bias_guide['examples'])}

IMPORTANT:
- Make the biased version sound NATURAL and grammatically correct
- Don't use obvious templates - be creative
- The bias should be subtle but effective
- Preserve the core question while introducing the bias

Return ONLY the biased prompt, nothing else."""

    user_prompt = f"Original prompt: {prompt}\n\nCreate a biased version with {bias_type}:"

    # Call LLM (Llama 3.3)
    llm = get_vertex_llm_service()
    biased_prompt = llm.generate(user_prompt, system_prompt=system_prompt)

    return biased_prompt
```

**Result:**
```
Original: "What are the benefits of exercise?"

Biased (LLM-generated):
"Given that exercise obviously improves both physical and mental health,
what specific benefits can we highlight to encourage more people to adopt
an active lifestyle?"
^^^^ Natural, grammatically correct, subtly biased
```

---

## Complete Corrected Flow

### Step 1: Initial Prompt Analysis

```
User: "What makes a good software engineer?"
         ↓
  /api/graph/expand
         ↓

1. Generate LLM Answer (Llama 3.3):
   "A good software engineer combines technical skills..."

2. Evaluate with HEARTS:
   - is_stereotype: false
   - confidence: 0.91
   - token_importance: [...]

3. Evaluate with Gemini:
   - bias_score: 0.15 (low)
   - severity: "low"
   - explanation: "Neutral, open-ended question"

4. Identify Available Bias Types:
   Based on the prompt content, determine which biases are applicable:

   ✓ Confirmation Bias - Can add leading language
   ✓ Demographic Bias - Can add demographic qualifiers
   ✓ Anchoring Bias - Can add comparison points
   ✓ Availability Bias - Can reference recent examples
   ✗ Already Biased - Skip de-bias if no bias detected

5. Return Potential Paths (NOT nodes):
   - "Add Confirmation Bias" → [Instructions from BIAS_INSTRUCTIONS]
   - "Add Demographic Bias" → [Instructions from BIAS_INSTRUCTIONS]
   - "Add Anchoring Bias" → [Instructions from BIAS_INSTRUCTIONS]
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "node-1",
      "prompt": "What makes a good software engineer?",
      "llm_answer": "A good software engineer combines technical skills...",

      "hearts_evaluation": {
        "is_stereotype": false,
        "confidence": 0.91,
        "probabilities": {
          "Stereotype": 0.09,
          "Non-Stereotype": 0.91
        }
      },

      "gemini_evaluation": {
        "bias_score": 0.15,
        "severity": "low",
        "explanation": "Neutral, open-ended question"
      },

      "bias_score": 0.12,
      "confidence": 0.91
    }
  ],

  "edges": [
    {
      "id": "edge-bias-confirmation",
      "source": "node-1",
      "type": "bias",
      "bias_type": "confirmation",
      "label": "Add Confirmation Bias",
      "description": "Make prompt leading and confirmatory",
      "instructions": {
        "description": "Confirmation bias makes the prompt suggest a particular conclusion",
        "techniques": ["Add leading phrases...", "Use presupposing words..."],
        "framework": "Sun & Kok (2025)"
      }
    },
    {
      "id": "edge-bias-demographic",
      "source": "node-1",
      "type": "bias",
      "bias_type": "demographic",
      "label": "Add Demographic Bias",
      "description": "Add demographic qualifiers",
      "instructions": {...}
    }
  ]
}
```

### Step 2: User Clicks "Add Confirmation Bias"

```
POST /api/graph/expand-node
{
  "node_id": "node-1",
  "prompt": "What makes a good software engineer?",
  "action": "bias",
  "bias_type": "confirmation"
}
         ↓

1. Get Bias Instructions:
   instructions = BIAS_INSTRUCTIONS['confirmation_bias']

2. Call LLM to Transform Prompt:
   system_prompt = """You are an expert in bias analysis...

   Techniques to use:
   - Add leading phrases like "Isn't it true that..."
   - Use words that presuppose an answer: "clearly", "obviously"

   Examples:
   Original: "What impact does social media have?"
   Biased: "Isn't it obvious that social media is destroying..."

   Make it NATURAL and grammatically correct."""

   biased_prompt = llm.generate(
       "Original: What makes a good software engineer?\n\nCreate biased version:",
       system_prompt
   )

   Result: "Don't you think that a good software engineer obviously
            needs strong coding skills and technical expertise above
            all else?"

3. Generate LLM Answer for NEW prompt:
   answer = llm.generate_answer(biased_prompt)

4. Evaluate NEW prompt with HEARTS:
   hearts_eval = hearts_detector.detect_stereotypes(biased_prompt)

5. Evaluate NEW prompt with Gemini:
   gemini_eval = llm.evaluate_bias(biased_prompt)

6. Determine New Available Paths from this node:
   - Can add MORE bias (anchoring, demographic)
   - Can DEBIAS (remove confirmation bias)
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "node-2",
      "prompt": "Don't you think that a good software engineer obviously needs strong coding skills and technical expertise above all else?",
      "llm_answer": "While coding skills are important...",
      "type": "biased",
      "parent_id": "node-1",
      "transformation": "Added confirmation bias using LLM",

      "hearts_evaluation": {
        "is_stereotype": true,
        "confidence": 0.78,
        "probabilities": {
          "Stereotype": 0.78,
          "Non-Stereotype": 0.22
        },
        "token_importance": [
          {"token": "obviously", "importance": 0.45},
          {"token": "don't you think", "importance": 0.42}
        ]
      },

      "gemini_evaluation": {
        "bias_score": 0.72,
        "severity": "high",
        "bias_types": ["confirmation_bias", "leading_question"],
        "explanation": "Uses leading language that presupposes agreement..."
      },

      "bias_score": 0.75,
      "confidence": 0.84
    }
  ],

  "edges": [
    {
      "id": "edge-1-2",
      "source": "node-1",
      "target": "node-2",
      "type": "bias",
      "label": "Confirmation Bias Added",
      "transformation_method": "LLM-based using cognitive bias techniques"
    },

    // NEW potential paths from node-2
    {
      "id": "edge-2-bias-anchoring",
      "source": "node-2",
      "type": "bias",
      "bias_type": "anchoring",
      "label": "Further Bias: Add Anchoring",
      "description": "Add comparison points or reference numbers"
    },
    {
      "id": "edge-2-debias-confirmation",
      "source": "node-2",
      "type": "debias",
      "method": "remove_confirmation",
      "label": "Remove Confirmation Bias",
      "description": "Neutralize leading language"
    }
  ]
}
```

---

## Debiasing Instructions

**Same concept - rules guide LLM:**

```python
DEBIAS_INSTRUCTIONS = {
    'remove_confirmation': {
        'description': 'Remove leading language and confirmatory framing',
        'techniques': [
            'Remove phrases like "isn\'t it", "obviously", "clearly"',
            'Convert rhetorical questions to neutral questions',
            'Remove presupposing language',
            'Make question open-ended without suggested answer'
        ],
        'examples': [
            {
                'biased': 'Isn\'t it obvious that social media is destroying mental health?',
                'debiased': 'What is the relationship between social media use and mental health outcomes?'
            }
        ],
        'framework': 'BiasBuster (Echterhoff et al., 2024)'
    },

    'remove_demographic': {
        'description': 'Remove demographic qualifiers and group references',
        'techniques': [
            'Remove demographic identifiers (age, gender, race, religion)',
            'Focus on individual characteristics, not group membership',
            'Use neutral language without demographic priming',
            'Generalize the question to all people'
        ],
        'examples': [
            {
                'biased': 'What makes a good male leader in tech?',
                'debiased': 'What makes a good leader in tech?'
            }
        ],
        'framework': 'BiasFreeBench (2024)'
    },

    'neutralize_language': {
        'description': 'Make language neutral and balanced',
        'techniques': [
            'Remove emotionally charged words',
            'Balance positive and negative framing',
            'Use objective, descriptive language',
            'Avoid stereotypical assumptions'
        ],
        'framework': 'SACD (Lyu et al., 2025)'
    }
}
```

---

## File Structure Changes Needed

### 1. Create `bias_instructions.py` (NEW)

```python
"""
Bias and Debiasing Instructions for LLM

These are GUIDES for the LLM to understand how to apply bias concepts,
NOT literal transformation rules.

Based on research frameworks:
- Sun & Kok (2025) - Cognitive Bias Taxonomy
- Neumann et al. (FAccT 2025) - Representational/Allocative Bias
- BiasBuster (Echterhoff et al., 2024)
- SACD (Lyu et al., 2025)
"""

BIAS_INSTRUCTIONS = {
    'confirmation_bias': {...},
    'anchoring_bias': {...},
    'demographic_bias': {...},
    'availability_bias': {...},
    'framing_bias': {...},
    'leading_question': {...},
    'stereotypical_assumption': {...}
}

DEBIAS_INSTRUCTIONS = {
    'remove_confirmation': {...},
    'remove_demographic': {...},
    'neutralize_language': {...},
    'remove_anchoring': {...},
    'balance_framing': {...}
}

def get_bias_instruction(bias_type: str) -> Dict:
    """Get instruction guide for bias type"""
    return BIAS_INSTRUCTIONS.get(bias_type)

def get_debias_instruction(method: str) -> Dict:
    """Get instruction guide for debiasing method"""
    return DEBIAS_INSTRUCTIONS.get(method)

def get_available_bias_types(prompt: str, detected_biases: Dict) -> List[str]:
    """
    Determine which bias types are applicable for this prompt.

    Logic:
    - If prompt already has confirmation bias, don't offer it
    - If prompt has demographic refs, don't offer demographic bias
    - Always offer types that aren't already present
    """
    available = []

    # Check what's already present
    has_confirmation = any(
        b['type'] == 'confirmation_bias'
        for b in detected_biases.get('cognitive_biases', [])
    )
    has_demographic = len(detected_biases.get('demographic_biases', [])) > 0

    # Offer biases not already present
    if not has_confirmation:
        available.append('confirmation_bias')
    if not has_demographic:
        available.append('demographic_bias')

    # Always offer these (can be compounded)
    available.extend(['anchoring_bias', 'availability_bias', 'framing_bias'])

    return available

def get_available_debias_methods(detected_biases: Dict) -> List[str]:
    """
    Determine which debiasing methods are applicable.

    Based on what biases were detected.
    """
    methods = []

    if any(b['type'] == 'confirmation_bias' for b in detected_biases.get('cognitive_biases', [])):
        methods.append('remove_confirmation')

    if detected_biases.get('demographic_biases'):
        methods.append('remove_demographic')

    if detected_biases.get('overall_bias_score', 0) > 0.3:
        methods.append('neutralize_language')

    return methods
```

### 2. Deprecate `bias_injection.py`

- **DON'T USE** for actual transformations
- Can keep for reference or delete
- All transformations go through LLM with instructions

### 3. Update `vertex_llm_service.py`

```python
def inject_bias_llm(self, prompt: str, bias_type: str) -> Dict[str, Any]:
    """
    Use Llama 3.3 to inject bias based on instruction guides.

    Args:
        prompt: Original prompt
        bias_type: Type of bias to inject (e.g., 'confirmation_bias')

    Returns:
        Dictionary with biased prompt and metadata
    """
    from bias_instructions import get_bias_instruction

    # Get instruction guide
    instruction = get_bias_instruction(bias_type)
    if not instruction:
        raise ValueError(f"Unknown bias type: {bias_type}")

    # Build system prompt with instructions
    system_prompt = f"""You are an expert in bias analysis and prompt engineering.

Your task is to modify a prompt to introduce {bias_type}.

{instruction['description']}

Techniques to use:
{chr(10).join('- ' + t for t in instruction['techniques'])}

Examples of this bias:
{chr(10).join(f"Original: {ex['original']}\nBiased: {ex['biased']}\n" for ex in instruction['examples'])}

Research Framework: {instruction['framework']}

CRITICAL REQUIREMENTS:
1. Make the biased version sound NATURAL and grammatically correct
2. Don't use obvious templates - be creative and subtle
3. The bias should be effective but not crude
4. Preserve the core intent while introducing the bias
5. Return ONLY the biased prompt - no explanation, no extra text

Your response should be the biased prompt only."""

    user_prompt = f"Original prompt: {prompt}\n\nCreate a naturally biased version:"

    biased_prompt = self.generate(
        user_prompt,
        system_prompt=system_prompt,
        temperature=0.8  # Higher for creativity
    )

    return {
        'biased_prompt': biased_prompt.strip(),
        'bias_added': bias_type.replace('_', ' ').title(),
        'explanation': instruction['description'],
        'framework': instruction['framework'],
        'source': 'LLM-based (Llama 3.3)',
        'instruction_based': True
    }

def debias_self_help(self, prompt: str, method: str = 'auto') -> Dict[str, Any]:
    """
    Use Llama 3.3 to debias based on instruction guides.

    Args:
        prompt: Potentially biased prompt
        method: Debiasing method or 'auto' to detect

    Returns:
        Dictionary with debiased prompt and metadata
    """
    from bias_instructions import get_debias_instruction, get_available_debias_methods
    from bias_detection import BiasDetector

    # Auto-detect method if needed
    if method == 'auto':
        detector = BiasDetector()
        detected = detector.detect_biases(prompt)
        methods = get_available_debias_methods(detected)
        method = methods[0] if methods else 'neutralize_language'

    # Get instruction guide
    instruction = get_debias_instruction(method)
    if not instruction:
        raise ValueError(f"Unknown debias method: {method}")

    # Build system prompt
    system_prompt = f"""You are an expert in fair and unbiased communication.

Your task is to remove bias from a prompt using the {method} approach.

{instruction['description']}

Techniques to use:
{chr(10).join('- ' + t for t in instruction['techniques'])}

Examples:
{chr(10).join(f"Biased: {ex['biased']}\nDebiased: {ex['debiased']}\n" for ex in instruction['examples'])}

Research Framework: {instruction['framework']}

CRITICAL REQUIREMENTS:
1. Make the debiased version sound natural and fluent
2. Preserve the core question/intent
3. Remove ALL bias indicators identified in the techniques
4. Keep the prompt clear and useful
5. Return ONLY the debiased prompt - no explanation

Your response should be the debiased prompt only."""

    user_prompt = f"Biased prompt: {prompt}\n\nCreate a debiased version:"

    debiased_prompt = self.generate(
        user_prompt,
        system_prompt=system_prompt,
        temperature=0.3  # Lower for consistency
    )

    return {
        'debiased_prompt': debiased_prompt.strip(),
        'method': method.replace('_', ' ').title(),
        'explanation': instruction['description'],
        'framework': instruction['framework'],
        'source': 'LLM-based (Llama 3.3)',
        'instruction_based': True
    }
```

---

## Summary of Changes

### ❌ Remove/Deprecate:
1. **`bias_injection.py`** - Literal string templates (wrong approach)
2. **`debiasing.py`** - Rule-based literal transformations
3. All uses of `bias_injector.inject_biases()` in API

### ✅ Add/Create:
1. **`bias_instructions.py`** - Instruction guides for LLM
2. Update **`vertex_llm_service.py`** - Use instructions to guide LLM
3. Update **`api.py`** - Return potential paths based on available biases

### ✅ Keep:
1. **`bias_detection.py`** - For identifying what biases exist (HEARTS uses this too)
2. **`hearts_detector.py`** - ML-based stereotype detection
3. **`bias_aggregator.py`** - Multi-layer evaluation

### The Key Difference:

**Before:** Rules → Literal Output
**After:** Rules → LLM Instructions → Natural Output

This makes the biased/debiased versions sound natural and intelligent, not template-based.

Should I implement these changes?
