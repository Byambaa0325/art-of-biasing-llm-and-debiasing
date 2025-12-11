import React, { useState, useCallback, useRef, useEffect } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButtonGroup,
  ToggleButton,
  Container,
} from '@mui/material';
import {
  Info,
  Close,
  Create,
  Explore,
} from '@mui/icons-material';
import axios from 'axios';
import './App.css';
import SourceDefinitions from './SourceDefinitions';
import ExplorePanel from './components/ExplorePanel';

// API URL from environment variable (set in .env file)
// Defaults to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// API Key from environment (optional - can be empty for local dev)
const DEFAULT_API_KEY = process.env.REACT_APP_API_KEY || '';

// Helper to get axios config with API key
const getAxiosConfig = (apiKey) => {
  if (!apiKey) return {};
  return {
    headers: {
      'X-API-Key': apiKey
    }
  };
};

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [expandingNodeId, setExpandingNodeId] = useState(null);
  const [viewMode, setViewMode] = useState('input'); // 'input' or 'graph'
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('meta/llama-3.3-70b-instruct-maas'); // Default model
  const [apiKey, setApiKey] = useState(DEFAULT_API_KEY); // API key for authentication
  const [inputMode, setInputMode] = useState('custom'); // 'custom' or 'explore'
  const [exploreData, setExploreData] = useState(null); // Data from explore mode

  // Use ref to always have access to current nodes
  const nodesRef = useRef(nodes);
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  // Fetch available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const headers = apiKey ? { 'X-API-Key': apiKey } : {};
        const response = await fetch(`${API_BASE_URL}/models`, { headers });
        if (response.ok) {
          const data = await response.json();
          setAvailableModels(data.generation_models || []);
        } else if (response.status === 401 || response.status === 403) {
          console.warn('API key required or invalid');
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
      }
    };
    fetchModels();
  }, [apiKey]);

  // Layout constants
  const LAYOUT_CONFIG = {
    centerX: 800,
    centerY: 400,
    radiusIncrement: 350,  // Distance between levels
    minAngleSeparation: 0.3,  // Minimum angle between siblings
  };

  // Calculate radial position for a node
  const calculateRadialPosition = (parentPos, childIndex, totalChildren, level, parentAngle = 0) => {
    const radius = LAYOUT_CONFIG.radiusIncrement * level;

    // Calculate angle spread based on number of children
    let angleSpread = Math.PI * 1.5; // 270 degrees by default
    if (totalChildren === 1) {
      angleSpread = 0;
    } else if (totalChildren === 2) {
      angleSpread = Math.PI; // 180 degrees
    }

    // Calculate angle for this child
    const startAngle = parentAngle - angleSpread / 2;
    const angleStep = totalChildren > 1 ? angleSpread / (totalChildren - 1) : 0;
    const angle = startAngle + (angleStep * childIndex);

    // Calculate position
    const x = parentPos.x + radius * Math.cos(angle);
    const y = parentPos.y + radius * Math.sin(angle);

    return { x, y, angle };
  };

  // Get all descendants of a node
  const getNodeDescendants = (nodeId, currentNodes, currentEdges) => {
    const descendants = new Set([nodeId]);
    const queue = [nodeId];

    while (queue.length > 0) {
      const current = queue.shift();
      const children = currentEdges
        .filter(e => e.source === current && e.target)
        .map(e => e.target);

      children.forEach(child => {
        if (!descendants.has(child)) {
          descendants.add(child);
          queue.push(child);
        }
      });
    }

    return descendants;
  };

  // Calculate level for each node (distance from root)
  const calculateNodeLevels = (currentNodes, currentEdges) => {
    const levels = {};
    const rootNode = currentNodes.find(n => n.data.isOriginal || n.data.type === 'original');
    if (!rootNode) return levels;

    levels[rootNode.id] = 0;
    const queue = [{ id: rootNode.id, level: 0 }];

    while (queue.length > 0) {
      const { id, level } = queue.shift();
      const children = currentEdges
        .filter(e => e.source === id && e.target)
        .map(e => e.target);

      children.forEach(childId => {
        if (levels[childId] === undefined) {
          levels[childId] = level + 1;
          queue.push({ id: childId, level: level + 1 });
        }
      });
    }

    return levels;
  };

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Track last known positions for drag delta calculation
  const lastPositionsRef = useRef({});

  // Handle node drag - move children along with parent
  const onNodeDrag = useCallback((event, draggedNode) => {
    const lastPos = lastPositionsRef.current[draggedNode.id];

    if (!lastPos) {
      // First drag event, just record position
      lastPositionsRef.current[draggedNode.id] = { ...draggedNode.position };
      return;
    }

    // Calculate delta from last position
    const deltaX = draggedNode.position.x - lastPos.x;
    const deltaY = draggedNode.position.y - lastPos.y;

    // Update last position
    lastPositionsRef.current[draggedNode.id] = { ...draggedNode.position };

    // If there's a meaningful delta, move all descendants
    if (Math.abs(deltaX) > 0.1 || Math.abs(deltaY) > 0.1) {
      const currentNodes = nodesRef.current;
      const currentEdges = edges;

      // Get all descendants of the dragged node
      const descendants = getNodeDescendants(draggedNode.id, currentNodes, currentEdges);
      descendants.delete(draggedNode.id); // Don't move the dragged node itself

      if (descendants.size > 0) {
        // Update positions of all descendants
        setNodes((nds) =>
          nds.map((node) => {
            if (descendants.has(node.id)) {
              return {
                ...node,
                position: {
                  x: node.position.x + deltaX,
                  y: node.position.y + deltaY,
                },
              };
            }
            return node;
          })
        );

        // Update last positions for all moved descendants
        descendants.forEach(descId => {
          const desc = currentNodes.find(n => n.id === descId);
          if (desc) {
            lastPositionsRef.current[descId] = {
              x: desc.position.x + deltaX,
              y: desc.position.y + deltaY,
            };
          }
        });
      }
    }
  }, [edges, setNodes]);

  // Clear last positions when drag ends
  const onNodeDragStop = useCallback((event, node) => {
    // Clear the position cache for this node
    delete lastPositionsRef.current[node.id];

    // Also clear for all descendants to avoid stale data
    const currentNodes = nodesRef.current;
    const descendants = getNodeDescendants(node.id, currentNodes, edges);
    descendants.forEach(descId => {
      delete lastPositionsRef.current[descId];
    });
  }, [edges]);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/graph/expand`,
        { prompt: prompt.trim(), model_id: selectedModel },
        getAxiosConfig(apiKey)
      );

      const { nodes: newNodes, edges: newEdges, root_id } = response.data;

      // Separate actual edges (have target) from potential paths (no target)
      const actualEdges = newEdges.filter(edge => edge.target);
      const potentialPaths = newEdges.filter(edge => !edge.target);

      console.log('Received nodes:', newNodes.length);
      console.log('Actual edges:', actualEdges.length);
      console.log('Potential paths:', potentialPaths.length);

      const allNodes = [];
      const allEdges = [];

      // Format the original node (center of canvas)
      const originalNode = newNodes[0];
      const centerPos = { x: LAYOUT_CONFIG.centerX, y: LAYOUT_CONFIG.centerY };

      allNodes.push({
        id: originalNode.id,
        data: {
          ...originalNode,
          isOriginal: true,
          level: 0,
          angle: 0,
          label: (
            <NodeLabel
              node={originalNode}
              nodeId={originalNode.id}
              isPotential={false}
              onInfo={handleNodeInfo}
            />
          ),
        },
        position: centerPos,
        style: getNodeStyle(originalNode),
        draggable: true,
        selectable: true,
      });

      // Create neighbor nodes for each potential path - spread in all directions
      const allPotentialPaths = potentialPaths;
      const totalPotentials = allPotentialPaths.length;

      allPotentialPaths.forEach((path, index) => {
        const nodeId = `potential-${path.id}`;

        // Calculate radial position around center
        const { x, y, angle } = calculateRadialPosition(
          centerPos,
          index,
          totalPotentials,
          1,  // Level 1 (first ring around center)
          0   // Parent angle (center has no angle)
        );

        allNodes.push({
          id: nodeId,
          data: {
            prompt: `${path.label}`,
            type: path.type === 'bias' ? 'potential_bias' : 'potential_debias',
            isPotential: true,
            pathData: path,
            parentId: originalNode.id,
            parentPrompt: originalNode.prompt,
            level: 1,
            angle: angle,
            label: (
              <NodeLabel
                node={{
                  prompt: path.label,
                  type: path.type === 'bias' ? 'potential_bias' : 'potential_debias',
                  description: path.description,
                }}
                nodeId={nodeId}
                isPotential={true}
                pathData={path}
                parentId={originalNode.id}
                parentPrompt={originalNode.prompt}
                onExpand={handleExpandPath}
                onInfo={handleNodeInfo}
                isExpanding={expandingNodeId === nodeId}
                isAnyExpanding={expandingNodeId !== null}
              />
            ),
          },
          position: { x, y },
          style: getPotentialNodeStyle(path.type === 'bias' ? 'bias' : 'debias'),
          draggable: true,
          selectable: true,
        });

        // Add edge from original to potential
        allEdges.push({
          id: `edge-${path.id}`,
          source: originalNode.id,
          target: nodeId,
          label: '',
          type: 'smoothstep',
          animated: false,
          style: {
            stroke: path.type === 'bias' ? '#ffc9c9' : '#b2f2bb',
            strokeWidth: 1,
            strokeDasharray: '5,5',
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: path.type === 'bias' ? '#ffc9c9' : '#b2f2bb',
          },
        });
      });

      setNodes(allNodes);
      setEdges(allEdges);

      // Switch to graph view and save the prompt
      setCurrentPrompt(prompt.trim());
      setViewMode('graph');
    } catch (error) {
      console.error('Error expanding graph:', error);
      alert('Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Reset to start over with new prompt
  const handleReset = () => {
    setViewMode('input');
    setPrompt('');
    setCurrentPrompt('');
    setNodes([]);
    setEdges([]);
    setExpandingNodeId(null);
    setExploreData(null);
  };

  // Handle dataset entry selection in explore mode
  const handleExploreEntry = async (data) => {
    const { mode, model, entry } = data;
    
    if (mode === 'explore') {
      // Fetch pre-generated model results
      setLoading(true);
      try {
        // First get model info
        const modelsResponse = await axios.get(`${API_BASE_URL}/models/available`);
        const allModels = [
          ...(modelsResponse.data.bedrock_models || []),
          ...(modelsResponse.data.ollama_models || []),
        ];
        const modelInfo = allModels.find(m => m.id === model);
        
        // Get results for this model and entry
        const response = await axios.get(
          `${API_BASE_URL}/models/${encodeURIComponent(model)}/result/${entry.entry_index}`
        );
        
        const result = response.data;
        
        // Store explore data for header display
        setExploreData({
          model: model,
          modelName: modelInfo?.name || model,
          entry: entry,
          result: result,
        });
        
        // Create graph visualization with pre-generated data
        await displayExploreResults(result, entry, model);
        
        // Switch to graph view
        setCurrentPrompt(entry.target_question || entry.emgsd_text);
        setViewMode('graph');
      } catch (error) {
        console.error('Error fetching model results:', error);
        alert('Error: ' + (error.response?.data?.error || error.message));
      } finally {
        setLoading(false);
      }
    } else {
      // Live generation mode - use existing flow but with dataset entry
      setPrompt(entry.target_question || entry.emgsd_text);
      setInputMode('custom');
      // User can then click "Generate Bias Graph" to use live generation
    }
  };

  // Display pre-generated results in graph format
  const displayExploreResults = async (result, entry, modelId) => {
    const allNodes = [];
    const allEdges = [];
    
    // Center position
    const centerPos = { x: LAYOUT_CONFIG.centerX, y: LAYOUT_CONFIG.centerY };
    
    // Create root node (original prompt/target question)
    const rootId = 'root-node';
    allNodes.push({
      id: rootId,
      data: {
        prompt: entry.target_question || entry.emgsd_text,
        type: 'original',
        isOriginal: true,
        level: 0,
        angle: 0,
        emgsd_trait: entry.emgsd_trait,
        emgsd_stereotype_type: entry.emgsd_stereotype_type,
        label: (
          <NodeLabel
            node={{
              prompt: entry.target_question || entry.emgsd_text,
              type: 'original',
              emgsd_trait: entry.emgsd_trait,
              emgsd_stereotype_type: entry.emgsd_stereotype_type,
            }}
            nodeId={rootId}
            isPotential={false}
            onInfo={handleNodeInfo}
          />
        ),
      },
      position: centerPos,
      style: getNodeStyle({ type: 'original' }),
      draggable: true,
      selectable: true,
    });
    
    // Create biased node (Turn 2 response after priming)
    const biasedId = 'biased-node';
    const biasedPos = calculateRadialPosition(centerPos, 0, 2, 1, 0);
    
    allNodes.push({
      id: biasedId,
      data: {
        prompt: entry.target_question || entry.emgsd_text,
        llm_answer: result.turn2_response,
        type: 'biased',
        transformation: result.bias_type,
        level: 1,
        angle: biasedPos.angle,
        transformation_details: {
          action: 'bias',
          bias_type: result.bias_type,
          framework: 'EMGSD Multi-turn',
          multi_turn: true,
          conversation: {
            turn1_question: result.turn1_question,
            turn1_response: result.turn1_response,
            original_prompt: entry.target_question || entry.emgsd_text,
            turn2_response: result.turn2_response,
            bias_count: 1,
          },
        },
        label: (
          <NodeLabel
            node={{
              prompt: entry.target_question || entry.emgsd_text,
              llm_answer: result.turn2_response,
              type: 'biased',
              transformation: result.bias_type,
              transformation_details: {
                action: 'bias',
                bias_type: result.bias_type,
                framework: 'EMGSD Multi-turn',
                multi_turn: true,
                conversation: {
                  turn1_question: result.turn1_question,
                  turn1_response: result.turn1_response,
                  original_prompt: entry.target_question || entry.emgsd_text,
                  turn2_response: result.turn2_response,
                  bias_count: 1,
                },
              },
            }}
            nodeId={biasedId}
            isPotential={false}
            onInfo={handleNodeInfo}
          />
        ),
      },
      position: { x: biasedPos.x, y: biasedPos.y },
      style: getNodeStyle({ type: 'biased' }),
      draggable: true,
      selectable: true,
    });
    
    // Create control node (no priming)
    const controlId = 'control-node';
    const controlPos = calculateRadialPosition(centerPos, 1, 2, 1, 0);
    
    allNodes.push({
      id: controlId,
      data: {
        prompt: entry.target_question || entry.emgsd_text,
        llm_answer: result.control_response,
        type: 'control',
        transformation: 'Control (No Bias)',
        level: 1,
        angle: controlPos.angle,
        transformation_details: {
          action: 'control',
          framework: 'EMGSD Multi-turn',
          explanation: 'This is the control response without any bias priming.',
        },
        label: (
          <NodeLabel
            node={{
              prompt: entry.target_question || entry.emgsd_text,
              llm_answer: result.control_response,
              type: 'control',
              transformation: 'Control (No Bias)',
              transformation_details: {
                action: 'control',
                framework: 'EMGSD Multi-turn',
                explanation: 'This is the control response without any bias priming.',
              },
            }}
            nodeId={controlId}
            isPotential={false}
            onInfo={handleNodeInfo}
          />
        ),
      },
      position: { x: controlPos.x, y: controlPos.y },
      style: getNodeStyle({ type: 'control' }),
      draggable: true,
      selectable: true,
    });
    
    // Add edges
    allEdges.push({
      id: `edge-${rootId}-${biasedId}`,
      source: rootId,
      target: biasedId,
      label: result.bias_type,
      type: 'smoothstep',
      animated: false,
      style: {
        stroke: '#ff6b6b',
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#ff6b6b',
      },
    });
    
    allEdges.push({
      id: `edge-${rootId}-${controlId}`,
      source: rootId,
      target: controlId,
      label: 'Control',
      type: 'smoothstep',
      animated: false,
      style: {
        stroke: '#868e96',
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#868e96',
      },
    });
    
    setNodes(allNodes);
    setEdges(allEdges);
  };

  const handleExpandPath = async (potentialNodeId, parentNodeId, parentPrompt, pathData) => {
    // Prevent multiple clicks on the same node
    if (expandingNodeId === potentialNodeId) {
      console.log('Already expanding this node, ignoring click');
      return;
    }

    // Prevent expanding multiple nodes at once
    if (expandingNodeId) {
      console.log('Another node is expanding, please wait');
      return;
    }

    console.log('Expanding path:', pathData);

    setExpandingNodeId(potentialNodeId);
    setLoading(true);
    try {
      // Get parent node to extract conversation history for nested bias injection
      let currentNodes = nodesRef.current;
      let parentNode = currentNodes.find(n => n.id === parentNodeId);
      
      // Extract parent conversation history if it exists (for nested bias injection)
      let parentConversation = null;
      if (parentNode?.data?.transformation_details?.conversation) {
        parentConversation = parentNode.data.transformation_details.conversation;
      }

      const payload = {
        node_id: parentNodeId,
        prompt: parentPrompt,
        action: pathData.type,  // 'bias' or 'debias'
        model_id: selectedModel,  // Include selected model
      };

      // Add specific params based on action type
      if (pathData.type === 'bias') {
        payload.bias_type = pathData.bias_type;
        // Include parent conversation for nested bias injection (to prepend new turns)
        if (parentConversation) {
          payload.parent_conversation = parentConversation;
        }
      } else {
        payload.method = pathData.method;
      }

      console.log('Sending payload:', payload);

      const response = await axios.post(
        `${API_BASE_URL}/graph/expand-node`,
        payload,
        getAxiosConfig(apiKey)
      );

      const { nodes: newNodes, edges: newEdges, new_node_id } = response.data;

      // Separate actual edges from potential paths
      const actualEdges = newEdges.filter(edge => edge.target);
      const potentialPaths = newEdges.filter(edge => !edge.target);

      console.log('Received new nodes:', newNodes.length);
      console.log('Actual edges:', actualEdges.length);
      console.log('Potential paths:', potentialPaths.length);

      // Refresh current nodes and find the potential node to replace
      currentNodes = nodesRef.current;
      const currentEdges = edges;
      const potentialNode = currentNodes.find(n => n.id === potentialNodeId);
      parentNode = currentNodes.find(n => n.id === parentNodeId);

      // Use the position and metadata of the potential node
      const actualNodePosition = potentialNode?.position || parentNode?.position || { x: LAYOUT_CONFIG.centerX, y: LAYOUT_CONFIG.centerY };
      const parentLevel = parentNode?.data?.level || 0;
      const parentAngle = potentialNode?.data?.angle || 0;
      const actualLevel = parentLevel + 1;

      const allNewNodes = [];
      const allNewEdges = [];

      // Format the actual node (replaces potential node at same position)
      const actualNode = newNodes[0];
      allNewNodes.push({
        id: actualNode.id,
        data: {
          ...actualNode,
          isActual: true,
          level: actualLevel,
          angle: parentAngle,
          label: (
            <NodeLabel
              node={actualNode}
              nodeId={actualNode.id}
              isPotential={false}
              onInfo={handleNodeInfo}
            />
          ),
        },
        position: actualNodePosition,
        style: getNodeStyle(actualNode),
        draggable: true,
        selectable: true,
      });

      // Add connecting edge from parent to actual node
      allNewEdges.push({
        id: `edge-${parentNodeId}-${actualNode.id}`,
        source: parentNodeId,
        target: actualNode.id,
        label: pathData.label,
        type: 'smoothstep',
        animated: false,
        style: {
          stroke: pathData.type === 'bias' ? '#ff6b6b' : '#51cf66',
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: pathData.type === 'bias' ? '#ff6b6b' : '#51cf66',
        },
      });

      // Create neighbor nodes for each potential path - spread radially around actual node
      const allPotentialPaths = potentialPaths;
      const totalPotentials = allPotentialPaths.length;

      allPotentialPaths.forEach((path, index) => {
        const nodeId = `potential-${path.id}`;

        // Calculate radial position around the actual node
        const { x, y, angle } = calculateRadialPosition(
          actualNodePosition,
          index,
          totalPotentials,
          1,  // One level out from actual node
          parentAngle  // Use parent's angle to spread children
        );

        allNewNodes.push({
          id: nodeId,
          data: {
            prompt: `${path.label}`,
            type: path.type === 'bias' ? 'potential_bias' : 'potential_debias',
            isPotential: true,
            pathData: path,
            parentId: actualNode.id,
            parentPrompt: actualNode.prompt,
            level: actualLevel + 1,
            angle: angle,
            label: (
              <NodeLabel
                node={{
                  prompt: path.label,
                  type: path.type === 'bias' ? 'potential_bias' : 'potential_debias',
                  description: path.description,
                }}
                nodeId={nodeId}
                isPotential={true}
                pathData={path}
                parentId={actualNode.id}
                parentPrompt={actualNode.prompt}
                onExpand={handleExpandPath}
                onInfo={handleNodeInfo}
                isExpanding={false}
                isAnyExpanding={false}
              />
            ),
          },
          position: { x, y },
          style: getPotentialNodeStyle(path.type === 'bias' ? 'bias' : 'debias'),
          draggable: true,
          selectable: true,
        });

        // Add dashed edge
        allNewEdges.push({
          id: `edge-${path.id}`,
          source: actualNode.id,
          target: nodeId,
          label: '',
          type: 'smoothstep',
          animated: false,
          style: {
            stroke: path.type === 'bias' ? '#ffc9c9' : '#b2f2bb',
            strokeWidth: 1,
            strokeDasharray: '5,5',
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: path.type === 'bias' ? '#ffc9c9' : '#b2f2bb',
          },
        });
      });

      // Remove the clicked potential node and its edge, then add new nodes
      setNodes((nds) => [
        ...nds.filter(n => n.id !== potentialNodeId),
        ...allNewNodes,
      ]);

      setEdges((eds) => [
        ...eds.filter(e => e.target !== potentialNodeId),
        ...allNewEdges,
      ]);

    } catch (error) {
      console.error('Error expanding path:', error);
      alert('Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      setExpandingNodeId(null);
    }
  };

  const handleEvaluateNode = async (nodeId) => {
    console.log('Evaluating node:', nodeId);
    
    // Use ref to get current nodes (avoids closure issues)
    const currentNodes = nodesRef.current;
    console.log('Current nodes from ref:', currentNodes.map(n => n.id));
    
    const node = currentNodes.find((n) => n.id === nodeId);
    if (!node) {
      console.error('Node not found:', nodeId);
      console.error('Available node IDs:', currentNodes.map(n => n.id));
      alert(`Node not found: ${nodeId}. Please try generating a new graph.`);
      return;
    }

    setEvaluating(true);
    try {
      // Get prompt from node data
      const nodePrompt = node.data?.prompt || node.data?.data?.prompt || '';
      if (!nodePrompt) {
        alert('Could not find prompt in node data. Please try again.');
        setEvaluating(false);
        return;
      }
      
      const response = await axios.post(`${API_BASE_URL}/graph/evaluate`, {
        node_id: nodeId,
        prompt: nodePrompt,
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
      padding: 0,
      borderRadius: '8px',
      border: '2px solid',
      width: '320px',
      maxWidth: '320px',
      background: 'white',
      overflow: 'hidden',
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
    } else if (node.type === 'control') {
      return {
        ...baseStyle,
        borderColor: '#868e96',
        background: '#f8f9fa',
      };
    } else {
      return {
        ...baseStyle,
        borderColor: '#667eea',
        background: '#f8f9fa',
      };
    }
  };

  const getPotentialNodeStyle = (type) => {
    const baseStyle = {
      padding: 0,
      borderRadius: '8px',
      border: '2px dashed',
      width: '180px',
      maxWidth: '180px',
      background: 'white',
      opacity: 0.85,
      cursor: 'pointer',
      overflow: 'hidden',
    };

    if (type === 'bias') {
      return {
        ...baseStyle,
        borderColor: '#ffc9c9',
        background: '#fff5f5',
      };
    } else {
      return {
        ...baseStyle,
        borderColor: '#b2f2bb',
        background: '#f4fdf6',
      };
    }
  };

  // Input Screen - Centered, prominent
  if (viewMode === 'input') {
    return (
      <Box
        sx={{
          width: '100vw',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          p: 3,
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography
            variant="h2"
            component="h1"
            sx={{
              color: 'white',
              mb: 2,
              fontWeight: 'bold',
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
            }}
          >
            🎯 Art of Biasing LLM
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255,255,255,0.95)',
              mb: 1,
            }}
          >
            Interactive Prompt Bias Analysis with Graph Visualization
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(255,255,255,0.8)',
              maxWidth: '800px',
              mx: 'auto',
            }}
          >
            Explore how biases affect LLM responses. Generate live bias injections or explore pre-generated results from 13+ models.
          </Typography>
        </Box>

        <Container maxWidth="lg">
          <Paper
            elevation={6}
            sx={{
              p: 4,
              borderRadius: 3,
              mb: 4,
            }}
          >
            {/* Mode Toggle */}
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
              <ToggleButtonGroup
                value={inputMode}
                exclusive
                onChange={(e, newMode) => {
                  if (newMode !== null) {
                    setInputMode(newMode);
                  }
                }}
                color="primary"
                sx={{ mb: 2 }}
              >
                <ToggleButton value="custom" sx={{ px: 4, py: 1.5 }}>
                  <Create sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">
                      Custom Prompt
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Enter your own prompt
                    </Typography>
                  </Box>
                </ToggleButton>
                <ToggleButton value="explore" sx={{ px: 4, py: 1.5 }}>
                  <Explore sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">
                      Explore Dataset
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Browse 1,158+ pre-generated results
                    </Typography>
                  </Box>
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>

            {/* Custom Prompt Mode */}
            {inputMode === 'custom' && (
              <>
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="model-select-label">LLM Model</InputLabel>
                  <Select
                    labelId="model-select-label"
                    id="model-select"
                    value={selectedModel}
                    label="LLM Model"
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {availableModels.length === 0 ? (
                      <MenuItem value={selectedModel}>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            Llama 3.3 70B (Default)
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Meta - Loading other models...
                          </Typography>
                        </Box>
                      </MenuItem>
                    ) : (
                      availableModels.map((model) => (
                        <MenuItem key={model.id} value={model.id}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {model.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {model.provider} - {model.description}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))
                    )}
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  label="Enter your starter prompt"
                  placeholder="Type your prompt here... (e.g., 'What are the benefits of exercise?' or 'Why are women always so emotional?')"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.ctrlKey && prompt.trim()) {
                      handleSubmit();
                    }
                  }}
                  sx={{ mb: 3 }}
                  variant="outlined"
                />
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleSubmit}
                    disabled={loading || !prompt.trim()}
                    fullWidth
                    sx={{
                      py: 1.5,
                      fontSize: '1.1rem',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                      },
                    }}
                  >
                    {loading ? <CircularProgress size={28} color="inherit" /> : 'Generate Bias Graph'}
                  </Button>
                </Box>
                <Typography variant="caption" sx={{ display: 'block', mt: 2, color: 'text.secondary', textAlign: 'center' }}>
                  Tip: Press Ctrl+Enter to submit
                </Typography>
              </>
            )}

            {/* Explore Dataset Mode */}
            {inputMode === 'explore' && (
              <ExplorePanel
                apiBaseUrl={API_BASE_URL}
                onExploreEntry={handleExploreEntry}
              />
            )}
          </Paper>
        </Container>
      </Box>
    );
  }

  // Graph Screen - Full screen with compact header
  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Compact Header */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          px: 3,
          py: 1.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <Box sx={{ flex: 1, mr: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 0.5, flexWrap: 'wrap' }}>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, fontSize: '0.75rem' }}>
              {exploreData ? 'Exploring Pre-generated Results:' : 'Analyzing Prompt:'}
            </Typography>
            <Box
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                backdropFilter: 'blur(10px)',
                px: 1.5,
                py: 0.3,
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
              }}
            >
              <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.7rem', fontWeight: 500 }}>
                Model:
              </Typography>
              <Typography variant="caption" sx={{ fontSize: '0.7rem', fontWeight: 'bold' }}>
                {exploreData?.modelName || availableModels.find(m => m.id === selectedModel)?.name || 'Llama 3.3 70B'}
              </Typography>
            </Box>
            {exploreData && (
              <Chip
                label="Pre-generated Results"
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.3)',
                  color: 'white',
                  fontSize: '0.65rem',
                  height: '20px',
                }}
              />
            )}
          </Box>
          <Typography
            variant="body1"
            sx={{
              fontWeight: 500,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            "{currentPrompt}"
          </Typography>
        </Box>
        <Button
          variant="contained"
          onClick={handleReset}
          sx={{
            bgcolor: 'rgba(255,255,255,0.2)',
            '&:hover': {
              bgcolor: 'rgba(255,255,255,0.3)',
            },
            backdropFilter: 'blur(10px)',
          }}
        >
          New Analysis
        </Button>
      </Box>

      {/* Full Screen Graph */}
      <Box sx={{ flex: 1, position: 'relative' }}>
        {/* Global loading overlay when any node is expanding */}
        {expandingNodeId && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              bgcolor: 'rgba(0, 0, 0, 0.02)',
              zIndex: 10,
              pointerEvents: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                bgcolor: 'background.paper',
                boxShadow: 3,
              }}
            >
              <CircularProgress size={32} />
              <Typography variant="body2" color="text.secondary">
                Expanding node...
              </Typography>
            </Paper>
          </Box>
        )}
        
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDrag={onNodeDrag}
          onNodeDragStop={onNodeDragStop}
          fitView
          nodesDraggable={!expandingNodeId}
          nodesConnectable={false}
          elementsSelectable={!expandingNodeId}
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
    </Box>
  );
}

function NodeLabel({ node, nodeId, isPotential, pathData, parentId, parentPrompt, onExpand, onInfo, isExpanding, isAnyExpanding }) {
  const [showDetails, setShowDetails] = useState(false);

  // Potential node (dashed border) - clickable to expand
  if (isPotential) {
    const isDisabled = isExpanding || isAnyExpanding;

    return (
      <Box
        sx={{
          width: '180px',
          maxWidth: '180px',
          p: 1.5,
          textAlign: 'center',
          cursor: isDisabled ? 'wait' : 'pointer',
          overflow: 'hidden',
          opacity: isDisabled ? 0.6 : 1,
          pointerEvents: isDisabled ? 'none' : 'auto',
          transition: 'all 0.2s',
          position: 'relative',
          // Add pulsing animation when expanding
          ...(isExpanding && {
            animation: 'pulse 2s ease-in-out infinite',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 0.6 },
              '50%': { opacity: 0.8 },
            },
          }),
        }}
        onClick={(e) => {
          e.stopPropagation();
          if (!isDisabled && onExpand && pathData && parentId && parentPrompt) {
            onExpand(nodeId, parentId, parentPrompt, pathData);
          }
        }}
      >
        {/* Loading overlay when expanding */}
        {isExpanding && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              bgcolor: 'rgba(255, 255, 255, 0.8)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1,
              borderRadius: 1,
            }}
          >
            <CircularProgress size={24} sx={{ mb: 1 }} />
            <Typography
              variant="caption"
              sx={{
                fontSize: '10px',
                fontWeight: 'bold',
                color: 'primary.main',
              }}
            >
              Expanding...
            </Typography>
          </Box>
        )}
        
        <Typography
          variant="caption"
          sx={{
            fontWeight: 'bold',
            fontSize: '11px',
            display: 'block',
            mb: 0.5,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            opacity: isExpanding ? 0.3 : 1,
          }}
        >
          {node.prompt}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            fontSize: '9px',
            color: isExpanding ? 'primary.main' : 'text.secondary',
            display: 'block',
            fontWeight: isExpanding ? 'bold' : 'normal',
          }}
        >
          {isExpanding ? 'Expanding...' : isAnyExpanding ? 'Please wait...' : 'Click to expand'}
        </Typography>
        {!isExpanding && isAnyExpanding && (
          <CircularProgress size={12} sx={{ mt: 0.5, opacity: 0.5 }} />
        )}
        {node.description && (
          <Typography
            variant="caption"
            sx={{
              fontSize: '8px',
              color: 'text.secondary',
              mt: 0.5,
              fontStyle: 'italic',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              opacity: isExpanding ? 0.3 : 1,
            }}
          >
            {node.description}
          </Typography>
        )}
      </Box>
    );
  }

  // Actual node (solid border) - shows full details
  return (
    <Box
      sx={{
        width: '320px',
        maxWidth: '320px',
        p: 2,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Typography
          variant="subtitle2"
          sx={{
            fontWeight: 'bold',
            fontSize: '12px',
            color: 'text.secondary',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {node.type === 'original' ? 'Original Prompt' :
           node.type === 'biased' ? `Biased (${node.transformation || 'Modified'})` :
           node.type === 'control' ? 'Control (No Bias)' :
           `Debiased (${node.transformation || 'Modified'})`}
        </Typography>
      </Box>

      {/* Prompt */}
      <Typography
        variant="body2"
        sx={{
          mb: 1.5,
          fontWeight: '600',
          fontSize: '13px',
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          wordBreak: 'break-word',
        }}
      >
        {node.prompt}
      </Typography>

      {/* LLM Answer */}
      {node.llm_answer && (
        <Box sx={{ mb: 1.5, width: '100%', overflow: 'hidden' }}>
          <Paper
            sx={{
              p: 1.5,
              bgcolor: 'grey.50',
              fontSize: '11px',
              maxHeight: '200px',
              overflowY: 'auto',
              overflowX: 'hidden',
              width: '100%',
              boxSizing: 'border-box',
            }}
            elevation={0}
          >
            <Typography
              variant="body2"
              sx={{
                display: 'block',
                wordBreak: 'break-word',
                overflowWrap: 'break-word',
                whiteSpace: 'pre-wrap',
                margin: 0,
              }}
            >
              {node.llm_answer || ''}
            </Typography>
          </Paper>
        </Box>
      )}

      {/* Main Evaluation Badges - Always Visible */}
      <Box sx={{ mb: 1, width: '100%', display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {/* HEARTS Badge */}
        {node.hearts_evaluation?.available && (
          <Chip
            label={`HEARTS: ${node.hearts_evaluation.prediction || 'Unknown'} (${(node.hearts_evaluation.confidence * 100).toFixed(0)}%)`}
            size="small"
            color={node.hearts_evaluation.is_stereotype ? 'error' : 'success'}
            sx={{ 
              fontSize: '9px', 
              height: '20px',
              fontWeight: 'bold',
              bgcolor: node.hearts_evaluation.is_stereotype ? '#fee' : '#efe',
              borderColor: node.hearts_evaluation.is_stereotype ? '#f66' : '#6f6',
              border: '1px solid'
            }}
            title={`HEARTS ALBERT-v2 stereotype detection - Confidence: ${(node.hearts_evaluation.confidence * 100).toFixed(0)}%`}
          />
        )}

        {/* Claude Badge */}
        {node.claude_evaluation?.available && (
          <Chip
            label={`Claude: ${node.claude_evaluation.severity || 'Unknown'} (${((node.claude_evaluation.bias_score || 0) * 100).toFixed(0)}%)`}
            size="small"
            color={
              node.claude_evaluation.severity === 'severe' || node.claude_evaluation.severity === 'high' ? 'error' :
              node.claude_evaluation.severity === 'medium' ? 'warning' : 
              node.claude_evaluation.severity === 'low' ? 'success' : 'default'
            }
            sx={{ 
              fontSize: '9px', 
              height: '20px',
              fontWeight: 'bold',
              bgcolor: 
                node.claude_evaluation.severity === 'severe' || node.claude_evaluation.severity === 'high' ? '#ffe0e0' :
                node.claude_evaluation.severity === 'medium' ? '#fff4e0' : 
                node.claude_evaluation.severity === 'low' ? '#e8f5e9' : '#f5f5f5',
              borderColor: 
                node.claude_evaluation.severity === 'severe' || node.claude_evaluation.severity === 'high' ? '#ff6b6b' :
                node.claude_evaluation.severity === 'medium' ? '#ffc107' : 
                node.claude_evaluation.severity === 'low' ? '#4caf50' : '#999',
              border: '1px solid'
            }}
            title={`Claude ${node.claude_evaluation.model || '3.5 Sonnet'} zero-shot bias evaluation - ${node.claude_evaluation.bias_types?.length || 0} bias types detected`}
          />
        )}

        {/* Gemini Badge */}
        {node.gemini_evaluation?.available && (
          <Chip
            label={`Gemini: ${node.gemini_evaluation.severity || 'Unknown'}`}
            size="small"
            color={
              node.gemini_evaluation.severity === 'severe' || node.gemini_evaluation.severity === 'high' ? 'error' :
              node.gemini_evaluation.severity === 'medium' ? 'warning' : 'success'
            }
            sx={{ 
              fontSize: '9px', 
              height: '20px',
              fontWeight: 'bold'
            }}
            title={`Gemini 2.5 Flash validation`}
          />
        )}
      </Box>

      {/* Bias Metrics from Multiple Judges */}
      {node.bias_metrics && node.bias_metrics.length > 0 && (
        <Box sx={{ mb: 1, width: '100%' }}>
          {node.bias_metrics.map((metric, idx) => (
            <Chip
              key={idx}
              label={`${metric.judge}: ${(metric.score * 100).toFixed(0)}%`}
              size="small"
              color={metric.score > 0.6 ? 'error' : metric.score > 0.3 ? 'warning' : 'success'}
              sx={{ 
                mb: 0.5, 
                mr: 0.5,
                fontSize: '9px', 
                height: '18px',
                display: 'inline-flex'
              }}
              title={`${metric.description} (${metric.framework || metric.model || ''})`}
            />
          ))}
        </Box>
      )}
      
      {/* Fallback: Single Bias Score (for backward compatibility) */}
      {(!node.bias_metrics || node.bias_metrics.length === 0) && node.bias_score !== undefined && (
        <Chip
          label={`Bias: ${(node.bias_score * 100).toFixed(0)}%`}
          size="small"
          color={node.bias_score > 0.6 ? 'error' : node.bias_score > 0.3 ? 'warning' : 'success'}
          sx={{ mb: 1, fontSize: '10px', height: '20px' }}
        />
      )}

      {/* Evaluations Toggle */}
      {(node.hearts_evaluation?.available || node.gemini_evaluation?.available || node.claude_evaluation?.available) && (
        <Box sx={{ mb: 1.5, width: '100%', overflow: 'hidden' }}>
          <Button
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setShowDetails(!showDetails);
            }}
            sx={{ fontSize: '10px', minHeight: 0, py: 0.5 }}
          >
            {showDetails ? '▼ Hide' : '▶ Show'} Evaluations
          </Button>

          {showDetails && (
            <Box sx={{ mt: 1, width: '100%' }}>
              {/* HEARTS Evaluation */}
              {node.hearts_evaluation?.available && (
                <Paper
                  sx={{
                    p: 1,
                    mb: 1,
                    bgcolor: 'blue.50',
                    width: '100%',
                    boxSizing: 'border-box',
                    overflow: 'hidden',
                  }}
                  elevation={0}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 'bold',
                      display: 'block',
                      fontSize: '10px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    HEARTS ALBERT-v2
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontSize: '9px',
                      display: 'block',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {node.hearts_evaluation.prediction || 'Unknown'}
                    {' '}({(node.hearts_evaluation.confidence * 100).toFixed(0)}%)
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.3, mt: 0.5 }}>
                    {node.hearts_evaluation.token_importance?.slice(0, 3).map((token, i) => (
                      <Chip
                        key={i}
                        label={`${token.token}: ${token.importance.toFixed(2)}`}
                        size="small"
                        sx={{
                          fontSize: '8px',
                          height: '16px',
                          maxWidth: '100%',
                          '& .MuiChip-label': {
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          },
                        }}
                      />
                    ))}
                  </Box>
                </Paper>
              )}

              {/* Gemini Evaluation */}
              {node.gemini_evaluation?.available && (
                <Paper
                  sx={{
                    p: 1,
                    mb: 1,
                    bgcolor: 'purple.50',
                    width: '100%',
                    boxSizing: 'border-box',
                    overflow: 'hidden',
                  }}
                  elevation={0}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 'bold',
                      display: 'block',
                      fontSize: '10px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    Gemini 2.5 Flash
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontSize: '9px',
                      display: 'block',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    Severity: {node.gemini_evaluation.severity || 'Unknown'}
                  </Typography>
                  {node.gemini_evaluation.explanation && (
                    <Typography
                      variant="caption"
                      sx={{
                        fontSize: '8px',
                        mt: 0.5,
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        wordBreak: 'break-word',
                      }}
                    >
                      {node.gemini_evaluation.explanation}
                    </Typography>
                  )}
                </Paper>
              )}

              {/* Claude Evaluation */}
              {node.claude_evaluation?.available && (
                <Paper
                  sx={{
                    p: 1,
                    bgcolor: 'orange.50',
                    width: '100%',
                    boxSizing: 'border-box',
                    overflow: 'hidden',
                  }}
                  elevation={0}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 'bold',
                      display: 'block',
                      fontSize: '10px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {node.claude_evaluation.model || 'Claude 3.5 Sonnet'} ({node.claude_evaluation.method || 'Zero-shot'})
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontSize: '9px',
                      display: 'block',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    Bias Score: {((node.claude_evaluation.bias_score || 0) * 100).toFixed(0)}% | Severity: {node.claude_evaluation.severity || 'Unknown'}
                  </Typography>
                  {node.claude_evaluation.bias_types && node.claude_evaluation.bias_types.length > 0 && (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.3, mt: 0.5 }}>
                      {node.claude_evaluation.bias_types.slice(0, 3).map((type, i) => (
                        <Chip
                          key={i}
                          label={type}
                          size="small"
                          sx={{
                            fontSize: '8px',
                            height: '16px',
                            maxWidth: '100%',
                            '& .MuiChip-label': {
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            },
                          }}
                        />
                      ))}
                    </Box>
                  )}
                  {node.claude_evaluation.explanation && (
                    <Typography
                      variant="caption"
                      sx={{
                        fontSize: '8px',
                        mt: 0.5,
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        wordBreak: 'break-word',
                      }}
                    >
                      {node.claude_evaluation.explanation}
                    </Typography>
                  )}
                </Paper>
              )}
            </Box>
          )}
        </Box>
      )}

      {/* Info Button */}
      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          size="small"
          startIcon={<Info />}
          onClick={(e) => {
            e.stopPropagation();
            e.preventDefault();
            if (onInfo) {
              onInfo(node);
            }
          }}
          sx={{ fontSize: '9px', minHeight: 0, py: 0.3 }}
        >
          Full Prompt
        </Button>
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

        {/* HEARTS, Gemini, and Claude Evaluations */}
        {(node.hearts_evaluation?.available || node.gemini_evaluation?.available || node.claude_evaluation?.available) && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Bias Evaluations:
            </Typography>
            
            {/* HEARTS Evaluation */}
            {node.hearts_evaluation?.available && (
              <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'blue.50' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  HEARTS ALBERT-v2
                </Typography>
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  Prediction: {node.hearts_evaluation.prediction || 'Unknown'} 
                  ({(node.hearts_evaluation.confidence * 100).toFixed(0)}% confidence)
                </Typography>
                {node.hearts_evaluation.token_importance && node.hearts_evaluation.token_importance.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5, fontWeight: 'bold' }}>
                      Top Biased Tokens:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {node.hearts_evaluation.token_importance.slice(0, 5).map((token, i) => (
                        <Chip
                          key={i}
                          label={`${token.token}: ${token.importance.toFixed(2)}`}
                          size="small"
                          sx={{ fontSize: '9px' }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Paper>
            )}

            {/* Gemini Evaluation */}
            {node.gemini_evaluation?.available && (
              <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'purple.50' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  Gemini 2.5 Flash
                </Typography>
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  Severity: {node.gemini_evaluation.severity || 'Unknown'}
                </Typography>
                {node.gemini_evaluation.explanation && (
                  <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                    {node.gemini_evaluation.explanation}
                  </Typography>
                )}
              </Paper>
            )}

            {/* Claude Evaluation */}
            {node.claude_evaluation?.available && (
              <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'orange.50' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  {node.claude_evaluation.model || 'Claude 3.5 Sonnet'} ({node.claude_evaluation.method || 'Zero-shot'})
                </Typography>
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  Bias Score: {((node.claude_evaluation.bias_score || 0) * 100).toFixed(0)}% | 
                  Severity: {node.claude_evaluation.severity || 'Unknown'}
                </Typography>
                {node.claude_evaluation.bias_types && node.claude_evaluation.bias_types.length > 0 && (
                  <Box sx={{ mt: 1, mb: 1 }}>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5, fontWeight: 'bold' }}>
                      Detected Bias Types:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {node.claude_evaluation.bias_types.map((type, i) => (
                        <Chip
                          key={i}
                          label={type}
                          size="small"
                          color={node.claude_evaluation.severity === 'high' || node.claude_evaluation.severity === 'severe' ? 'error' : 'warning'}
                          sx={{ fontSize: '9px' }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
                {node.claude_evaluation.bias_scores && Object.keys(node.claude_evaluation.bias_scores).length > 0 && (
                  <Box sx={{ mt: 1, mb: 1 }}>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5, fontWeight: 'bold' }}>
                      Bias Category Scores:
                    </Typography>
                    {Object.entries(node.claude_evaluation.bias_scores).slice(0, 5).map(([category, data]) => (
                      <Box key={category} sx={{ mb: 0.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                          {category.replace(/_/g, ' ')}:
                        </Typography>
                        <Chip
                          label={`${((typeof data === 'object' && data.score) ? data.score : data) * 100}%`}
                          size="small"
                          color={((typeof data === 'object' && data.score) ? data.score : data) > 0.6 ? 'error' : ((typeof data === 'object' && data.score) ? data.score : data) > 0.3 ? 'warning' : 'success'}
                          sx={{ fontSize: '9px', height: '20px' }}
                        />
                      </Box>
                    ))}
                  </Box>
                )}
                {node.claude_evaluation.explanation && (
                  <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                    {node.claude_evaluation.explanation}
                  </Typography>
                )}
                {node.claude_evaluation.recommendations && (
                  <Paper sx={{ p: 1, mt: 1, bgcolor: 'info.light' }}>
                    <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 0.5 }}>
                      Recommendations:
                    </Typography>
                    <Typography variant="body2">
                      {node.claude_evaluation.recommendations}
                    </Typography>
                  </Paper>
                )}
              </Paper>
            )}
          </Box>
        )}

        {/* Bias Metrics from Multiple Judges */}
        {node.bias_metrics && node.bias_metrics.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Bias Evaluations ({node.judge_count} {node.judge_count === 1 ? 'Judge' : 'Judges'}):
            </Typography>
            {node.bias_metrics.map((metric, idx) => (
              <Paper key={idx} sx={{ p: 1.5, mb: 1, bgcolor: 'grey.50' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    {metric.judge}
                  </Typography>
                  <Chip
                    label={`${(metric.score * 100).toFixed(0)}%`}
                    size="small"
                    color={metric.score > 0.6 ? 'error' : metric.score > 0.3 ? 'warning' : 'success'}
                  />
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  {metric.description}
                </Typography>
                {(metric.framework || metric.model) && (
                  <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    {metric.framework || metric.model}
                  </Typography>
                )}
                {metric.confidence !== undefined && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    Confidence: {(metric.confidence * 100).toFixed(0)}%
                  </Typography>
                )}
                {metric.severity && (
                  <Chip label={`Severity: ${metric.severity}`} size="small" sx={{ mt: 0.5 }} />
                )}
                
                {/* Gemini Bias Categories Breakdown */}
                {metric.bias_categories && metric.bias_categories.length > 0 && (
                  <Box sx={{ mt: 1, pl: 1, borderLeft: '2px solid #e0e0e0' }}>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5, fontWeight: 'bold' }}>
                      Bias Categories:
                    </Typography>
                    {metric.bias_categories.map((category, catIdx) => (
                      <Box key={catIdx} sx={{ mb: 0.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                            {category.category}:
                          </Typography>
                          <Chip
                            label={`${(category.score * 100).toFixed(0)}%`}
                            size="small"
                            color={category.score > 0.6 ? 'error' : category.score > 0.3 ? 'warning' : 'success'}
                            sx={{ height: '16px', fontSize: '9px' }}
                          />
                        </Box>
                        {category.detected_types && category.detected_types.length > 0 && (
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '10px' }}>
                            {category.detected_types.join(', ')}
                          </Typography>
                        )}
                        {category.description && (
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '10px', display: 'block' }}>
                            {category.description}
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </Box>
                )}
              </Paper>
            ))}
          </Box>
        )}

        {node.explanation && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Explanation:
            </Typography>
            <Typography variant="body2">{node.explanation}</Typography>
          </Box>
        )}

        {/* Node Type and Transformation Info */}
        {(node.type || node.transformation) && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Node Information:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {node.type && (
                <Chip 
                  label={`Type: ${node.type}`} 
                  size="small" 
                  color={node.type === 'biased' ? 'error' : node.type === 'debiased' ? 'success' : 'default'}
                />
              )}
              {node.transformation && (
                <Chip 
                  label={node.transformation} 
                  size="small" 
                  color="primary"
                />
              )}
            </Box>
          </Box>
        )}

        {/* Transformation Details (for biased/debiased nodes) */}
        {node.transformation_details && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Transformation Details:
            </Typography>
            <Paper sx={{ p: 1.5, bgcolor: 'grey.50' }}>
              {node.transformation_details.action && (
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  <strong>Action:</strong> {node.transformation_details.action}
                </Typography>
              )}
              {node.transformation_details.bias_type && (
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  <strong>Bias Type:</strong> {node.transformation_details.bias_type}
                </Typography>
              )}
              {node.transformation_details.method && (
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  <strong>Method:</strong> {node.transformation_details.method}
                </Typography>
              )}
              {node.transformation_details.framework && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, fontStyle: 'italic' }}>
                  Framework: {node.transformation_details.framework}
                </Typography>
              )}
              {node.transformation_details.explanation && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {node.transformation_details.explanation}
                </Typography>
              )}
              {node.transformation_details.multi_turn && (
                <Chip 
                  label="Multi-Turn Injection" 
                  size="small" 
                  color="warning" 
                  sx={{ mt: 1 }}
                />
              )}
            </Paper>
          </Box>
        )}

        {/* Multi-Turn Conversation History */}
        {node.transformation_details?.conversation && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Multi-Turn Conversation History:
              {node.transformation_details.conversation.bias_count > 1 && (
                <Chip 
                  label={`${node.transformation_details.conversation.bias_count} Bias Injections`} 
                  size="small" 
                  color="warning" 
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
            <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
              {/* Render previous conversations if they exist */}
              {node.transformation_details.conversation.previous_conversation && (
                <Box sx={{ mb: 3, pb: 2, borderBottom: '2px solid', borderColor: 'divider' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                    Previous Bias Injections:
                  </Typography>
                  {(() => {
                    const renderConversation = (conv, level = 0) => {
                      if (!conv) return null;
                      
                      return (
                        <Box key={level} sx={{ ml: level * 2, mb: 2 }}>
                          {conv.previous_conversation && renderConversation(conv.previous_conversation, level + 1)}
                          <Box sx={{ mb: 1, p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
                            <Typography variant="caption" color="primary" sx={{ fontWeight: 'bold', display: 'block', mb: 0.5 }}>
                              Bias Injection #{level + 1}
                            </Typography>
                            {conv.turn1_question && (
                              <Box sx={{ mb: 1 }}>
                                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '10px' }}>
                                  Q: {conv.turn1_question.substring(0, 100)}...
                                </Typography>
                              </Box>
                            )}
                            {conv.original_prompt && (
                              <Box>
                                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '10px' }}>
                                  Prompt: {conv.original_prompt.substring(0, 100)}...
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        </Box>
                      );
                    };
                    return renderConversation(node.transformation_details.conversation.previous_conversation);
                  })()}
                </Box>
              )}

              {/* Current Turn 1 - Priming Question */}
              <Box sx={{ mb: 2, pb: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                <Typography variant="caption" color="primary" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                  {node.transformation_details.conversation.bias_count > 1 
                    ? `Turn ${(node.transformation_details.conversation.bias_count - 1) * 2 + 1}: Additional Priming Question`
                    : 'Turn 1: Priming Question'}
                </Typography>
                <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'background.paper' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    User:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      whiteSpace: 'pre-wrap', 
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      maxHeight: '200px',
                      overflow: 'auto'
                    }}
                  >
                    {node.transformation_details.conversation.turn1_question || ''}
                  </Typography>
                </Paper>
                <Paper sx={{ p: 1.5, bgcolor: 'info.light', opacity: 0.8 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    Assistant:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      whiteSpace: 'pre-wrap', 
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      maxHeight: '200px',
                      overflow: 'auto'
                    }}
                  >
                    {node.transformation_details.conversation.turn1_response || ''}
                  </Typography>
                </Paper>
              </Box>

              {/* Current Turn 2 - Original Prompt */}
              <Box>
                <Typography variant="caption" color="primary" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                  {node.transformation_details.conversation.bias_count > 1 
                    ? `Turn ${node.transformation_details.conversation.bias_count * 2}: Original Prompt (After All Priming)`
                    : 'Turn 2: Original Prompt (After Priming)'}
                </Typography>
                <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'background.paper' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    User:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      whiteSpace: 'pre-wrap', 
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      maxHeight: '200px',
                      overflow: 'auto'
                    }}
                  >
                    {node.transformation_details.conversation.original_prompt || ''}
                  </Typography>
                </Paper>
                <Paper sx={{ p: 1.5, bgcolor: node.type === 'biased' ? 'error.light' : 'success.light', opacity: 0.8 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    Assistant (Primed Response):
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      whiteSpace: 'pre-wrap', 
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      maxHeight: '300px',
                      overflow: 'auto'
                    }}
                  >
                    {node.transformation_details.conversation.turn2_response || ''}
                  </Typography>
                </Paper>
              </Box>
            </Paper>
          </Box>
        )}

        {/* Research Frameworks Used */}
        {node.frameworks && node.frameworks.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Research Frameworks:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {node.frameworks.map((framework, idx) => (
                <Chip key={idx} label={framework} size="small" color="info" />
              ))}
            </Box>
          </Box>
        )}

        {/* Detection Sources */}
        {node.detection_sources && node.detection_sources.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Detection Sources:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {node.detection_sources.map((source, idx) => (
                <Chip key={idx} label={source} size="small" variant="outlined" />
              ))}
            </Box>
          </Box>
        )}

        {node.source && (
          <Box sx={{ mb: 2 }}>
            <Chip label={`Source: ${node.source}`} size="small" />
          </Box>
        )}

        {/* Old evaluation field - now merged into bias_metrics above */}
        {node.evaluation && !node.bias_metrics && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Bias Evaluation (Legacy Format)
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

        {/* Legacy bias_type field (for nodes that don't have transformation_details) */}
        {node.bias_type && !node.transformation_details && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Bias Type: {node.bias_type}
            </Typography>
            <SourceDefinitions biasType={node.bias_type} />
          </Box>
        )}

        {/* Legacy framework field (now shown in frameworks array above) */}
        {node.framework && (!node.frameworks || node.frameworks.length === 0) && (
          <Box sx={{ mt: 2 }}>
            <Chip label={`Framework: ${node.framework}`} size="small" color="info" />
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

