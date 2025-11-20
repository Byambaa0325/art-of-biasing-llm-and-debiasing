import React, { useState, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  AddCircle,
  RemoveCircle,
  Assessment,
  Info,
  Close,
} from '@mui/icons-material';
import axios from 'axios';
import './App.css';
import SourceDefinitions from './SourceDefinitions';

// API URL from environment variable (set in .env file)
// Defaults to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [evaluating, setEvaluating] = useState(false);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/graph/expand`, {
        prompt: prompt.trim(),
      });

      const { nodes: newNodes, edges: newEdges, root_id } = response.data;

      // Format nodes for ReactFlow
      const formattedNodes = newNodes.map((node, index) => ({
        id: node.id,
        data: {
          label: (
            <NodeLabel
              node={node}
              onExpand={handleExpandNode}
              onEvaluate={handleEvaluateNode}
              onInfo={handleNodeInfo}
            />
          ),
          ...node,
        },
        position: {
          x: index % 3 * 300,
          y: Math.floor(index / 3) * 200,
        },
        style: getNodeStyle(node),
      }));

      // Format edges for ReactFlow
      const formattedEdges = newEdges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        type: 'smoothstep',
        animated: edge.highlight,
        style: {
          stroke: edge.highlight ? '#51cf66' : edge.type === 'bias' ? '#ff6b6b' : '#339af0',
          strokeWidth: edge.highlight ? 3 : 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: edge.highlight ? '#51cf66' : edge.type === 'bias' ? '#ff6b6b' : '#339af0',
        },
      }));

      setNodes(formattedNodes);
      setEdges(formattedEdges);
    } catch (error) {
      console.error('Error expanding graph:', error);
      alert('Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleExpandNode = async (nodeId, action, biasType = 'confirmation') => {
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/graph/expand-node`, {
        node_id: nodeId,
        prompt: node.data.prompt,
        action: action, // 'bias' or 'debias'
        bias_type: biasType,
      });

      const { nodes: newNodes, edges: newEdges } = response.data;

      // Add new nodes
      const formattedNodes = newNodes.map((newNode, index) => ({
        id: newNode.id,
        data: {
          label: (
            <NodeLabel
              node={newNode}
              onExpand={handleExpandNode}
              onEvaluate={handleEvaluateNode}
              onInfo={handleNodeInfo}
            />
          ),
          ...newNode,
        },
        position: {
          x: node.position.x + (index + 1) * 250,
          y: node.position.y + (action === 'debias' ? -100 : 100),
        },
        style: getNodeStyle(newNode),
      }));

      // Add new edges
      const formattedEdges = newEdges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label || (action === 'debias' ? 'Debias' : 'Bias'),
        type: 'smoothstep',
        animated: edge.highlight,
        style: {
          stroke: edge.highlight ? '#51cf66' : '#ff6b6b',
          strokeWidth: edge.highlight ? 3 : 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: edge.highlight ? '#51cf66' : '#ff6b6b',
        },
      }));

      setNodes((nds) => [...nds, ...formattedNodes]);
      setEdges((eds) => [...eds, ...formattedEdges]);
    } catch (error) {
      console.error('Error expanding node:', error);
      alert('Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateNode = async (nodeId) => {
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;

    setEvaluating(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/graph/evaluate`, {
        node_id: nodeId,
        prompt: node.data.prompt,
      });

      const evaluation = response.data.evaluation;
      setSelectedNode({ ...node.data, evaluation });
      setDialogOpen(true);
    } catch (error) {
      console.error('Error evaluating node:', error);
      alert('Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setEvaluating(false);
    }
  };

  const handleNodeInfo = (node) => {
    setSelectedNode(node);
    setDialogOpen(true);
  };

  const getNodeStyle = (node) => {
    const baseStyle = {
      padding: '10px',
      borderRadius: '8px',
      border: '2px solid',
      minWidth: '200px',
      background: 'white',
    };

    if (node.type === 'debiased') {
      return {
        ...baseStyle,
        borderColor: '#51cf66',
        background: '#f0fdf4',
      };
    } else if (node.type === 'biased') {
      return {
        ...baseStyle,
        borderColor: '#ff6b6b',
        background: '#fff1f2',
      };
    } else {
      return {
        ...baseStyle,
        borderColor: '#667eea',
        background: '#f8f9fa',
      };
    }
  };

  return (
    <div className="app">
      <Box className="header">
        <Typography variant="h3" component="h1" sx={{ color: 'white', mb: 1 }}>
          🎯 Art of Biasing LLM
        </Typography>
        <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.9)' }}>
          Interactive Prompt Bias Analysis with Graph Visualization
        </Typography>
      </Box>

      <Box className="input-section">
        <Paper elevation={3} sx={{ p: 3, maxWidth: '800px', mx: 'auto' }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Enter your starter prompt"
            placeholder="Type your prompt here... (e.g., 'What are the best programming languages?')"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            size="large"
            onClick={handleSubmit}
            disabled={loading || !prompt.trim()}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            }}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Bias Graph'}
          </Button>
        </Paper>
      </Box>

      <Box className="graph-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </Box>

      <NodeDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        node={selectedNode}
        evaluating={evaluating}
      />
    </div>
  );
}

function NodeLabel({ node, onExpand, onEvaluate, onInfo }) {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
          {node.label}
        </Typography>
        <Chip
          label={node.type === 'debiased' ? 'Debiased' : node.type === 'biased' ? 'Biased' : 'Original'}
          size="small"
          color={node.type === 'debiased' ? 'success' : node.type === 'biased' ? 'error' : 'primary'}
        />
      </Box>
      <Box sx={{ display: 'flex', gap: 0.5, mt: 1 }}>
        {node.type !== 'original' && (
          <>
            <Tooltip title="Further debias">
              <IconButton
                size="small"
                color="success"
                onClick={(e) => {
                  e.stopPropagation();
                  onExpand(node.id, 'debias');
                }}
              >
                <AddCircle fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Add bias">
              <IconButton
                size="small"
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  onExpand(node.id, 'bias');
                }}
              >
                <RemoveCircle fontSize="small" />
              </IconButton>
            </Tooltip>
          </>
        )}
        <Tooltip title="Evaluate bias (Gemini 2.5 Flash)">
          <IconButton
            size="small"
            color="primary"
            onClick={(e) => {
              e.stopPropagation();
              onEvaluate(node.id);
            }}
          >
            <Assessment fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="View details">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onInfo(node);
            }}
          >
            <Info fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
}

function NodeDialog({ open, onClose, node, evaluating }) {
  if (!node) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">{node.label}</Typography>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Prompt:
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              {node.prompt}
            </Typography>
          </Paper>
        </Box>

        {node.explanation && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Explanation:
            </Typography>
            <Typography variant="body2">{node.explanation}</Typography>
          </Box>
        )}

        {node.source && (
          <Box sx={{ mb: 2 }}>
            <Chip label={`Source: ${node.source}`} size="small" />
          </Box>
        )}

        {node.evaluation && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Bias Evaluation (Gemini 2.5 Flash)
            </Typography>
            {evaluating ? (
              <CircularProgress />
            ) : (
              <Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Bias Score: {node.evaluation.evaluation?.bias_score?.toFixed(2) || 'N/A'}</Typography>
                  <Typography variant="subtitle2">Severity: {node.evaluation.evaluation?.severity || 'N/A'}</Typography>
                </Box>
                {node.evaluation.evaluation?.explanation && (
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {node.evaluation.evaluation.explanation}
                  </Typography>
                )}
                {node.evaluation.evaluation?.recommendations && (
                  <Paper sx={{ p: 2, bgcolor: 'info.light' }}>
                    <Typography variant="body2">
                      <strong>Recommendations:</strong> {node.evaluation.evaluation.recommendations}
                    </Typography>
                  </Paper>
                )}
              </Box>
            )}
          </Box>
        )}

        {node.framework && (
          <Box sx={{ mt: 2 }}>
            <Chip label={`Framework: ${node.framework}`} size="small" color="info" />
          </Box>
        )}

        {node.bias_type && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Bias Type: {node.bias_type}
            </Typography>
            <SourceDefinitions biasType={node.bias_type} />
          </Box>
        )}

        {node.how_it_works && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              How It Works:
            </Typography>
            <Typography variant="body2">{node.how_it_works}</Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}

export default App;

