"""
EMGSD Multi-Turn Dataset Client

Provides easy access to the multi-turn EMGSD dataset with bias injection questions.
"""

import json
import os
from typing import List, Dict, Optional, Any
from pathlib import Path


class EMGSDDatasetClient:
    """
    Client for accessing multi-turn EMGSD dataset.

    The dataset contains stereotypes from EMGSD with pre-generated bias injection
    questions for 8 different cognitive bias types.

    Example:
        >>> client = EMGSDDatasetClient()
        >>> entry = client.get_entry(0)
        >>> print(entry['target_question'])
        'The supervisor is'
        >>> print(entry['turn1_question_confirmation_bias'])
        "Isn't it generally true that supervisors tend to be bossy..."
    """

    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize dataset client.

        Args:
            dataset_path: Path to dataset JSON file. If None, uses default location.
        """
        if dataset_path is None:
            # Default to data/multiturn_emgsd_dataset.json
            current_dir = Path(__file__).parent
            dataset_path = current_dir.parent / "data" / "multiturn_emgsd_dataset.json"

        self.dataset_path = Path(dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")

        # Load dataset
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # Bias types available
        self.bias_types = [
            'confirmation_bias',
            'anchoring_bias',
            'demographic_bias',
            'availability_bias',
            'framing_bias',
            'leading_question',
            'stereotypical_assumption',
            'negativity_bias'
        ]

    def __len__(self) -> int:
        """Return number of entries in dataset"""
        return len(self.data)

    def get_entry(self, index: int) -> Dict[str, Any]:
        """
        Get a single entry by index.

        Args:
            index: Entry index (0 to len-1)

        Returns:
            Dictionary with entry data

        Example:
            >>> client = EMGSDDatasetClient()
            >>> entry = client.get_entry(0)
            >>> entry.keys()
        """
        if index < 0 or index >= len(self.data):
            raise IndexError(f"Index {index} out of range [0, {len(self.data)-1}]")
        return self.data[index]

    def get_target_question(self, index: int) -> str:
        """
        Get the target question (original prompt) for an entry.

        Args:
            index: Entry index

        Returns:
            Target question string

        Example:
            >>> client = EMGSDDatasetClient()
            >>> client.get_target_question(0)
            'The supervisor is'
        """
        entry = self.get_entry(index)
        return entry['target_question']

    def get_bias_question(self, index: int, bias_type: str) -> Optional[str]:
        """
        Get the Turn 1 priming question for a specific bias type.

        Args:
            index: Entry index
            bias_type: Type of bias (e.g., 'confirmation_bias', 'anchoring_bias')

        Returns:
            Priming question string, or None if not available

        Example:
            >>> client = EMGSDDatasetClient()
            >>> q = client.get_bias_question(0, 'confirmation_bias')
            >>> print(q)
            "Isn't it generally true that supervisors tend to be bossy..."
        """
        if bias_type not in self.bias_types:
            raise ValueError(
                f"Unknown bias_type '{bias_type}'. "
                f"Available: {', '.join(self.bias_types)}"
            )

        entry = self.get_entry(index)
        field_name = f'turn1_question_{bias_type}'
        return entry.get(field_name)

    def get_all_bias_questions(self, index: int) -> Dict[str, Optional[str]]:
        """
        Get all Turn 1 priming questions for an entry.

        Args:
            index: Entry index

        Returns:
            Dictionary mapping bias_type to priming question

        Example:
            >>> client = EMGSDDatasetClient()
            >>> questions = client.get_all_bias_questions(0)
            >>> questions['confirmation_bias']
            "Isn't it generally true that..."
        """
        entry = self.get_entry(index)
        return {
            bias_type: entry.get(f'turn1_question_{bias_type}')
            for bias_type in self.bias_types
        }

    def get_metadata(self, index: int) -> Dict[str, Any]:
        """
        Get EMGSD metadata for an entry.

        Args:
            index: Entry index

        Returns:
            Dictionary with EMGSD metadata fields

        Example:
            >>> client = EMGSDDatasetClient()
            >>> meta = client.get_metadata(0)
            >>> meta['emgsd_trait']
            'bossy'
        """
        entry = self.get_entry(index)
        return {
            'emgsd_text': entry.get('emgsd_text'),
            'emgsd_text_with_marker': entry.get('emgsd_text_with_marker'),
            'emgsd_stereotype_type': entry.get('emgsd_stereotype_type'),
            'emgsd_category': entry.get('emgsd_category'),
            'emgsd_data_source': entry.get('emgsd_data_source'),
            'emgsd_label': entry.get('emgsd_label'),
            'emgsd_target_group': entry.get('emgsd_target_group'),
            'emgsd_trait': entry.get('emgsd_trait'),
            'emgsd_target_word': entry.get('emgsd_target_word'),
        }

    def filter_by_stereotype_type(self, stereotype_type: str) -> List[Dict[str, Any]]:
        """
        Filter entries by stereotype type.

        Args:
            stereotype_type: Type (e.g., 'profession', 'gender', 'race')

        Returns:
            List of matching entries

        Example:
            >>> client = EMGSDDatasetClient()
            >>> prof_entries = client.filter_by_stereotype_type('profession')
            >>> len(prof_entries)
        """
        return [
            entry for entry in self.data
            if entry.get('emgsd_stereotype_type') == stereotype_type
        ]

    def filter_by_trait(self, trait: str) -> List[Dict[str, Any]]:
        """
        Filter entries by trait.

        Args:
            trait: Trait to search for (e.g., 'bossy', 'lazy')

        Returns:
            List of matching entries

        Example:
            >>> client = EMGSDDatasetClient()
            >>> bossy_entries = client.filter_by_trait('bossy')
        """
        return [
            entry for entry in self.data
            if entry.get('emgsd_trait') == trait
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get dataset statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> client = EMGSDDatasetClient()
            >>> stats = client.get_statistics()
            >>> stats['total_entries']
            1158
        """
        # Count by stereotype type
        stereotype_counts = {}
        for entry in self.data:
            stype = entry.get('emgsd_stereotype_type', 'unknown')
            stereotype_counts[stype] = stereotype_counts.get(stype, 0) + 1

        # Count successful generations per bias type
        bias_success_counts = {}
        for bias_type in self.bias_types:
            field_name = f'turn1_question_{bias_type}'
            count = sum(
                1 for entry in self.data
                if entry.get(field_name) is not None
            )
            bias_success_counts[bias_type] = count

        # Count refusals per bias type
        refusal_counts = {}
        for bias_type in self.bias_types:
            field_name = f'refusal_detected_{bias_type}'
            count = sum(
                1 for entry in self.data
                if entry.get(field_name) is True
            )
            refusal_counts[bias_type] = count

        return {
            'total_entries': len(self.data),
            'stereotype_type_counts': stereotype_counts,
            'bias_success_counts': bias_success_counts,
            'refusal_counts': refusal_counts,
            'bias_generator_model': self.data[0].get('bias_generator_model', 'unknown'),
            'prompt_approach': self.data[0].get('prompt_approach', 'unknown'),
        }

    def get_random_entry(self, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a random entry.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Random entry

        Example:
            >>> client = EMGSDDatasetClient()
            >>> entry = client.get_random_entry(seed=42)
        """
        import random
        if seed is not None:
            random.seed(seed)
        index = random.randint(0, len(self.data) - 1)
        return self.get_entry(index)

    def sample(self, n: int, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get a random sample of entries.

        Args:
            n: Number of entries to sample
            seed: Random seed for reproducibility

        Returns:
            List of sampled entries

        Example:
            >>> client = EMGSDDatasetClient()
            >>> sample = client.sample(10, seed=42)
            >>> len(sample)
            10
        """
        import random
        if seed is not None:
            random.seed(seed)

        if n > len(self.data):
            n = len(self.data)

        indices = random.sample(range(len(self.data)), n)
        return [self.data[i] for i in indices]


def print_dataset_info():
    """Print dataset information"""
    try:
        client = EMGSDDatasetClient()
        stats = client.get_statistics()

        print("=" * 80)
        print("EMGSD MULTI-TURN DATASET INFO")
        print("=" * 80)
        print(f"\nTotal Entries: {stats['total_entries']}")
        print(f"Bias Generator Model: {stats['bias_generator_model']}")
        print(f"Prompt Approach: {stats['prompt_approach']}")

        print("\n" + "-" * 80)
        print("STEREOTYPE TYPE DISTRIBUTION:")
        print("-" * 80)
        for stype, count in sorted(stats['stereotype_type_counts'].items()):
            print(f"  {stype}: {count}")

        print("\n" + "-" * 80)
        print("BIAS GENERATION SUCCESS RATES:")
        print("-" * 80)
        for bias_type, count in sorted(stats['bias_success_counts'].items()):
            success_rate = (count / stats['total_entries']) * 100
            print(f"  {bias_type}: {count}/{stats['total_entries']} ({success_rate:.1f}%)")

        print("\n" + "-" * 80)
        print("REFUSAL COUNTS:")
        print("-" * 80)
        for bias_type, count in sorted(stats['refusal_counts'].items()):
            refusal_rate = (count / stats['total_entries']) * 100
            print(f"  {bias_type}: {count}/{stats['total_entries']} ({refusal_rate:.1f}%)")

        print("\n" + "=" * 80)
        print("SAMPLE ENTRY:")
        print("=" * 80)
        entry = client.get_entry(0)
        print(f"Target Question: {entry['target_question']}")
        print(f"EMGSD Trait: {entry['emgsd_trait']}")
        print(f"\nBias Questions:")
        for bias_type in client.bias_types:
            q = client.get_bias_question(0, bias_type)
            if q:
                print(f"  {bias_type}: {q[:80]}...")

        print("=" * 80)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print_dataset_info()
