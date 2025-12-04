# Bedrock Proxy API Integration

This directory contains a complete Python client for interacting with the AWS Bedrock Proxy API, providing access to multiple LLM families including Claude, Llama, Nova, Mistral, and DeepSeek.

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
pip install pydantic  # Optional, for structured output validation
```

### 2. Configure Credentials

Copy the example configuration file:

```bash
cp .env.bedrock.example .env.bedrock
```

Edit `.env.bedrock` and add your team credentials:

```env
BEDROCK_TEAM_ID=your_team_id_here
BEDROCK_API_TOKEN=your_api_token_here
```

### 3. Run Examples

```bash
cd backend
python bedrock_examples.py
```

### 4. Monitor Quota

```bash
python quota_monitor.py
```

## Files Overview

- **bedrock_client.py** - Main API client with comprehensive functionality
- **bedrock_examples.py** - 10+ usage examples covering all features
- **quota_monitor.py** - Budget tracking and monitoring utility
- **.env.bedrock.example** - Configuration template

## Available Models

### Anthropic Claude Series (Recommended)

| Model | ID | Best For |
|-------|-----|----------|
| Claude 3.5 Sonnet v2 | `us.anthropic.claude-3-5-sonnet-20241022-v2:0` | Balanced performance |
| Claude 3.5 Haiku | `us.anthropic.claude-3-5-haiku-20241022-v1:0` | Fast responses |
| Claude 3 Opus | `us.anthropic.claude-3-opus-20240229-v1:0` | Most powerful |
| Claude Sonnet 4.5 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Latest Sonnet |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | Latest Haiku |

### Meta Llama Series

| Model | ID | Size |
|-------|-----|------|
| Llama 3.2 90B | `us.meta.llama3-2-90b-instruct-v1:0` | Large |
| Llama 3.2 11B | `us.meta.llama3-2-11b-instruct-v1:0` | Balanced |
| Llama 3.2 3B | `us.meta.llama3-2-3b-instruct-v1:0` | Lightweight |
| Llama 4 Scout | `us.meta.llama4-scout-17b-instruct-v1:0` | Latest |

### Amazon Nova Series

| Model | ID | Best For |
|-------|-----|----------|
| Nova Premier | `us.amazon.nova-premier-v1:0` | Most powerful |
| Nova Pro | `us.amazon.nova-pro-v1:0` | Recommended |
| Nova Lite | `us.amazon.nova-lite-v1:0` | Fast |
| Nova Micro | `us.amazon.nova-micro-v1:0` | Ultra-fast |

### Mistral Series

| Model | ID |
|-------|-----|
| Pixtral Large | `us.mistral.pixtral-large-2502-v1:0` |
| Mistral Large | `mistral.mistral-large-2402-v1:0` |
| Mistral Small | `mistral.mistral-small-2402-v1:0` |

### DeepSeek Series

| Model | ID |
|-------|-----|
| DeepSeek R1 | `us.deepseek.r1-v1:0` |

## Usage Examples

### Basic Conversation

```python
from bedrock_client import BedrockClient, load_env_file

load_env_file(".env.bedrock")
client = BedrockClient()

response = client.chat("Hello, how are you?")
print(response)
```

### Multi-turn Conversation

```python
conversation = [
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
]

response = client.multi_turn_chat(conversation)
print(response)
```

### Using Different Models

```python
from bedrock_client import BedrockModels

# Use Claude 3.5 Haiku for fast responses
response = client.chat(
    "Quick question: what is 2+2?",
    model=BedrockModels.CLAUDE_3_5_HAIKU
)

# Use Nova Pro for balanced performance
response = client.chat(
    "Write a short poem",
    model=BedrockModels.NOVA_PRO
)
```

### Quota Monitoring

```python
messages = [{"role": "user", "content": "Hello"}]
response = client.invoke(messages)

# Check remaining quota
quota_info = client.get_quota_info(response)
print(f"Remaining budget: ${quota_info.remaining_budget:.2f}")
print(f"Usage: {quota_info.budget_usage_percent:.1f}%")
```

### Structured Output (JSON Schema)

```python
from bedrock_client import BedrockModels

person_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "city": {"type": "string"}
    },
    "required": ["name", "age", "city"]
}

result = client.structured_output(
    "Extract info: John is 30 years old and lives in New York.",
    schema=person_schema,
    model=BedrockModels.CLAUDE_3_5_SONNET_V2
)

print(result)
# Output: {"name": "John", "age": 30, "city": "New York"}
```

### Function/Tool Calling

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.function_calling(
    "What's the weather in San Francisco?",
    tools=tools,
    model=BedrockModels.CLAUDE_3_5_SONNET_V2
)

# Check for tool calls in response
for content in response["content"]:
    if content.get("type") == "tool_use":
        print(f"Tool: {content['name']}")
        print(f"Input: {content['input']}")
```

### Using Pydantic Models

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="Person's full name")
    age: int = Field(ge=0, le=150, description="Person's age")
    city: str = Field(description="City where person lives")

# Get schema from Pydantic model
schema = Person.model_json_schema()

result = client.structured_output(
    "Extract: Sarah is 28 and lives in London",
    schema=schema,
    model=BedrockModels.CLAUDE_3_5_SONNET_V2
)

# Validate with Pydantic
person = Person.model_validate(result)
print(f"{person.name}, {person.age}, {person.city}")
```

## Quota Management

### Check Quota Status

```python
from quota_monitor import QuotaMonitor

monitor = QuotaMonitor(client)
quota_info = monitor.check_quota()
monitor.print_quota_report()
```

### Log Quota Usage

```python
monitor.log_quota(quota_info, notes="After batch processing")
monitor.print_usage_stats()
```

### Budget Warnings

```python
if not monitor.should_continue(threshold_percent=90):
    print("WARNING: Budget critically low!")
```

### Estimate Remaining Requests

```python
remaining = monitor.estimate_requests_remaining(
    avg_tokens_per_request=1000,
    model_cost_per_1k_tokens=0.003
)
print(f"Estimated requests remaining: {remaining}")
```

## Error Handling

The client includes automatic retry logic for transient errors:

```python
# Retries up to 3 times by default
client = BedrockClient(max_retries=3, retry_delay=1.0)

try:
    response = client.chat("Hello")
except BedrockAPIError as e:
    print(f"Error {e.status_code}: {e.message}")
```

### Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Unauthorized | Check team_id and api_token |
| 403 | Forbidden | Verify model ID is allowed |
| 429 | Too Many Requests | Budget exhausted, check quota |
| 400 | Bad Request | Check request format |

## Best Practices

### 1. Choose the Right Model

- **Simple tasks**: Use Haiku or Nova Lite for speed and cost
- **Complex tasks**: Use Sonnet or Opus for better reasoning
- **Agent/Tool use**: Claude series has best tool calling support
- **Cost-sensitive**: Start with smaller models (Llama 3B, Nova Micro)

### 2. Manage Conversation History

```python
# Keep history concise
conversation = conversation[-10:]  # Only keep last 10 messages

# Remove redundant information
conversation = [msg for msg in conversation if msg["content"].strip()]
```

### 3. Optimize Token Usage

```python
# Limit output length
response = client.chat(message, max_tokens=200)

# Use concise prompts
message = "Capital of France?" instead of "Can you please tell me..."
```

### 4. Monitor Budget

```python
from quota_monitor import QuotaMonitor

monitor = QuotaMonitor(client)

# Check before expensive operations
if monitor.should_continue():
    process_large_batch()
else:
    print("Budget too low, stopping")
```

### 5. Handle Errors Gracefully

```python
try:
    response = client.chat(message)
except BedrockAPIError as e:
    if e.status_code == 429:
        print("Budget exhausted!")
    elif e.status_code == 403:
        print("Model not available, trying different model")
        response = client.chat(message, model=BedrockModels.CLAUDE_3_5_HAIKU)
    else:
        raise
```

## Advanced Features

### Custom Configuration

```python
client = BedrockClient(
    team_id="your_team_id",
    api_token="your_token",
    default_model=BedrockModels.NOVA_PRO,
    max_retries=5,
    retry_delay=2.0
)
```

### Direct API Access

```python
# Use invoke() for full control
response = client.invoke(
    messages=[{"role": "user", "content": "Hello"}],
    model=BedrockModels.CLAUDE_3_5_SONNET_V2,
    max_tokens=1024,
    temperature=0.7,  # Custom parameters
    top_p=0.9
)
```

### Batch Processing with Progress

```python
from quota_monitor import QuotaMonitor

monitor = QuotaMonitor(client)
results = []

for i, item in enumerate(items):
    # Check budget periodically
    if i % 10 == 0:
        quota = monitor.check_quota()
        print(f"Progress: {i}/{len(items)}, Budget: {quota.remaining_budget:.2f}")

        if not monitor.should_continue():
            print("Budget low, stopping early")
            break

    result = client.chat(item)
    results.append(result)
```

## Model Capabilities Comparison

### Tool/Function Calling Support

- ✅ **Full Support**: Claude series, DeepSeek, Amazon Nova
- ⚠️ **Prompt Engineering**: Llama, Mistral (no native API support)

### Structured Output Support

- ✅ **JSON Schema**: Claude series, DeepSeek, Amazon Nova
- ⚠️ **Prompt-based**: Llama, Mistral (request JSON in prompt)

## Troubleshooting

### Issue: "team_id and api_token are required"

**Solution**: Create `.env.bedrock` file with credentials

```bash
cp .env.bedrock.example .env.bedrock
# Edit .env.bedrock with your credentials
```

### Issue: "Model not allowed" (403)

**Solution**: Check available models list, some models may not be enabled

### Issue: "Budget exhausted" (429)

**Solution**: Check quota with `python quota_monitor.py`

### Issue: Structured output not working

**Solution**: Ensure you're using a model with tool calling support (Claude, Nova, DeepSeek)

## Support

For issues or questions:

1. Check the [examples](bedrock_examples.py) for usage patterns
2. Review the [API documentation PDF](../docs/Bedrock%20Proxy%20API%20-%20Hackathon%20Participant%20Guide.pdf)
3. Contact hackathon organizers for API access issues

## License

This client is part of the art-of-biasing-LLM project.
