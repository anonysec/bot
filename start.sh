#!/bin/bash
# VPN Bot Start Script

echo "🚀 Starting VPN Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./scripts/install.py first"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d venv ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the bot
echo "🤖 Starting bot..."
cd src
python main.py