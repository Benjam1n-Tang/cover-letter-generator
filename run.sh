#!/bin/bash

# Cover Letter Generator Startup Script

echo "🚀 Starting Cover Letter Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for GitHub token
if grep -q "your_github_token_here" .env; then
    echo "⚠️  WARNING: Please update your GitHub token in the .env file"
    echo "   Visit: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
    echo ""
fi

# Start the application
echo "🌐 Starting web server on http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

./venv/bin/python main.py