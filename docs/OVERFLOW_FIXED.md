# Node Overflow Fixed

## Problem
Node content was overflowing outside the cell boundaries, making the graph look messy and hard to read.

## Solution

Added comprehensive overflow handling to all node components with fixed widths and proper text truncation.

## Changes Made

### 1. Node Container Styles (Lines 515-573)

**Actual Nodes:**
```javascript
const baseStyle = {
  padding: 0,
  width: '320px',           // Fixed width
  maxWidth: '320px',        // Prevent expansion
  overflow: 'hidden',       // Hide overflow
};
```

**Potential Nodes:**
```javascript
const baseStyle = {
  padding: 0,
  width: '180px',           // Fixed width
  maxWidth: '180px',        // Prevent expansion
  overflow: 'hidden',       // Hide overflow
};
```

### 2. Potential Node Content (Lines 646-705)

**Title:**
- Fixed width: 180px
- Text ellipsis for long titles
- `whiteSpace: 'nowrap'` prevents wrapping
- `textOverflow: 'ellipsis'` shows "..." for overflow

**Description:**
- Line clamping: max 2 lines
- Uses `-webkit-box` for multi-line ellipsis
- `wordBreak: 'break-word'` for long words

```javascript
<Typography
  sx={{
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',  // Single line with ellipsis
  }}
>
  {node.prompt}
</Typography>
```

### 3. Actual Node Content (Lines 711-958)

**Prompt Text:**
- Max 3 lines with ellipsis
- Word break for long words
- Fixed container width

**LLM Answer:**
- Scrollable container (max 150px height)
- Word wrap enabled
- Full width with box-sizing

```javascript
<Paper
  sx={{
    maxHeight: '150px',
    overflow: 'auto',          // Scrollable
    width: '100%',
    boxSizing: 'border-box',
  }}
>
  <Typography
    sx={{
      wordBreak: 'break-word',
      whiteSpace: 'pre-wrap',  // Preserve formatting
    }}
  >
    {node.llm_answer}
  </Typography>
</Paper>
```

**HEARTS Evaluation:**
- Full width container
- Text ellipsis for long content
- Chips with overflow handling

**Gemini Evaluation:**
- Full width container
- Explanation clamped to 2 lines
- Word break for long explanations

## Text Overflow Strategies

### 1. Single-Line Ellipsis
Used for: Headers, titles, single-line labels

```css
overflow: hidden;
textOverflow: ellipsis;
whiteSpace: nowrap;
```

Result: `This is a very long text th...`

### 2. Multi-Line Clamping
Used for: Descriptions, explanations, prompts

```css
overflow: hidden;
display: -webkit-box;
WebkitLineClamp: 3;
WebkitBoxOrient: vertical;
wordBreak: break-word;
```

Result:
```
This is a very long text
that spans multiple lines
and gets cut off with...
```

### 3. Scrollable Container
Used for: LLM answers, long content

```css
maxHeight: 150px;
overflow: auto;
wordBreak: break-word;
whiteSpace: pre-wrap;
```

Result: Content scrolls vertically within fixed height

## Visual Examples

### Before (Overflow):
```
┌────────────────────────┐
│ Add Very Long Bias Type That Extends Beyond Container │
│ Click to expand        │
└────────────────────────┘
```

### After (Fixed):
```
┌────────────────────────┐
│ Add Very Long Bias ... │
│ Click to expand        │
└────────────────────────┘
```

## Node Width Specifications

| Node Type | Width | Content Strategy |
|-----------|-------|------------------|
| Potential | 180px | Single-line ellipsis |
| Actual | 320px | Multi-line clamping + scroll |
| LLM Answer | 100% | Scrollable (max 150px) |
| Evaluations | 100% | Ellipsis + clamping |

## Spacing Remains Same

The node positioning hasn't changed, only the overflow handling:

- Horizontal spacing: 400px
- Vertical spacing: 120px
- Fixed widths ensure consistent layout

## Benefits

✅ **No Content Overflow**: All text stays within node boundaries
✅ **Readable**: Long text truncated with ellipsis (...)
✅ **Scrollable Details**: LLM answers scroll instead of overflow
✅ **Consistent Width**: All nodes same width per type
✅ **Professional Look**: Clean, organized graph appearance
✅ **Word Breaking**: Long URLs/words break properly

## Technical Details

**Box Sizing:**
- All containers use `boxSizing: 'border-box'`
- Ensures padding included in width calculation

**Overflow Properties:**
- `overflow: 'hidden'` on containers
- `overflow: 'auto'` on scrollable content
- `textOverflow: 'ellipsis'` on truncated text

**Width Control:**
- `width: 'X px'` sets fixed width
- `maxWidth: 'X px'` prevents expansion
- `width: '100%'` for full container width

## Files Modified

**File**: `frontend-react/src/App.js`

**Lines**:
- 515-573: Node style functions with fixed widths
- 646-705: Potential node overflow handling
- 711-958: Actual node overflow handling

---

**Status**: ✅ All overflow issues fixed, nodes display cleanly within boundaries
