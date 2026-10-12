# Multi-Stage Production Dockerfile for Loom Fabric
# Supports: CPU, NVIDIA CUDA, and AMD ROCm / Vulkan execution

FROM python:3.12-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install system utilities and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    pciutils \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install "fastapi>=0.110.0" "uvicorn[standard]>=0.28.0" "pydantic>=2.5.0" \
    "typer>=0.9.0" "rich>=13.7.0" "psutil>=5.9.0" "httpx>=0.27.0" "ray[default]>=2.9.0" \
    "nvidia-ml-py>=12.535.133"

# Copy source repository
COPY loom/ ./loom/
COPY scripts/ ./scripts/
COPY README.md .

# Install package in production mode
RUN pip install -e .

EXPOSE 8000

# Health check against native gateway
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch Loom Fabric Sovereign Gateway & Web Dashboard
CMD ["uvicorn", "loom.gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]
