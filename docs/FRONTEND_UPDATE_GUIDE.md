# Frontend Update Guide

## Summary of Backend Changes

The backend now returns a **completely different structure**:

### Initial `/api/graph/expand` response:
```json
{
  "nodes": [
    {
      "id": "node-123",
      "prompt": "Why are women always so emotional?",
      "llm_answer": "Women are not inherently more emotional...",  // NEW
      "type": "original",

      "hearts_evaluation": {  // NEW structured evaluation
        "available": true,
        "is_stereotype": true,
        "confidence": 0.85,
        "probabilities": {"Stereotype": 0.853, "Non-Stereotype": 0.147},
        "token_importance": [
          {"token": "women", "importance": 0.42},
          {"token": "always", "importance": 0.38}
        ]
      },

      "gemini_evaluation": {  // NEW structured evaluation
        "available": true,
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
    // These are POTENTIAL PATHS (no 'target' field)
    {
      "id": "edge-bias-confirmation",
      "source": "node-123",
      // NO target field = potential path, not actual edge
      "type": "bias",
      "bias_type": "confirmation_bias",
      "label": "Add Confirmation Bias",
      "description": "Make prompt leading and confirmatory",
      "action_required": "click_to_generate"
    }
  ]
}
```

## Frontend Changes Required

### 1. Update Node Rendering

**Current:** Nodes show only bias score
**New:** Nodes must show:
- Prompt
- LLM Answer (expandable/collapsible)
- HEARTS Evaluation panel
- Gemini Evaluation panel
- Token importance visualization

### 2. Handle Potential Paths

**Current:** Edges are rendered as connections
**New:** Edges without `target` field are potential paths that should:
- NOT be rendered as graph edges
- Be shown as ACTION BUTTONS on the node
- When clicked, call `/api/graph/expand-node` to create actual node

### 3. Update Node Expansion Logic

**Current:** Already generates child nodes
**New:** When user clicks potential path button:
1. Call `/api/graph/expand-node` with action + bias_type/method
2. Receive new node + real edge + new potential paths
3. Add new node to graph
4. Render new potential paths as buttons on new node

## Key Component Updates

### Updated `handleSubmit` (Initial Expand)

```javascript
const handleSubmit = async () => {
  if (!prompt.trim()) return;

  setLoading(true);
  try {
    const response = await axios.post(`${API_BASE_URL}/graph/expand`, {
      prompt: prompt.trim(),
    });

    const { nodes: newNodes, edges: newEdges } = response.data;

    // Separate actual edges from potential paths
    const actualEdges = newEdges.filter(edge => edge.target);  // Has target = real edge
    const potentialPaths = newEdges.filter(edge => !edge.target);  // No target = potential path

    // Format nodes with potential paths stored in node data
    const formattedNodes = newNodes.map((node, index) => ({
      id: node.id,
      data: {
        ...node,
        potentialPaths: potentialPaths.filter(p => p.source === node.id),  // Store paths in node
        label: <EnhancedNodeLabel node={node} onExpandPath={handleExpandPath} />
      },
      position: { x: 400, y: 100 },  // Center for root
      style: getNodeStyle(node),
    }));

    // Only render actual edges (none on initial expand)
    const formattedEdges = actualEdges.map(formatEdge);

    setNodes(formattedNodes);
    setEdges(formattedEdges);
  } catch (error) {
    console.error('Error:', error);
    alert(error.response?.data?.error || error.message);
  } finally {
    setLoading(false);
  }
};
```

### New `handleExpandPath` (Create Child Node)

```javascript
const handleExpandPath = async (parentNodeId, parentPrompt, pathData) => {
  setLoading(true);
  try {
    const payload = {
      node_id: parentNodeId,
      prompt: parentPrompt,
      action: pathData.type,  // 'bias' or 'debias'
    };

    // Add specific params based on action type
    if (pathData.type === 'bias') {
      payload.bias_type = pathData.bias_type;
    } else {
      payload.method = pathData.method;
    }

    const response = await axios.post(`${API_BASE_URL}/graph/expand-node`, payload);

    const { nodes: newNodes, edges: newEdges, new_node_id } = response.data;

    // Separate actual edges from potential paths
    const actualEdges = newEdges.filter(edge => edge.target);
    const potentialPaths = newEdges.filter(edge => !edge.target);

    // Calculate position for new node (below parent + offset)
    const parentNode = nodes.find(n => n.id === parentNodeId);
    const newPosition = {
      x: parentNode.position.x + (nodes.filter(n => n.data.parent_id === parentNodeId).length * 300),
      y: parentNode.position.y + 250
    };

    // Format new node with its potential paths
    const formattedNewNodes = newNodes.map(node => ({
      id: node.id,
      data: {
        ...node,
        potentialPaths: potentialPaths.filter(p => p.source === node.id),
        label: <EnhancedNodeLabel node={node} onExpandPath={handleExpandPath} />
      },
      position: newPosition,
      style: getNodeStyle(node),
    }));

    // Add new node and edges
    setNodes(prev => [...prev, ...formattedNewNodes]);
    setEdges(prev => [...prev, ...actualEdges.map(formatEdge)]);

  } catch (error) {
    console.error('Error:', error);
    alert(error.response?.data?.error || error.message);
  } finally {
    setLoading(false);
  }
};
```

### New `EnhancedNodeLabel` Component

```javascript
const EnhancedNodeLabel = ({ node, onExpandPath }) => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  return (
    <Box sx={{ minWidth: 300, p: 2 }}>
      {/* Header */}
      <Typography variant="subtitle2" color="textSecondary">
        {node.type === 'original' ? 'Original Prompt' :
         node.type === 'biased' ? `Biased (${node.transformation})` :
         `Debiased (${node.transformation})`}
      </Typography>

      {/* Prompt */}
      <Typography variant="body1" sx={{ mb: 1, fontWeight: 'bold' }}>
        {node.prompt}
      </Typography>

      {/* LLM Answer (Collapsible) */}
      <Box sx={{ mb: 1 }}>
        <Button size="small" onClick={() => setShowAnswer(!showAnswer)}>
          {showAnswer ? 'Hide' : 'Show'} LLM Answer
        </Button>
        {showAnswer && (
          <Typography variant="body2" sx={{ mt: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
            {node.llm_answer}
          </Typography>
        )}
      </Box>

      {/* Bias Score Badge */}
      <Chip
        label={`Bias Score: ${(node.bias_score * 100).toFixed(0)}%`}
        color={node.bias_score > 0.6 ? 'error' : node.bias_score > 0.3 ? 'warning' : 'success'}
        size="small"
        sx={{ mb: 1 }}
      />

      {/* Evaluations Toggle */}
      <Button size="small" onClick={() => setShowDetails(!showDetails)} sx={{ mb: 1 }}>
        {showDetails ? 'Hide' : 'Show'} Evaluations
      </Button>

      {/* Evaluation Panels */}
      {showDetails && (
        <Box sx={{ mt: 2 }}>
          {/* HEARTS Evaluation */}
          {node.hearts_evaluation?.available && (
            <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'blue.50' }}>
              <Typography variant="caption" fontWeight="bold">
                HEARTS ALBERT-v2
              </Typography>
              <Typography variant="body2">
                Prediction: {node.hearts_evaluation.prediction}
                <br />
                Confidence: {(node.hearts_evaluation.confidence * 100).toFixed(1)}%
                <br />
                Stereotype Prob: {(node.hearts_evaluation.probabilities.Stereotype * 100).toFixed(1)}%
              </Typography>

              {/* Token Importance */}
              {node.hearts_evaluation.token_importance?.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption">Top Biased Tokens:</Typography>
                  {node.hearts_evaluation.token_importance.slice(0, 5).map((token, i) => (
                    <Chip
                      key={i}
                      label={`${token.token}: ${token.importance.toFixed(2)}`}
                      size="small"
                      sx={{ m: 0.5, fontSize: '0.7rem' }}
                    />
                  ))}
                </Box>
              )}
            </Paper>
          )}

          {/* Gemini Evaluation */}
          {node.gemini_evaluation?.available && (
            <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'purple.50' }}>
              <Typography variant="caption" fontWeight="bold">
                Gemini 2.5 Flash
              </Typography>
              <Typography variant="body2">
                Severity: {node.gemini_evaluation.severity}
                <br />
                Bias Score: {(node.gemini_evaluation.bias_score * 100).toFixed(0)}%
                <br />
                Types: {node.gemini_evaluation.bias_types.join(', ')}
              </Typography>
              {node.gemini_evaluation.explanation && (
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  {node.gemini_evaluation.explanation}
                </Typography>
              )}
            </Paper>
          )}
        </Box>
      )}

      {/* Potential Path Buttons */}
      {node.potentialPaths && node.potentialPaths.length > 0 && (
        <Box sx={{ mt: 2, borderTop: '1px solid #ddd', pt: 1 }}>
          <Typography variant="caption" color="textSecondary">
            Available Actions:
          </Typography>

          {/* Bias Actions */}
          {node.potentialPaths.filter(p => p.type === 'bias').map(path => (
            <Button
              key={path.id}
              size="small"
              variant="outlined"
              color="error"
              onClick={() => onExpandPath(node.id, node.prompt, path)}
              sx={{ m: 0.5 }}
              startIcon={<AddCircle />}
            >
              {path.label}
            </Button>
          ))}

          {/* Debias Actions */}
          {node.potentialPaths.filter(p => p.type === 'debias').map(path => (
            <Button
              key={path.id}
              size="small"
              variant="outlined"
              color="success"
              onClick={() => onExpandPath(node.id, node.prompt, path)}
              sx={{ m: 0.5 }}
              startIcon={<RemoveCircle />}
            >
              {path.label}
            </Button>
          ))}
        </Box>
      )}
    </Box>
  );
};
```

### Update `getNodeStyle`

```javascript
const getNodeStyle = (node) => {
  const baseStyle = {
    background: '#fff',
    border: '2px solid',
    borderRadius: 8,
    padding: 0,
    minWidth: 320,
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  };

  if (node.type === 'original') {
    return { ...baseStyle, borderColor: '#339af0' };
  } else if (node.type === 'biased') {
    return { ...baseStyle, borderColor: '#ff6b6b' };
  } else if (node.type === 'debiased') {
    return { ...baseStyle, borderColor: '#51cf66' };
  }

  return baseStyle;
};
```

## Testing Checklist

- [ ] Initial prompt creates 1 node with LLM answer
- [ ] HEARTS evaluation displays correctly
- [ ] Gemini evaluation displays correctly
- [ ] Token importance chips show top biased tokens
- [ ] Potential path buttons render (not as edges)
- [ ] Clicking bias button creates biased child node
- [ ] Clicking debias button creates debiased child node
- [ ] New child nodes show their own potential paths
- [ ] Can expand nodes multiple levels deep
- [ ] Graph layout positions nodes correctly

## Quick Implementation Steps

1. Update `handleSubmit` to separate potential paths from actual edges
2. Store `potentialPaths` in node data
3. Create `EnhancedNodeLabel` component with all new UI elements
4. Implement `handleExpandPath` function
5. Update `getNodeStyle` for new node types
6. Test with a simple prompt

## Example Test Flow

```
1. Enter: "What makes a good leader?"
   → Shows 1 node with answer
   → HEARTS: Non-stereotype (91%)
   → Gemini: Low bias
   → Buttons: "Add Confirmation Bias", "Add Demographic Bias", etc.

2. Click "Add Confirmation Bias"
   → API transforms to: "Don't you think a good leader obviously needs..."
   → Shows new node with answer
   → HEARTS: Stereotype (78%)
   → Gemini: High bias
   → New buttons appear on this node

3. Click "Remove Confirmation Bias" on biased node
   → API transforms back to neutral
   → Shows debiased node
   → HEARTS: Non-stereotype
   → Gemini: Low bias
```
