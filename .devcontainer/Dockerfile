FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# Install low-level dependencies for LightGBM and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/prescriptai