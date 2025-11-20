# Art of Biasing LLM: Interactive Prompt Bias Analysis Tool

An educational tool that helps users understand how their prompts can contain bias, demonstrates different ways to bias prompts, and shows methods to normalize/de-bias them using **Vertex AI (Llama 3.3)** and **Gemini 2.5 Flash**.

## Features

1. **Graph-Based Visualization**: Interactive React Flow graph showing bias pathways
2. **Bias Detection**: Analyzes user prompts to identify potential biases
3. **LLM-Based Bias Injection**: Uses Llama 3.3 to generate biased prompt variations
4. **LLM-Based Debiasing**: Self-help debiasing using Llama 3.3 (BiasBuster method)
5. **Bias Evaluation**: Uses Gemini 2.5 Flash to evaluate bias in prompts
6. **Interactive Expansion**: Expand any node to further bias or debias
7. **Source References**: Visual display of bias definitions and research sources

## Architecture

- **Backend**: Flask API with Vertex AI REST API integration (Dockerized for Cloud Run)
- **Frontend**: React with ReactFlow for graph visualization
- **LLM Services**:
  - **Llama 3.3** (Vertex AI REST API): Prompt generation (bias injection, debiasing)
    - Model: `meta/llama-3.3-70b-instruct-maas`
    - Endpoint: `/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi/chat/completions`
  - **Gemini 2.5 Flash** (Vertex AI): Bias evaluation

## Project Structure

```
art-of-biasing-LLM/
├── backend/
│   ├── bias_detection.py      # Detect biases in prompts
│   ├── bias_injection.py       # Inject different types of biases
│   ├── debiasing.py           # Normalize/de-bias prompts
│   ├── vertex_llm_service.py  # Vertex AI LLM integration
│   └── api.py                 # API endpoints
├── frontend-react/            # React frontend with graph visualization
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   └── ...
│   └── package.json
├── Dockerfile                 # Docker configuration
├── cloudbuild.yaml            # Cloud Build configuration
└── requirements.txt           # Python dependencies
```

## Installation

### Backend

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file from example
   # Windows:
   setup_env.bat
   
   # Linux/Mac:
   chmod +x setup_env.sh
   ./setup_env.sh
   
   # Or manually copy:
   cp .env.example .env
   ```

4. **Edit .env file:**
   ```bash
   # Set your Google Cloud project ID
   GOOGLE_CLOUD_PROJECT=your-project-id
   GCP_LOCATION=us-central1
   ```

5. **Set up Google Cloud:**
   ```bash
   # Authenticate
   gcloud auth login
   gcloud auth application-default login
   
   # Set project (should match .env file)
   export GOOGLE_CLOUD_PROJECT=your-project-id
   ```

### Frontend

```bash
cd frontend-react
npm install
```

## Configuration

### Environment Variables

Create `.env` file:

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GCP_LOCATION=us-central1
```

For frontend, create `frontend-react/.env`:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

## Usage

### Local Development

1. **Verify environment setup:**
   ```bash
   python check_env.py
   ```

2. **Start backend:**
   ```bash
   cd backend
   python api.py
   ```
   The server will automatically load variables from `.env` file.

3. **Start frontend:**
   ```bash
   cd frontend-react
   npm start
   ```
   Frontend will use `REACT_APP_API_URL` from `frontend-react/.env`.

4. **Open browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Docker (Local Testing)

```bash
# Build image
docker build -t bias-analysis-tool .

# Run
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  -e GCP_LOCATION=us-central1 \
  bias-analysis-tool
```

### Google Cloud Run Deployment

See [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md) for detailed deployment instructions.

Quick deploy:

```bash
gcloud run deploy bias-analysis-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCP_LOCATION=us-central1
```

## How It Works

1. **User enters a starter prompt** in the React interface
2. **Graph expands** showing:
   - Original prompt (root node)
   - Biased versions (red nodes, rule-based and LLM-generated)
   - Debiased versions (green nodes, always highlighted)
3. **Interactive expansion**: Click any node to further bias or debias
4. **Bias evaluation**: Use Gemini 2.5 Flash to evaluate any prompt
5. **Source references**: View definitions and research sources for each bias type

## API Endpoints

- `POST /api/graph/expand` - Expand graph from starter prompt
- `POST /api/graph/evaluate` - Evaluate bias using Gemini 2.5 Flash
- `POST /api/graph/expand-node` - Expand specific node (bias/debias)
- `GET /api/health` - Health check

## Research Background

This tool is built on established bias frameworks and research:

### Core Frameworks
- **Neumann et al. (FAccT 2025)**: Representational vs. Allocative bias classification
- **BiasBuster (Echterhoff et al., 2024)**: Cognitive bias evaluation and self-help debiasing
- **BEATS Framework**: 29 comprehensive bias metrics
- **Sun & Kok (2025)**: Cognitive bias taxonomy and injection
- **Xu et al. (LREC 2024)**: Structural/template prompt bias
- **Lyu et al. (2025)**: Self-Adaptive Cognitive Debiasing (SACD)

See [BIAS_FRAMEWORK.md](BIAS_FRAMEWORK.md) for detailed framework documentation.

## Cost Estimation

For moderate usage (1000 users/month):
- **Vertex AI (Llama 3.3)**: ~$10-15/month
- **Gemini 2.5 Flash**: ~$5-10/month
- **Cloud Run**: ~$5-10/month
- **Total: ~$20-35/month**

## License

MIT
