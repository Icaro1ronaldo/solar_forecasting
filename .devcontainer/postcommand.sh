#!/bin/bash
echo "🚀 Setting up Poetry environment..."

# Install Poetry (official method)
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH for this session
export PATH="/root/.local/bin:$PATH"

# Install dependencies
poetry install

echo "✅ Poetry setup complete!"
