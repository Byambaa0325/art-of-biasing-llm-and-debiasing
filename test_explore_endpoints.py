#!/usr/bin/env python3
"""
Test script for Explore Mode API endpoints

This script tests all the API endpoints required for the frontend explore mode integration.
Run this before testing the frontend to ensure backend is properly configured.

Usage:
    python test_explore_endpoints.py
"""

import requests
import json
import sys
from typing import Dict, Any


API_BASE = "http://localhost:5000/api"
COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'END': '\033[0m'
}


def print_status(test_name: str, success: bool, message: str = ""):
    """Print test status with color"""
    status = f"{COLORS['GREEN']}✓{COLORS['END']}" if success else f"{COLORS['RED']}✗{COLORS['END']}"
    print(f"{status} {test_name}")
    if message:
        print(f"  {message}")


def test_models_available() -> bool:
    """Test GET /api/models/available"""
    print(f"\n{COLORS['BLUE']}Testing: GET /api/models/available{COLORS['END']}")
    
    try:
        response = requests.get(f"{API_BASE}/models/available", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate structure
            if 'bedrock_models' not in data or 'ollama_models' not in data:
                print_status("Structure validation", False, "Missing required keys")
                return False
            
            bedrock_count = len(data.get('bedrock_models', []))
            ollama_count = len(data.get('ollama_models', []))
            total = data.get('total_models', bedrock_count + ollama_count)
            
            print_status("Endpoint response", True, f"Found {total} models ({bedrock_count} Bedrock, {ollama_count} Ollama)")
            
            # Check model structure
            if bedrock_count > 0:
                sample = data['bedrock_models'][0]
                required = ['id', 'name', 'type', 'supports_live_generation']
                if all(key in sample for key in required):
                    print_status("Model structure", True, f"Sample: {sample['name']}")
                else:
                    print_status("Model structure", False, f"Missing keys: {[k for k in required if k not in sample]}")
                    return False
            
            return True
        else:
            print_status("Endpoint response", False, f"Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("Connection", False, "Could not connect to backend. Is it running?")
        return False
    except Exception as e:
        print_status("Request", False, str(e))
        return False


def test_dataset_stats() -> bool:
    """Test GET /api/dataset/stats"""
    print(f"\n{COLORS['BLUE']}Testing: GET /api/dataset/stats{COLORS['END']}")
    
    try:
        response = requests.get(f"{API_BASE}/dataset/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate structure
            required = ['total_entries', 'stereotype_type_counts']
            if not all(key in data for key in required):
                print_status("Structure validation", False, f"Missing keys: {[k for k in required if k not in data]}")
                return False
            
            total = data['total_entries']
            types = data['stereotype_type_counts']
            
            print_status("Endpoint response", True, f"Total entries: {total}")
            print(f"  Stereotype counts:")
            for stype, count in types.items():
                print(f"    - {stype}: {count}")
            
            return True
        else:
            print_status("Endpoint response", False, f"Status {response.status_code}")
            return False
            
    except Exception as e:
        print_status("Request", False, str(e))
        return False


def test_dataset_entries() -> Dict[str, Any]:
    """Test GET /api/dataset/entries"""
    print(f"\n{COLORS['BLUE']}Testing: GET /api/dataset/entries{COLORS['END']}")
    
    try:
        # Test with limit
        response = requests.get(f"{API_BASE}/dataset/entries?limit=5", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate structure
            if 'entries' not in data:
                print_status("Structure validation", False, "Missing 'entries' key")
                return {}
            
            entries = data['entries']
            total = data.get('total', 0)
            
            print_status("Endpoint response", True, f"Retrieved {len(entries)} entries (Total: {total})")
            
            # Check entry structure
            if entries:
                sample = entries[0]
                required = ['target_question', 'emgsd_trait', 'emgsd_stereotype_type']
                if all(key in sample for key in required):
                    print_status("Entry structure", True)
                    print(f"  Sample entry:")
                    print(f"    - Question: {sample.get('target_question', 'N/A')[:50]}...")
                    print(f"    - Trait: {sample.get('emgsd_trait')}")
                    print(f"    - Type: {sample.get('emgsd_stereotype_type')}")
                    
                    # Check for entry_index
                    if 'entry_index' in sample:
                        print_status("Entry index field", True, f"Index: {sample['entry_index']}")
                    else:
                        print_status("Entry index field", False, "Missing (will use array index)")
                    
                    return {'sample_entry': sample, 'success': True}
                else:
                    print_status("Entry structure", False, f"Missing keys: {[k for k in required if k not in sample]}")
                    return {'success': False}
            else:
                print_status("Entries", False, "No entries returned")
                return {'success': False}
        else:
            print_status("Endpoint response", False, f"Status {response.status_code}")
            return {'success': False}
            
    except Exception as e:
        print_status("Request", False, str(e))
        return {'success': False}


def test_model_result(model_id: str = None, entry_index: int = 0) -> bool:
    """Test GET /api/models/{model_id}/result/{entry_index}"""
    print(f"\n{COLORS['BLUE']}Testing: GET /api/models/{{model_id}}/result/{{entry_index}}{COLORS['END']}")
    
    # Get a model ID if not provided
    if not model_id:
        try:
            response = requests.get(f"{API_BASE}/models/available", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Try Ollama first (more likely to have results)
                if data.get('ollama_models'):
                    model_id = data['ollama_models'][0]['id']
                elif data.get('bedrock_models'):
                    model_id = data['bedrock_models'][0]['id']
                
                if not model_id:
                    print_status("Model selection", False, "No models available")
                    return False
                
                print(f"  Using model: {model_id}")
            else:
                print_status("Model selection", False, "Could not fetch models")
                return False
        except Exception as e:
            print_status("Model selection", False, str(e))
            return False
    
    try:
        # URL encode model ID
        from urllib.parse import quote
        encoded_model = quote(model_id, safe='')
        
        url = f"{API_BASE}/models/{encoded_model}/result/{entry_index}"
        print(f"  URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate structure
            required = ['turn1_question', 'turn1_response', 'turn2_response', 'control_response']
            if not all(key in data for key in required):
                print_status("Structure validation", False, f"Missing keys: {[k for k in required if k not in data]}")
                print(f"  Available keys: {list(data.keys())}")
                return False
            
            print_status("Endpoint response", True)
            print(f"  Model: {data.get('model_id', 'N/A')}")
            print(f"  Bias type: {data.get('bias_type', 'N/A')}")
            print(f"  Turn 1 question: {data['turn1_question'][:50]}...")
            print(f"  Turn 2 response length: {len(data['turn2_response'])} chars")
            print(f"  Control response length: {len(data['control_response'])} chars")
            
            return True
        elif response.status_code == 404:
            print_status("Endpoint response", False, "Result not found (404)")
            print(f"  This might mean:")
            print(f"    1. Model '{model_id}' doesn't have pre-generated results")
            print(f"    2. Entry index {entry_index} doesn't exist")
            print(f"    3. Evaluation file is missing")
            return False
        else:
            print_status("Endpoint response", False, f"Status {response.status_code}")
            try:
                error = response.json()
                print(f"  Error: {error.get('error', 'Unknown')}")
            except:
                print(f"  Response: {response.text[:100]}")
            return False
            
    except Exception as e:
        print_status("Request", False, str(e))
        return False


def test_filter_entries() -> bool:
    """Test dataset entries with filters"""
    print(f"\n{COLORS['BLUE']}Testing: Dataset entries with filters{COLORS['END']}")
    
    try:
        # Test stereotype type filter
        response = requests.get(
            f"{API_BASE}/dataset/entries?stereotype_type=profession&limit=3",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            
            if entries:
                all_profession = all(e.get('emgsd_stereotype_type') == 'profession' for e in entries)
                if all_profession:
                    print_status("Stereotype filter", True, f"All {len(entries)} entries are 'profession'")
                else:
                    print_status("Stereotype filter", False, "Filter not working correctly")
                    return False
            else:
                print_status("Stereotype filter", False, "No entries returned")
                return False
        else:
            print_status("Stereotype filter", False, f"Status {response.status_code}")
            return False
        
        # Test trait filter
        response = requests.get(
            f"{API_BASE}/dataset/entries?trait=bossy&limit=3",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            
            if entries:
                print_status("Trait filter", True, f"Found {len(entries)} entries with trait filter")
            else:
                print_status("Trait filter", False, "No entries returned (might be expected)")
        else:
            print_status("Trait filter", False, f"Status {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_status("Filter test", False, str(e))
        return False


def main():
    """Run all tests"""
    print(f"\n{COLORS['YELLOW']}{'='*60}{COLORS['END']}")
    print(f"{COLORS['YELLOW']}  Explore Mode API Endpoint Tests{COLORS['END']}")
    print(f"{COLORS['YELLOW']}{'='*60}{COLORS['END']}")
    
    results = {}
    
    # Test 1: Models available
    results['models_available'] = test_models_available()
    
    # Test 2: Dataset stats
    results['dataset_stats'] = test_dataset_stats()
    
    # Test 3: Dataset entries
    entry_result = test_dataset_entries()
    results['dataset_entries'] = entry_result.get('success', False)
    
    # Test 4: Filtered entries
    results['filtered_entries'] = test_filter_entries()
    
    # Test 5: Model result (using first available model)
    results['model_result'] = test_model_result()
    
    # Summary
    print(f"\n{COLORS['YELLOW']}{'='*60}{COLORS['END']}")
    print(f"{COLORS['YELLOW']}  Test Summary{COLORS['END']}")
    print(f"{COLORS['YELLOW']}{'='*60}{COLORS['END']}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{COLORS['GREEN']}PASS{COLORS['END']}" if result else f"{COLORS['RED']}FAIL{COLORS['END']}"
        print(f"  {test_name}: {status}")
    
    print(f"\n  {COLORS['BLUE']}Total: {passed}/{total} tests passed{COLORS['END']}")
    
    if passed == total:
        print(f"\n{COLORS['GREEN']}✓ All tests passed! Frontend integration should work.{COLORS['END']}")
        return 0
    else:
        print(f"\n{COLORS['RED']}✗ Some tests failed. Please fix backend before testing frontend.{COLORS['END']}")
        print(f"\n{COLORS['YELLOW']}Troubleshooting:{COLORS['END']}")
        print(f"  1. Ensure backend is running: python backend/api.py")
        print(f"  2. Check that model evaluation files exist in data/model_evaluations/")
        print(f"  3. Verify multiturn_emgsd_dataset.json exists in data/")
        print(f"  4. Check backend logs for errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
