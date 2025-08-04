# =============================================================================
# Garden Planner Pro - Unified Multi-Stage Dockerfile
# Supports: development, production backend, production frontend
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Backend Dependencies Builder
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm as backend-builder

# Set environment variables for build efficiency
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for dependency isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Frontend Builder  
# -----------------------------------------------------------------------------
FROM node:18-alpine as frontend-builder

WORKDIR /app

# Copy package files for dependency caching
COPY package*.json ./

# Install dependencies (production only for smaller build)
RUN npm ci --only=production && npm cache clean --force

# Copy source code and build
COPY . .
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Development Backend (for docker-compose dev)
# -----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm as development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies for development
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly (no venv for dev simplicity)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

# Development command (with auto-reload)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

# -----------------------------------------------------------------------------
# Stage 4: Production Backend
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm as production

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=backend-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/cache && \
    chown -R appuser:appuser /app

# Switch to non-root user for security
USER appuser

EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with multiple workers
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]

# -----------------------------------------------------------------------------
# Stage 5: Production Frontend (Nginx)
# -----------------------------------------------------------------------------
FROM nginx:alpine as frontend-production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy unified nginx configuration
COPY config/nginx.conf /etc/nginx/nginx.conf

# Copy built application from frontend builder
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Create non-root user for security
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Set proper permissions for nginx directories
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

EXPOSE 80

# Health check for load balancer
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]

# -----------------------------------------------------------------------------
# Usage Examples:
#
# Development:
#   docker build --target development -t garden-planner:dev .
#
# Production Backend:  
#   docker build --target backend-production -t garden-planner:backend .
#
# Production Frontend:
#   docker build --target frontend-production -t garden-planner:frontend .
#
# Or use docker-compose which targets the appropriate stages automatically
# -----------------------------------------------------------------------------