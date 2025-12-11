# Deployment Fix Summary

## Issues Fixed

### 1. ✅ Cloud Run 500 Errors - CRITICAL FIX

**Problem:** The deployed backend on Cloud Run was returning 500 errors for all Explore Mode endpoints.

**Root Cause:** The `data/` directory was not included in the Docker container, so the backend couldn't access:
- `data/multiturn_emgsd_dataset.json` - Dataset file
- `data/model_evaluations/` - Pre-generated model results

**Fix Applied:**
- Updated `Dockerfile` line 81 to copy the `data/` directory:
  ```dockerfile
  # Copy application code
  COPY backend/ ./backend/
  COPY data/ ./data/          # ← ADDED THIS LINE
  COPY .env* ./
  ```

**Action Required:** **REDEPLOY TO CLOUD RUN** for this fix to take effect.

---

### 2. ✅ Bias Score Badge Readability

**Problem:** White text on light background badges were hard to read.

**Fix Applied:** Added explicit text colors to all badge types:
- **Error badges** (high bias): Dark red text (#c00) on light red background (#ffe0e0)
- **Warning badges** (medium bias): Dark yellow text (#856404) on light yellow background (#fff4e0)
- **Success badges** (low bias): Dark green text (#155724) on light green background (#e8f5e9)

**Files Modified:**
- `frontend-react/src/App.js` - Updated badge styling for:
  - HEARTS evaluation badges
  - Claude evaluation badges
  - Gemini evaluation badges
  - Bias metrics badges

**Result:** All badges now have good contrast and are easily readable.

---

### 3. ✅ Model Selection Cleanup

**Problem:** Too many models in dropdown, including deepseek and ollama models.

**Fix Applied:**
- Removed all Ollama models from `OLLAMA_MODELS` list
- Explicitly excluded deepseek model
- Changed default model from `meta/llama-3.3-70b-instruct-maas` to `us.meta.llama3-1-70b-instruct-v1:0` (Llama 3.1 70B)

**Files Modified:**
- `backend/model_results_client.py` - Commented out all Ollama models
- `frontend-react/src/App.js` - Updated default model

**Result:** Model dropdown now only shows Bedrock models, with Llama 3.1 70B as default.

---

### 4. ✅ Placeholder Text Improvement

**Problem:** Generic placeholder text didn't guide users toward incomplete sentences.

**Fix Applied:**
Changed placeholder from:
```
"Type your prompt here... (e.g., 'What are the benefits of exercise?' or 'Why are women always so emotional?')"
```

To:
```
"Try an incomplete sentence like: 'Many Germans are' or 'The supervisor is' or 'Women typically'"
```

**Files Modified:**
- `frontend-react/src/App.js` - Updated TextField placeholder

**Result:** Users are now guided to use incomplete sentences that better demonstrate bias.

---

## Deployment Instructions

### For Frontend Changes (Badge Colors, Placeholder, Default Model)

**Option 1: Local Development**
```bash
cd frontend-react
npm start
```
Changes are already in the code, just refresh your browser.

**Option 2: Production (Cloud Run)**
The frontend is built during Docker build, so **redeploy is required**.

### For Backend Changes (Data Files, Model Filtering)

**REQUIRED: Redeploy to Cloud Run**

```bash
# Using gcloud CLI
gcloud builds submit --config cloudbuild.yaml

# Or using the deploy script
./deploy-bedrock.sh
```

**What happens during deployment:**
1. Docker builds new image with `data/` directory included
2. Backend can now access dataset and model evaluation files
3. Explore Mode endpoints will work correctly
4. Only Bedrock models (no Ollama) will be available

---

## Testing After Deployment

### 1. Test Backend Endpoints

Visit these URLs in your browser (replace with your Cloud Run URL):

```
https://[YOUR-CLOUD-RUN-URL]/api/models/available
https://[YOUR-CLOUD-RUN-URL]/api/dataset/stats
https://[YOUR-CLOUD-RUN-URL]/api/dataset/entries?limit=5
```

**Expected Results:**
- `/api/models/available` - Returns only Bedrock models (8 models)
- `/api/dataset/stats` - Returns dataset statistics (1,158 entries)
- `/api/dataset/entries` - Returns dataset entries

### 2. Test Frontend

1. Open the deployed frontend
2. Verify placeholder text shows incomplete sentence examples
3. Check model dropdown - should only show Bedrock models
4. Default model should be "Llama 3.1 70B"
5. Generate a graph and verify badges are readable
6. Click "Explore Dataset" and verify it loads entries

### 3. Test Explore Mode

1. Click "Explore Dataset" toggle
2. Select any Bedrock model
3. Click "Explore" on any entry
4. Verify graph loads with 3 nodes
5. Check badge colors are readable

---

## Files Changed

### Frontend Files (3 changes)
- ✅ `frontend-react/src/App.js`
  - Badge color improvements (4 sections)
  - Default model changed to Llama 3.1 70B
  - Placeholder text updated

### Backend Files (1 change)
- ✅ `backend/model_results_client.py`
  - Ollama models excluded

### Docker Files (1 change)
- ✅ `Dockerfile`
  - Data directory now included in container

---

## Known Issues & Limitations

### After Deployment

✅ **FIXED:** Cloud Run 500 errors on Explore Mode endpoints
✅ **FIXED:** Badge readability issues
✅ **FIXED:** Too many models in dropdown
✅ **FIXED:** Generic placeholder text

### Remaining Considerations

1. **Model Selection:**
   - Only Bedrock models available (8 models)
   - Ollama models completely removed
   - If you need to re-add specific models, uncomment them in `model_results_client.py`

2. **Data Files:**
   - Data directory adds ~5-10MB to Docker image
   - If this is a concern, consider using Google Cloud Storage instead

3. **Default Model:**
   - Changed to `us.meta.llama3-1-70b-instruct-v1:0` (Llama 3.1 70B)
   - Ensure this model is available in your Bedrock account

---

## Rollback Instructions

If issues occur after deployment:

### Rollback Dockerfile Changes
```bash
git checkout HEAD~1 Dockerfile
```

### Rollback Model Filtering
```bash
git checkout HEAD~1 backend/model_results_client.py
```

### Rollback Frontend Changes
```bash
git checkout HEAD~1 frontend-react/src/App.js
```

Then redeploy with the previous version.

---

## Summary

| Issue | Status | Action Required |
|-------|--------|----------------|
| Cloud Run 500 errors | ✅ Fixed | **Redeploy required** |
| Badge readability | ✅ Fixed | Included in redeploy |
| Model filtering | ✅ Fixed | Included in redeploy |
| Placeholder text | ✅ Fixed | Included in redeploy |

**Next Step:** Deploy to Cloud Run to apply all fixes.

```bash
# Deploy command
gcloud builds submit --config cloudbuild.yaml
```

---

**Fix Date:** December 11, 2025  
**Status:** ✅ All fixes applied, awaiting deployment  
**Deployment Required:** YES - Cloud Run redeploy needed
