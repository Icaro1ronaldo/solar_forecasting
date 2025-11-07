
FROM mcr.microsoft.com/devcontainers/python:3.10

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /workspace
