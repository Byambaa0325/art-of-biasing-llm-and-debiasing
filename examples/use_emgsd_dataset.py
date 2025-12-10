"""
Example: Using the EMGSD Multi-Turn Dataset

This script demonstrates how to use the dataset client to access
pre-generated bias injection questions.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dataset_client import EMGSDDatasetClient


def example_basic_usage():
    """Example 1: Basic dataset access"""
    print("=" * 80)
    print("EXAMPLE 1: BASIC DATASET ACCESS")
    print("=" * 80)

    # Initialize client
    client = EMGSDDatasetClient()

    # Get dataset size
    print(f"\nDataset has {len(client)} entries")

    # Get a single entry
    entry = client.get_entry(0)
    print(f"\nTarget Question: {entry['target_question']}")
    print(f"EMGSD Trait: {entry['emgsd_trait']}")
    print(f"Stereotype Type: {entry['emgsd_stereotype_type']}")

    # Get bias questions for this entry
    print("\nAvailable bias questions:")
    for bias_type in client.bias_types:
        question = client.get_bias_question(0, bias_type)
        if question:
            print(f"  - {bias_type}: {question[:60]}...")


def example_filter_by_type():
    """Example 2: Filter by stereotype type"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: FILTER BY STEREOTYPE TYPE")
    print("=" * 80)

    client = EMGSDDatasetClient()

    # Filter by profession stereotypes
    profession_entries = client.filter_by_stereotype_type('profession')
    print(f"\nFound {len(profession_entries)} profession stereotypes")

    # Show first 3
    print("\nFirst 3 profession stereotypes:")
    for i, entry in enumerate(profession_entries[:3]):
        print(f"{i+1}. {entry['target_question']} (trait: {entry['emgsd_trait']})")


def example_filter_by_trait():
    """Example 3: Filter by specific trait"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: FILTER BY TRAIT")
    print("=" * 80)

    client = EMGSDDatasetClient()

    # Find all entries with 'lazy' trait
    lazy_entries = client.filter_by_trait('lazy')
    print(f"\nFound {len(lazy_entries)} entries with 'lazy' trait")

    # Show with different bias types
    if lazy_entries:
        entry = lazy_entries[0]
        print(f"\nTarget Question: {entry['target_question']}")
        print("\nBias questions for 'lazy' trait:")
        print(f"  Confirmation: {client.get_bias_question(client.data.index(entry), 'confirmation_bias')}")
        print(f"  Anchoring: {client.get_bias_question(client.data.index(entry), 'anchoring_bias')}")


def example_random_sampling():
    """Example 4: Random sampling"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: RANDOM SAMPLING")
    print("=" * 80)

    client = EMGSDDatasetClient()

    # Get a random sample of 5 entries
    sample = client.sample(5, seed=42)  # seed for reproducibility
    print(f"\nRandom sample of 5 entries:")

    for i, entry in enumerate(sample):
        print(f"\n{i+1}. {entry['target_question']}")
        print(f"   Trait: {entry['emgsd_trait']}")
        print(f"   Type: {entry['emgsd_stereotype_type']}")


def example_statistics():
    """Example 5: Dataset statistics"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: DATASET STATISTICS")
    print("=" * 80)

    client = EMGSDDatasetClient()
    stats = client.get_statistics()

    print(f"\nTotal Entries: {stats['total_entries']}")
    print(f"Bias Generator: {stats['bias_generator_model']}")
    print(f"Approach: {stats['prompt_approach']}")

    print("\nStereotype Types:")
    for stype, count in sorted(stats['stereotype_type_counts'].items()):
        percentage = (count / stats['total_entries']) * 100
        print(f"  {stype}: {count} ({percentage:.1f}%)")

    print("\nGeneration Success Rates:")
    for bias_type, count in sorted(stats['bias_success_counts'].items()):
        success_rate = (count / stats['total_entries']) * 100
        print(f"  {bias_type}: {success_rate:.1f}%")


def example_integration_with_llm():
    """Example 6: Integration with LLM service"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: INTEGRATION WITH LLM SERVICE")
    print("=" * 80)

    client = EMGSDDatasetClient()

    # Get a random entry
    entry = client.get_random_entry(seed=123)

    print("\nUsing dataset with LLM service:")
    print(f"Target Question: {entry['target_question']}")
    print(f"Trait: {entry['emgsd_trait']}")

    # Get pre-generated bias question
    bias_type = 'confirmation_bias'
    turn1_question = client.get_bias_question(
        client.data.index(entry),
        bias_type
    )

    print(f"\nPre-generated Turn 1 Question ({bias_type}):")
    print(f"  {turn1_question}")

    print("\nTo use with LLM service:")
    print("""
    from bedrock_llm_service import BedrockLLMService

    service = BedrockLLMService()

    # Option 1: Use inject_bias_llm to generate new question
    result = service.inject_bias_llm(
        prompt=entry['target_question'],
        bias_type='confirmation_bias',
        model_id='us.anthropic.claude-3-5-sonnet-20241022-v2:0'
    )

    # Option 2: Use pre-generated question from dataset
    # Build conversation manually
    conversation = [
        {"role": "user", "content": turn1_question},
        # ... continue with multi-turn
    ]
    """)


def example_metadata():
    """Example 7: Accessing metadata"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: ACCESSING METADATA")
    print("=" * 80)

    client = EMGSDDatasetClient()
    entry = client.get_entry(0)

    # Get all metadata
    metadata = client.get_metadata(0)

    print("\nEMGSD Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    # Get all bias questions
    all_questions = client.get_all_bias_questions(0)

    print("\nAll Bias Questions for this entry:")
    for bias_type, question in all_questions.items():
        if question:
            print(f"\n{bias_type}:")
            print(f"  {question}")


if __name__ == "__main__":
    example_basic_usage()
    example_filter_by_type()
    example_filter_by_trait()
    example_random_sampling()
    example_statistics()
    example_integration_with_llm()
    example_metadata()

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)
    print("\nFor more information, see backend/dataset_client.py")
