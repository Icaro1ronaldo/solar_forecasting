
#!/bin/bash

# Colors and icons
GREEN="\e[32m"
BLUE="\e[34m"
RESET="\e[0m"
CHECK="✅"
INFO="ℹ️"
ROCKET="🚀"

# Ensure Poetry is in PATH
export PATH="$HOME/.local/bin:$PATH"


echo -e "${INFO} ${ROCKET} Setting up Poetry environment..."

# Install Poetry (official method)
echo -e "${INFO} Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
echo -e "${GREEN}${CHECK} Poetry installed successfully!${RESET}"
echo -e "${INFO} Poetry already installed, skipping."

# Create .venv folder if not exists

echo -e "${INFO} Creating .venv directory..."
python -m venv .venv
echo -e "${GREEN}${CHECK} .venv directory created!${RESET}"


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
