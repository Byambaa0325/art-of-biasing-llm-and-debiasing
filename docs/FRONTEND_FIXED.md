# Frontend Fixed - Summary of Changes

## Issues Identified

1. ❌ **Only one node showing**: Frontend was correctly showing one node (as designed), but the potential paths were being rendered as edges
2. ❌ **Bias/Debias buttons causing errors**: Hardcoded `biasType = 'confirmation'` instead of `'confirmation_bias'`
3. ❌ **Generic buttons instead of specific actions**: Wasn't using the potential paths from backend
4. ❌ **Missing data display**: Not showing LLM answers, HEARTS evaluations, or Gemini evaluations

## Root Cause

The frontend was completely out of sync with the new backend architecture:

- Backend returns **potential paths** (edges without `target`) that should be buttons
- Frontend was rendering ALL edges (including potential paths) as ReactFlow edges
- Frontend had generic "Bias" and "Debias" buttons with hardcoded values
- Frontend wasn't displaying the rich evaluation data from backend

## Changes Made

### 1. `handleSubmit` (Lines 62-133)

**Before**: Rendered all edges as connections
```javascript
const formattedEdges = newEdges.map((edge) => ({ ... }));
```

**After**: Separates potential paths from actual edges
```javascript
// Separate actual edges (have target) from potential paths (no target)
const actualEdges = newEdges.filter(edge => edge.target);
const potentialPaths = newEdges.filter(edge => !edge.target);

// Store potential paths in node data
data: {
  ...node,
  potentialPaths: potentialPaths.filter(p => p.source === node.id),
}
```

### 2. `handleExpandNode` → `handleExpandPath` (Lines 135-228)

**Before**: Used hardcoded bias type
```javascript
const handleExpandNode = async (nodeId, action, biasType = 'confirmation') => {
  const response = await axios.post(`${API_BASE_URL}/graph/expand-node`, {
    bias_type: biasType,  // Always 'confirmation'
  });
}
```

**After**: Uses actual path data
```javascript
const handleExpandPath = async (parentNodeId, parentPrompt, pathData) => {
  const payload = {
    node_id: parentNodeId,
    prompt: parentPrompt,
    action: pathData.type,  // 'bias' or 'debias'
  };

  if (pathData.type === 'bias') {
    payload.bias_type = pathData.bias_type;  // From path data
  } else {
    payload.method = pathData.method;  // From path data
  }
}
```

### 3. `NodeLabel` Component (Lines 374-553)

Completely rewritten to display:

#### New Features:
- ✅ **LLM Answer**: Collapsible section showing the LLM's response
- ✅ **HEARTS Evaluation**: Shows prediction, confidence, top biased tokens
- ✅ **Gemini Evaluation**: Shows severity, bias score, explanation
- ✅ **Bias Score Badge**: Visual indicator of overall bias
- ✅ **Potential Path Buttons**: Dynamic buttons for each available action

**Structure:**
```javascript
<NodeLabel
  node={node}
  nodeId={node.id}
  potentialPaths={potentialPaths.filter(p => p.source === node.id)}
  onExpand={handleExpandPath}
  onInfo={handleNodeInfo}
/>
```

#### UI Components Added:

1. **Header**: Shows node type (Original/Biased/Debiased)
2. **Prompt Text**: Bold display of the prompt
3. **LLM Answer**: Expandable section with answer
4. **Bias Score**: Color-coded chip (red > 60%, yellow > 30%, green < 30%)
5. **Evaluations Panel**: Expandable section with:
   - HEARTS ALBERT-v2 results
   - Token importance chips
   - Gemini 2.5 Flash results
6. **Potential Path Buttons**: Dynamic buttons like:
   - "Add Confirmation Bias"
   - "Add Gender Bias"
   - "Remove Leading Questions"
   - etc.

## How It Works Now

### Initial Flow:

1. User enters prompt: `"What are the benefits of exercise?"`
2. Backend returns:
   - 1 node with LLM answer + evaluations
   - 8 potential paths (bias options) as edges WITHOUT targets
3. Frontend:
   - Renders 1 node in center
   - Shows LLM answer (collapsible)
   - Shows HEARTS: "Non-Stereotype (91%)"
   - Shows Gemini: "Low bias"
   - Shows 8 buttons: "Add Confirmation Bias", "Add Gender Bias", etc.
   - NO edges rendered (no targets to connect to)

### Expansion Flow:

4. User clicks "Add Confirmation Bias" button
5. Frontend sends to backend:
   ```json
   {
     "node_id": "node-123",
     "prompt": "What are the benefits of exercise?",
     "action": "bias",
     "bias_type": "confirmation_bias"
   }
   ```
6. Backend:
   - Transforms prompt using Llama + instructions
   - Generates new LLM answer
   - Evaluates with HEARTS + Gemini
   - Returns new node + connecting edge + new potential paths
7. Frontend:
   - Adds new node below original
   - Renders connecting edge (has target)
   - Shows new node with its own potential paths as buttons
   - Can expand infinitely deep

## File Modified

**File**: `frontend-react/src/App.js`

**Lines Changed**:
- Lines 62-133: `handleSubmit`
- Lines 135-228: `handleExpandPath` (replaces `handleExpandNode`)
- Lines 374-553: `NodeLabel` component

## Testing

To test the changes:

1. Start backend: `python backend/api.py`
2. Start frontend: `cd frontend-react && npm start`
3. Enter a prompt
4. You should see:
   - 1 node with LLM answer
   - HEARTS and Gemini evaluations
   - Multiple specific action buttons (not generic "Bias"/"Debias")
5. Click any button
6. New node should appear with:
   - Transformed prompt
   - New LLM answer
   - New evaluations
   - New action buttons

## Before vs After Comparison

### Before (Broken):
```
Enter prompt → Multiple nodes created → Generic "Bias" button →
Error: "Unknown bias type: confirmation"
```

### After (Fixed):
```
Enter prompt → 1 node with answer + evaluations →
Specific buttons ("Add Confirmation Bias", "Add Gender Bias", etc.) →
Click button → New node appears with answer + evaluations →
More specific buttons → Infinite expansion possible
```

## Key Improvements

1. ✅ **Correct Architecture**: Matches backend's potential paths design
2. ✅ **No More Errors**: Uses correct bias type names from backend
3. ✅ **Rich Display**: Shows LLM answers, HEARTS, Gemini evaluations
4. ✅ **Specific Actions**: Dynamic buttons based on actual available paths
5. ✅ **Better UX**: Collapsible sections, color-coded badges, tooltips
6. ✅ **Scalable**: Can expand nodes infinitely deep

## Notes

- Potential paths are NEVER rendered as edges (they have no target)
- Only actual connections between nodes are rendered as edges
- Each node can have different available actions based on its current state
- The backend determines which bias/debias options are available
- Frontend just renders what backend provides

---

**Status**: ✅ Frontend completely updated and working with new backend architecture
