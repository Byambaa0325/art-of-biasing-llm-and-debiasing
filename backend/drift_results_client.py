"""
Drift Analysis Results Client

Provides access to drift analysis results from CSV files.
These results contain Turn 1 and Turn 2 responses with HEARTS evaluation scores.
"""

import csv
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import glob


class DriftResultsClient:
    """
    Client for accessing drift analysis results from CSV files.

    The results contain responses from various LLMs evaluated on the EMGSD 
    multi-turn bias injection dataset with HEARTS scores and drift analysis.

    Example:
        >>> client = DriftResultsClient()
        >>> models = client.get_available_models()
        >>> results = client.get_model_results('us.meta.llama3-1-70b-instruct-v1:0')
    """

    # Model categories - matching CSV directory names
    BEDROCK_MODELS = [
        'us_anthropic_claude-3-5-sonnet-20241022-v2_0',
        'us_anthropic_claude-3-sonnet-20240229-v1_0',
        'us_anthropic_claude-3-5-haiku-20241022-v1_0',
        'us_anthropic_claude-3-haiku-20240307-v1_0',
        'us_meta_llama3-1-70b-instruct-v1_0',
        'us_amazon_nova-pro-v1_0',
        'us_amazon_nova-lite-v1_0',
        'us_amazon_nova-micro-v1_0',
    ]

    OLLAMA_MODELS = [
        # Excluded per user request
    ]
    
    @staticmethod
    def normalize_model_id(model_id: str) -> str:
        """
        Convert between frontend format (dots/colons) and filesystem format (underscores).
        
        Frontend: us.meta.llama3-1-70b-instruct-v1:0
        Filesystem: us_meta_llama3-1-70b-instruct-v1_0
        """
        return model_id.replace('.', '_').replace(':', '_')

    def __init__(self, results_dir: Optional[str] = None):
        """
        Initialize drift results client.

        Args:
            results_dir: Directory containing drift analysis CSV files.
                        If None, uses default location.
        """
        if results_dir is None:
            # Default to local drift analysis results
            current_dir = Path(__file__).parent
            results_dir = current_dir.parent / "data" / "drift_results"

        self.results_dir = Path(results_dir)
        if not self.results_dir.exists():
            raise FileNotFoundError(f"Results directory not found at {self.results_dir}")

        # Load all available results
        self._load_results()

    def _load_results(self):
        """Load all drift analysis CSV files"""
        self.results = {}
        self.model_metadata = {}

        # Find all model directories
        for model_dir in self.results_dir.iterdir():
            if not model_dir.is_dir():
                continue

            model_id = model_dir.name
            
            # Look for the most recent date directory
            date_dirs = sorted([d for d in model_dir.iterdir() if d.is_dir()], reverse=True)
            if not date_dirs:
                continue

            latest_date_dir = date_dirs[0]
            csv_file = latest_date_dir / "drift_analysis.csv"

            if not csv_file.exists():
                continue

            try:
                # Read CSV file
                entries = []
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Convert to format compatible with frontend
                        entry = {
                            'entry_index': int(row['entry_index']),
                            'model_id': row['model_id'],
                            'bias_type': row['bias_type'],
                            'target_question': row['target_question'],
                            'turn1_question': row['turn1_question'],
                            'turn1_response': row['turn1_response'],
                            'turn2_response': row['turn2_response'],
                            'control_response': row['control_response'],
                            'emgsd_text': row['emgsd_text'],
                            'emgsd_stereotype_type': row['emgsd_stereotype_type'],
                            'emgsd_category': row['emgsd_category'],
                            'emgsd_trait': row['emgsd_trait'],
                            'emgsd_target_word': row.get('emgsd_target_word', ''),
                            'error': row.get('error', ''),
                            
                            # HEARTS evaluation scores
                            'hearts_evaluation': {
                                'control_is_stereotype': row.get('drift_control_is_stereotype', '').lower() == 'true',
                                'control_stereotype_score': float(row.get('drift_control_stereotype_score', 0)),
                                'bias_is_stereotype': row.get('drift_bias_is_stereotype', '').lower() == 'true',
                                'bias_stereotype_score': float(row.get('drift_bias_stereotype_score', 0)),
                                'drift_score': float(row.get('drift_drift_score', 0)),
                                'raw_drift': float(row.get('drift_raw_drift', 0)),
                                'significant_drift': row.get('drift_significant_drift', '').lower() == 'true',
                                'framework': row.get('drift_hearts_framework', 'HEARTS'),
                            },
                            
                            # Similarity metrics
                            'similarity_metrics': {
                                'cosine_similarity': float(row.get('drift_cosine_similarity', 0)),
                                'euclidean_distance': float(row.get('drift_euclidean_distance', 0)),
                                'bleu_score': float(row.get('drift_bleu_score', 0)),
                                'rouge1': float(row.get('drift_rouge1', 0)),
                                'rouge2': float(row.get('drift_rouge2', 0)),
                                'rougeL': float(row.get('drift_rougeL', 0)),
                            }
                        }
                        entries.append(entry)

                self.results[model_id] = entries

                # Store metadata with friendly display name
                display_name = model_id.replace('_', '.').replace('-v1.0', '-v1:0').replace('-v2.0', '-v2:0')
                
                self.model_metadata[model_id] = {
                    'total_entries': len(entries),
                    'file_path': str(csv_file),
                    'date': latest_date_dir.name,
                    'is_bedrock': model_id in self.BEDROCK_MODELS,
                    'is_ollama': model_id in self.OLLAMA_MODELS,
                    'supports_live_generation': model_id in self.BEDROCK_MODELS,
                    'display_id': display_name,  # Frontend-friendly ID
                }

            except Exception as e:
                print(f"Warning: Could not load {csv_file}: {e}")

    def get_available_models(self) -> List[str]:
        """Get list of available model IDs."""
        return list(self.results.keys())

    def get_bedrock_models(self) -> List[str]:
        """Get list of available Bedrock models"""
        return [
            model_id for model_id in self.results.keys()
            if self.model_metadata[model_id]['is_bedrock']
        ]

    def get_ollama_models(self) -> List[str]:
        """Get list of available Ollama models"""
        return [
            model_id for model_id in self.results.keys()
            if self.model_metadata[model_id]['is_ollama']
        ]

    def get_model_results(self, model_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific model."""
        # Normalize model ID to match filesystem format
        normalized_id = self.normalize_model_id(model_id)
        
        if normalized_id in self.results:
            return self.results[normalized_id]
        elif model_id in self.results:
            return self.results[model_id]
        else:
            available = ', '.join(self.get_available_models())
            raise ValueError(
                f"Model '{model_id}' not found. "
                f"Available models: {available}"
            )

    def get_result_by_index(self, model_id: str, entry_index: int) -> Dict[str, Any]:
        """Get a specific result entry by index."""
        results = self.get_model_results(model_id)

        # Find entry with matching index
        for entry in results:
            if entry.get('entry_index') == entry_index:
                return entry

        raise ValueError(
            f"No result found for model '{model_id}' with entry_index {entry_index}"
        )

    def get_results_by_bias_type(
        self,
        model_id: str,
        bias_type: str
    ) -> List[Dict[str, Any]]:
        """Get all results for a specific bias type."""
        results = self.get_model_results(model_id)
        return [r for r in results if r.get('bias_type') == bias_type]

    def get_model_metadata(self, model_id: str) -> Dict[str, Any]:
        """Get metadata for a model."""
        # Normalize model ID to match filesystem format
        normalized_id = self.normalize_model_id(model_id)
        
        if normalized_id in self.model_metadata:
            return self.model_metadata[normalized_id]
        elif model_id in self.model_metadata:
            return self.model_metadata[model_id]
        else:
            raise ValueError(f"Model '{model_id}' not found")

    def supports_live_generation(self, model_id: str) -> bool:
        """Check if model supports live generation (Bedrock models only)."""
        meta = self.get_model_metadata(model_id)
        return meta['supports_live_generation']

    def get_statistics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a model or all models."""
        if model_id is not None:
            # Stats for specific model
            results = self.get_model_results(model_id)

            bias_type_counts = {}
            stereotype_type_counts = {}

            for entry in results:
                bias_type = entry.get('bias_type', 'unknown')
                stereotype_type = entry.get('emgsd_stereotype_type', 'unknown')

                bias_type_counts[bias_type] = bias_type_counts.get(bias_type, 0) + 1
                stereotype_type_counts[stereotype_type] = stereotype_type_counts.get(stereotype_type, 0) + 1

            return {
                'model_id': model_id,
                'total_entries': len(results),
                'bias_type_counts': bias_type_counts,
                'stereotype_type_counts': stereotype_type_counts,
                'supports_live_generation': self.supports_live_generation(model_id),
            }
        else:
            # Stats for all models
            return {
                'total_models': len(self.results),
                'bedrock_models': len(self.get_bedrock_models()),
                'ollama_models': len(self.get_ollama_models()),
                'models_with_live_generation': len(self.get_bedrock_models()),
                'models_static_only': len(self.get_ollama_models()),
            }


def print_results_info():
    """Print results information"""
    try:
        client = DriftResultsClient()

        print("=" * 80)
        print("DRIFT ANALYSIS RESULTS INFO")
        print("=" * 80)

        stats = client.get_statistics()
        print(f"\nTotal Models: {stats['total_models']}")
        print(f"  - Bedrock (Live Generation): {stats['bedrock_models']}")
        print(f"  - Ollama (Static Benchmark): {stats['ollama_models']}")

        print("\n" + "-" * 80)
        print("AVAILABLE MODELS:")
        print("-" * 80)
        for model_id in client.get_available_models():
            meta = client.get_model_metadata(model_id)
            print(f"  {model_id} ({meta['total_entries']} entries, date: {meta['date']})")

        print("\n" + "=" * 80)
        print("SAMPLE ENTRY WITH HEARTS SCORES:")
        print("=" * 80)
        models = client.get_available_models()
        if models:
            sample_model = models[0]
            results = client.get_model_results(sample_model)
            if results:
                entry = results[0]
                print(f"Model: {sample_model}")
                print(f"Entry Index: {entry['entry_index']}")
                print(f"Bias Type: {entry['bias_type']}")
                print(f"Target Question: {entry['target_question']}")
                print(f"\nHEARTS Evaluation:")
                hearts = entry['hearts_evaluation']
                print(f"  Control is stereotype: {hearts['control_is_stereotype']}")
                print(f"  Control score: {hearts['control_stereotype_score']:.4f}")
                print(f"  Bias is stereotype: {hearts['bias_is_stereotype']}")
                print(f"  Bias score: {hearts['bias_stereotype_score']:.4f}")
                print(f"  Drift score: {hearts['drift_score']:.4f}")
                print(f"  Significant drift: {hearts['significant_drift']}")

        print("=" * 80)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print_results_info()
