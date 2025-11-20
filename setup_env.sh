#!/bin/bash
# Setup script to create .env file from .env.example

echo "========================================"
echo "Environment Variables Setup"
echo "========================================"
echo ""

if [ ! -f .env.example ]; then
    echo "ERROR: .env.example file not found!"
    echo "Please create it first."
    exit 1
fi

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "✓ .env file created successfully!"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and set your GOOGLE_CLOUD_PROJECT"
    echo ""
    read -p "Open .env file for editing? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
    echo ""
    echo "After editing, run: python check_env.py"
    echo "to verify your configuration."
else
    echo ".env file already exists."
    echo ""
    echo "To recreate it, delete .env and run this script again."
    echo ""
    echo "Current .env file location: $(pwd)/.env"
fi

