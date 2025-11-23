#!/usr/bin/env python
"""
Test Runner Script

Run tests with various configurations:
- All tests: python run_tests.py
- Unit tests only: python run_tests.py --unit
- API tests only: python run_tests.py --api
- With coverage: python run_tests.py --cov
- Verbose: python run_tests.py -v
"""

import subprocess
import sys
import os
import argparse

# Ensure we're in the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BACKEND_DIR)


def run_pytest(args: list[str]) -> int:
    """Run pytest with given arguments."""
    cmd = [sys.executable, '-m', 'pytest'] + args
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser(description='Run tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--cov', action='store_true', help='Run with coverage')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-x', '--exitfirst', action='store_true', help='Exit on first failure')
    parser.add_argument('-k', type=str, help='Filter tests by keyword expression')
    parser.add_argument('--markers', action='store_true', help='Show available markers')

    args = parser.parse_args()

    pytest_args = []

    # Test selection
    if args.unit:
        pytest_args.extend(['tests/unit'])
    elif args.api:
        pytest_args.extend(['tests/api'])
    elif args.integration:
        pytest_args.extend(['tests/integration'])
    else:
        pytest_args.extend(['tests'])

    # Coverage
    if args.cov:
        pytest_args.extend([
            '--cov=.',
            '--cov-report=term-missing',
            '--cov-config=.coveragerc'
        ])
        if args.html:
            pytest_args.append('--cov-report=html')

    # Verbosity
    if args.verbose:
        pytest_args.append('-v')

    # Exit on first failure
    if args.exitfirst:
        pytest_args.append('-x')

    # Keyword filter
    if args.k:
        pytest_args.extend(['-k', args.k])

    # Show markers
    if args.markers:
        pytest_args.append('--markers')

    return run_pytest(pytest_args)


if __name__ == '__main__':
    sys.exit(main())
