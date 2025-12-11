/**
 * Explore Panel Component
 *
 * Main panel that integrates Mode Selector, Model Selector, and Dataset Explorer
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  Button,
  Divider,
} from '@mui/material';
import ModeSelector from './ModeSelector';
import ModelSelector from './ModelSelector';
import DatasetExplorer from './DatasetExplorer';

const ExplorePanel = ({ apiBaseUrl, onExploreEntry }) => {
  const [mode, setMode] = useState('explore'); // 'live' or 'explore'
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedModelInfo, setSelectedModelInfo] = useState(null);
  const [models, setModels] = useState({ bedrock_models: [], ollama_models: [] });

  // Fetch models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/models/available`);
        if (response.ok) {
          const data = await response.json();
          setModels(data);
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
      }
    };
    fetchModels();
  }, [apiBaseUrl]);

  useEffect(() => {
    // Set default model when models are loaded
    if (models.bedrock_models.length > 0 && !selectedModel) {
      setSelectedModel(models.bedrock_models[0].id);
    } else if (models.ollama_models.length > 0 && !selectedModel) {
      setSelectedModel(models.ollama_models[0].id);
    }
  }, [models, selectedModel]);

  useEffect(() => {
    // Update selected model info
    const allModels = [
      ...models.bedrock_models,
      ...models.ollama_models,
    ];
    const modelInfo = allModels.find(m => m.id === selectedModel);
    setSelectedModelInfo(modelInfo);

    // Auto-switch to explore mode if model doesn't support live generation
    if (modelInfo && !modelInfo.supports_live_generation && mode === 'live') {
      setMode('explore');
    }
  }, [selectedModel, models, mode]);

  const handleModeChange = (newMode) => {
    setMode(newMode);
  };

  const handleModelChange = (newModel) => {
    setSelectedModel(newModel);
  };

  const handleSelectEntry = (entry) => {
    // Pass entry to parent component
    if (onExploreEntry) {
      onExploreEntry({
        mode,
        model: selectedModel,
        entry,
      });
    }
  };

  const supportsLiveGeneration = selectedModelInfo?.supports_live_generation || false;

  return (
    <Box>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 2, mb: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h5" fontWeight="bold">
          Bias Exploration Tool
        </Typography>
        <Typography variant="body2">
          Explore bias transfer in LLMs through live generation or pre-generated results
        </Typography>
      </Paper>

      {/* Model Selector */}
      <ModelSelector
        selectedModel={selectedModel}
        onModelChange={handleModelChange}
        apiBaseUrl={apiBaseUrl}
      />

      {/* Mode Selector */}
      <ModeSelector
        mode={mode}
        onModeChange={handleModeChange}
        supportsLiveGeneration={supportsLiveGeneration}
      />

      {/* Mode-Specific Content */}
      {mode === 'live' ? (
        <Paper elevation={2} sx={{ p: 3, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Live Generation Mode
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            In Live Generation mode, you can generate bias injections in real-time using Amazon Nova Pro.
            This mode requires Bedrock API credentials.
          </Alert>

          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>How it works:</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary" component="div">
            <ol style={{ paddingLeft: 20 }}>
              <li>Enter a custom prompt or select from dataset</li>
              <li>Choose a bias type (e.g., confirmation, anchoring)</li>
              <li>Amazon Nova Pro generates a persona-based priming question (Turn 1)</li>
              <li>The selected model responds to the priming</li>
              <li>The original prompt is asked (Turn 2)</li>
              <li>Compare biased response with control</li>
            </ol>
          </Typography>

          <Divider sx={{ my: 2 }} />

          <Typography variant="body2" color="text.secondary">
            Use the existing graph interface to start exploring with live generation.
          </Typography>
        </Paper>
      ) : (
        <>
          {/* Dataset Explorer for Explore Mode */}
          <DatasetExplorer
            onSelectEntry={handleSelectEntry}
            apiBaseUrl={apiBaseUrl}
          />

          {/* Instructions */}
          <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
            <Typography variant="caption" color="text.secondary">
              <strong>Tip:</strong> Select an entry from the table above to explore pre-generated
              bias injection results for the selected model ({selectedModel}).
              You can compare Turn 2 responses (with bias priming) against control responses
              (without priming).
            </Typography>
          </Paper>
        </>
      )}
    </Box>
  );
};

export default ExplorePanel;
