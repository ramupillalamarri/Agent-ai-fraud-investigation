# ==============================================================================
# Build Stage
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies needed for compiling python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Production Runtime Stage
# ==============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime dependencies (e.g. libpq for pg connection)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY . .

# Create a non-root system user and change ownership
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -d /app -s /sbin/nologin appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
