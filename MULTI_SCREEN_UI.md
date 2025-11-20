# Multi-Screen UI - Input Screen → Full-Screen Graph

## Overview

Implemented a two-screen interface that maximizes space efficiency:
1. **Input Screen**: Full-screen, centered prompt entry
2. **Graph Screen**: Full-screen graph with compact header

## Visual Flow

### Screen 1: Input Mode
```
┌─────────────────────────────────────────┐
│                                         │
│         🎯 Art of Biasing LLM           │
│   Interactive Prompt Bias Analysis      │
│                                         │
│   ┌───────────────────────────────┐    │
│   │ Enter your starter prompt      │    │
│   │                                │    │
│   │ [Text input - 6 rows]          │    │
│   │                                │    │
│   │ [Generate Bias Graph]          │    │
│   └───────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```
- Centered, prominent
- Full viewport height
- Gradient background
- Large input area

### Screen 2: Graph Mode
```
┌─────────────────────────────────────────┐
│ Analyzing: "prompt..." [New Analysis]   │ ← Compact header
├─────────────────────────────────────────┤
│                                         │
│                                         │
│         [Full-screen graph here]        │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```
- Compact header (~60px)
- Full-screen graph below
- Maximizes visualization space

## Implementation

### State Management (Lines 51-52)

```javascript
const [viewMode, setViewMode] = useState('input');
const [currentPrompt, setCurrentPrompt] = useState('');
```

**viewMode:**
- `'input'`: Show input screen
- `'graph'`: Show graph screen

**currentPrompt:**
- Stores the submitted prompt
- Displayed in graph mode header

### Screen Switching (Lines 341-343)

After successful graph generation:
```javascript
setCurrentPrompt(prompt.trim());
setViewMode('graph');
```

### Reset Function (Lines 353-360)

Go back to input screen:
```javascript
const handleReset = () => {
  setViewMode('input');
  setPrompt('');
  setCurrentPrompt('');
  setNodes([]);
  setEdges([]);
  setExpandingNodeId(null);
};
```

## Input Screen Design (Lines 663-761)

### Layout
- **Full viewport**: 100vw × 100vh
- **Centered content**: Flexbox center alignment
- **Gradient background**: Purple gradient (brand colors)

### Components

**1. Title Section**
```javascript
<Typography variant="h2">
  🎯 Art of Biasing LLM
</Typography>
```
- Large, bold title
- Text shadow for depth
- White color on gradient

**2. Description**
```
Interactive Prompt Bias Analysis with Graph Visualization
Explore how biases affect LLM responses...
```
- Brief explanation
- Sets expectations

**3. Input Card**
```javascript
<Paper elevation={6} sx={{ maxWidth: '700px' }}>
  <TextField rows={6} />
  <Button fullWidth>Generate Bias Graph</Button>
</Paper>
```
- Elevated paper (shadow)
- 6-row text input (spacious)
- Large, full-width button
- Ctrl+Enter shortcut

### Features

**Keyboard Shortcut:**
```javascript
onKeyDown={(e) => {
  if (e.key === 'Enter' && e.ctrlKey && prompt.trim()) {
    handleSubmit();
  }
}}
```
Press Ctrl+Enter to submit without clicking.

**Loading State:**
```javascript
{loading ? <CircularProgress /> : 'Generate Bias Graph'}
```
Shows spinner during generation.

## Graph Screen Design (Lines 765-847)

### Layout Structure
```
Box (100vh, flex column)
  ├─ Header Box (~60px)
  └─ Graph Box (flex: 1, fills remaining space)
```

### Compact Header (Lines 776-817)

**Layout:**
- Gradient background (brand colors)
- Horizontal flexbox
- Space-between alignment

**Left Side:**
```
Analyzing Prompt:
"What are the benefits of exercise?"
```
- Shows current prompt
- Text overflow ellipsis for long prompts

**Right Side:**
```
[New Analysis]
```
- Semi-transparent button
- Resets to input screen

### Full-Screen Graph (Lines 820-838)

**Container:**
```javascript
<Box sx={{ flex: 1, position: 'relative' }}>
  <ReactFlow ... />
</Box>
```
- `flex: 1`: Takes all remaining vertical space
- `position: relative`: For ReactFlow positioning

**ReactFlow:**
- All features enabled (drag, controls, minimap)
- No height restriction
- Fills parent container

## Space Efficiency Comparison

### Before (Single Screen)
```
Header:        80px  (10%)
Input Section: 300px (38%)
Graph:         420px (52%)
──────────────────────────
Total:         800px (100%)
```
**Graph gets only 52% of viewport**

### After (Multi-Screen)

**Input Mode:**
```
Full screen for input: 100%
```

**Graph Mode:**
```
Header:  60px  (6%)
Graph:   940px (94%)
──────────────────────────
Total:   1000px (100%)
```
**Graph gets 94% of viewport - 80% more space!**

## User Flow

```
1. User lands on app
   ↓
   [Input Screen - Full viewport]
   ↓
2. User types prompt
   ↓
3. User clicks "Generate" or presses Ctrl+Enter
   ↓
   [Loading...]
   ↓
4. Graph generated successfully
   ↓
   [Switches to Graph Screen]
   ↓
   [Graph takes 94% of screen]
   ↓
5. User explores graph (drag, expand nodes, etc.)
   ↓
6. User clicks "New Analysis"
   ↓
   [Returns to Input Screen]
   ↓
7. User enters new prompt
   ↓
   [Cycle repeats]
```

## Benefits

### ✅ Maximized Graph Space
- 80% more vertical space for graph
- Can see more nodes without scrolling
- Better overview of entire tree

### ✅ Focused Input Experience
- No distractions during prompt entry
- Clear call-to-action
- Prominent branding

### ✅ Clean Separation
- Clear mode separation (input vs visualization)
- No visual clutter
- Professional appearance

### ✅ Easy Reset
- "New Analysis" button always visible
- One click to start over
- Clears all state

## Design Patterns

### Landing Page Pattern
```
Input screen = Landing page
Graph screen = App interface
```
Common in:
- Search engines (Google)
- Analysis tools (data visualizers)
- Generation tools (AI image generators)

### Progressive Disclosure
```
Show simple → User acts → Show complex
```
- Input screen: Simple (just text input)
- Graph screen: Complex (full visualization)

### Task-Oriented Layouts
```
Different tasks = Different screens
```
- Input task: Full-screen form
- Analysis task: Full-screen graph

## Technical Details

### Viewport Units
```css
width: 100vw  /* Full viewport width */
height: 100vh /* Full viewport height */
```
Ensures screens fill entire browser window.

### Flex Layout
```css
display: flex
flex-direction: column
flex: 1  /* Child takes remaining space */
```
Graph box expands to fill available space.

### Overflow Handling
```css
overflow: hidden  /* Prevent scrollbars */
```
Graph mode container prevents body scroll.

### Gradient Consistency
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```
Same gradient on input screen and graph header for brand consistency.

## Responsive Considerations

### Mobile
- Input screen: Still centered, padding adjusts
- Graph screen: Header stacks vertically if needed
- Full-screen approach works well on mobile

### Desktop
- Input screen: Max-width 700px keeps form readable
- Graph screen: Expands to use large monitors

### Tablet
- Optimal for both modes
- Touch-friendly buttons
- Drag gestures work well

## Keyboard Shortcuts

### Input Mode
- **Ctrl+Enter**: Submit prompt
- **Tab**: Navigate form elements

### Graph Mode
- **Arrow keys**: Pan graph
- **+/-**: Zoom in/out
- **Ctrl+Z**: Undo (if implemented)

## Future Enhancements

### 1. Transition Animation
```javascript
<Fade in={viewMode === 'graph'}>
  {/* Graph screen */}
</Fade>
```

### 2. Breadcrumb Navigation
```
Home > Analysis > "your prompt"
```

### 3. History Sidebar
```
Recent Analyses:
- "Benefits of exercise"
- "Women emotional"
- "Best programming languages"
```

### 4. Split View Option
```
[Show Input Sidebar] button
→ Opens side panel with input form
```

## Files Modified

**File:** `frontend-react/src/App.js`

**Lines:**
- 51-52: View mode state
- 341-343: Switch to graph mode after generation
- 353-360: Reset function
- 663-761: Input screen render
- 765-847: Graph screen render

## Testing

### Test 1: Initial Load
1. Open app
2. **Verify**: Shows input screen centered
3. **Verify**: Gradient background visible

### Test 2: Submit Flow
1. Type prompt
2. Click "Generate"
3. **Verify**: Switches to graph screen
4. **Verify**: Header shows submitted prompt

### Test 3: Reset Flow
1. In graph mode
2. Click "New Analysis"
3. **Verify**: Returns to input screen
4. **Verify**: Previous graph cleared

### Test 4: Keyboard Shortcut
1. Type prompt
2. Press Ctrl+Enter
3. **Verify**: Submits like clicking button

### Test 5: Long Prompt
1. Enter very long prompt (200+ characters)
2. Generate graph
3. **Verify**: Header shows ellipsis for overflow

---

**Status**: ✅ Multi-screen UI implemented - Full-screen input → Full-screen graph
