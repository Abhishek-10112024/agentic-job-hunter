#!/usr/bin/env bash
# Start the backend API server for local development.
# Usage (from project root):
#   ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

# Activate virtual environment if present
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Install / sync dependencies from the single requirements.txt
echo "📦 Installing backend dependencies..."
pip install -q -r requirements.txt

echo "🚀 Starting Agentic Job Hunter API on http://127.0.0.1:8000 ..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload