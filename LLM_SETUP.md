# LLM Setup Guide

Quick guide to setting up LLM features for the Bias Analysis Tool.

## Quick Start

### Option 1: OpenAI API (Recommended for Demo)

1. **Get API Key:**
   - Sign up at https://platform.openai.com
   - Go to API Keys section
   - Create a new secret key

2. **Set Environment Variable:**
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-your-key-here"
   
   # Windows CMD
   set OPENAI_API_KEY=sk-your-key-here
   
   # Linux/Mac
   export OPENAI_API_KEY="sk-your-key-here"
   ```

3. **Or create .env file:**
   ```
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-3.5-turbo
   OPENAI_API_KEY=sk-your-key-here
   ```

4. **Test:**
   ```bash
   python -c "from backend.llm_service import get_llm_service; print(get_llm_service().generate('Hello'))"
   ```

### Option 2: Local Ollama (Free)

1. **Install Ollama:**
   - Download from https://ollama.ai
   - Install and start the service

2. **Pull a Model:**
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   ```

3. **Set Environment Variables:**
   ```bash
   export LLM_PROVIDER=ollama
   export LLM_MODEL=llama2
   export OLLAMA_URL=http://localhost:11434
   ```

4. **Test:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

## API Endpoints

Once LLM is configured, these endpoints become available:

### LLM-Based Debiasing
```bash
POST /api/llm/debias
{
  "prompt": "Why are teenagers so bad at making decisions?"
}
```

### LLM-Based Bias Injection
```bash
POST /api/llm/inject
{
  "prompt": "What are the best programming languages?",
  "bias_type": "confirmation"
}
```

### Answer Comparison
```bash
POST /api/llm/compare
{
  "original_prompt": "What are good programming languages?",
  "modified_prompts": [
    {
      "prompt": "What are the best programming languages for men?",
      "type": "biased",
      "label": "Biased Version"
    },
    {
      "prompt": "What programming languages would you recommend?",
      "type": "debiased",
      "label": "Debiased Version"
    }
  ]
}
```

### Enhanced Analysis (with LLM)
```bash
POST /api/analyze
{
  "prompt": "Your prompt here",
  "use_llm": true,
  "generate_answers": true
}
```

## Cost Considerations

### OpenAI API
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **GPT-4**: ~$0.03 per 1K tokens
- **Estimated monthly cost** for demo: $5-20 (depending on usage)

### Ollama (Local)
- **Free** to run
- Requires server with:
  - CPU: 8+ cores recommended
  - RAM: 8GB+ (16GB+ for larger models)
  - GPU: Optional but recommended (8GB+ VRAM)

## Troubleshooting

### "LLM service not available"
- Check that environment variables are set correctly
- For OpenAI: Verify API key is valid
- For Ollama: Make sure Ollama is running (`ollama serve`)

### "OpenAI API error"
- Check API key is correct
- Verify you have credits/quota
- Check rate limits

### "Ollama API error"
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_URL is correct
- Verify model is pulled: `ollama list`

## Testing LLM Integration

```python
# Test script
from backend.llm_service import get_llm_service

try:
    llm = get_llm_service()
    print("✓ LLM service initialized")
    
    # Test debiasing
    result = llm.debias_self_help("Why are teenagers so bad?")
    print("✓ Debiasing works:", result['debiased_prompt'][:50])
    
    # Test answer generation
    answer = llm.generate_answer("What is Python?")
    print("✓ Answer generation works:", answer[:50])
    
except Exception as e:
    print("✗ Error:", str(e))
```

## Next Steps

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment options.

