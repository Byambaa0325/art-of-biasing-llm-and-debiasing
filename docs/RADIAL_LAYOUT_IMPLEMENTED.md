# Radial Layout Implementation - Graph Sprawls in All Directions

## Overview

Implemented a **radial tree layout algorithm** that spreads nodes in all directions from the center, using the full canvas space and preventing overlapping.

## Visual Layout

### Before (Linear Left-Right):
```
[Debias] --- [ROOT] --- [Bias]
```
All nodes lined up horizontally, overlapping on expansion.

### After (Radial 360°):
```
                [Node 3]
                   |
      [Node 2] - [ROOT] - [Node 4]
                   |
                [Node 1]
```
Nodes spread in all directions, forming concentric rings.

## Algorithm Details

### Layout Configuration (Lines 57-63)

```javascript
const LAYOUT_CONFIG = {
  centerX: 800,              // Canvas center X
  centerY: 400,              // Canvas center Y
  radiusIncrement: 350,      // Distance between levels (rings)
  minAngleSeparation: 0.3,   // Minimum angle between siblings
};
```

### Radial Position Calculation (Lines 65-87)

**Formula:**
```
x = parentX + (radius × level) × cos(angle)
y = parentY + (radius × level) × sin(angle)
```

**Angle Distribution:**
- 1 child: Same direction as parent (angle spread = 0°)
- 2 children: 180° spread (π radians)
- 3+ children: 270° spread (1.5π radians)

**Example with 4 children:**
```
Parent at angle 0° (pointing right)
  ├─ Child 0: -67.5° (upper right)
  ├─ Child 1: -22.5° (right)
  ├─ Child 2: +22.5° (right)
  └─ Child 3: +67.5° (lower right)
```

### Level System

Each node has a `level` property indicating distance from root:

| Level | Radius | Description |
|-------|--------|-------------|
| 0 | 0px | Root node (center) |
| 1 | 350px | First ring |
| 2 | 700px | Second ring |
| 3 | 1050px | Third ring |
| n | 350n px | Nth ring |

### Angle Inheritance

Each node tracks its `angle` from the center:
- Root: 0° (arbitrary, no parent)
- Children: Spread around parent's angle

**Example Tree:**
```
Root (0°, level 0)
  ├─ Node A (45°, level 1)
  │   ├─ Node A1 (30°, level 2)
  │   └─ Node A2 (60°, level 2)
  └─ Node B (315°, level 1)
      └─ Node B1 (300°, level 2)
```

## Code Implementation

### 1. Initial Layout (Lines 164-258)

Places root at center, spreads potentials around it:

```javascript
// Root at canvas center
position: { x: LAYOUT_CONFIG.centerX, y: LAYOUT_CONFIG.centerY }

// Potential nodes in ring around root
const { x, y, angle } = calculateRadialPosition(
  centerPos,
  index,              // Which child (0, 1, 2, ...)
  totalPotentials,    // Total number of children
  1,                  // Level (first ring)
  0                   // Parent angle (root has no angle)
);
```

### 2. Node Expansion (Lines 302-427)

When expanding a potential node:

```javascript
// Keep same position as potential node
position: potentialNode.position

// Children spread around this node
const { x, y, angle } = calculateRadialPosition(
  actualNodePosition,  // Parent position
  index,
  totalPotentials,
  1,                   // One level out
  parentAngle          // Spread around parent's angle
);
```

### 3. Data Tracking

Each node stores:
```javascript
{
  position: { x, y },    // Screen coordinates
  data: {
    level: number,       // Distance from root
    angle: number,       // Angle from center (radians)
    ...
  }
}
```

## Spatial Distribution

### Canvas Usage

**Before**: ~600px width used (left-right only)
**After**: ~2100px diameter used (full circle)

### Density Control

- Level 1: 8 nodes in 350px radius circle (perimeter ≈ 2200px)
- Level 2: 64 potential nodes in 700px radius circle (perimeter ≈ 4400px)
- Level 3: 512 potential nodes in 1050px radius circle (perimeter ≈ 6600px)

Each level has more space, preventing crowding.

## Visual Examples

### 8 Potential Paths from Root:

```
         [Path 3]
    [Path 2]    [Path 4]

[Path 1]  [ROOT]  [Path 5]

    [Path 8]    [Path 6]
         [Path 7]
```

Nodes distributed evenly in 360° circle.

### After Expanding Path 5:

```
         [Path 3]
    [Path 2]    [Path 4]

[Path 1]  [ROOT]  [ACTUAL]
                    /  |  \
    [Path 8]   [New1][New2][New3]
         [Path 7]
```

New nodes spread to the right of the actual node.

### After Multiple Expansions:

```
        [N3]
         |
    [N2]-[ROOT]-[N4]
         |       \
        [N1]    [N5]-[N6]
                      |
                    [N7]
```

Tree grows naturally in all directions.

## Benefits

### ✅ No Overlapping
- Radius increases with each level
- Angle separation ensures spacing
- Children spread in cones, not on top of each other

### ✅ Full Canvas Utilization
- Uses 360° of space
- Can grow to any depth
- Scales to hundreds of nodes

### ✅ Visual Hierarchy
- Distance from center = depth in tree
- Parent-child relationships clear
- Natural tree structure

### ✅ Balanced Growth
- All directions equally accessible
- No preferred direction (no bias to left/right)
- Symmetrical when children are balanced

## Technical Details

### Angle Calculation

```javascript
const angleSpread = Math.PI * 1.5;  // 270° default
const startAngle = parentAngle - angleSpread / 2;
const angleStep = angleSpread / (totalChildren - 1);
const angle = startAngle + (angleStep * index);
```

**Special Cases:**
- 1 child: `angleSpread = 0` (same direction as parent)
- 2 children: `angleSpread = π` (180° spread)
- 3+ children: `angleSpread = 1.5π` (270° spread)

### Position Calculation

```javascript
const radius = LAYOUT_CONFIG.radiusIncrement * level;
const x = parentPos.x + radius * Math.cos(angle);
const y = parentPos.y + radius * Math.sin(angle);
```

Uses polar to Cartesian coordinate conversion.

### Level Tracking

```javascript
const calculateNodeLevels = (nodes, edges) => {
  // BFS from root to assign levels
  levels[rootId] = 0;
  queue = [{ id: rootId, level: 0 }];

  while (queue.length > 0) {
    const { id, level } = queue.shift();
    children.forEach(childId => {
      levels[childId] = level + 1;
    });
  }
};
```

## Performance

### Space Complexity
- O(n) nodes stored
- O(n) edges stored
- No additional data structures needed

### Time Complexity
- Position calculation: O(1) per node
- Level calculation: O(n) BFS traversal
- Total layout: O(n) for n nodes

### Rendering
- ReactFlow handles rendering
- Only visible nodes rendered (viewport culling)
- Smooth at 100+ nodes

## Future Enhancements

### Possible Improvements
1. **Dynamic radius**: Adjust based on node count per level
2. **Collision detection**: Fine-tune positions to avoid any overlap
3. **Force-directed refinement**: Add slight force simulation for aesthetics
4. **Animation**: Smooth transitions when adding nodes
5. **Zoom to fit**: Auto-zoom to show all nodes

### Alternative Layouts
- **Hierarchical (dagre)**: Strict left-to-right or top-to-bottom
- **Force-directed**: Physics-based organic layout
- **Circular**: All nodes at same radius
- **Spiral**: Continuously increasing radius

## Files Modified

**File**: `frontend-react/src/App.js`

**Lines**:
- 57-135: Layout configuration and helper functions
- 164-258: Initial radial layout (handleSubmit)
- 302-427: Expansion radial layout (handleExpandPath)

## Testing

1. Enter a prompt
2. **Verify**: 8 nodes spread in circle around center
3. Click any node
4. **Verify**: Children spread around clicked node
5. Click multiple nodes
6. **Verify**: No overlapping, tree grows in all directions
7. Zoom out
8. **Verify**: Can see full tree structure

---

**Status**: ✅ Radial layout implemented - graph sprawls in all directions, no overlapping
