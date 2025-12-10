/**
 * Explore Demo Component
 *
 * Standalone demo of the Explore Panel functionality
 * Can be used for testing or as a starting point for integration
 */

import React from 'react';
import { Box, Container } from '@mui/material';
import ExplorePanel from './ExplorePanel';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function ExploreDemo() {
  const handleExploreEntry = (data) => {
    console.log('Entry selected for exploration:', data);
    const { mode, model, entry } = data;

    if (mode === 'explore') {
      console.log('Loading pre-generated results for:');
      console.log('  Model:', model);
      console.log('  Entry:', entry.target_question);
      console.log('  Trait:', entry.emgsd_trait);

      // Here you would:
      // 1. Fetch model results from API
      // 2. Create graph nodes
      // 3. Display comparison
      alert(`Explore mode: Would load results for model "${model}" and entry "${entry.target_question}"`);
    } else {
      console.log('Live generation mode:');
      console.log('  Model:', model);
      console.log('  Entry:', entry.target_question);

      // Here you would:
      // 1. Use existing live generation flow
      // 2. Generate Turn 1 with Nova Pro
      // 3. Send to selected model
      alert(`Live mode: Would generate bias injection for "${entry.target_question}"`);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <ExplorePanel
        apiBaseUrl={API_BASE_URL}
        onExploreEntry={handleExploreEntry}
      />

      <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <p><strong>Demo Instructions:</strong></p>
        <ol>
          <li>Select a model from the dropdown (try both Bedrock and Ollama models)</li>
          <li>Toggle between "Live Generation" and "Explore Dataset" modes</li>
          <li>In Explore mode, use the filters to browse dataset entries</li>
          <li>Click "Explore" on any entry to see the console output</li>
          <li>Check the browser console for detailed logging</li>
        </ol>
        <p><strong>Note:</strong> This is a demo. In the full integration, selecting an entry would load the graph visualization with pre-generated results.</p>
      </Box>
    </Container>
  );
}

export default ExploreDemo;
