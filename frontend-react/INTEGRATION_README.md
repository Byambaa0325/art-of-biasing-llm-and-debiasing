# Frontend Integration Guide

## New Components Added

### 1. ModeSelector.js
Allows users to toggle between "Live Generation" and "Explore Dataset" modes.

**Props:**
- `mode` - Current mode ('live' or 'explore')
- `onModeChange` - Callback when mode changes
- `supportsLiveGeneration` - Whether selected model supports live generation

### 2. ModelSelector.js
Enhanced model selector with Bedrock/Ollama grouping and live/static indicators.

**Props:**
- `selectedModel` - Currently selected model ID
- `onModelChange` - Callback when model changes
- `apiBaseUrl` - API base URL

**Features:**
- Groups models by type (Bedrock / Ollama)
- Shows [LIVE] badge for Bedrock models
- Shows [STATIC] badge for Ollama models
- Displays model metadata (type, live support, entry count)

### 3. DatasetExplorer.js
Browse and filter dataset entries for exploration.

**Props:**
- `onSelectEntry` - Callback when entry is selected
- `apiBaseUrl` - API base URL

**Features:**
- Filter by stereotype type, trait
- Pagination
- Shows dataset statistics
- Displays number of available bias types per entry

### 4. ExplorePanel.js
Main integration component that combines all new components.

**Props:**
- `apiBaseUrl` - API base URL
- `onExploreEntry` - Callback when dataset entry is selected for exploration

**Features:**
- Manages mode state
- Manages model selection
- Auto-switches to explore mode for Ollama models
- Provides instructions for each mode

## Integration with App.js

### Option 1: Add as New Tab/View

```jsx
import ExplorePanel from './components/ExplorePanel';

function App() {
  const [view, setView] = useState('graph'); // 'graph' or 'explore'

  const handleExploreEntry = (data) => {
    const { mode, model, entry } = data;

    if (mode === 'explore') {
      // Load pre-generated results for this model and entry
      loadModelResults(model, entry.emgsd_text);
    } else {
      // Use existing live generation flow
      handleLiveGeneration(entry.target_question);
    }
  };

  return (
    <Box>
      {/* View Selector */}
      <ToggleButtonGroup value={view} exclusive onChange={(e, v) => setView(v)}>
        <ToggleButton value="graph">Graph Mode</ToggleButton>
        <ToggleButton value="explore">Explore Mode</ToggleButton>
      </ToggleButtonGroup>

      {view === 'graph' ? (
        <GraphView /> // Existing graph interface
      ) : (
        <ExplorePanel
          apiBaseUrl={API_BASE_URL}
          onExploreEntry={handleExploreEntry}
        />
      )}
    </Box>
  );
}
```

### Option 2: Add as Sidebar

```jsx
import ExplorePanel from './components/ExplorePanel';

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      {/* Left Panel: Explore Controls */}
      <Box sx={{ width: 400, p: 2, borderRight: 1, borderColor: 'divider' }}>
        <ExplorePanel
          apiBaseUrl={API_BASE_URL}
          onExploreEntry={handleExploreEntry}
        />
      </Box>

      {/* Right Panel: Graph View */}
      <Box sx={{ flexGrow: 1, p: 2 }}>
        <GraphView />
      </Box>
    </Box>
  );
}
```

### Option 3: Replace Existing Input Panel

```jsx
import ExplorePanel from './components/ExplorePanel';

// Replace the current input panel with ExplorePanel
// Use ExplorePanel to select entries/models, then load into graph
```

## API Endpoints Used

The new components use these API endpoints:

1. `GET /api/models/available` - Get available models (ModelSelector)
2. `GET /api/dataset/stats` - Get dataset statistics (DatasetExplorer)
3. `GET /api/dataset/entries` - Get dataset entries with filters (DatasetExplorer)
4. `GET /api/models/{model_id}/results` - Get model results (when entry selected)
5. `GET /api/models/{model_id}/result/{index}` - Get specific result

## Loading Model Results

When a dataset entry is selected in Explore mode:

```jsx
const handleExploreEntry = async (data) => {
  const { mode, model, entry } = data;

  if (mode === 'explore') {
    try {
      // Get the entry index from the dataset
      const entryIndex = entry.entry_index || 0;

      // Fetch pre-generated results for this model and entry
      const response = await axios.get(
        `${API_BASE_URL}/models/${model}/result/${entryIndex}`
      );

      const result = response.data.result;

      // Create nodes for the multi-turn conversation
      const nodes = [
        {
          id: 'root',
          type: 'input',
          data: {
            label: 'Turn 1 (Priming)',
            prompt: result.turn1_question,
          },
          position: { x: 100, y: 100 },
        },
        {
          id: 'turn1-response',
          data: {
            label: 'Turn 1 Response',
            llm_answer: result.turn1_response,
          },
          position: { x: 100, y: 250 },
        },
        {
          id: 'turn2',
          data: {
            label: 'Turn 2 (Target)',
            prompt: result.target_question,
          },
          position: { x: 100, y: 400 },
        },
        {
          id: 'turn2-biased',
          data: {
            label: 'Biased Response',
            llm_answer: result.turn2_response,
            type: 'biased',
          },
          position: { x: 100, y: 550 },
        },
        {
          id: 'control',
          data: {
            label: 'Control (No Priming)',
            llm_answer: result.control_response,
            type: 'control',
          },
          position: { x: 400, y: 400 },
        },
      ];

      // Update graph with these nodes
      setNodes(nodes);

    } catch (error) {
      console.error('Failed to load model results:', error);
    }
  }
};
```

## Styling

All components use Material-UI (MUI) and are styled consistently with:
- Paper components for cards
- Chips for badges/labels
- Icons from @mui/icons-material
- Responsive layouts with flexbox

## Dependencies

Make sure these are installed:

```bash
npm install @mui/material @mui/icons-material axios
```

## Testing

1. Start the backend: `python backend/api.py`
2. Start the frontend: `cd frontend-react && npm start`
3. Navigate to the Explore view
4. Select a model (try both Bedrock and Ollama)
5. Switch between Live and Explore modes
6. Use the dataset explorer to browse entries
7. Select an entry to load results

## Next Steps

1. Add the components to App.js
2. Implement the `handleExploreEntry` logic
3. Update graph visualization for explore mode
4. Add comparison view for biased vs control
5. Add download/export functionality
6. Add HEARTS evaluation overlay for explore mode results

## File Structure

```
frontend-react/src/
├── components/
│   ├── ModeSelector.js        # Mode toggle (Live/Explore)
│   ├── ModelSelector.js       # Enhanced model selector
│   ├── DatasetExplorer.js     # Dataset browser
│   └── ExplorePanel.js        # Main integration component
├── App.js                     # Main app (update this)
└── INTEGRATION_README.md      # This file
```
