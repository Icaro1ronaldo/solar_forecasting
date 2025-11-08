
#!/bin/bash

# Colors and icons
GREEN="\e[32m"
BLUE="\e[34m"
RESET="\e[0m"
CHECK="✅"
INFO="ℹ️"
ROCKET="🚀"

echo -e "${INFO} ${ROCKET} Setting up Poetry environment..."

# Install Poetry (official method)
if ! command -v poetry &> /dev/null; then
    echo -e "${INFO} Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="/root/.local/bin:$PATH"
    echo -e "${GREEN}${CHECK} Poetry installed successfully!${RESET}"
else
    echo -e "${INFO} Poetry already installed, skipping."
fi

# Create .venv folder if not exists
if [ ! -d ".venv" ]; then
    echo -e "${INFO} Creating .venv directory..."
    python -m venv .venv
    echo -e "${GREEN}${CHECK} .venv directory created!${RESET}"
else
    echo -e "${INFO} .venv already exists, skipping creation."
fi

# Activate .venv environment
echo -e "${INFO} Activating .venv environment..."
source .venv/bin/activate
echo -e "${GREEN}${CHECK} .venv activated!${RESET}"

# Install dependencies with Poetry
echo -e "${INFO} Installing dependencies with Poetry..."
poetry install
echo -e "${GREEN}${CHECK} Poetry setup complete!${RESET}"

# Activate Poetry shell
echo -e "${INFO} Activating Poetry shell..."
poetry shell
