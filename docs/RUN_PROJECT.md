# How to Run the Project

Quick guide to run the Bias Analysis Tool locally.

## Prerequisites Check

✅ Environment variables are set (`.env` file exists)
✅ Project ID: `lazy-jeopardy`

## Step 1: Activate Virtual Environment

**Windows:**
```powershell
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

## Step 2: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

## Step 3: Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

This will open a browser for authentication. This is required for Vertex AI API access.

## Step 4: Start Backend Server

Open a **new terminal window** and run:

```bash
cd backend
python api.py
```

You should see:
```
Starting Bias Analysis API server...
Environment: development
Debug mode: True

API endpoints:
  POST /api/graph/expand - Expand graph from starter prompt
  POST /api/graph/evaluate - Evaluate bias using Gemini 2.5 Flash
  POST /api/graph/expand-node - Expand specific node
  GET  /api/health - Health check

Server running on port 5000
```

✅ Backend is running at: http://localhost:5000

## Step 5: Start Frontend (React)

Open **another terminal window** and run:

```bash
cd frontend-react
npm install  # First time only
npm start
```

You should see:
```
Compiled successfully!

You can now view bias-analysis-tool in the browser.

  Local:            http://localhost:3000
```

✅ Frontend is running at: http://localhost:3000

## Step 6: Use the Application

1. Open browser: http://localhost:3000
2. Enter a prompt in the text field
3. Click "Generate Bias Graph"
4. Explore the interactive graph!

## Troubleshooting

### "Failed to get access token"
- Run: `gcloud auth application-default login`
- Make sure you're authenticated

### "Module not found"
- Activate virtual environment: `.\venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### "npm: command not found"
- Install Node.js from https://nodejs.org/
- Restart terminal after installation

### "Port 5000 already in use"
- Change port in `.env`: `PORT=5001`
- Or stop the process using port 5000

### Frontend can't connect to backend
- Check backend is running on port 5000
- Verify `frontend-react/.env` has: `REACT_APP_API_URL=http://localhost:5000/api`
- Restart frontend after changing `.env`

## Quick Commands Summary

**Terminal 1 (Backend):**
```bash
.\venv\Scripts\activate
cd backend
python api.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend-react
npm start
```

## Testing

### Test Backend API

```bash
# Health check
curl http://localhost:5000/api/health

# Test graph expansion
curl -X POST http://localhost:5000/api/graph/expand \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the best programming languages?"}'
```

### Test Frontend

1. Open http://localhost:3000
2. Enter a test prompt
3. Click "Generate Bias Graph"
4. Verify graph appears

