# Bias Metrics Display Update

## Changes Made

### Overview
Updated the bias evaluation system to display **individual bias metrics from multiple judges** instead of aggregating them into a single score. This provides more transparency and allows users to see how different bias detection models rate the same prompt.

### Backend Changes

#### 1. `backend/bias_aggregator.py`

**Changed:** `_calculate_ensemble_score()` method

**Before:**
- Returned a single float (0-1) representing weighted average of all judges
- Hidden which judge contributed what score

**After:**
- Returns a dictionary with array of individual bias metrics
- Each metric includes:
  - `judge`: Name of the evaluation model/system
  - `score`: Bias score (0-1)
  - `confidence`: Detection confidence
  - `description`: What this judge evaluates
  - `framework`: Research framework or model identifier
  - `model`: Model name (for ML models)
  - `severity`: (Gemini only) Severity level
  - `bias_types`: (Gemini only) Detected bias categories

**Example Response:**
```json
{
  "bias_metrics": [
    {
      "judge": "Rule-Based Detector",
      "score": 0.42,
      "confidence": 1.0,
      "description": "Pattern-matching for cognitive, demographic, and structural biases",
      "framework": "BEATS Framework, Neumann et al. (FAccT 2025)"
    },
    {
      "judge": "HEARTS ALBERT-v2",
      "score": 0.73,
      "confidence": 0.89,
      "description": "ML-based stereotype detection with 81.5% F1 score",
      "framework": "HEARTS (King et al., 2024)",
      "model": "holistic-ai/bias_classifier_albertv2"
    },
    {
      "judge": "Gemini 2.5 Flash",
      "score": 0.65,
      "confidence": 0.85,
      "description": "LLM-based bias evaluation with contextual understanding",
      "severity": "medium",
      "bias_types": ["gender", "stereotyping"],
      "model": "publishers/google/models/gemini-2.0-flash-exp"
    }
  ],
  "judge_count": 3,
  "judges_used": ["Rule-Based Detector", "HEARTS ALBERT-v2", "Gemini 2.5 Flash"]
}
```

#### 2. `backend/api.py`

**Changed:** Node data structure in `/api/graph/expand` and `/api/graph/expand-node`

**Added fields:**
- `bias_metrics`: Array of individual judge evaluations
- `judge_count`: Number of judges that evaluated this node
- `judges_used`: List of judge names

**Kept for backward compatibility:**
- `bias_score`: Average of all judge scores (for systems expecting single value)

### Frontend Changes

#### 1. `frontend-react/src/App.js` - Node Display

**Changed:** Bias score chips in node visualization

**Before:**
```jsx
<Chip label={`Bias: 65%`} color="warning" />
```

**After:**
```jsx
<Chip label={`Rule-Based Detector: 42%`} color="success" />
<Chip label={`HEARTS ALBERT-v2: 73%`} color="error" />
<Chip label={`Gemini 2.5 Flash: 65%`} color="warning" />
```

**Features:**
- Multiple chips, one per judge
- Color-coded by score: red (>60%), yellow (>30%), green (≤30%)
- Hover tooltip shows judge description and framework
- Compact display with smaller font sizes

#### 2. `frontend-react/src/App.js` - Node Dialog

**Added:** Detailed bias metrics section in the "Full Prompt" dialog

Shows each judge's evaluation in a card format:
- Judge name and score (with color-coded chip)
- Description of what this judge evaluates
- Framework/model identifier
- Confidence level
- Severity (for Gemini)

#### 3. Button Rename

**Changed:** "More Info" → "Full Prompt"

Makes it clearer that clicking this button shows the complete prompt text and detailed evaluations.

## Benefits

### 1. **Transparency**
Users can now see:
- Which detection system flagged what
- How much each judge agrees/disagrees
- The strengths of each approach (e.g., HEARTS for stereotypes, Gemini for context)

### 2. **Research Alignment**
Each metric shows:
- The research framework it's based on
- The model or system used
- Validation metrics (e.g., "81.5% F1 score")

### 3. **Debugging**
When judges disagree, users can understand why:
- Rule-based: Pattern matching (good for known biases)
- HEARTS: ML stereotype detection (good for subtle stereotypes)
- Gemini: Contextual understanding (good for complex scenarios)

### 4. **Confidence**
Users see confidence levels for each judge, helping them:
- Trust high-confidence evaluations
- Question low-confidence ones
- Understand when multiple judges agree (high source_agreement)

## Example Use Cases

### Case 1: High Agreement
```
Rule-Based: 75% | HEARTS: 78% | Gemini: 72%
→ Clear consensus: prompt is biased
```

### Case 2: Disagreement
```
Rule-Based: 25% | HEARTS: 82% | Gemini: 45%
→ HEARTS detected subtle stereotype that rules missed
→ User can investigate HEARTS token importance
```

### Case 3: Context-Dependent
```
Rule-Based: 60% | HEARTS: 42% | Gemini: 75%
→ Gemini caught contextual bias that HEARTS missed
→ User can read Gemini's explanation
```

## Migration Notes

### Backward Compatibility
- `bias_score` field still exists (average of all judges)
- Existing integrations expecting single score will still work
- Frontend falls back to single score if `bias_metrics` not available

### API Changes
No breaking changes - only additions:
- ✅ Old clients: Use `bias_score` (still works)
- ✅ New clients: Use `bias_metrics` array (more detail)

## Testing

### To Test Locally:
```bash
# Start backend
cd backend
python api.py

# Start frontend
cd frontend-react
npm start

# Test prompt
curl -X POST http://localhost:5000/api/graph/expand \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Women are naturally better at nursing than men"}'
```

### Expected Output:
Should see 3 bias metrics in response:
1. Rule-Based Detector (demographic bias)
2. HEARTS ALBERT-v2 (stereotype detection)
3. Gemini 2.5 Flash (contextual evaluation)

## Future Enhancements

### Potential Additions:
1. **Weighted Display**: Show larger chips for higher-confidence judges
2. **Judge Selection**: Let users toggle which judges to use
3. **Comparison Mode**: Compare bias metrics across multiple prompts side-by-side
4. **Export**: Download bias metrics as CSV for analysis
5. **Threshold Customization**: Let users set custom thresholds per judge

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Display** | Single aggregated score | Array of individual judge scores |
| **Transparency** | Hidden which judge contributed what | Clear attribution per judge |
| **Research** | Generic "bias score" | Specific frameworks and models cited |
| **Debugging** | Hard to understand disagreements | Easy to see why judges differ |
| **Button Label** | "More Info" | "Full Prompt" (clearer purpose) |

This update aligns with research best practices for bias evaluation, providing users with detailed, transparent, and actionable bias metrics from multiple validated detection systems.

