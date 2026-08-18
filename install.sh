#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$PROJECT_ROOT")"
VENV_DIR="${HOME}/venv/${PROJECT_NAME}"

echo "🚀 ${PROJECT_NAME} — Setup"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ python3 not found."
    exit 1
fi

# Create venv (idempotent)
if [[ ! -d "${VENV_DIR}" ]]; then
    python3 -m venv "${VENV_DIR}"
    echo "✅ Created venv at ${VENV_DIR}"
else
    echo "ℹ️  Venv already exists at ${VENV_DIR} — skipping."
fi

# Activate
source "${VENV_DIR}/bin/activate"
echo "✅ Activated: ${VENV_DIR}/bin/python"

# Upgrade pip and install
pip install --upgrade pip --quiet

if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt --quiet
    echo "✅ Dependencies installed"
else
    echo "⚠️  No requirements.txt found"
fi

# Create .env if missing
if [[ ! -f ".env" ]]; then
    cp .env.example .env
    echo "📝 Created .env from .env.example"
fi

# Create temp dir for generated audio
mkdir -p temp

echo "─────────────────────────────────────────────"
echo "✅ Setup complete!"
echo "   Venv:     ${VENV_DIR}"
echo "   Backend:  backend/"
echo "   Frontend: frontend/"
echo "   Start:    bash run.sh [IP] [PORT]"
echo "─────────────────────────────────────────────"
