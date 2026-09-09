# ─────────────────────────────────────────────────────────
# LEGACYX Backend — Dockerfile (Development)
# ─────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"

# Copy application source
# In dev, this is overridden by a bind mount — the COPY here is for
# production image builds or CI runs.
COPY . .

# Create storage directory
RUN mkdir -p /app/storage/repositories /app/storage/artifacts

EXPOSE 8000

# Default command (overridden in docker-compose for hot-reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
