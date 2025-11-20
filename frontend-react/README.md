# Bias Analysis Frontend (React)

React frontend with graph visualization for the Bias Analysis Tool.

## Features

- **Interactive Graph**: ReactFlow-based visualization of bias pathways
- **Node Expansion**: Click nodes to further bias or debias
- **Bias Evaluation**: Evaluate prompts using Gemini 2.5 Flash
- **Source References**: View research sources and definitions
- **Highlighted Debiasing**: Debiased paths are always highlighted in green

## Installation

```bash
npm install
```

## Configuration

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

For production, set to your Cloud Run URL:

```env
REACT_APP_API_URL=https://your-cloud-run-url/api
```

## Development

```bash
npm start
```

Opens http://localhost:3000

## Build for Production

```bash
npm run build
```

Outputs to `build/` directory.

## Deployment

### Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Select build directory
firebase deploy
```

### Cloud Storage + CDN

```bash
npm run build
gsutil -m cp -r build/* gs://your-bucket-name/
```

### Netlify/Vercel

Connect your repository and set build command to `npm run build`.

## Usage

1. Enter a starter prompt
2. Click "Generate Bias Graph" to see expansion
3. Click nodes to:
   - **Further debias** (green + button)
   - **Add bias** (red - button)
   - **Evaluate** (assessment icon) - Uses Gemini 2.5 Flash
   - **View details** (info icon)
4. Debiased paths are always highlighted in green

