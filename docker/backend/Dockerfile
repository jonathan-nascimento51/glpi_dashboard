# GLPI Dashboard Backend Dockerfile
# =================================

# Multi-stage build for optimized production image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -e .[dev,testing,linting]

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p logs .cache && \
    chown -R appuser:appuser logs .cache

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command for development
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]

# Testing stage
FROM development as testing

# Install additional testing tools
RUN pip install pytest-xdist pytest-benchmark pytest-mock

# Copy test files
COPY --chown=appuser:appuser tests/ tests/

# Run tests by default
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=backend", "--cov=scripts", "--cov-report=html", "--cov-report=term-missing"]

# Production stage
FROM base as production

# Install only production dependencies
RUN pip install --no-dev .

# Copy application code
COPY --chown=appuser:appuser backend/ backend/
COPY --chown=appuser:appuser scripts/ scripts/
COPY --chown=appuser:appuser pyproject.toml ./

# Create necessary directories
RUN mkdir -p logs .cache && \
    chown -R appuser:appuser logs .cache

# Remove unnecessary packages to reduce image size
RUN apt-get purge -y build-essential git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "30", "--keepalive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "warning", "backend.app:create_app()"]

# Security stage (optional)
FROM production as security

# Install security scanning tools
USER root
RUN pip install safety bandit

# Run security checks
RUN safety check && \
    bandit -r backend/ scripts/ -f json -o security-report.json || true

USER appuser