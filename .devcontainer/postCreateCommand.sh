
#!/bin/bash
set -euo pipefail

# -------------------------------
# Solar Forecasting Dev Setup
# -------------------------------

# Define workspace folder
WORKSPACE_FOLDER="/workspaces/solar_forecasting"
cd "${WORKSPACE_FOLDER}"

echo "🔧 Installing pre-commit..."
pip install --quiet pre-commit

echo "🔄 Initializing Git submodules..."
git submodule init
git submodule update
echo "✅ Submodules initialized."

# -------------------------------
# Environment Configuration
# -------------------------------

ENV_FILE="${WORKSPACE_FOLDER}/.env"
PYTHONPATH_LINE="PYTHONPATH=\$PYTHONPATH:/workspaces/solar_forecasting"

# Add PYTHONPATH to .env if not already present
if ! grep -Fxq "$PYTHONPATH_LINE" "$ENV_FILE"; then
  echo "$PYTHONPATH_LINE" >> "$ENV_FILE"
  echo "✅ PYTHONPATH added to .env"
else
  echo "ℹ️ PYTHONPATH already set in .env"
fi

# -------------------------------
# Python Environment Setup
# -------------------------------

echo "🐍 Creating virtual environment..."
python3 -m venv "${WORKSPACE_FOLDER}/.venv"
source "${WORKSPACE_FOLDER}/.venv/bin/activate"

echo "📦 Installing Poetry via pipx..."
pip install --quiet pipx
pipx ensurepath
pipx install poetry

echo "📜 Installing dependencies with Poetry..."
poetry install --no-root

echo "🔗 Installing pre-commit hooks..."
pre-commit install

echo "✅ Dev container setup complete."
