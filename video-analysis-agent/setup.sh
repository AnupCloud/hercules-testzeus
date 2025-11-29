#!/bin/bash
# Quick setup script using uv

echo "🚀 Setting up Video Analysis Agent with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment using uv
echo "📦 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -e .

echo ""
echo "✨ Setup complete!"
echo ""
echo "To run the agent:"
echo "  source .venv/bin/activate"
echo "  python main.py --planning-log sample_inputs/agent_inner_logs.json \\"
echo "                 --video sample_inputs/video.webm \\"
echo "                 --test-output sample_inputs/test_result.xml"
