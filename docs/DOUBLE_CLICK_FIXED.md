# Double-Click Prevention Fixed

## Problem

When clicking on a potential node multiple times rapidly while it's expanding, multiple duplicate nodes were created due to a race condition.

## Root Cause

The node expansion is an **async operation**:
1. User clicks potential node
2. API call starts (takes 2-3 seconds)
3. User clicks again (before API completes)
4. Second API call starts
5. Both calls complete → duplicate nodes created

## Solution

Implemented a **global expansion lock** with visual feedback.

### 1. Added Expansion State (Line 50)

```javascript
const [expandingNodeId, setExpandingNodeId] = useState(null);
```

Tracks which node is currently being expanded (null = none).

### 2. Guard Clauses in handleExpandPath (Lines 272-283)

```javascript
// Prevent multiple clicks on same node
if (expandingNodeId === potentialNodeId) {
  console.log('Already expanding this node, ignoring click');
  return;
}

// Prevent expanding multiple nodes at once
if (expandingNodeId) {
  console.log('Another node is expanding, please wait');
  return;
}

setExpandingNodeId(potentialNodeId);  // Lock
```

**Behavior:**
- Same node clicked twice → Ignore second click
- Different node clicked while one expanding → Ignore, show "Please wait"

### 3. Clear Lock After Completion (Lines 458-460)

```javascript
} finally {
  setLoading(false);
  setExpandingNodeId(null);  // Unlock
}
```

Clears lock whether API succeeds or fails.

### 4. Visual Feedback in NodeLabel (Lines 641-695)

**Props added:**
```javascript
isExpanding={expandingNodeId === nodeId}      // This node is expanding
isAnyExpanding={expandingNodeId !== null}     // Any node is expanding
```

**Disabled state:**
```javascript
const isDisabled = isExpanding || isAnyExpanding;

sx={{
  cursor: isDisabled ? 'wait' : 'pointer',
  opacity: isDisabled ? 0.5 : 1,
  pointerEvents: isDisabled ? 'none' : 'auto',
}}
```

**Text feedback:**
```javascript
{isExpanding ? 'Expanding...' :
 isAnyExpanding ? 'Please wait...' :
 'Click to expand'}
```

**Loading spinner:**
```javascript
{isExpanding && (
  <CircularProgress size={16} sx={{ mt: 0.5 }} />
)}
```

## Visual States

### Normal State (No expansion)
```
┌─────────────────┐
│ Add Bias Type   │
│ Click to expand │
└─────────────────┘
  cursor: pointer
  opacity: 1.0
```

### This Node Expanding
```
┌─────────────────┐
│ Add Bias Type   │
│ Expanding...    │
│       ⟳         │  ← Spinner
└─────────────────┘
  cursor: wait
  opacity: 0.5
```

### Another Node Expanding
```
┌─────────────────┐
│ Add Bias Type   │
│ Please wait...  │
└─────────────────┘
  cursor: wait
  opacity: 0.5
  clicks ignored
```

## Flow Diagram

```
User clicks Node A
    ↓
expandingNodeId = 'node-a'
    ↓
API call starts
    ↓
[User tries to click Node A again]
    ↓
Guard: expandingNodeId === 'node-a' → IGNORE
    ↓
[User tries to click Node B]
    ↓
Guard: expandingNodeId !== null → IGNORE
    ↓
API completes
    ↓
expandingNodeId = null
    ↓
All nodes clickable again
```

## Benefits

### ✅ Prevents Duplicates
- Can't click same node twice
- Can't click multiple nodes simultaneously
- One expansion at a time

### ✅ Clear Visual Feedback
- Expanding node shows spinner
- Other nodes grayed out with "Please wait"
- Cursor changes to "wait"

### ✅ Better UX
- User knows something is happening
- Clear which node is being expanded
- Prevents confusion

### ✅ Robust
- Works even if user clicks rapidly
- Handles errors (lock cleared in finally)
- No race conditions

## Code Changes

**Files Modified:** `frontend-react/src/App.js`

**Lines:**
- 50: Added `expandingNodeId` state
- 272-283: Guard clauses in `handleExpandPath`
- 458-460: Clear lock in finally block
- 232-233, 416-417: Pass expansion state to NodeLabel
- 641-695: NodeLabel disabled state and visual feedback

## Testing

### Test Case 1: Rapid Clicks Same Node
1. Click a potential node
2. Immediately click it again 5 times
3. **Result**: Only 1 node created

### Test Case 2: Multiple Nodes
1. Click potential node A
2. While loading, click potential node B
3. **Result**: Only node A expands, B ignored

### Test Case 3: Visual Feedback
1. Click a potential node
2. **Verify**: Node shows "Expanding..." with spinner
3. **Verify**: Other nodes show "Please wait..." and are grayed out
4. **Verify**: After completion, all nodes become clickable

### Test Case 4: Error Handling
1. Disconnect from backend
2. Click a potential node
3. Wait for error
4. **Verify**: Lock cleared, can click nodes again

## Technical Details

### State Management

```javascript
expandingNodeId: string | null

- null: No expansion in progress
- 'node-123': Node with ID 'node-123' is expanding
```

### Prop Flow

```
App Component (has expandingNodeId state)
    ↓
handleSubmit / handleExpandPath
    ↓
NodeLabel component (receives isExpanding, isAnyExpanding)
    ↓
Disabled UI based on props
```

### CSS Transitions

```css
transition: opacity 0.2s
```

Smooth fade when nodes become disabled/enabled.

### Pointer Events

```css
pointerEvents: isDisabled ? 'none' : 'auto'
```

Completely blocks click events when disabled (belt-and-suspenders with guard clauses).

## Alternative Solutions Considered

### ❌ Immediate Removal
Remove potential node immediately on click (optimistic UI).

**Problem**: If API fails, how to restore node?

### ❌ Per-Node Loading State
Track loading for each node individually.

**Problem**: More complex state management, still allows multiple expansions.

### ✅ Global Lock (Chosen)
Simple, clear, prevents all race conditions.

## Future Enhancements

### Queue System
Allow clicking multiple nodes, queue expansions:
```
Click A → Expanding A
Click B → Queued
Click C → Queued
A done → Expanding B
B done → Expanding C
```

### Parallel Expansions
Allow multiple nodes to expand simultaneously (needs backend support).

---

**Status**: ✅ Double-click prevention implemented with visual feedback
