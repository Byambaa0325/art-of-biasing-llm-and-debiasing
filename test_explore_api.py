"""
Test Explore Mode API Endpoints

Tests the new model exploration and dataset APIs.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model_results_client import ModelResultsClient
from dataset_client import EMGSDDatasetClient


def test_model_results_client():
    """Test ModelResultsClient"""
    print("=" * 80)
    print("TESTING MODEL RESULTS CLIENT")
    print("=" * 80)

    client = ModelResultsClient()

    # Test 1: Get available models
    print("\n1. Available Models:")
    models = client.get_available_models()
    print(f"   Total: {len(models)}")
    print(f"   Bedrock: {len(client.get_bedrock_models())}")
    print(f"   Ollama: {len(client.get_ollama_models())}")

    # Test 2: Get model results
    print("\n2. Model Results:")
    for model_id in models[:2]:  # Test first 2 models
        results = client.get_model_results(model_id)
        supports_live = client.supports_live_generation(model_id)
        print(f"   {model_id}: {len(results)} entries, Live: {supports_live}")

    # Test 3: Get specific entry
    print("\n3. Specific Entry (llama3.1:8b, index 0):")
    try:
        entry = client.get_result_by_index('llama3.1:8b', 0)
        print(f"   Target: {entry['target_question']}")
        print(f"   Bias Type: {entry['bias_type']}")
        print(f"   Turn 2 Response: {entry['turn2_response'][:60]}...")
        print(f"   Control: {entry['control_response'][:60]}...")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 4: Filter by bias type
    print("\n4. Filter by Bias Type (llama3.1:8b, confirmation_bias):")
    try:
        results = client.get_results_by_bias_type('llama3.1:8b', 'confirmation_bias')
        print(f"   Found: {len(results)} entries")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 5: Statistics
    print("\n5. Statistics:")
    stats = client.get_statistics()
    print(f"   Total Models: {stats['total_models']}")
    print(f"   Bedrock (Live): {stats['bedrock_models']}")
    print(f"   Ollama (Static): {stats['ollama_models']}")


def test_dataset_client():
    """Test EMGSDDatasetClient"""
    print("\n" + "=" * 80)
    print("TESTING DATASET CLIENT")
    print("=" * 80)

    client = EMGSDDatasetClient()

    # Test 1: Basic info
    print("\n1. Dataset Info:")
    print(f"   Total Entries: {len(client)}")

    # Test 2: Get entry
    print("\n2. Sample Entry (index 0):")
    entry = client.get_entry(0)
    print(f"   Target: {entry['target_question']}")
    print(f"   Trait: {entry['emgsd_trait']}")
    print(f"   Type: {entry['emgsd_stereotype_type']}")

    # Test 3: Get bias questions
    print("\n3. Bias Questions for Entry 0:")
    questions = client.get_all_bias_questions(0)
    for bias_type, question in list(questions.items())[:3]:
        if question:
            print(f"   {bias_type}: {question[:60]}...")

    # Test 4: Filter
    print("\n4. Filter by Stereotype Type (profession):")
    prof_entries = client.filter_by_stereotype_type('profession')
    print(f"   Found: {len(prof_entries)} entries")

    # Test 5: Statistics
    print("\n5. Dataset Statistics:")
    stats = client.get_statistics()
    print(f"   Total: {stats['total_entries']}")
    print(f"   Generator: {stats['bias_generator_model']}")
    print(f"   Approach: {stats['prompt_approach']}")


def test_model_comparison():
    """Test model comparison"""
    print("\n" + "=" * 80)
    print("TESTING MODEL COMPARISON")
    print("=" * 80)

    model_client = ModelResultsClient()
    dataset_client = EMGSDDatasetClient()

    # Compare first entry across all models
    entry_index = 0
    dataset_entry = dataset_client.get_entry(entry_index)

    print(f"\nDataset Entry {entry_index}:")
    print(f"  Target: {dataset_entry['target_question']}")
    print(f"  Trait: {dataset_entry['emgsd_trait']}")

    print(f"\nModel Responses (confirmation_bias):")

    # Get responses from different models
    models_to_test = [
        'llama3.1:8b',
        'mistral:7b',
        'us.amazon.nova-pro-v1:0',
    ]

    for model_id in models_to_test:
        try:
            result = model_client.get_result_by_index(model_id, entry_index)
            if result.get('bias_type') == 'confirmation_bias':
                print(f"\n  {model_id}:")
                print(f"    Turn 2: {result['turn2_response'][:60]}...")
                print(f"    Control: {result['control_response'][:60]}...")
        except Exception as e:
            print(f"\n  {model_id}: Not available")


def test_live_vs_static():
    """Test distinguishing live vs static models"""
    print("\n" + "=" * 80)
    print("TESTING LIVE VS STATIC MODELS")
    print("=" * 80)

    client = ModelResultsClient()

    print("\nBedrock Models (Support Live Generation):")
    for model_id in client.get_bedrock_models():
        meta = client.get_model_metadata(model_id)
        print(f"  [LIVE] {model_id}")
        print(f"         Entries: {meta['total_entries']}, Can Generate: Yes")

    print("\nOllama Models (Static Benchmark Only):")
    for model_id in client.get_ollama_models():
        meta = client.get_model_metadata(model_id)
        print(f"  [STATIC] {model_id}")
        print(f"           Entries: {meta['total_entries']}, Can Generate: No")


if __name__ == "__main__":
    test_model_results_client()
    test_dataset_client()
    test_model_comparison()
    test_live_vs_static()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Update React frontend to add mode selector")
    print("2. Create dataset browser component")
    print("3. Update model selector to show live/static capabilities")
    print("4. Add result comparison view")
    print("=" * 80)
