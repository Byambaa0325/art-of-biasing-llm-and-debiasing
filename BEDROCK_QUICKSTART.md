# Bedrock API Quick Start Guide

This guide will help you get started with the Bedrock Proxy API integration in under 5 minutes.

## What Was Added

A complete Python client for calling multiple LLM providers (Claude, Llama, Nova, Mistral, DeepSeek) through the AWS Bedrock Proxy API.

## Setup (3 steps)

### 1. Configure Credentials

```bash
# Copy the template
cp .env.bedrock.example .env.bedrock

# Edit the file and add your credentials
# BEDROCK_TEAM_ID=your_team_id_here
# BEDROCK_API_TOKEN=your_api_token_here
```

### 2. Install Dependencies (if needed)

```bash
pip install requests pydantic
```

### 3. Test Connection

```bash
cd backend
python test_bedrock_connection.py
```

If successful, you'll see:
```
✓ All tests passed! Setup is complete.
```

## Basic Usage

### Simple Chat

```python
from bedrock_client import BedrockClient, load_env_file

load_env_file(".env.bedrock")
client = BedrockClient()

response = client.chat("What is the capital of France?")
print(response)
```

### Using Different Models

```python
from bedrock_client import BedrockModels

# Fast responses with Haiku
response = client.chat("Quick question", model=BedrockModels.CLAUDE_3_5_HAIKU)

# Better reasoning with Sonnet
response = client.chat("Complex analysis", model=BedrockModels.CLAUDE_3_5_SONNET_V2)

# Try other providers
response = client.chat("Hello", model=BedrockModels.NOVA_PRO)
response = client.chat("Hello", model=BedrockModels.LLAMA_3_2_11B)
```

### Check Your Budget

```bash
python quota_monitor.py
```

## Examples

Run the comprehensive examples:

```bash
python bedrock_examples.py
```

This includes 10+ examples covering:
- Basic conversations
- Multi-turn dialogues
- Different model families
- Structured output (JSON)
- Function calling
- Quota monitoring
- Error handling
- And more!

## File Structure

```
.env.bedrock.example          # Configuration template
backend/
  ├── bedrock_client.py       # Main API client
  ├── bedrock_examples.py     # 10+ usage examples
  ├── quota_monitor.py        # Budget tracking
  ├── test_bedrock_connection.py  # Test script
  └── BEDROCK_README.md       # Full documentation
docs/
  └── Bedrock Proxy API - Hackathon Participant Guide.pdf
```

## Available Models

### Anthropic Claude (Recommended)
- `CLAUDE_3_5_SONNET_V2` - Best balanced model
- `CLAUDE_3_5_HAIKU` - Fastest responses
- `CLAUDE_SONNET_4_5` - Latest Sonnet
- More in [BEDROCK_README.md](backend/BEDROCK_README.md)

### Meta Llama
- `LLAMA_3_2_90B`, `LLAMA_3_2_11B`, `LLAMA_3_2_3B`
- `LLAMA_4_SCOUT`, `LLAMA_4_MAVERICK`

### Amazon Nova
- `NOVA_PREMIER`, `NOVA_PRO`, `NOVA_LITE`, `NOVA_MICRO`

### Mistral
- `PIXTRAL_LARGE`, `MISTRAL_LARGE`, `MISTRAL_SMALL`

### DeepSeek
- `DEEPSEEK_R1`

## Key Features

✅ **Simple API** - Easy-to-use client with sensible defaults
✅ **Multiple Models** - 30+ models from 5 providers
✅ **Error Handling** - Automatic retries and clear error messages
✅ **Quota Tracking** - Monitor your budget in real-time
✅ **Structured Output** - Get JSON responses matching your schema
✅ **Function Calling** - Use tools/functions with Claude, Nova, DeepSeek
✅ **Well Documented** - Examples, docs, and inline comments

## Common Tasks

### Multi-turn Conversation

```python
conversation = [
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Nice to meet you!"},
    {"role": "user", "content": "What's my name?"}
]

response = client.multi_turn_chat(conversation)
```

### Get Structured JSON Output

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

result = client.structured_output(
    "Extract: John is 30 years old",
    schema=schema
)
# Returns: {"name": "John", "age": 30}
```

### Monitor Budget

```python
from quota_monitor import QuotaMonitor

monitor = QuotaMonitor(client)
quota = monitor.check_quota()
print(f"Remaining: ${quota.remaining_budget:.2f}")

# Log usage
monitor.log_quota(quota, notes="After processing batch")
```

## Troubleshooting

**Error: "team_id and api_token are required"**
- Create `.env.bedrock` file with your credentials

**Error: "Unauthorized" (401)**
- Check your `BEDROCK_TEAM_ID` and `BEDROCK_API_TOKEN`

**Error: "Budget exhausted" (429)**
- Run `python quota_monitor.py` to check remaining budget

**Structured output not working**
- Use Claude, Nova, or DeepSeek models (Llama/Mistral don't support this)

## Next Steps

1. **Read the full documentation**: [backend/BEDROCK_README.md](backend/BEDROCK_README.md)
2. **Try the examples**: `python bedrock_examples.py`
3. **Monitor your quota**: `python quota_monitor.py`
4. **Integrate with your project**: Import `bedrock_client` in your code

## Support

- Full docs: [backend/BEDROCK_README.md](backend/BEDROCK_README.md)
- API reference: [docs/Bedrock Proxy API - Hackathon Participant Guide.pdf](docs/Bedrock%20Proxy%20API%20-%20Hackathon%20Participant%20Guide.pdf)
- Contact hackathon organizers for API access issues

## Branch

This integration is on the `bedrock-api-integration` branch.

```bash
# View changes
git log -1

# Switch back to main
git checkout main

# Merge when ready
git merge bedrock-api-integration
```

---

**Happy Hacking!** 🚀
