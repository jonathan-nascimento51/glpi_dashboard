# GLPI Dashboard Docker Configuration

This directory contains all Docker-related configurations for the GLPI Dashboard project, including multi-environment support, monitoring, logging, and development tools.

## 📁 Directory Structure

```
docker/
├── backend/
│   └── Dockerfile              # Multi-stage backend container
├── frontend/
│   └── Dockerfile              # Multi-stage frontend container
├── nginx/
│   ├── nginx.conf              # Main Nginx configuration
│   └── conf.d/
│       ├── default.conf        # Default server configuration
│       ├── dev.conf           # Development environment
│       └── prod.conf          # Production environment
├── redis/
│   ├── redis.conf             # Development Redis config
│   └── redis-prod.conf        # Production Redis config
├── prometheus/
│   └── prometheus.yml         # Monitoring configuration
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml # Grafana datasources
│   │   └── dashboards/
│   │       └── dashboards.yml # Dashboard provisioning
│   └── dashboards/
│       └── glpi-dashboard.json # Main dashboard
├── fluentd/
│   ├── Dockerfile             # Custom Fluentd image
│   └── fluent.conf           # Log aggregation config
├── dev-tools/
│   ├── Dockerfile             # Development utilities
│   ├── init-dev.sh           # Environment initialization
│   └── run-tests.sh          # Test runner script
└── README.md                  # This file
```

## 🚀 Quick Start

### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Initialize development environment
docker-compose exec dev-tools /workspace/docker/dev-tools/init-dev.sh

# View logs
docker-compose logs -f
```

### Production Environment

```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f
```

### Monitoring Stack

```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access Grafana: http://localhost:3000 (admin/admin)
# Access Prometheus: http://localhost:9090
```

## 🐳 Docker Images

### Backend (Flask API)

**Multi-stage build with targets:**
- `base`: Common dependencies and user setup
- `development`: Development dependencies and Flask dev server
- `testing`: Testing dependencies and pytest
- `production`: Optimized for production with Gunicorn
- `security`: Security scanning tools

**Features:**
- Non-root user execution
- Health checks
- Optimized layer caching
- Security best practices

### Frontend (React/Vite)

**Multi-stage build with targets:**
- `base`: Node.js setup and common dependencies
- `development`: Development server with HMR
- `builder`: Build optimized production assets
- `testing`: Testing environment with Jest
- `production`: Nginx serving static files
- `static-server`: Alternative static file server

**Features:**
- Hot module replacement in development
- Optimized production builds
- Nginx serving with caching
- Health checks

### Development Tools

**Includes:**
- Python 3.11 with development tools
- Node.js with package managers
- Code quality tools (black, isort, flake8, mypy, eslint, prettier)
- Testing frameworks (pytest, jest)
- Docker CLI and Docker Compose
- Git and development utilities
- Oh My Bash with custom aliases

### Fluentd (Log Aggregation)

**Features:**
- Custom plugins for Elasticsearch, GeoIP, filtering
- Log parsing for Nginx, Flask, Redis
- Rate limiting and sampling
- Multiple output targets
- Health checks

## 🔧 Configuration Files

### Docker Compose Files

- `docker-compose.yml`: Base services (Redis, Backend, Frontend)
- `docker-compose.dev.yml`: Development overrides
- `docker-compose.prod.yml`: Production configuration

### Nginx Configuration

- **Development**: Proxy to dev servers, CORS enabled, relaxed timeouts
- **Production**: SSL termination, security headers, caching, rate limiting
- **Features**: Health checks, status endpoints, static file serving

### Redis Configuration

- **Development**: Relaxed settings, keyspace notifications
- **Production**: Security hardening, memory optimization, persistence

### Monitoring

- **Prometheus**: Scrapes metrics from all services
- **Grafana**: Pre-configured dashboards and datasources
- **Targets**: Application metrics, system metrics, logs

## 🛠️ Development Workflow

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd glpi_dashboard

# Start development environment
make docker-dev-up

# Initialize development environment
make dev-init
```

### 2. Development Commands

```bash
# Start backend development server
make dev-backend

# Start frontend development server
make dev-frontend

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

### 3. Testing

```bash
# Run all tests
docker-compose exec dev-tools ./run-tests.sh

# Run specific test types
docker-compose exec dev-tools ./run-tests.sh -t backend -c
docker-compose exec dev-tools ./run-tests.sh -t frontend -w
docker-compose exec dev-tools ./run-tests.sh -t unit -f
```

## 📊 Monitoring and Logging

### Grafana Dashboards

- **GLPI Dashboard Overview**: Application metrics, request rates, response times
- **System Monitoring**: Resource usage, container health
- **Application Metrics**: Custom business metrics

### Log Aggregation

- **Fluentd**: Collects logs from all services
- **Parsing**: Structured logging for Nginx, Flask, Redis
- **Outputs**: Elasticsearch (if available), file-based fallback
- **Features**: GeoIP enrichment, rate limiting, filtering

### Metrics Collection

- **Prometheus**: Time-series metrics database
- **Targets**: Application, system, and infrastructure metrics
- **Retention**: Configurable data retention policies

## 🔒 Security

### Container Security

- Non-root user execution
- Minimal base images
- Security scanning with tools
- Read-only root filesystems where possible
- Resource limits and constraints

### Network Security

- Internal Docker networks
- Service isolation
- Nginx security headers
- Rate limiting and DDoS protection

### Secrets Management

- Environment variable injection
- Docker secrets support
- No hardcoded credentials

## 🚀 Production Deployment

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- SSL certificates (for HTTPS)
- Environment variables configured

### Deployment Steps

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with production values

# 2. Build images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Verify deployment
docker-compose ps
docker-compose logs
```

### Health Checks

- All services include health check endpoints
- Automatic restart on failure
- Load balancer integration ready

## 🔧 Customization

### Adding New Services

1. Create service directory in `docker/`
2. Add Dockerfile and configuration
3. Update docker-compose files
4. Add monitoring and logging
5. Update documentation

### Environment-Specific Overrides

- Use Docker Compose override files
- Environment variable substitution
- Volume mounts for configuration

### Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3
```

## 📝 Troubleshooting

### Common Issues

1. **Port conflicts**: Check for running services on required ports
2. **Permission issues**: Ensure proper file permissions
3. **Memory issues**: Increase Docker memory limits
4. **Network issues**: Check Docker network configuration

### Debugging Commands

```bash
# View service logs
docker-compose logs <service-name>

# Execute commands in containers
docker-compose exec <service-name> bash

# Check service health
docker-compose ps

# Inspect networks
docker network ls
docker network inspect <network-name>

# Check resource usage
docker stats
```

### Log Locations

- Application logs: `logs/` directory
- Container logs: `docker-compose logs`
- Nginx logs: `/var/log/nginx/`
- Fluentd logs: `/var/log/fluentd-output/`

## 🤝 Contributing

1. Follow Docker best practices
2. Update documentation for changes
3. Test in both development and production modes
4. Add monitoring for new services
5. Include health checks

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Fluentd Documentation](https://docs.fluentd.org/)