#!/usr/bin/env bash
set -euo pipefail

IP="${1:-0.0.0.0}"
PORT="${2:-8643}"
cd "$(dirname "$0")"

# Check if .env exists, if not create from example
if [[ ! -f ".env" ]]; then
    cp .env.example .env
fi

source "${HOME}/venv/$(basename "$PWD")/bin/activate"

echo "🎵 MiniMax-Music3 — starting on http://${IP}:${PORT}"
echo "   Open: http://${IP}:${PORT}"
echo "   Press Ctrl+C to stop"

exec uvicorn backend.main:app --host "$IP" --port "$PORT"
