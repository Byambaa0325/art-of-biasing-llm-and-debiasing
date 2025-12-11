# Quick Start Guide - Explore Mode Integration

## Overview

The frontend has been successfully integrated with the Explore Mode functionality. This guide will help you quickly test the new features.

## Prerequisites

- Backend running on `http://localhost:5000`
- Model evaluation files in `data/model_evaluations/`
- Dataset file: `data/multiturn_emgsd_dataset.json`
- Node.js and npm installed

## Quick Test (5 minutes)

### Step 1: Test Backend Endpoints (2 minutes)

```bash
# Run the endpoint test script
python test_explore_endpoints.py
```

**Expected Output:**
```
✓ models_available
✓ dataset_stats
✓ dataset_entries
✓ filtered_entries
✓ model_result

Total: 5/5 tests passed
✓ All tests passed! Frontend integration should work.
```

**If tests fail:**
- Ensure backend is running: `python backend/api.py`
- Check that data files exist (see [Data Files](#data-files))

### Step 2: Start Frontend (1 minute)

```bash
cd frontend-react
npm install  # If first time
npm start
```

Frontend opens at `http://localhost:3000`

### Step 3: Test Explore Mode (2 minutes)

1. **Click "Explore Dataset"** toggle button on home screen
2. **Select a model** from dropdown (e.g., "llama3.1:8b")
3. **Click "Explore"** on any dataset entry
4. **Verify graph shows:**
   - Root node (purple) - Original question
   - Biased node (red) - Response after priming
   - Control node (gray) - Response without priming
5. **Click "Full Prompt"** on biased node to see conversation

## Detailed Testing (15 minutes)

### Test 1: Model Selection

**Objective:** Verify both Bedrock and Ollama models appear

**Steps:**
1. Go to home screen
2. Click "Explore Dataset" toggle
3. Open model dropdown

**Expected:**
- Bedrock models show "LIVE" badge (green)
- Ollama models show "STATIC" badge (gray)
- Models are grouped by type

**Screenshot checkpoint:**
```
Bedrock Models (Live + Explore)
  ✓ claude-3-5-haiku [LIVE]
  ✓ nova-pro [LIVE]
  ...

Ollama Models (Explore Only)
  ✓ llama3.1:8b [STATIC]
  ✓ mistral:7b [STATIC]
  ...
```

### Test 2: Mode Selection

**Objective:** Verify mode toggle works correctly

**Steps:**
1. Select a Bedrock model
2. Toggle between "Live Generation" and "Explore Dataset"
3. Select an Ollama model
4. Try to select "Live Generation"

**Expected:**
- Bedrock: Both modes available
- Ollama: "Live Generation" is disabled
- Warning message appears for Ollama

### Test 3: Dataset Filtering

**Objective:** Verify filters and pagination work

**Steps:**
1. In "Explore Dataset" mode
2. Change "Stereotype Type" to "profession"
3. Enter "bossy" in trait search
4. Change rows per page to 25
5. Navigate to page 2

**Expected:**
- Entries update based on filters
- Pagination shows correct total
- All entries match selected filters

### Test 4: Result Exploration

**Objective:** Verify pre-generated results display correctly

**Steps:**
1. Select model: "llama3.1:8b"
2. Click "Explore" on first entry
3. Wait for graph to load
4. Click on biased node (red)
5. Click "Full Prompt" button

**Expected:**
- Graph shows 3 nodes (root, biased, control)
- Biased node shows longer response
- Dialog shows multi-turn conversation:
  - Turn 1: Priming question + response
  - Turn 2: Original question + biased response

### Test 5: Custom Prompt Mode

**Objective:** Verify existing functionality still works

**Steps:**
1. Click "Custom Prompt" toggle
2. Enter: "What are the benefits of exercise?"
3. Click "Generate Bias Graph"

**Expected:**
- Live generation works as before
- Bias paths appear around center
- Clicking paths expands them

## Data Files

### Required Backend Files

```
data/
├── multiturn_emgsd_dataset.json          # Main dataset (1,158 entries)
└── model_evaluations/                     # Pre-generated results
    ├── evaluation_llama3_1_8b.json        # 800 entries
    ├── evaluation_llama3_2_3b.json        # 800 entries
    ├── evaluation_mistral_7b.json         # 800 entries
    ├── evaluation_gemma2_9b.json          # 806 entries
    ├── evaluation_qwen2_5_7b.json         # 800 entries
    ├── evaluation_deepseek-llm_7b.json    # 800 entries
    ├── evaluation_us_amazon_nova-pro-v1_0.json
    ├── evaluation_us_amazon_nova-lite-v1_0.json
    ├── evaluation_us_amazon_nova-micro-v1_0.json
    ├── evaluation_us_anthropic_claude-3-5-haiku-20241022-v1_0.json
    ├── evaluation_us_anthropic_claude-3-haiku-20240307-v1_0.json
    └── evaluation_us_meta_llama3-1-70b-instruct-v1_0.json
```

### Verify Data Files

```bash
# Check dataset
ls -lh data/multiturn_emgsd_dataset.json

# Check evaluation files
ls -lh data/model_evaluations/

# Count entries in dataset
python -c "import json; print(len(json.load(open('data/multiturn_emgsd_dataset.json'))))"
```

## Troubleshooting

### Backend Issues

**Problem:** `Connection refused` error

**Solution:**
```bash
# Start backend
cd backend
python api.py

# Or with specific port
python api.py --port 5000
```

**Problem:** `404 Not Found` on endpoints

**Solution:**
- Check backend logs
- Verify API routes are registered
- Ensure `model_results_client.py` exists

### Frontend Issues

**Problem:** Models dropdown is empty

**Solution:**
- Check browser console (F12)
- Verify `/api/models/available` returns data
- Check CORS settings if backend is remote

**Problem:** "No entries found" in dataset explorer

**Solution:**
- Verify dataset file exists
- Check `/api/dataset/entries` endpoint
- Ensure dataset is loaded in backend

**Problem:** Graph doesn't display

**Solution:**
- Check browser console for errors
- Verify React Flow CSS is loaded
- Check that nodes and edges have correct format

### Data Issues

**Problem:** Entry index errors

**Solution:**
- The frontend has fallback logic (uses array index)
- Check that evaluation files have matching entry_index
- Verify dataset and evaluation files are in sync

## Common Questions

### Q: Can I use live generation with Ollama models?

**A:** No, Ollama models only have pre-generated results. Live generation requires Bedrock API access.

### Q: How many models can I explore?

**A:** Currently 13+ models have pre-generated results:
- 8 Bedrock models
- 5+ Ollama models

### Q: Can I add more models?

**A:** Yes, generate evaluation files using the evaluation scripts and place them in `data/model_evaluations/`. The frontend will automatically detect them.

### Q: What bias types are available?

**A:** The dataset includes 8 bias types:
- confirmation_bias
- anchoring_bias
- availability_bias
- framing_bias
- stereotyping_bias
- bandwagon_bias
- sunk_cost_bias
- authority_bias

### Q: Can I export results?

**A:** Not yet implemented, but planned for future enhancement.

## Performance Tips

1. **Use pagination:** Keep rows per page at 10-25 for best performance
2. **Filter first:** Use filters to narrow down entries before exploring
3. **Close dialogs:** Close the "Full Prompt" dialog when done to free memory
4. **Refresh models:** The models list is cached; refresh page to reload

## Next Features (Roadmap)

- [ ] Side-by-side model comparison
- [ ] Export results to CSV/JSON
- [ ] Bias type filtering in dataset explorer
- [ ] Aggregate bias scores per model
- [ ] Search across all fields
- [ ] Favorites and history
- [ ] Batch exploration mode

## Support

### Documentation

- `EXPLORE_MODE_README.md` - Full feature documentation
- `FRONTEND_INTEGRATION_COMPLETE.md` - Technical integration details
- `INTEGRATION_FLOW.md` - Data flow and component hierarchy

### Testing

- `test_explore_endpoints.py` - Backend endpoint tests
- `test_explore_api.py` - API integration tests (if exists)

### Components

- `frontend-react/src/App.js` - Main application
- `frontend-react/src/components/ExplorePanel.js` - Explore panel
- `frontend-react/src/components/ModelSelector.js` - Model selection
- `frontend-react/src/components/DatasetExplorer.js` - Dataset browser

## Success Criteria

✅ All endpoint tests pass
✅ Models appear in dropdown
✅ Dataset entries load and filter correctly
✅ Graph displays with 3 nodes (root, biased, control)
✅ Full conversation shows in dialog
✅ Custom prompt mode still works
✅ No console errors in browser

---

**Last Updated:** December 10, 2025
**Integration Status:** Complete ✅
**Testing Status:** Ready for user testing 🚀
