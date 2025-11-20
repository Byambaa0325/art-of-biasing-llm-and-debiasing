#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check environment variables setup.

Run this script to verify your .env file is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)
print()

# Required variables
required_vars = {
    'GOOGLE_CLOUD_PROJECT': 'Google Cloud Project ID (required for Vertex AI)',
    'GCP_PROJECT_ID': 'Alternative name for project ID',
}

# Optional variables with defaults
optional_vars = {
    'GCP_LOCATION': ('us-central1', 'GCP region for Vertex AI'),
    'LLAMA_MODEL': ('llama-3.3-70b-instruct', 'Llama model name'),
    'GEMINI_MODEL': ('gemini-2.0-flash-exp', 'Gemini model name'),
    'FLASK_ENV': ('development', 'Flask environment'),
    'FLASK_DEBUG': ('True', 'Flask debug mode'),
    'PORT': ('5000', 'Server port'),
}

print("Required Variables:")
print("-" * 60)
all_required_set = True
for var, description in required_vars.items():
    value = os.getenv(var)
    if value and value != 'your-project-id':
        print(f"✓ {var:25} = {value}")
    else:
        print(f"✗ {var:25} = NOT SET - {description}")
        all_required_set = False

print()
print("Optional Variables:")
print("-" * 60)
for var, (default, description) in optional_vars.items():
    value = os.getenv(var, default)
    if value == default:
        print(f"  {var:25} = {value} (default) - {description}")
    else:
        print(f"✓ {var:25} = {value} - {description}")

print()
print("=" * 60)
if all_required_set:
    print("✓ All required variables are set!")
    print()
    print("Next steps:")
    print("1. Authenticate with Google Cloud:")
    print("   gcloud auth application-default login")
    print("2. Start the server:")
    print("   cd backend && python api.py")
else:
    print("✗ Some required variables are missing!")
    print()
    print("To fix:")
    print("1. Create .env file: cp .env.example .env")
    print("2. Edit .env and set GOOGLE_CLOUD_PROJECT=your-project-id")
    print("3. Run this script again to verify")
print("=" * 60)

