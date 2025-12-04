"""
Quota Monitoring Utility for Bedrock Proxy API
Provides tools to track and monitor API budget usage.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from bedrock_client import BedrockClient, QuotaInfo, load_env_file


class QuotaMonitor:
    """Monitor and track API quota usage"""

    def __init__(self, client: BedrockClient, log_file: str = "quota_log.json"):
        """
        Initialize quota monitor.

        Args:
            client: BedrockClient instance
            log_file: Path to JSON file for logging quota history
        """
        self.client = client
        self.log_file = log_file
        self.last_quota: Optional[QuotaInfo] = None

    def check_quota(self, test_message: str = "ping") -> Optional[QuotaInfo]:
        """
        Check current quota by making a minimal API call.

        Args:
            test_message: Simple message to send (keep it short to minimize cost)

        Returns:
            QuotaInfo object or None
        """
        try:
            messages = [{"role": "user", "content": test_message}]
            response = self.client.invoke(messages, max_tokens=10)
            quota_info = self.client.get_quota_info(response)
            self.last_quota = quota_info
            return quota_info
        except Exception as e:
            print(f"Error checking quota: {e}")
            return None

    def log_quota(self, quota_info: QuotaInfo, notes: str = "") -> None:
        """
        Log quota information to file.

        Args:
            quota_info: QuotaInfo object to log
            notes: Optional notes about this log entry
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "llm_cost": quota_info.llm_cost,
            "gpu_cost": quota_info.gpu_cost,
            "total_cost": quota_info.total_cost,
            "budget_limit": quota_info.budget_limit,
            "remaining_budget": quota_info.remaining_budget,
            "budget_usage_percent": quota_info.budget_usage_percent,
            "notes": notes
        }

        try:
            # Read existing logs
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []

            # Append new log
            logs.append(log_entry)

            # Write back
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"Error logging quota: {e}")

    def print_quota_report(self, quota_info: Optional[QuotaInfo] = None) -> None:
        """
        Print a formatted quota report.

        Args:
            quota_info: QuotaInfo to display (uses last_quota if None)
        """
        quota = quota_info or self.last_quota

        if not quota:
            print("No quota information available")
            return

        print("\n" + "=" * 60)
        print("BUDGET QUOTA REPORT")
        print("=" * 60)
        print(f"Budget Limit:      ${quota.budget_limit:.2f}")
        print(f"Remaining Budget:  ${quota.remaining_budget:.2f}")
        print(f"Budget Used:       ${quota.total_cost:.2f} ({quota.budget_usage_percent:.1f}%)")
        print(f"  - LLM Cost:      ${quota.llm_cost:.2f}")
        print(f"  - GPU Cost:      ${quota.gpu_cost:.2f}")
        print("=" * 60)

        # Status indicator
        if quota.budget_usage_percent < 50:
            status = "✓ Good"
            color = ""
        elif quota.budget_usage_percent < 80:
            status = "⚠ Moderate"
            color = ""
        else:
            status = "⚠️ High Usage"
            color = ""

        print(f"Status: {status}")

        # Warnings
        if quota.remaining_budget < 5:
            print("\n⚠️  WARNING: Less than $5 remaining!")
        elif quota.budget_usage_percent > 90:
            print("\n⚠️  WARNING: Over 90% of budget used!")

        print("=" * 60 + "\n")

    def should_continue(self, threshold_percent: float = 95.0) -> bool:
        """
        Check if there's enough budget to continue operations.

        Args:
            threshold_percent: Budget usage threshold (default 95%)

        Returns:
            True if should continue, False if budget is too low
        """
        if not self.last_quota:
            self.check_quota()

        if not self.last_quota:
            return True  # Can't check, assume OK

        return self.last_quota.budget_usage_percent < threshold_percent

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics from log file.

        Returns:
            Dict with usage statistics
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "No logs available"}

        if not logs:
            return {"error": "No logs available"}

        # Calculate stats
        total_requests = len(logs)
        total_llm_cost = sum(log["llm_cost"] for log in logs)
        total_gpu_cost = sum(log["gpu_cost"] for log in logs)
        total_cost = sum(log["total_cost"] for log in logs)

        latest = logs[-1]
        earliest = logs[0]

        return {
            "total_requests_logged": total_requests,
            "cumulative_llm_cost": total_llm_cost,
            "cumulative_gpu_cost": total_gpu_cost,
            "cumulative_total_cost": total_cost,
            "current_remaining": latest["remaining_budget"],
            "current_usage_percent": latest["budget_usage_percent"],
            "first_log": earliest["timestamp"],
            "last_log": latest["timestamp"]
        }

    def print_usage_stats(self) -> None:
        """Print usage statistics from logs."""
        stats = self.get_usage_stats()

        if "error" in stats:
            print(f"Error: {stats['error']}")
            return

        print("\n" + "=" * 60)
        print("USAGE STATISTICS")
        print("=" * 60)
        print(f"Total Logged Requests: {stats['total_requests_logged']}")
        print(f"Cumulative LLM Cost:   ${stats['cumulative_llm_cost']:.4f}")
        print(f"Cumulative GPU Cost:   ${stats['cumulative_gpu_cost']:.4f}")
        print(f"Cumulative Total Cost: ${stats['cumulative_total_cost']:.4f}")
        print(f"Current Remaining:     ${stats['current_remaining']:.2f}")
        print(f"Current Usage:         {stats['current_usage_percent']:.1f}%")
        print(f"\nFirst Log: {stats['first_log']}")
        print(f"Last Log:  {stats['last_log']}")
        print("=" * 60 + "\n")

    def estimate_requests_remaining(
        self,
        avg_tokens_per_request: int = 500,
        model_cost_per_1k_tokens: float = 0.003
    ) -> int:
        """
        Estimate how many requests can be made with remaining budget.

        Args:
            avg_tokens_per_request: Average tokens per request
            model_cost_per_1k_tokens: Cost per 1000 tokens (approximate)

        Returns:
            Estimated number of requests remaining
        """
        if not self.last_quota:
            return 0

        cost_per_request = (avg_tokens_per_request / 1000) * model_cost_per_1k_tokens
        estimated_requests = int(self.last_quota.remaining_budget / cost_per_request)

        return max(0, estimated_requests)


def main():
    """Demo quota monitoring functionality"""
    print("Bedrock Quota Monitor")
    print("=" * 60)

    # Load credentials
    load_env_file(".env.bedrock")

    # Initialize client and monitor
    try:
        client = BedrockClient()
        monitor = QuotaMonitor(client)

        # Check current quota
        print("\nChecking current quota...")
        quota_info = monitor.check_quota()

        if quota_info:
            # Print report
            monitor.print_quota_report(quota_info)

            # Log quota
            monitor.log_quota(quota_info, notes="Manual quota check")

            # Check if should continue
            if monitor.should_continue(threshold_percent=90):
                print("✓ Budget is sufficient to continue operations")
            else:
                print("⚠️  Budget is critically low!")

            # Estimate remaining requests
            estimated = monitor.estimate_requests_remaining(
                avg_tokens_per_request=1000,
                model_cost_per_1k_tokens=0.003
            )
            print(f"\nEstimated requests remaining: ~{estimated}")
            print("(Based on 1000 tokens/request at $0.003/1k tokens)")

            # Print usage stats if logs exist
            print("\n" + "=" * 60)
            monitor.print_usage_stats()

        else:
            print("Could not retrieve quota information")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Created .env.bedrock file with your credentials")
        print("2. Set BEDROCK_TEAM_ID and BEDROCK_API_TOKEN")


if __name__ == "__main__":
    main()
