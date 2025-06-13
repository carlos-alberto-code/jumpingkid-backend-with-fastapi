FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install Poetry
RUN pip install poetry==1.8.0

# Install PostgreSQL client
RUN apt-get update && apt-get install -y \
    postgresql-client \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure Poetry
RUN poetry config virtualenvs.create true
RUN poetry config virtualenvs.in-project false
RUN poetry config virtualenvs.path ~/.cache/pypoetry/virtualenvs

# Set the default user to vscode
USER vscode
