# Graph Visualization Fixed - Neighbor Nodes Architecture

## Changes Made

The frontend has been completely restructured to show **potential bias/debias options as neighbor nodes** instead of action buttons.

## New Architecture

### Initial State (After entering prompt)

```
                    [Add Demographic Bias]
                            |
                            | (dashed)
     [Add Confirmation]     |
              |             |
              | (dashed)    |
              |             |
    [Remove Leading] --- [ORIGINAL] --- [Add Gender Bias]
              |             |
              | (dashed)    |
              |             |
    [Simplify Question]     |
                            |
                            | (dashed)
                            |
                    [Add Authority Bias]
```

**Visual Elements:**
- **Center**: Original prompt node (solid border, blue)
- **Right side**: Potential bias nodes (dashed border, light red)
- **Left side**: Potential debias nodes (dashed border, light green)
- **Edges**: Dashed lines connecting to potential nodes

### After Clicking a Potential Node

When user clicks "Add Confirmation Bias":

```
[Add Demographic]
        |
        | (dashed)
        |
[ORIGINAL] ========> [CONFIRMATION BIASED] --- [Add Gender]
        |                      |                     |
        | (dashed)             | (dashed)            | (dashed)
        |                      |                     |
[Remove Leading]      [Remove Leading]        [Add Demographic]
                             |
                             | (dashed)
                             |
                      [Simplify Question]
```

**What Happens:**
1. Potential node is **replaced** with actual transformed node
2. Dashed edge becomes **solid edge** (red for bias, green for debias)
3. New potential nodes appear as **neighbors** of the new node
4. Can continue expanding infinitely

## Code Changes

### 1. `handleSubmit()` - Lines 62-240

**Creates neighbor nodes for potential paths:**

```javascript
// Original node in center
position: { x: 500, y: 100 }

// Bias nodes on the right
biasNodes.forEach((path, index) => {
  position: {
    x: 500 + 400,  // Right side
    y: 100 + index * 120,  // Spread vertically
  },
  style: getPotentialNodeStyle('bias'),  // Dashed red border
});

// Debias nodes on the left
debiasNodes.forEach((path, index) => {
  position: {
    x: 500 - 400,  // Left side
    y: 100 + index * 120,  // Spread vertically
  },
  style: getPotentialNodeStyle('debias'),  // Dashed green border
});
```

### 2. `handleExpandPath()` - Lines 242-467

**Replaces potential node with actual node:**

```javascript
// Remove potential node
setNodes((nds) => [
  ...nds.filter(n => n.id !== potentialNodeId),
  ...allNewNodes,  // Add actual + new potentials
]);

// Remove dashed edge, add solid edge
setEdges((eds) => [
  ...eds.filter(e => e.target !== potentialNodeId),
  ...allNewEdges,  // Add solid + new dashed
]);
```

### 3. `NodeLabel` Component - Lines 639-797

**Two different views:**

**Potential Node (dashed border):**
- Small, simple display
- Shows action label (e.g., "Add Confirmation Bias")
- Shows description
- Entire node is clickable
- "Click to expand" hint

**Actual Node (solid border):**
- Full details display
- Shows prompt, LLM answer, evaluations
- Shows bias score, HEARTS, Gemini results
- Collapsible sections
- Info button

### 4. `getPotentialNodeStyle()` - Lines 413-437

**Styling for potential nodes:**
- Dashed border (distinguishes from actual nodes)
- Lower opacity (0.85)
- Cursor: pointer
- Light red background for bias
- Light green background for debias

## Node Positioning Strategy

### Horizontal Layout

```
Left (Debias)          Center (Original)         Right (Bias)
    -400px                  500px                    +400px
```

### Vertical Spacing

```
Node 0:  y = 100
Node 1:  y = 220  (+120)
Node 2:  y = 340  (+120)
Node 3:  y = 460  (+120)
```

**Benefits:**
- ✅ Prevents overlapping
- ✅ Clear visual separation (bias vs debias)
- ✅ Scales with multiple options
- ✅ Maintains tree structure

## Visual Distinctions

| Type | Border | Background | Opacity | Edge |
|------|--------|------------|---------|------|
| Original | Solid blue | Light blue | 1.0 | N/A |
| Biased | Solid red | Light red | 1.0 | Solid red |
| Debiased | Solid green | Light green | 1.0 | Solid green |
| Potential Bias | **Dashed red** | Very light red | 0.85 | **Dashed red** |
| Potential Debias | **Dashed green** | Very light green | 0.85 | **Dashed green** |

## User Flow

1. **Enter prompt**: "What are the benefits of exercise?"
2. **See graph**:
   - 1 center node (original with LLM answer + evaluations)
   - 8 right nodes (potential biases, dashed borders)
   - 0 left nodes (no debiasing needed for neutral prompt)
3. **Click "Add Confirmation Bias"** (dashed node)
4. **Backend processes**:
   - Transforms prompt using Llama
   - Generates new LLM answer
   - Evaluates with HEARTS + Gemini
5. **See updated graph**:
   - Original node (unchanged)
   - Solid edge connecting to new node
   - New biased node (solid border, shows full data)
   - New potential nodes as neighbors of biased node
6. **Can expand any potential node** → Process repeats

## Benefits

### ✅ Visual Clarity
- Potential options are **visible as nodes** (not hidden in buttons)
- Clear distinction between potential (dashed) and actual (solid)
- Spatial layout shows relationships

### ✅ Better Organization
- Nodes don't overlap (proper spacing)
- Left/right separation (debias vs bias)
- Vertical spacing prevents crowding

### ✅ Scalability
- Can expand infinitely deep
- Each node can have multiple children
- Graph grows naturally

### ✅ Intuitive Interaction
- Click any potential node to expand
- Visual feedback (dashed → solid)
- Clear parent-child relationships

## Example Graph Structure

```
Initial Prompt: "Why are women always so emotional?"

                    [Add Demographics]
                            |
    [Remove "always"] --- [ORIGINAL] --- [Add Confirmation]
                            |                    |
                        (click)              (click)
                            ↓                    ↓
                    [Why do women...]    [Isn't it true that women...]
                            |                    |
                    [Add Stereotyping]   [Remove "always"]
```

## Files Modified

**File**: `frontend-react/src/App.js`

**Lines**:
- 62-240: `handleSubmit()` - Create neighbor nodes
- 242-467: `handleExpandPath()` - Replace potential with actual
- 413-437: `getPotentialNodeStyle()` - Style potential nodes
- 639-797: `NodeLabel` - Two views (potential vs actual)

## Testing

1. Enter a prompt
2. **Verify**: See center node + multiple neighbor nodes with dashed borders
3. Click any dashed node
4. **Verify**:
   - Dashed node becomes solid
   - Edge becomes solid
   - New dashed neighbors appear
5. Click another dashed node
6. **Verify**: Graph continues to grow without overlap

---

**Status**: ✅ Graph visualization complete with neighbor node architecture
