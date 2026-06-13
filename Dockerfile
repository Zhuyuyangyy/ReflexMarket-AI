# ReflexMarket-AI Dockerfile
# Multi-stage build for production deployment

# ── Stage 1: Builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production ──────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="ReflexMarket-AI Team"
LABEL description="Financial Reflexivity Multi-Agent Simulation API"
LABEL version="1.0.0"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY experiments/ ./experiments/
COPY tests/ ./tests/
COPY requirements.txt .

# Set environment variables
ENV PYTHONPATH=/app:/app/backend/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8020

# Expose port
EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8020/health')" || exit 1

# Switch to non-root user
USER appuser

# Start the application
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8020"]
