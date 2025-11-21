# Model Selection Feature - Multi-Provider LLM Support

## Overview

Implemented dynamic model selection allowing users to choose from multiple LLM providers available through Vertex AI:
- **Meta** (Llama 3.1, 3.2, 3.3 models)
- **Mistral AI** (Mistral Medium 3, Mistral Small 3.1)
- **Google** (Gemini models for evaluation)

Users can now switch between different models for bias injection and debiasing operations.

## Architecture

### Backend Components

#### 1. Model Configuration (`backend/model_config.py`)

Centralized configuration for all available models:

```python
AVAILABLE_MODELS = {
    # Meta Llama 3.3
    'meta/llama-3.3-70b-instruct-maas': {
        'name': 'Llama 3.3 70B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Latest Llama 3.3, excellent for reasoning',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },

    # Meta Llama 3.2
    'meta/llama-3.2-90b-vision-instruct-maas': {
        'name': 'Llama 3.2 90B Vision',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Llama 3.2 with vision and strong reasoning',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },

    # Mistral AI
    'mistral-medium-2505': {
        'name': 'Mistral Medium 3',
        'provider': 'Mistral AI',
        'category': 'both',
        'description': 'Balanced performance for most tasks',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },

    # ... more models
}
```

**Key Features:**
- Model metadata (name, provider, description, context window)
- Endpoint type routing (OpenAPI vs Vertex SDK)
- Category classification (generation, evaluation, or both)
- Helper functions for UI and API

#### 2. LLM Service Updates (`backend/vertex_llm_service.py`)

**Enhanced `generate()` method:**
```python
def generate(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    model_override: Optional[str] = None  # NEW parameter
) -> str:
    """Generate text using specified model."""
    model_id = model_override or self.llama_model_name

    # Validate and route to appropriate endpoint
    if endpoint_type == 'openapi':
        return self._generate_openapi(...)
    elif endpoint_type == 'vertex_sdk':
        return self._generate_vertex_sdk(...)
```

**Two Generation Methods:**

1. **OpenAPI Endpoint** (for Llama models):
   - Uses REST API chat completions endpoint
   - Message-based conversation format
   - Direct HTTP requests with Bearer token

2. **Vertex SDK** (for Claude, Mistral, Gemini):
   - Uses Vertex AI Python SDK
   - Publisher-based model paths
   - Unified GenerativeModel interface

**Model Path Routing:**
```python
if 'mistral' in model_id:
    model_path = f"publishers/mistralai/models/{model_id}"
elif 'gemini' in model_id:
    model_path = f"publishers/google/models/{model_id}"
```

**Updated Methods:**
- `inject_bias_llm(prompt, bias_type, model_id=None)`
- `debias_self_help(prompt, method='auto', model_id=None)`
- Returns include `model_id` and formatted `source` with model name

#### 3. API Endpoints (`backend/api.py`)

**New Endpoint: GET `/api/models`**
```python
@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models for generation."""
    return jsonify({
        'generation_models': get_generation_models(),
        'evaluation_models': get_evaluation_models()
    })
```

**Response Format:**
```json
{
  "generation_models": [
    {
      "id": "meta/llama-3.3-70b-instruct-maas",
      "name": "Llama 3.3 70B",
      "provider": "Meta",
      "description": "Meta's latest Llama model, excellent for reasoning"
    },
    {
      "id": "claude-3-5-sonnet-v2@20241022",
      "name": "Claude 3.5 Sonnet v2",
      "provider": "Anthropic",
      "description": "Latest Claude with enhanced reasoning"
    }
    // ... more models
  ],
  "evaluation_models": [...]
}
```

**Updated: POST `/api/graph/expand-node`**
```python
parent_id = data.get('node_id', '')
parent_prompt = data.get('prompt', '')
action = data.get('action', 'debias')
bias_type = data.get('bias_type')
debias_method = data.get('method')
model_id = data.get('model_id')  # NEW parameter

# Pass to LLM methods
if action == 'bias':
    transformation = llm.inject_bias_llm(parent_prompt, bias_type, model_id=model_id)
else:
    transformation = llm.debias_self_help(parent_prompt, method=debias_method, model_id=model_id)
```

### Frontend Components

#### 1. State Management (`frontend-react/src/App.js`)

**New State Variables:**
```javascript
const [availableModels, setAvailableModels] = useState([]);
const [selectedModel, setSelectedModel] = useState('meta/llama-3.3-70b-instruct-maas');
```

**Fetch Models on Mount:**
```javascript
useEffect(() => {
  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.generation_models || []);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    }
  };
  fetchModels();
}, []);
```

#### 2. Model Selector UI

**Location:** Input screen, before prompt TextField

```jsx
<FormControl fullWidth sx={{ mb: 3 }}>
  <InputLabel id="model-select-label">LLM Model</InputLabel>
  <Select
    labelId="model-select-label"
    value={selectedModel}
    label="LLM Model"
    onChange={(e) => setSelectedModel(e.target.value)}
  >
    {availableModels.map((model) => (
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
    ))}
  </Select>
</FormControl>
```

**Visual Design:**
- Dropdown with model name in bold
- Provider and description as subtitle
- Full-width, matches prompt TextField style
- Placed above prompt input for visibility

#### 3. API Integration

**Updated `handleExpandPath`:**
```javascript
const payload = {
  node_id: parentNodeId,
  prompt: parentPrompt,
  action: pathData.type,
  model_id: selectedModel,  // Include selected model
};

if (pathData.type === 'bias') {
  payload.bias_type = pathData.bias_type;
} else {
  payload.method = pathData.method;
}

const response = await axios.post(`${API_BASE_URL}/graph/expand-node`, payload);
```

## Available Models

### Meta Llama 3.3 Models (OpenAPI Endpoint)

| Model ID | Name | Context | Description |
|----------|------|---------|-------------|
| `meta/llama-3.3-70b-instruct-maas` | Llama 3.3 70B | 128K | Latest Llama, excellent reasoning (Default) |

### Meta Llama 3.2 Models (OpenAPI Endpoint)

| Model ID | Name | Context | Description |
|----------|------|---------|-------------|
| `meta/llama-3.2-90b-vision-instruct-maas` | Llama 3.2 90B Vision | 128K | Llama 3.2 with vision and strong reasoning |
| `meta/llama-3.2-11b-vision-instruct-maas` | Llama 3.2 11B Vision | 128K | Compact with vision, fast and efficient |

### Meta Llama 3.1 Models (OpenAPI Endpoint)

| Model ID | Name | Context | Description |
|----------|------|---------|-------------|
| `meta/llama-3.1-405b-instruct-maas` | Llama 3.1 405B | 128K | Largest Llama, exceptional performance |
| `meta/llama-3.1-70b-instruct-maas` | Llama 3.1 70B | 128K | Balanced performance and speed |

### Mistral AI Models (Vertex SDK)

| Model ID | Name | Context | Description |
|----------|------|---------|-------------|
| `mistral-medium-2505` | Mistral Medium 3 | 128K | Balanced performance for most tasks |
| `mistral-small-2501` | Mistral Small 3.1 | 128K | Fast and cost-effective |

### Google Gemini Models (Vertex SDK)

| Model ID | Name | Context | Description |
|----------|------|---------|-------------|
| `gemini-2.0-flash-exp` | Gemini 2.0 Flash | 1M | Latest flash, fast and capable |
| `gemini-1.5-pro-002` | Gemini 1.5 Pro | 2M | Pro model with massive context |
| `gemini-1.5-flash-002` | Gemini 1.5 Flash | 1M | Fast for quick tasks |

## User Flow

### 1. Initial Load
```
User opens app
    ↓
Frontend fetches available models from /api/models
    ↓
Model selector populated with options
    ↓
Default: Llama 3.3 70B selected
```

### 2. Model Selection
```
User clicks model dropdown
    ↓
Sees list of models grouped by provider
    ↓
Each option shows:
  - Model name (bold)
  - Provider - Description (subtitle)
    ↓
User selects a model (e.g., Llama 3.2 90B Vision)
    ↓
Selection stored in state
```

### 3. Bias Injection/Debiasing
```
User enters prompt → clicks potential node
    ↓
Frontend sends request with model_id
    ↓
Backend routes to appropriate endpoint:
  - OpenAPI for Llama models
  - Vertex SDK for Mistral/Gemini
    ↓
Model generates biased/debiased prompt
    ↓
Response includes model info in metadata
    ↓
Node displays transformation with model source
```

## Benefits

### ✅ Model Diversity
- Access to 10+ models from 3 major providers
- Different strengths for different bias types
- Experiment with various approaches

### ✅ Performance Optimization
- Choose faster models (Small 3.1, 11B) for quick iterations
- Use powerful models (405B, 90B) for complex biases
- Balance cost and quality

### ✅ Provider Flexibility
- Not locked into single provider
- Leverage each provider's strengths:
  - Meta: Open models, good balance, vision capabilities
  - Mistral: European alternative, balanced performance
  - Google: Massive context, multimodal

### ✅ Easy Switching
- Single dropdown, no configuration
- Instant model switching
- Persistent selection during session

## Technical Details

### Endpoint Type Routing

**OpenAPI (Llama):**
```python
POST https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/endpoints/openapi/chat/completions

{
  "model": "meta/llama-3.3-70b-instruct-maas",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Vertex SDK (Mistral/Gemini):**
```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("publishers/mistralai/models/mistral-medium-2505")
response = model.generate_content(
    prompt,
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 1000
    }
)
```

### Model Metadata Flow

**Backend transformation result:**
```python
{
    'biased_prompt': '...',
    'bias_added': 'Confirmation Bias',
    'bias_type': 'confirmation_bias',
    'source': 'LLM-based (Llama 3.3 70B)',  # Formatted with model name
    'model_id': 'meta/llama-3.3-70b-instruct-maas',
    'explanation': '...',
    'framework': '...'
}
```

**Displayed in node:**
- Transformation label shows bias type
- Source shows model used
- Users can track which model generated each transformation

### Error Handling

**Invalid Model:**
```python
if not is_valid_model(model_id):
    raise ValueError(f"Invalid model ID: {model_id}")
```

**Model Not Available:**
```python
if not VERTEX_AI_SDK_AVAILABLE:
    raise Exception("Vertex AI SDK not available...")
```

**Fallback to Default:**
- If model_id not provided, uses default Llama 3.3
- If models endpoint fails, shows default option in dropdown

## Testing

### Test 1: Model Selection
1. Open app input screen
2. **Verify**: Model dropdown shows "LLM Model" label
3. Click dropdown
4. **Verify**: See list of models with names, providers, descriptions
5. Select "Llama 3.2 90B Vision"
6. **Verify**: Dropdown shows selected model

### Test 2: Bias Injection with Different Models
1. Select "Llama 3.3 70B"
2. Enter prompt, generate graph
3. Click bias potential node
4. **Verify**: New node shows "Source: LLM-based (Llama 3.3 70B)"
5. Return to input
6. Select "Mistral Medium 3"
7. Enter prompt, generate graph
8. Click bias potential node
9. **Verify**: New node shows "Source: LLM-based (Mistral Medium 3)"

### Test 3: Model Persistence
1. Select "Mistral Medium 3"
2. Generate graph
3. Expand multiple nodes
4. **Verify**: All use Mistral Medium 3
5. Change to "Llama 3.1 405B"
6. Expand new nodes
7. **Verify**: New nodes use Llama 3.1 405B

### Test 4: API Fallback
1. Disconnect backend
2. Open app
3. **Verify**: Dropdown shows "Llama 3.3 70B (Default) - Loading other models..."
4. Still functional with default selection

## Configuration

### Adding New Models

1. **Update `model_config.py`:**
```python
AVAILABLE_MODELS['new-model-id'] = {
    'name': 'Model Name',
    'provider': 'Provider Name',
    'category': 'both',  # or 'generation' or 'evaluation'
    'description': 'Brief description',
    'context_window': 100000,
    'recommended_for': ['generation', 'evaluation'],
    'endpoint_type': 'vertex_sdk'  # or 'openapi'
}
```

2. **Update model path routing (if new provider):**
```python
# In vertex_llm_service.py _generate_vertex_sdk()
elif 'newprovider' in model_id:
    model_path = f"publishers/newprovider/models/{model_id}"
```

3. **Test with real API call**

### Environment Variables

```bash
# .env file
GOOGLE_CLOUD_PROJECT=your-project-id
GCP_LOCATION=us-central1
LLAMA_MODEL=meta/llama-3.3-70b-instruct-maas  # Default generation model
GEMINI_MODEL=gemini-2.0-flash-exp  # Default evaluation model
```

## Performance Considerations

### Model Speed Comparison

**Fast** (< 2s response):
- Gemini Flash models
- Mistral Small 3.1
- Llama 3.2 11B Vision

**Medium** (2-5s):
- Llama 3.3 70B
- Llama 3.2 90B Vision
- Mistral Medium 3

**Slow** (5-10s):
- Llama 3.1 405B
- Gemini Pro (large context)

### Cost Optimization

Models are priced differently. For production:
- Use fast/cheap models for exploration
- Use powerful models for final analysis
- Consider caching results

### Context Window Usage

- Most prompts: < 1K tokens (all models fine)
- Long conversations: Use models with larger context
- Complex bias chains: Gemini (1M-2M context) or Llama (128K context)

## Future Enhancements

### 1. Model-Specific Settings
```jsx
<ModelSettingsDialog>
  <TextField label="Temperature" />
  <TextField label="Max Tokens" />
  <Switch label="Streaming" />
</ModelSettingsDialog>
```

### 2. Model Performance Tracking
```javascript
{
  model_id: 'meta/llama-3.3-70b-instruct-maas',
  avg_response_time: '3.2s',
  success_rate: '98.5%',
  bias_quality_score: 4.7
}
```

### 3. Provider Grouping in UI
```
Meta
  ├─ Llama 3.3 70B
  ├─ Llama 3.2 90B Vision
  ├─ Llama 3.1 405B
  └─ Llama 3.1 70B
Mistral AI
  ├─ Mistral Medium 3
  └─ Mistral Small 3.1
Google
  └─ Gemini 2.0 Flash
```

### 4. Favorites/Presets
```javascript
const favoriteModels = [
  'meta/llama-3.3-70b-instruct-maas',
  'mistral-medium-2505'
];
```

### 5. A/B Comparison
```
Generate with Model A and Model B side-by-side
Compare bias injection quality
Show differences in approach
```

## Files Modified

### Backend
- **Created:** `backend/model_config.py` (267 lines)
- **Modified:** `backend/vertex_llm_service.py`
  - Lines 158-307: Enhanced `generate()` with routing
  - Lines 309-410: Updated `inject_bias_llm()` with model_id
  - Lines 444-560: Updated `debias_self_help()` with model_id
  - Lines 412-442, 562-594: Updated fallback methods
- **Modified:** `backend/api.py`
  - Lines 422-444: New `/api/models` endpoint
  - Lines 672, 687-688, 697-698: Updated expand-node with model_id

### Frontend
- **Modified:** `frontend-react/src/App.js`
  - Lines 26-29: Added FormControl, Select, MenuItem imports
  - Lines 53-54: Added model state variables
  - Lines 62-76: Fetch models on mount
  - Lines 402: Pass model_id in API payload
  - Lines 744-779: Model selector UI component

---

**Status**: ✅ Model selection implemented - Users can switch between 10+ models from Meta (Llama 3.1, 3.2, 3.3), Mistral AI (Medium 3, Small 3.1), and Google (Gemini)
