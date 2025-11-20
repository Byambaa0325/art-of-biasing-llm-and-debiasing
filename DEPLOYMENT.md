# Deployment Guide for Public Demo

This guide covers options for deploying the Bias Analysis Tool with LLM integration for a public demo.

## LLM Provider Options

### Option 1: OpenAI API (Recommended for Public Demo)

**Pros:**
- ✅ Easiest to set up
- ✅ Reliable and fast
- ✅ No infrastructure management
- ✅ Pay-per-use pricing
- ✅ High-quality models (GPT-3.5, GPT-4)

**Cons:**
- ❌ Costs money (but reasonable for demos)
- ❌ Requires API key management

**Setup:**
1. Get OpenAI API key from https://platform.openai.com
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. Configure in `.env`:
   ```
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-3.5-turbo
   OPENAI_API_KEY=sk-...
   ```

**Cost Estimate:**
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- For a demo with 100 users/day: ~$5-10/month
- GPT-4: ~$0.03 per 1K tokens (more expensive)

### Option 2: Local Models with Ollama (Cost-Effective)

**Pros:**
- ✅ Free to run
- ✅ No API costs
- ✅ Full control
- ✅ Privacy (data stays local)

**Cons:**
- ❌ Requires server with GPU (or CPU, slower)
- ❌ More setup complexity
- ❌ Need to manage infrastructure

**Setup:**
1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   ```
3. Set environment variables:
   ```
   LLM_PROVIDER=ollama
   LLM_MODEL=llama2
   OLLAMA_URL=http://localhost:11434
   ```

**Server Requirements:**
- CPU: 8+ cores recommended
- RAM: 8GB+ (16GB+ for larger models)
- GPU: Optional but recommended (NVIDIA GPU with 8GB+ VRAM)
- Storage: 4GB+ per model

### Option 3: Hybrid Approach (Recommended for Production)

Use OpenAI for public demo, with fallback to Ollama for cost savings:

```python
# In llm_service.py, add fallback logic
try:
    service = LLMService(provider="openai")
except:
    service = LLMService(provider="ollama")  # Fallback
```

## Deployment Platforms

### Option A: Cloud Platforms (Recommended)

#### 1. **Heroku** (Easiest)
- Free tier available
- Easy deployment
- Automatic scaling
- **Cost:** Free tier or $7/month+

**Deploy:**
```bash
heroku create bias-analysis-demo
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

#### 2. **Railway** (Good for Demos)
- Simple deployment
- Pay-per-use
- **Cost:** ~$5-20/month

#### 3. **Render** (Free Tier Available)
- Free tier with limitations
- Easy setup
- **Cost:** Free or $7/month+

#### 4. **AWS/GCP/Azure**
- More control
- Better for production
- **Cost:** Varies (can be $10-50/month)

### Option B: Self-Hosted VPS

**Recommended Providers:**
- DigitalOcean: $6-12/month
- Linode: $5-10/month
- Vultr: $6-12/month

**Setup:**
1. Get VPS with Ubuntu
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```
3. Set up application
4. Use systemd for service management
5. Configure Nginx as reverse proxy

## Environment Configuration

Create `.env` file:

```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your-key-here

# Or for Ollama:
# LLM_PROVIDER=ollama
# LLM_MODEL=llama2
# OLLAMA_URL=http://localhost:11434

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Optional: Rate limiting
RATE_LIMIT_PER_MINUTE=10
```

## Security Considerations

1. **API Key Protection:**
   - Never commit API keys to git
   - Use environment variables
   - Rotate keys regularly

2. **Rate Limiting:**
   - Implement rate limiting for public demo
   - Prevent abuse and control costs

3. **CORS:**
   - Configure CORS properly for your domain
   - Don't allow all origins in production

4. **Input Validation:**
   - Validate and sanitize user inputs
   - Limit prompt length

## Cost Optimization

1. **Use GPT-3.5-turbo** instead of GPT-4 for demos
2. **Cache responses** for common prompts
3. **Implement rate limiting** to prevent abuse
4. **Use local models** (Ollama) for development/testing
5. **Monitor usage** and set spending limits

## Monitoring

1. **API Usage:**
   - Monitor OpenAI API usage dashboard
   - Set up alerts for high usage

2. **Application Monitoring:**
   - Use services like Sentry for error tracking
   - Monitor response times

3. **Logging:**
   - Log API calls (without sensitive data)
   - Track usage patterns

## Recommended Setup for Public Demo

**For Quick Demo:**
1. Use OpenAI API (GPT-3.5-turbo)
2. Deploy to Render or Railway
3. Set rate limiting (10 requests/minute)
4. Monitor costs daily

**For Production:**
1. Use OpenAI API with fallback to Ollama
2. Deploy to AWS/GCP with auto-scaling
3. Implement caching
4. Set up monitoring and alerts
5. Use CDN for frontend

## Example Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash
# Deploy script for public demo

# Set environment variables
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-3.5-turbo
export OPENAI_API_KEY=$1

# Install dependencies
pip install -r requirements.txt

# Run migrations/setup if needed
# python setup.py

# Start server
gunicorn -w 2 -b 0.0.0.0:5000 backend.api:app
```

## Frontend Deployment

The frontend can be:
1. **Static hosting:** GitHub Pages, Netlify, Vercel (free)
2. **Same server:** Serve from Flask or Nginx
3. **CDN:** CloudFlare, AWS CloudFront

## Quick Start for Demo

1. **Get OpenAI API key**
2. **Deploy backend to Railway/Render:**
   ```bash
   # Set environment variables in platform dashboard
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```
3. **Deploy frontend to Netlify/Vercel:**
   - Update `API_BASE_URL` in `frontend/app.js` to your backend URL
   - Deploy static files
4. **Test and monitor**

## Troubleshooting

- **API errors:** Check API key and quota
- **Slow responses:** Consider using faster model or caching
- **High costs:** Implement rate limiting and monitor usage
- **CORS issues:** Configure CORS for your frontend domain

