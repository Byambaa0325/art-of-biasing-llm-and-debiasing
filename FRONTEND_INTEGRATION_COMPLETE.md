# Frontend Integration Complete ✅

## Summary

The frontend has been successfully integrated with the Explore Mode functionality described in `EXPLORE_MODE_README.md`. Users can now:

1. **Choose between two input modes:**
   - **Custom Prompt**: Enter a custom prompt for live bias graph generation
   - **Explore Dataset**: Browse and explore pre-generated model evaluation results

2. **Browse 13+ models with pre-generated results:**
   - 8 Bedrock models (support both live generation and exploration)
   - 5+ Ollama models (pre-generated results only)

3. **Explore 1,158+ dataset entries** with filters:
   - Filter by stereotype type (profession, nationality, gender, religion)
   - Search by trait (bossy, lazy, smart, etc.)
   - View bias questions for each entry

4. **Compare biased vs control responses:**
   - View Turn 1 priming question
   - See model's response to priming
   - Compare Turn 2 biased response vs control (no priming)

## Changes Made

### 1. Main App (`App.js`)

#### New State Variables:
- `inputMode`: Tracks whether user is in 'custom' or 'explore' mode
- `exploreData`: Stores information about the selected model and entry for display

#### New Functions:
- `handleExploreEntry()`: Handles dataset entry selection and fetches pre-generated results
- `displayExploreResults()`: Creates graph visualization with biased vs control nodes

#### Updated Functions:
- `handleReset()`: Clears explore data when resetting
- `getNodeStyle()`: Added support for 'control' node type (gray)

#### Updated UI:
- Added toggle buttons to switch between "Custom Prompt" and "Explore Dataset" modes
- Integrated `ExplorePanel` component in explore mode
- Updated graph header to show "Pre-generated Results" badge when in explore mode
- Made input screen scrollable for longer content

### 2. ExplorePanel Component (`ExplorePanel.js`)

#### Fixes:
- Added `useEffect` to fetch models from API on mount
- Properly populates `models` state with Bedrock and Ollama models
- Fixed dependency arrays in `useEffect` hooks

### 3. DatasetExplorer Component (`DatasetExplorer.js`)

#### Fixes:
- Added fallback for `entry_index` field (uses array index if not present)
- Ensures all entries have an `entry_index` for API calls

### 4. Supporting Components

All existing components are working as designed:
- `ModelSelector.js`: Shows Bedrock and Ollama models with live/static indicators
- `ModeSelector.js`: Toggles between live generation and explore modes
- `DatasetExplorer.js`: Browse and filter dataset entries with pagination

## File Structure

```
frontend-react/
├── src/
│   ├── App.js                          # ✅ Updated - Main application
│   ├── components/
│   │   ├── ExplorePanel.js            # ✅ Updated - Main explore panel
│   │   ├── ModelSelector.js           # ✅ Existing - Model selection
│   │   ├── ModeSelector.js            # ✅ Existing - Live vs Explore toggle
│   │   ├── DatasetExplorer.js         # ✅ Updated - Dataset browser
│   │   └── ExploreDemo.js             # ✅ Existing - Standalone demo
```

## API Endpoints Used

The frontend now uses these explore mode endpoints:

1. **GET `/api/models/available`**
   - Fetches list of available models with metadata
   - Returns: `{ bedrock_models: [], ollama_models: [], total_models: N }`

2. **GET `/api/models/{model_id}/result/{entry_index}`**
   - Fetches pre-generated result for specific model and entry
   - Returns: Model evaluation result with turn1_question, turn1_response, turn2_response, control_response

3. **GET `/api/dataset/entries`**
   - Fetches dataset entries with optional filters
   - Query params: `stereotype_type`, `trait`, `limit`, `offset`
   - Returns: `{ entries: [], total: N, offset: N, limit: N }`

4. **GET `/api/dataset/stats`**
   - Fetches dataset statistics
   - Returns: Total entries, stereotype counts, bias success counts

## How to Test

### 1. Start the Backend

```bash
cd backend
python api.py
```

The backend should be running on `http://localhost:5000`

### 2. Start the Frontend

```bash
cd frontend-react
npm install  # If not already installed
npm start
```

The frontend will open at `http://localhost:3000`

### 3. Test Explore Mode

1. **On the home screen**, click the "Explore Dataset" toggle button
2. **Select a model** from the dropdown (try both Bedrock and Ollama models)
3. **Choose a mode:**
   - For Bedrock models: Toggle between "Live Generation" and "Explore Dataset"
   - For Ollama models: Only "Explore Dataset" is available
4. **In Explore Dataset mode:**
   - Use filters to narrow down entries (stereotype type, trait)
   - Click "Explore" on any entry
   - View the graph with:
     - **Root node**: Original prompt/question
     - **Biased node** (red): Turn 2 response after bias priming
     - **Control node** (gray): Response without priming
5. **Click "Full Prompt" on any node** to see:
   - Multi-turn conversation history
   - Turn 1 priming question and response
   - Turn 2 biased response vs control

### 4. Test Custom Mode

1. Click the "Custom Prompt" toggle button
2. Enter a custom prompt
3. Click "Generate Bias Graph" for live generation (existing functionality)

## Graph Visualization

### Node Types:

1. **Original Node** (Purple border):
   - The original prompt/target question
   - Center of the graph

2. **Biased Node** (Red border):
   - Turn 2 response after bias priming
   - Shows the multi-turn conversation in details
   - Displays bias type (e.g., confirmation_bias)

3. **Control Node** (Gray border):
   - Response without any bias priming
   - Direct answer to the original prompt
   - Used for comparison

### Node Information:

Each node shows:
- **Prompt**: The question asked
- **LLM Answer**: The model's response
- **Transformation Details**: How the bias was applied
- **Multi-turn Conversation**: Full conversation history (for biased nodes)

## Features Implemented

✅ Mode selector on input screen (Custom vs Explore)
✅ Model selector with Bedrock/Ollama grouping
✅ Live generation indicator for supported models
✅ Dataset explorer with filters and pagination
✅ Pre-generated results visualization
✅ Biased vs Control comparison graph
✅ Multi-turn conversation display
✅ Model metadata display in header
✅ Proper error handling for API calls
✅ Responsive layout for different screen sizes

## Known Limitations

1. **Entry Index Handling**: The integration assumes dataset entries have an `entry_index` field. A fallback is implemented using array index if not present.

2. **Model ID Encoding**: Model IDs with special characters (e.g., colons in `llama3.1:8b`) are URL-encoded in API calls.

3. **Live Generation with Dataset Entries**: In live mode, selecting a dataset entry populates the custom prompt field, but the user must still click "Generate Bias Graph" to use live generation.

4. **Backend Availability**: The frontend expects all explore mode API endpoints to be available. If the backend is outdated, some features may not work.

## Next Steps (Optional Enhancements)

1. **Add result comparison view**: Side-by-side comparison of multiple models on the same entry
2. **Add export functionality**: Download results as JSON/CSV
3. **Add bias type filter**: Filter dataset entries by available bias types
4. **Add model performance metrics**: Show aggregate bias scores per model
5. **Add search functionality**: Full-text search across dataset entries
6. **Add favorites**: Save favorite entries for quick access
7. **Add history**: Track recently explored entries

## Testing Checklist

- [ ] Switch between Custom and Explore modes
- [ ] Select different models (Bedrock and Ollama)
- [ ] Verify live generation toggle is disabled for Ollama models
- [ ] Filter dataset entries by stereotype type
- [ ] Search dataset entries by trait
- [ ] Click "Explore" on a dataset entry
- [ ] Verify graph shows root, biased, and control nodes
- [ ] Click "Full Prompt" to see conversation details
- [ ] Verify multi-turn conversation display is correct
- [ ] Test pagination in dataset explorer
- [ ] Test reset functionality
- [ ] Test responsive layout on different screen sizes

## Troubleshooting

### Issue: "Failed to fetch models"
**Solution**: Ensure backend is running and `/api/models/available` endpoint exists

### Issue: "Error fetching model results"
**Solution**: Check that model ID is correct and result exists for that entry_index

### Issue: "No entries found"
**Solution**: Verify dataset is loaded in backend and `/api/dataset/entries` returns data

### Issue: Graph doesn't display properly
**Solution**: Check browser console for errors, ensure React Flow CSS is loaded

### Issue: Models dropdown is empty
**Solution**: Check network tab, verify `/api/models/available` returns data

## Conclusion

The frontend integration is complete and ready for testing. All components described in `EXPLORE_MODE_README.md` have been implemented and integrated into the main application.

The integration maintains backward compatibility with existing live generation features while adding powerful new dataset exploration capabilities.

---

**Integration Date**: December 10, 2025
**Components Updated**: 3 (App.js, ExplorePanel.js, DatasetExplorer.js)
**New Features**: Dataset exploration, pre-generated results visualization, model comparison
