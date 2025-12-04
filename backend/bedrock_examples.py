"""
Bedrock Proxy API Usage Examples
Demonstrates various use cases for the Bedrock API client.
"""

import json
from bedrock_client import BedrockClient, BedrockModels, load_env_file


def example_1_basic_conversation():
    """Example 1: Basic single-turn conversation"""
    print("\n=== Example 1: Basic Conversation ===")

    # Load credentials from .env.bedrock file
    load_env_file(".env.bedrock")

    # Initialize client
    client = BedrockClient()

    # Simple chat
    response_text = client.chat("Hello, how are you?")
    print(f"Response: {response_text}")


def example_2_multi_turn_conversation():
    """Example 2: Multi-turn conversation with memory"""
    print("\n=== Example 2: Multi-turn Conversation ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    # Build conversation history
    conversation = [
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Nice to meet you, Alice!"},
        {"role": "user", "content": "What's my name?"}
    ]

    response_text = client.multi_turn_chat(conversation)
    print(f"Response: {response_text}")


def example_3_different_models():
    """Example 3: Using different models"""
    print("\n=== Example 3: Different Models ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    models_to_test = [
        ("Claude 3.5 Sonnet", BedrockModels.CLAUDE_3_5_SONNET_V2),
        ("Claude 3.5 Haiku", BedrockModels.CLAUDE_3_5_HAIKU),
        ("Nova Pro", BedrockModels.NOVA_PRO),
        ("Llama 3.2 11B", BedrockModels.LLAMA_3_2_11B),
    ]

    question = "What is the capital of France? Answer in one word."

    for name, model in models_to_test:
        try:
            response = client.chat(question, model=model, max_tokens=50)
            print(f"{name}: {response}")
        except Exception as e:
            print(f"{name}: Error - {e}")


def example_4_quota_monitoring():
    """Example 4: Monitoring budget and quota"""
    print("\n=== Example 4: Quota Monitoring ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    # Make a request and check quota
    messages = [{"role": "user", "content": "Tell me a short joke"}]
    response = client.invoke(messages, max_tokens=200)

    # Extract quota info
    quota_info = client.get_quota_info(response)
    if quota_info:
        print(f"\n{quota_info}")
        print(f"LLM Cost: ${quota_info.llm_cost:.4f}")
        print(f"Total Cost: ${quota_info.total_cost:.4f}")
        print(f"Remaining Budget: ${quota_info.remaining_budget:.2f}")

        # Warning if budget is low
        if quota_info.budget_usage_percent > 80:
            print("\n⚠️  WARNING: Budget usage is above 80%!")
    else:
        print("Quota information not available in response")

    print(f"\nResponse: {response['content'][0]['text']}")


def example_5_structured_output():
    """Example 5: Getting structured JSON output"""
    print("\n=== Example 5: Structured Output ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    # Define schema for person information
    person_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "city": {"type": "string"},
            "occupation": {"type": "string"}
        },
        "required": ["name", "age", "city"]
    }

    # Extract structured information
    message = "Extract info: John is 30 years old, lives in New York and works as a software engineer."

    try:
        result = client.structured_output(
            message,
            schema=person_schema,
            schema_name="person_info",
            model=BedrockModels.CLAUDE_3_5_SONNET_V2
        )

        print(f"Structured output:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Structured output requires models with tool calling support (Claude, Nova, DeepSeek)")


def example_6_function_calling():
    """Example 6: Function/Tool calling"""
    print("\n=== Example 6: Function Calling ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    # Define tools
    tools = [
        {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "calculate",
            "description": "Perform a mathematical calculation",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    ]

    message = "What's the weather like in San Francisco and what's 125 * 48?"

    try:
        response = client.function_calling(
            message,
            tools=tools,
            model=BedrockModels.CLAUDE_3_5_SONNET_V2,
            max_tokens=1024
        )

        print("Response:")
        for content_block in response["content"]:
            if content_block.get("type") == "tool_use":
                tool_call = content_block
                print(f"\nTool: {tool_call['name']}")
                print(f"Input: {json.dumps(tool_call['input'], indent=2)}")
            elif "text" in content_block:
                print(f"\nText: {content_block['text']}")

    except Exception as e:
        print(f"Error: {e}")
        print("Note: Function calling requires models with tool support (Claude, Nova, DeepSeek)")


def example_7_pydantic_models():
    """Example 7: Using Pydantic models for structured output"""
    print("\n=== Example 7: Pydantic Models ===")

    try:
        from pydantic import BaseModel, Field
    except ImportError:
        print("Pydantic not installed. Install with: pip install pydantic")
        return

    load_env_file(".env.bedrock")
    client = BedrockClient()

    # Define Pydantic model
    class Person(BaseModel):
        """Person information"""
        name: str = Field(description="Person's full name")
        age: int = Field(ge=0, le=150, description="Person's age")
        city: str = Field(description="City where person lives")
        hobbies: list[str] = Field(default=[], description="List of hobbies")

    # Get JSON schema from Pydantic model
    json_schema = Person.model_json_schema()

    message = "Extract person info: Sarah is 28, lives in London, and enjoys reading, hiking, and photography."

    try:
        result = client.structured_output(
            message,
            schema=json_schema,
            schema_name="person_info",
            model=BedrockModels.CLAUDE_3_5_SONNET_V2
        )

        # Validate with Pydantic
        person = Person.model_validate(result)
        print(f"\nParsed Person:")
        print(f"  Name: {person.name}")
        print(f"  Age: {person.age}")
        print(f"  City: {person.city}")
        print(f"  Hobbies: {', '.join(person.hobbies)}")

    except Exception as e:
        print(f"Error: {e}")


def example_8_error_handling():
    """Example 8: Error handling and retries"""
    print("\n=== Example 8: Error Handling ===")

    load_env_file(".env.bedrock")

    # Test with invalid credentials
    try:
        bad_client = BedrockClient(team_id="invalid", api_token="invalid")
        bad_client.chat("Hello")
    except Exception as e:
        print(f"Expected error with bad credentials: {e}")

    # Test with invalid model
    try:
        client = BedrockClient()
        client.chat("Hello", model="invalid-model-id")
    except Exception as e:
        print(f"Expected error with invalid model: {e}")

    # Client has built-in retry logic for transient errors
    print("\nThe client automatically retries on transient errors (network issues, rate limits)")


def example_9_streaming_conversation():
    """Example 9: Simulating a conversation with context"""
    print("\n=== Example 9: Conversation with Context ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    conversation_history = []

    def add_message(role: str, content: str):
        """Add message to conversation history"""
        conversation_history.append({"role": role, "content": content})

    def chat(user_message: str) -> str:
        """Send message and get response"""
        add_message("user", user_message)
        response = client.multi_turn_chat(conversation_history, max_tokens=500)
        add_message("assistant", response)
        return response

    # Have a conversation
    print("\nUser: Tell me about Python programming")
    response = chat("Tell me about Python programming")
    print(f"Assistant: {response[:200]}...")

    print("\nUser: What are its main advantages?")
    response = chat("What are its main advantages?")
    print(f"Assistant: {response[:200]}...")

    print("\nUser: Can you give me a code example?")
    response = chat("Can you give me a code example?")
    print(f"Assistant: {response[:200]}...")


def example_10_batch_processing():
    """Example 10: Processing multiple queries efficiently"""
    print("\n=== Example 10: Batch Processing ===")

    load_env_file(".env.bedrock")
    client = BedrockClient()

    questions = [
        "What is 2+2?",
        "Name a color",
        "What day comes after Monday?",
        "What is the opposite of hot?",
    ]

    print("Processing multiple questions:")
    for i, question in enumerate(questions, 1):
        try:
            response = client.chat(question, max_tokens=50)
            print(f"{i}. Q: {question}")
            print(f"   A: {response}\n")
        except Exception as e:
            print(f"{i}. Q: {question}")
            print(f"   Error: {e}\n")


def main():
    """Run all examples"""
    examples = [
        ("Basic Conversation", example_1_basic_conversation),
        ("Multi-turn Conversation", example_2_multi_turn_conversation),
        ("Different Models", example_3_different_models),
        ("Quota Monitoring", example_4_quota_monitoring),
        ("Structured Output", example_5_structured_output),
        ("Function Calling", example_6_function_calling),
        ("Pydantic Models", example_7_pydantic_models),
        ("Error Handling", example_8_error_handling),
        ("Conversation Context", example_9_streaming_conversation),
        ("Batch Processing", example_10_batch_processing),
    ]

    print("=" * 60)
    print("Bedrock Proxy API Examples")
    print("=" * 60)

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n" + "=" * 60)

    # Run first few examples by default
    # To run all, uncomment the loop below
    for name, example_func in examples[:4]:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("Edit this file to run specific examples or add your own.")
    print("=" * 60)


if __name__ == "__main__":
    main()
