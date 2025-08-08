# GLPI Dashboard Frontend Dockerfile
# ==================================

# Multi-stage build for optimized production image
FROM node:18-alpine as base

# Set environment variables
ENV NODE_ENV=production \
    NPM_CONFIG_LOGLEVEL=warn \
    NPM_CONFIG_COLOR=false

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl \
    && rm -rf /var/cache/apk/*

# Create app user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

# Set work directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Development stage
FROM base as development

# Set development environment
ENV NODE_ENV=development

# Install all dependencies (including dev dependencies)
RUN npm ci --include=dev

# Copy source code
COPY --chown=appuser:appuser frontend/ .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3001 || exit 1

# Default command for development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]

# Build stage
FROM base as builder

# Install all dependencies
RUN npm ci --include=dev

# Copy source code
COPY frontend/ .

# Set build environment variables
ENV VITE_API_BASE_URL=/api \
    VITE_APP_TITLE="GLPI Dashboard" \
    VITE_APP_VERSION="1.0.0"

# Build the application
RUN npm run build

# Remove dev dependencies and clean cache
RUN npm prune --production && \
    npm cache clean --force

# Testing stage
FROM development as testing

# Install additional testing dependencies
RUN npm install --save-dev \
    @vitest/coverage-v8 \
    @vitest/ui \
    jsdom

# Copy test configuration
COPY frontend/vitest.config.ts .
COPY frontend/src/__tests__/ src/__tests__/

# Run tests by default
CMD ["npm", "run", "test:ci"]

# Production stage
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Create nginx user and set permissions
RUN addgroup -g 1001 -S nginx-app && \
    adduser -S nginx-app -u 1001 -G nginx-app && \
    chown -R nginx-app:nginx-app /usr/share/nginx/html && \
    chown -R nginx-app:nginx-app /var/cache/nginx && \
    chown -R nginx-app:nginx-app /var/log/nginx && \
    chown -R nginx-app:nginx-app /etc/nginx/conf.d

# Switch to non-root user
USER nginx-app

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# Static file server stage (alternative to nginx)
FROM node:18-alpine as static-server

# Install serve package globally
RUN npm install -g serve

# Create app user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

# Copy built application
COPY --from=builder --chown=appuser:appuser /app/dist /app

# Switch to non-root user
USER appuser

# Set work directory
WORKDIR /app

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Serve static files
CMD ["serve", "-s", ".", "-l", "3000"]