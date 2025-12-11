# Frontend Integration Flow Diagram

## User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Home Screen                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  [Custom Prompt]  |  [Explore Dataset]  ◄── Toggle     │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                    │                        │
                    │                        │
        ┌───────────┘                        └──────────┐
        │                                                │
        ▼                                                ▼
┌──────────────────┐                        ┌──────────────────────┐
│  Custom Prompt   │                        │   Explore Dataset    │
│      Mode        │                        │       Mode           │
│                  │                        │                      │
│  1. Select Model │                        │  1. Model Selector   │
│  2. Enter Prompt │                        │     └─ Bedrock       │
│  3. Generate     │                        │     └─ Ollama        │
│                  │                        │                      │
│  [Live Gen ...]  │                        │  2. Mode Selector    │
│                  │                        │     ◯ Live Gen       │
│                  │                        │     ● Explore        │
│                  │                        │                      │
│                  │                        │  3. Dataset Explorer │
│                  │                        │     - Filters        │
│                  │                        │     - Table          │
│                  │                        │     - Pagination     │
│                  │                        │                      │
└──────────────────┘                        └──────────────────────┘
        │                                                │
        │                                                │
        └─────────────────┐                ┌────────────┘
                          │                │
                          ▼                ▼
                  ┌────────────────────────────┐
                  │   Graph Visualization      │
                  │                            │
                  │        ┌────────┐          │
                  │        │ Root   │          │
                  │        │ Node   │          │
                  │        └────┬───┘          │
                  │             │              │
                  │     ┌───────┴───────┐      │
                  │     │               │      │
                  │     ▼               ▼      │
                  │ ┌────────┐     ┌────────┐ │
                  │ │ Biased │     │Control │ │
                  │ │  Node  │     │  Node  │ │
                  │ └────────┘     └────────┘ │
                  │                            │
                  │  [Click for details...]   │
                  │                            │
                  └────────────────────────────┘
```

## Component Hierarchy

```
App.js
├── Input Screen (viewMode === 'input')
│   ├── Toggle: Custom vs Explore
│   │
│   ├── Custom Mode
│   │   ├── Model Selector (Simple dropdown)
│   │   ├── Text Field (Prompt input)
│   │   └── Generate Button
│   │
│   └── Explore Mode
│       └── ExplorePanel
│           ├── ModelSelector
│           │   ├── Bedrock Models (with LIVE badge)
│           │   └── Ollama Models (with STATIC badge)
│           │
│           ├── ModeSelector
│           │   ├── Live Generation (disabled for Ollama)
│           │   └── Explore Dataset
│           │
│           └── DatasetExplorer (when mode === 'explore')
│               ├── Stats Summary
│               ├── Filters
│               │   ├── Stereotype Type
│               │   └── Trait Search
│               └── Results Table
│                   └── Explore Buttons
│
└── Graph Screen (viewMode === 'graph')
    ├── Header (shows model and prompt)
    ├── ReactFlow Graph
    │   ├── Nodes
    │   │   ├── NodeLabel Component
    │   │   │   ├── Prompt
    │   │   │   ├── LLM Answer
    │   │   │   └── Evaluations
    │   │   └── Full Prompt Dialog
    │   └── Edges
    └── Reset Button
```

## Data Flow

### Explore Mode Flow

```
User selects entry
      │
      ▼
handleExploreEntry({ mode, model, entry })
      │
      ├─── mode === 'explore' ────┐
      │                            │
      │                            ▼
      │                   Fetch model info
      │                   GET /api/models/available
      │                            │
      │                            ▼
      │                   Fetch model result
      │                   GET /api/models/{model}/result/{index}
      │                            │
      │                            ▼
      │                   displayExploreResults()
      │                            │
      │                            ▼
      │                   Create 3 nodes:
      │                   - Root (original prompt)
      │                   - Biased (turn2_response)
      │                   - Control (control_response)
      │                            │
      │                            ▼
      │                   setNodes([...])
      │                   setEdges([...])
      │                            │
      │                            ▼
      │                   setViewMode('graph')
      │
      └─── mode === 'live' ────────┐
                                    │
                                    ▼
                           setPrompt(entry.target_question)
                           setInputMode('custom')
                           (User clicks "Generate Bias Graph")
```

### Custom Mode Flow (Existing)

```
User enters prompt
      │
      ▼
handleSubmit()
      │
      ▼
POST /api/graph/expand
      │
      ▼
Create nodes and edges
      │
      ▼
setNodes([...])
setEdges([...])
      │
      ▼
setViewMode('graph')
```

## API Integration

### Endpoints Used

```
┌─────────────────────────────────────────────────────────┐
│ Frontend                                                 │
│                                                          │
│  ExplorePanel ──────────────────────────────┐           │
│       │                                      │           │
│       │ ModelSelector                        │           │
│       │      │                                │           │
│       │      └─ GET /api/models/available    │           │
│       │                                      │           │
│       │ DatasetExplorer                      │           │
│       │      │                                │           │
│       │      ├─ GET /api/dataset/stats       │           │
│       │      └─ GET /api/dataset/entries     │           │
│       │                                      │           │
│       └─ handleExploreEntry                  │           │
│              │                                │           │
│              └─ GET /api/models/{id}/result/{idx}       │
│                                                          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│ Backend API                                             │
│                                                          │
│  /api/models/available                                  │
│    └─ Returns: { bedrock_models: [], ollama_models: [] }│
│                                                          │
│  /api/dataset/stats                                     │
│    └─ Returns: { total_entries, stereotype_counts, ... }│
│                                                          │
│  /api/dataset/entries?stereotype_type=X&trait=Y         │
│    └─ Returns: { entries: [], total, offset, limit }    │
│                                                          │
│  /api/models/{model_id}/result/{entry_index}            │
│    └─ Returns: { turn1_question, turn1_response,        │
│                  turn2_response, control_response, ... } │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## State Management

### App.js State

```javascript
// View state
viewMode: 'input' | 'graph'
inputMode: 'custom' | 'explore'

// Prompt state
prompt: string                    // User input (custom mode)
currentPrompt: string             // Currently displayed prompt
selectedModel: string             // Model ID

// Graph state
nodes: Node[]                     // React Flow nodes
edges: Edge[]                     // React Flow edges
expandingNodeId: string | null    // Currently expanding node

// Explore state
exploreData: {                    // Data from explore mode
  model: string,
  modelName: string,
  entry: Object,
  result: Object
} | null

// Loading state
loading: boolean
evaluating: boolean

// Dialog state
dialogOpen: boolean
selectedNode: Node | null
```

### ExplorePanel State

```javascript
mode: 'live' | 'explore'          // Mode selector state
selectedModel: string             // Selected model ID
selectedModelInfo: Object | null  // Model metadata
models: {                         // Available models
  bedrock_models: Model[],
  ollama_models: Model[]
}
```

### DatasetExplorer State

```javascript
entries: Entry[]                  // Dataset entries
loading: boolean
page: number                      // Current page
rowsPerPage: number              // Items per page
total: number                     // Total entries
stats: Object | null             // Dataset statistics

// Filters
stereotypeType: string
biasType: string
traitFilter: string
```

## Node Types and Styles

### Node Types

1. **Original** (`type: 'original'`)
   - Border: Purple (#667eea)
   - Background: Light gray (#f8f9fa)
   - Display: Initial prompt/question

2. **Biased** (`type: 'biased'`)
   - Border: Red (#ff6b6b)
   - Background: Light red (#fff1f2)
   - Display: Response after bias priming

3. **Control** (`type: 'control'`)
   - Border: Gray (#868e96)
   - Background: Light gray (#f8f9fa)
   - Display: Response without priming

4. **Debiased** (`type: 'debiased'`)
   - Border: Green (#51cf66)
   - Background: Light green (#f0fdf4)
   - Display: Response after debiasing

## Testing Flow

```
1. Start Backend
   └─ python api.py

2. Start Frontend
   └─ npm start

3. Test Explore Mode
   ├─ Click "Explore Dataset"
   ├─ Select model (e.g., llama3.1:8b)
   ├─ Choose "Explore Dataset" mode
   ├─ Filter by stereotype type
   ├─ Click "Explore" on entry
   └─ Verify graph shows:
      ├─ Root node (original)
      ├─ Biased node (red)
      └─ Control node (gray)

4. Test Details
   ├─ Click "Full Prompt" button
   ├─ Verify conversation display
   └─ Check multi-turn history

5. Test Custom Mode
   ├─ Click "Custom Prompt"
   ├─ Enter text
   └─ Click "Generate Bias Graph"
```

## Error Handling

```javascript
// API Errors
try {
  const response = await axios.get(url);
  // Process response...
} catch (error) {
  console.error('Error:', error);
  alert('Error: ' + (error.response?.data?.error || error.message));
}

// Missing Data
entry_index: entry.entry_index !== undefined 
  ? entry.entry_index 
  : (page * rowsPerPage + idx)

// Model Info Fallback
modelName: modelInfo?.name || model
```

## Performance Considerations

1. **Lazy Loading**: Dataset entries are paginated (10-50 per page)
2. **Caching**: Models list is fetched once and cached
3. **Error Boundaries**: Error handling prevents app crashes
4. **URL Encoding**: Model IDs with special chars are encoded
5. **State Management**: Minimal re-renders with proper useEffect dependencies

---

**Last Updated**: December 10, 2025
