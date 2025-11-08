# Set the workspace folder variable
workspaceFolder="/workspaces/solar_forecasting"
cd ${workspaceFolder}

# Activate the appropriate submodule(s)
pip install pre-commit
git submodule init
git submodule update
echo "Submodules initialized and updated."

# Create the .venv and run poetry
python3 -m venv ${workspaceFolder}/.venv
source ${workspaceFolder}/.venv/bin/activate
pipx install poetry
poetry install --no-root
pre-commit install
