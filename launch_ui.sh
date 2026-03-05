#!/usr/bin/env bash
# launch_ui.sh — Start the AI Test Generator UI
# Usage: bash launch_ui.sh

set -e

echo ""
echo "🎭  AI Playwright Test Generator — UI Launcher"
echo "================================================"
echo ""

# Check Python
if ! command -v python &>/dev/null; then
  echo "❌  Python not found."
  exit 1
fi
echo "✅  Python: $(python --version)"

# Check uv
if ! command -v uv &>/dev/null; then
  echo "❌  uv not found. Install it with: pip install uv"
  exit 1
fi
echo "✅  uv: $(uv --version)"

# Sync dependencies (installs streamlit if missing)
echo "📦  Syncing dependencies…"
uv sync

# Activate venv if not already active
if [[ "$VIRTUAL_ENV" == "" ]]; then
  source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
fi

# Start mock site in background if it's not already running
if ! curl -s http://localhost:8080 &>/dev/null; then
  echo "🌐  Starting mock site at http://localhost:8080…"
  python -m http.server 8080 --directory generated_tests &
  MOCK_PID=$!
  sleep 1
  echo "✅  Mock site running (PID $MOCK_PID)"
else
  echo "✅  Mock site already running on port 8080"
fi

echo ""
echo "🚀  Starting UI at http://localhost:8501"
echo "    Press Ctrl+C to stop"
echo ""

uv run streamlit run streamlit_app.py \
  --server.port 8501 \
  --server.headless false \
  --browser.gatherUsageStats false \
  --theme.base dark \
  --theme.backgroundColor "#0d0f14" \
  --theme.secondaryBackgroundColor "#111318" \
  --theme.textColor "#e2e8f0" \
  --theme.primaryColor "#4ade80"
