"""
Simple test script to verify Bedrock API connection
Run this to test your setup after configuring credentials.
"""

import sys
from bedrock_client import BedrockClient, BedrockModels, load_env_file, BedrockAPIError


def test_connection():
    """Test basic connection to Bedrock API"""
    print("=" * 60)
    print("Bedrock API Connection Test")
    print("=" * 60)

    # Step 1: Load credentials
    print("\n[1/4] Loading credentials from .env.bedrock...")
    try:
        load_env_file(".env.bedrock")
        print("✓ Credentials loaded")
    except Exception as e:
        print(f"✗ Error loading credentials: {e}")
        print("\nPlease create .env.bedrock file with your credentials:")
        print("  1. Copy .env.bedrock.example to .env.bedrock")
        print("  2. Edit .env.bedrock and add your BEDROCK_TEAM_ID and BEDROCK_API_TOKEN")
        return False

    # Step 2: Initialize client
    print("\n[2/4] Initializing Bedrock client...")
    try:
        client = BedrockClient()
        print("✓ Client initialized")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nMake sure .env.bedrock contains:")
        print("  BEDROCK_TEAM_ID=your_team_id")
        print("  BEDROCK_API_TOKEN=your_api_token")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    # Step 3: Test API call
    print("\n[3/4] Testing API call...")
    try:
        response = client.chat(
            "Respond with just the word 'success' and nothing else.",
            model=BedrockModels.CLAUDE_3_5_HAIKU,
            max_tokens=50
        )
        print(f"✓ API call successful")
        print(f"  Response: {response[:100]}")
    except BedrockAPIError as e:
        print(f"✗ API Error [{e.status_code}]: {e.message}")
        if e.status_code == 401:
            print("\n  → Check your team_id and api_token")
        elif e.status_code == 403:
            print("\n  → Model may not be available")
        elif e.status_code == 429:
            print("\n  → Budget exhausted")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    # Step 4: Check quota
    print("\n[4/4] Checking quota information...")
    try:
        messages = [{"role": "user", "content": "ping"}]
        response = client.invoke(messages, max_tokens=10)
        quota_info = client.get_quota_info(response)

        if quota_info:
            print(f"✓ Quota retrieved")
            print(f"  Budget Limit: ${quota_info.budget_limit:.2f}")
            print(f"  Remaining: ${quota_info.remaining_budget:.2f}")
            print(f"  Usage: {quota_info.budget_usage_percent:.1f}%")

            # Warning if low
            if quota_info.budget_usage_percent > 80:
                print(f"\n  ⚠️  WARNING: Budget usage is high!")
        else:
            print("✓ API working (quota info not available)")
    except Exception as e:
        print(f"✗ Error checking quota: {e}")
        return False

    # Success
    print("\n" + "=" * 60)
    print("✓ All tests passed! Setup is complete.")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Run: python bedrock_examples.py")
    print("  - Check quota: python quota_monitor.py")
    print("  - Read documentation: BEDROCK_README.md")
    return True


def test_models():
    """Test availability of different models"""
    print("\n" + "=" * 60)
    print("Testing Model Availability")
    print("=" * 60)

    load_env_file(".env.bedrock")
    client = BedrockClient()

    test_models = [
        ("Claude 3.5 Sonnet", BedrockModels.CLAUDE_3_5_SONNET_V2),
        ("Claude 3.5 Haiku", BedrockModels.CLAUDE_3_5_HAIKU),
        ("Nova Pro", BedrockModels.NOVA_PRO),
        ("Llama 3.2 11B", BedrockModels.LLAMA_3_2_11B),
    ]

    for name, model_id in test_models:
        try:
            client.chat("Hi", model=model_id, max_tokens=10)
            print(f"✓ {name:20s} - Available")
        except BedrockAPIError as e:
            if e.status_code == 403:
                print(f"✗ {name:20s} - Not available")
            else:
                print(f"? {name:20s} - Error: {e.status_code}")
        except Exception as e:
            print(f"? {name:20s} - Unknown error")


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--models":
        test_models()
    else:
        success = test_connection()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
