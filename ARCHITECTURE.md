# Architecture Overview

## System Architecture

```
┌─────────────────┐
│  React Frontend │  (Graph Visualization)
│  (ReactFlow)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask API      │  (Backend)
│  (Cloud Run)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Llama   │ │ Gemini 2.5   │
│ 3.3     │ │ Flash        │
│ (Vertex)│ │ (Vertex)     │
└─────────┘ └──────────────┘
    │              │
    │              │
    ▼              ▼
┌─────────────────────────┐
│  Google Cloud Vertex AI │
└─────────────────────────┘
```

## Components

### Frontend (React)

- **Technology**: React 18, ReactFlow, Material-UI
- **Features**:
  - Interactive graph visualization
  - Node expansion (bias/debias)
  - Bias evaluation integration
  - Source definitions display
  - Always highlights debiased paths

### Backend (Flask)

- **Technology**: Flask, Python 3.11
- **Endpoints**:
  - `/api/graph/expand` - Create graph from prompt
  - `/api/graph/evaluate` - Evaluate bias (Gemini)
  - `/api/graph/expand-node` - Expand specific node
  - `/api/health` - Health check

### LLM Services

#### Llama 3.3 (Vertex AI)
- **Purpose**: Prompt generation
  - Bias injection
  - Self-help debiasing
  - Answer generation
- **Model**: `publishers/meta/models/llama-3.3-70b-instruct`
- **Location**: Vertex AI (us-central1)

#### Gemini 2.5 Flash (Vertex AI)
- **Purpose**: Bias evaluation
- **Model**: `publishers/google/models/gemini-2.0-flash-exp`
- **Location**: Vertex AI (us-central1)

## Data Flow

1. **User Input**: User enters starter prompt in React UI
2. **Graph Expansion**: 
   - Backend detects biases (rule-based)
   - Generates biased versions (rule-based + LLM)
   - Generates debiased versions (rule-based + LLM)
   - Returns graph structure (nodes + edges)
3. **Visualization**: ReactFlow renders graph
4. **Interaction**: 
   - User clicks node to expand
   - User clicks evaluate (Gemini 2.5 Flash)
   - User views source definitions
5. **Further Expansion**: User can bias/debias any node

## Graph Structure

```
Original Prompt (Root)
├── Biased Version 1 (Rule-based)
│   ├── Further Biased
│   └── Debiased
├── Biased Version 2 (LLM)
│   └── Debiased
├── Debiased Version 1 (Rule-based) [HIGHLIGHTED]
│   └── Further Debiased [HIGHLIGHTED]
└── Debiased Version 2 (LLM) [HIGHLIGHTED]
    └── Further Debiased [HIGHLIGHTED]
```

## Deployment

### Backend
- **Platform**: Google Cloud Run
- **Container**: Docker
- **Scaling**: Auto-scaling (0-10 instances)
- **Resources**: 2 CPU, 2GB RAM

### Frontend
- **Options**:
  - Firebase Hosting (recommended)
  - Cloud Storage + CDN
  - Netlify/Vercel

## Security

- **API Keys**: Stored in environment variables
- **CORS**: Configured for frontend domain
- **Authentication**: Optional (not included by default)
- **Rate Limiting**: Recommended for production

## Cost Optimization

1. **Caching**: Cache common prompt analyses
2. **Rate Limiting**: Prevent abuse
3. **Model Selection**: Use Gemini Flash for evaluation (cheaper)
4. **Auto-scaling**: Scale to zero when not in use

## Monitoring

- **Cloud Run Logs**: Application logs
- **Vertex AI Metrics**: API usage and costs
- **Error Tracking**: Cloud Error Reporting
- **Performance**: Cloud Trace

