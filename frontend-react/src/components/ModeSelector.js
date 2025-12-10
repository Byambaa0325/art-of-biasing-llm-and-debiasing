/**
 * Mode Selector Component
 *
 * Allows users to choose between Live Generation and Explore Dataset modes
 */

import React from 'react';
import {
  Box,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Paper,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Explore,
  Info,
} from '@mui/icons-material';

const ModeSelector = ({ mode, onModeChange, supportsLiveGeneration }) => {
  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Mode
        </Typography>
        <Tooltip title="Choose between generating new bias injections in real-time (Live) or browsing pre-generated results (Explore)">
          <Info fontSize="small" color="action" />
        </Tooltip>
      </Box>

      <ToggleButtonGroup
        value={mode}
        exclusive
        onChange={(e, newMode) => {
          if (newMode !== null) {
            onModeChange(newMode);
          }
        }}
        fullWidth
        color="primary"
      >
        <ToggleButton
          value="live"
          disabled={!supportsLiveGeneration}
          sx={{ py: 2 }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            <PlayArrow sx={{ mb: 0.5 }} />
            <Typography variant="subtitle2" fontWeight="bold">
              Live Generation
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {supportsLiveGeneration
                ? 'Generate bias injections in real-time'
                : 'Not available for this model'}
            </Typography>
          </Box>
        </ToggleButton>

        <ToggleButton value="explore" sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            <Explore sx={{ mb: 0.5 }} />
            <Typography variant="subtitle2" fontWeight="bold">
              Explore Dataset
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Browse pre-generated results (800+ entries)
            </Typography>
          </Box>
        </ToggleButton>
      </ToggleButtonGroup>

      {!supportsLiveGeneration && mode === 'live' && (
        <Box sx={{ mt: 2, p: 1.5, bgcolor: 'warning.light', borderRadius: 1 }}>
          <Typography variant="body2" color="warning.dark">
            <strong>Note:</strong> Live generation is only available for Bedrock models.
            Ollama models can only be explored using pre-generated results.
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ModeSelector;
