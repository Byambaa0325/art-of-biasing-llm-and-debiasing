# Bias Evaluation System Update

## Overview
This update enhances the bias evaluation system with:
1. **Multi-category Gemini evaluation** - Gemini now scores across multiple bias types
2. **Enhanced node dialog** - Full display of node transformations, sources, and frameworks

## Changes Made

### 1. Gemini Multi-Category Evaluation

**File:** `backend/vertex_llm_service.py`

#### Before:
Gemini returned a single bias score with basic metadata:
```json
{
  "bias_score": 0.65,
  "severity": "moderate",
  "bias_types": ["gender", "stereotyping"],
  "explanation": "..."
}
```

#### After:
Gemini now evaluates across **4 distinct bias categories**, each with its own score:

```json
{
  "bias_categories": [
    {
      "category": "demographic",
      "score": 0.72,
      "detected_types": ["gender", "race"],
      "description": "Detected gender stereotypes and racial assumptions"
    },
    {
      "category": "cognitive",
      "score": 0.45,
      "detected_types": ["confirmation bias", "anchoring"],
      "description": "Moderate confirmation bias in question framing"
    },
    {
      "category": "stereotyping",
      "score": 0.83,
      "detected_types": ["gender stereotypes", "occupational stereotypes"],
      "description": "Strong gender-occupation associations"
    },
    {
      "category": "structural",
      "score": 0.31,
      "detected_types": ["leading questions"],
      "description": "Slight leading question structure"
    }
  ],
  "overall_severity": "high",
  "explanation": "Overall assessment...",
  "recommendations": "Suggestions..."
}
```

**Bias Categories:**
1. **Demographic** - Race, gender, age, religion, nationality, socioeconomic status, sexual orientation, disability
2. **Cognitive** - Confirmation bias, availability bias, anchoring, framing, etc.
3. **Stereotyping** - Cultural stereotypes, gender stereotypes, occupational stereotypes
4. **Structural** - Template bias, positional bias, leading questions, assumption-laden language

**Research Alignment:**
- Demographic: Neumann et al. (FAccT 2025), BEATS Framework
- Cognitive: Sun & Kok (2025), BiasBuster (Echterhoff et al., 2024)
- Stereotyping: HEARTS (King et al., 2024)
- Structural: Xu et al. (LREC 2024)

### 2. Enhanced Bias Metrics Display

**File:** `backend/bias_aggregator.py`

The Gemini judge metric now includes the full category breakdown:

```python
{
    'judge': 'Gemini 2.5 Flash',
    'score': 0.58,  # Average across categories
    'confidence': 0.85,
    'description': 'LLM-based bias evaluation across multiple categories',
    'severity': 'moderate',
    'bias_categories': [
        # Detailed category scores as shown above
    ],
    'model': 'publishers/google/models/gemini-2.0-flash-exp'
}
```

This allows users to see:
- Which bias category is most problematic
- Where different judges agree/disagree
- Specific bias types within each category

### 3. Enhanced "Full Prompt" Dialog

**File:** `frontend-react/src/App.js`

The dialog now displays comprehensive node information:

#### A. Node Information Section
Shows the node type and transformation applied:
- **Type**: original, biased, debiased
- **Transformation**: Label describing what changed (e.g., "Gender Bias Added", "Confirmation Bias Removed")

#### B. Transformation Details Section
For biased/debiased nodes, shows detailed transformation info:
- **Action**: bias or debias
- **Bias Type**: Which bias was injected (e.g., "confirmation", "gender")
- **Method**: Debiasing method used (e.g., "self-help", "counterfactual")
- **Framework**: Research framework applied (e.g., "BiasBuster (Echterhoff et al., 2024)")
- **Explanation**: How the transformation was performed

**Example:**
```
Transformation Details:
━━━━━━━━━━━━━━━━━━━━
Action: bias
Bias Type: confirmation
Framework: BiasBuster (Echterhoff et al., 2024)
Explanation: Injected confirmation bias by adding language
that assumes pre-existing beliefs...
```

#### C. Research Frameworks Section
Lists all research frameworks used in detecting/evaluating this node:
- BEATS Framework
- Neumann et al. (FAccT 2025)
- HEARTS (King et al., 2024)
- BiasBuster (Echterhoff et al., 2024)
- Sun & Kok (2025)

#### D. Detection Sources Section
Shows which systems evaluated the node:
- Rule-Based Detector
- HEARTS ALBERT-v2
- Gemini 2.5 Flash

#### E. Bias Evaluations Section (Enhanced)
Shows each judge's evaluation with:
- Overall score
- Confidence level
- Description and model info

**NEW:** For Gemini, displays category breakdown:
```
Gemini 2.5 Flash - 58%
Model: publishers/google/models/gemini-2.0-flash-exp
Severity: moderate

Bias Categories:
  ├─ demographic: 72% (gender, race)
  ├─ cognitive: 45% (confirmation bias, anchoring)
  ├─ stereotyping: 83% (gender stereotypes, occupational)
  └─ structural: 31% (leading questions)
```

## User Benefits

### 1. **Transparency**
Users can now see:
- Exactly which bias categories are problematic
- How each detection system rated each category
- The specific bias types within each category
- Complete provenance of transformations

### 2. **Actionable Insights**
Instead of "bias score: 65%", users see:
- "High demographic bias (72%) - gender and race"
- "Moderate cognitive bias (45%) - confirmation bias"
- "Very high stereotyping (83%) - gender-occupation associations"
- "Low structural bias (31%)"

This makes it clear **where to focus debiasing efforts**.

### 3. **Research Grounding**
Every evaluation is explicitly tied to:
- Academic research papers
- Validated frameworks
- Specific detection models

Users can trace any finding back to its source.

### 4. **Debugging & Understanding**
When different judges disagree, users can see:
- Which category they disagree on
- What specific bias types each detected
- The confidence level of each judgment

## Example Scenarios

### Scenario 1: Subtle Gender Bias

**Prompt:** "Women are naturally better at nursing. Why?"

**Gemini Evaluation:**
- Demographic: 15% (low - explicit mention but not allocative)
- Cognitive: 22% (low-moderate - slight confirmation bias)
- **Stereotyping: 91%** ← Clear signal
- Structural: 38% (moderate - assumption-laden)

**Action:** User focuses on stereotyping, which is the main issue.

### Scenario 2: Leading Question

**Prompt:** "Given that studies show X leads to Y, how can we use this?"

**Gemini Evaluation:**
- Demographic: 5% (none)
- **Cognitive: 78%** ← Anchoring + confirmation
- Stereotyping: 12% (low)
- **Structural: 82%** ← Leading question

**Action:** User addresses cognitive and structural issues, not demographics.

### Scenario 3: Multi-Faceted Bias

**Prompt:** "Why do Asian students perform better in math?"

**Gemini Evaluation:**
- **Demographic: 85%** ← Racial assumptions
- Cognitive: 67% ← Confirmation bias
- **Stereotyping: 94%** ← Model minority stereotype
- Structural: 45% ← Assumption-laden

**Action:** User sees this hits multiple categories - needs comprehensive debiasing.

## API Response Structure

### Node Structure (API Response)
```json
{
  "id": "uuid",
  "type": "biased",
  "prompt": "Modified prompt text",
  "transformation": "Confirmation Bias Added",
  
  "transformation_details": {
    "action": "bias",
    "bias_type": "confirmation",
    "method": null,
    "framework": "BiasBuster (Echterhoff et al., 2024)",
    "explanation": "Injected confirmation bias..."
  },
  
  "bias_metrics": [
    {
      "judge": "Rule-Based Detector",
      "score": 0.62,
      "confidence": 1.0,
      "description": "Pattern-matching for cognitive biases",
      "framework": "BEATS Framework"
    },
    {
      "judge": "HEARTS ALBERT-v2",
      "score": 0.73,
      "confidence": 0.89,
      "description": "ML-based stereotype detection",
      "framework": "HEARTS (King et al., 2024)",
      "model": "holistic-ai/bias_classifier_albertv2"
    },
    {
      "judge": "Gemini 2.5 Flash",
      "score": 0.58,
      "confidence": 0.85,
      "description": "Multi-category bias evaluation",
      "severity": "moderate",
      "bias_categories": [
        {
          "category": "demographic",
          "score": 0.45,
          "detected_types": ["gender"],
          "description": "Slight gender associations"
        },
        {
          "category": "cognitive",
          "score": 0.78,
          "detected_types": ["confirmation bias"],
          "description": "Strong confirmation bias"
        },
        {
          "category": "stereotyping",
          "score": 0.52,
          "detected_types": [],
          "description": "Moderate stereotypical language"
        },
        {
          "category": "structural",
          "score": 0.57,
          "detected_types": ["leading questions"],
          "description": "Leading question structure"
        }
      ],
      "model": "publishers/google/models/gemini-2.0-flash-exp"
    }
  ],
  
  "frameworks": [
    "BEATS Framework",
    "HEARTS (King et al., 2024)",
    "BiasBuster (Echterhoff et al., 2024)"
  ],
  
  "detection_sources": [
    "Rule-Based Detector",
    "HEARTS ALBERT-v2",
    "Gemini 2.5 Flash"
  ]
}
```

## Migration Notes

### Backward Compatibility
✅ All changes are backward compatible:
- Old nodes without `transformation_details` still work
- Legacy `bias_score` field still present
- Old `evaluation` format still supported

### New Fields (Optional)
- `bias_metrics[].bias_categories` - Gemini category breakdown
- `transformation_details` - Detailed transformation info
- `frameworks` - Array of research frameworks
- `detection_sources` - Array of detection systems

## Testing

### To Test Multi-Category Evaluation:
```bash
curl -X POST http://localhost:5000/api/graph/expand \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Women are naturally better at nursing than men"}'
```

**Expected:** Gemini metric includes `bias_categories` array with 4 entries.

### To Test Dialog Display:
1. Create a graph from starter prompt
2. Click a bias injection path (e.g., "Add Confirmation Bias")
3. Click "Full Prompt" on the new node
4. Verify you see:
   - Node type and transformation
   - Transformation details with framework
   - Research frameworks used
   - Detection sources
   - Gemini category breakdown

## Future Enhancements

### Potential Additions:
1. **Category Weighting** - Let users prioritize certain categories
2. **Category-Specific Debiasing** - Target specific bias types
3. **Historical Comparison** - Track how categories change across graph
4. **Category Filtering** - Filter graph by specific bias category
5. **Export by Category** - Download category-specific analyses

## Summary

| Feature | Before | After |
|---------|--------|-------|
| **Gemini Evaluation** | Single score | 4 category scores |
| **Category Detail** | Generic "bias_types" list | Specific types per category |
| **Dialog Info** | Minimal | Comprehensive (type, transformation, sources, frameworks) |
| **Research Attribution** | Generic | Explicit per category |
| **Actionability** | "Fix bias" | "Fix demographic and stereotyping, cognitive is okay" |
| **Button Label** | "More Info" | "Full Prompt" |

This update provides users with **granular, actionable, research-backed bias analysis** across multiple dimensions, making it easier to understand, debug, and address specific types of bias in their prompts.

