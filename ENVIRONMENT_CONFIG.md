# 🌍 Configuração de Ambientes - GLPI Dashboard

## 📋 Índice
- [Visão Geral](#-visão-geral)
- [Ambientes](#-ambientes)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Configuração Docker](#-configuração-docker)
- [Scripts de Deploy](#-scripts-de-deploy)
- [Monitoramento](#-monitoramento)
- [Backup e Recovery](#-backup-e-recovery)

## 🎯 Visão Geral

Este documento define as configurações para diferentes ambientes do GLPI Dashboard, incluindo desenvolvimento, teste, homologação e produção.

### Ambientes Disponíveis
- **Development** (local)
- **Testing** (CI/CD)
- **Staging** (homologação)
- **Production** (produção)

## 🏗️ Ambientes

### Development Environment
```bash
# Características
- Hot reload ativado
- Debug mode habilitado
- Logs verbosos
- Cache desabilitado
- CORS permissivo
- Banco de dados local

# Portas
Frontend: 3001
Backend: 5000
Database: 3306
Redis: 6379

# URLs
Frontend: http://localhost:3001
Backend: http://localhost:5000
API: http://localhost:5000/api
```

### Testing Environment
```bash
# Características
- Testes automatizados
- Coverage reports
- Mock services
- Banco de dados em memória
- CI/CD pipeline

# Configurações
Test Database: SQLite in-memory
Test Redis: Redis mock
Test Coverage: >80%
```

### Staging Environment
```bash
# Características
- Ambiente similar à produção
- Dados de teste
- SSL/TLS habilitado
- Monitoramento básico
- Deploy automático

# URLs
Frontend: https://staging-dashboard.company.com
Backend: https://staging-api.company.com
API: https://staging-api.company.com/api
```

### Production Environment
```bash
# Características
- Alta disponibilidade
- SSL/TLS obrigatório
- Logs estruturados
- Cache otimizado
- Monitoramento completo
- Backup automático

# URLs
Frontend: https://dashboard.company.com
Backend: https://api.company.com
API: https://api.company.com/api
```

## 🔧 Variáveis de Ambiente

### Frontend (.env)
```bash
# Development
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_TITLE=GLPI Dashboard - Dev
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
VITE_DEBUG=true
VITE_ENABLE_DEVTOOLS=true

# Staging
VITE_API_BASE_URL=https://staging-api.company.com/api
VITE_APP_TITLE=GLPI Dashboard - Staging
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=staging
VITE_DEBUG=false
VITE_ENABLE_DEVTOOLS=false

# Production
VITE_API_BASE_URL=https://api.company.com/api
VITE_APP_TITLE=GLPI Dashboard
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
VITE_DEBUG=false
VITE_ENABLE_DEVTOOLS=false
VITE_SENTRY_DSN=https://your-sentry-dsn
```

### Backend (.env)
```bash
# Development
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=mysql://user:password@localhost:3306/glpi_dashboard_dev
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3001
LOG_LEVEL=DEBUG
CACHE_TTL=300

# Testing
FLASK_ENV=testing
FLASK_DEBUG=False
SECRET_KEY=test-secret-key
DATABASE_URL=sqlite:///:memory:
REDIS_URL=redis://localhost:6379/1
LOG_LEVEL=WARNING
CACHE_TTL=60

# Staging
FLASK_ENV=staging
FLASK_DEBUG=False
SECRET_KEY=${STAGING_SECRET_KEY}
DATABASE_URL=${STAGING_DATABASE_URL}
REDIS_URL=${STAGING_REDIS_URL}
CORS_ORIGINS=https://staging-dashboard.company.com
LOG_LEVEL=INFO
CACHE_TTL=900
SENTRY_DSN=${STAGING_SENTRY_DSN}

# Production
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=${PROD_SECRET_KEY}
DATABASE_URL=${PROD_DATABASE_URL}
REDIS_URL=${PROD_REDIS_URL}
CORS_ORIGINS=https://dashboard.company.com
LOG_LEVEL=WARNING
CACHE_TTL=1800
SENTRY_DSN=${PROD_SENTRY_DSN}
NEW_RELIC_LICENSE_KEY=${NEW_RELIC_KEY}
```

### Database Configuration
```bash
# Development
DB_HOST=localhost
DB_PORT=3306
DB_NAME=glpi_dashboard_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_CHARSET=utf8mb4
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Production
DB_HOST=${PROD_DB_HOST}
DB_PORT=3306
DB_NAME=glpi_dashboard_prod
DB_USER=${PROD_DB_USER}
DB_PASSWORD=${PROD_DB_PASSWORD}
DB_CHARSET=utf8mb4
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_SSL_MODE=REQUIRED
```

## 🐳 Configuração Docker

### docker-compose.yml (Development)
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3001:3001"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_BASE_URL=http://backend:5000/api
    depends_on:
      - backend
    networks:
      - glpi-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
      - DATABASE_URL=mysql://root:password@db:3306/glpi_dashboard
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - glpi-network

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=glpi_dashboard
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - glpi-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - glpi-network

volumes:
  mysql_data:
  redis_data:

networks:
  glpi-network:
    driver: bridge
```

### docker-compose.prod.yml (Production)
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - VITE_API_BASE_URL=${API_BASE_URL}
      - VITE_ENVIRONMENT=production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`dashboard.company.com`)"
      - "traefik.http.routers.frontend.tls=true"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
    networks:
      - glpi-network
      - traefik-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.company.com`)"
      - "traefik.http.routers.backend.tls=true"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
    depends_on:
      - db
      - redis
    networks:
      - glpi-network
      - traefik-network

  db:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
      - MYSQL_DATABASE=${DB_NAME}
      - MYSQL_USER=${DB_USER}
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/backup:/backup
    networks:
      - glpi-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - glpi-network

  traefik:
    image: traefik:v2.10
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "letsencrypt_data:/letsencrypt"
    networks:
      - traefik-network

volumes:
  mysql_data:
  redis_data:
  letsencrypt_data:

networks:
  glpi-network:
    driver: bridge
  traefik-network:
    external: true
```

### Dockerfile.prod (Frontend)
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Dockerfile.prod (Backend)
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

## 🚀 Scripts de Deploy

### deploy.sh (Production)
```bash
#!/bin/bash

# GLPI Dashboard Production Deploy Script
# Usage: ./deploy.sh [version]

set -e

# Configuration
PROJECT_NAME="glpi-dashboard"
DOCKER_REGISTRY="your-registry.com"
ENVIRONMENT="production"
VERSION=${1:-"latest"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting deployment of ${PROJECT_NAME} v${VERSION}${NC}"

# Pre-deployment checks
echo -e "${YELLOW}📋 Running pre-deployment checks...${NC}"

# Check if required environment variables are set
required_vars=("SECRET_KEY" "DATABASE_URL" "REDIS_URL")
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo -e "${RED}❌ Error: $var is not set${NC}"
        exit 1
    fi
done

# Check if services are healthy
echo -e "${YELLOW}🔍 Checking service health...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Backup database
echo -e "${YELLOW}💾 Creating database backup...${NC}"
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="backup_${timestamp}.sql"

docker-compose -f docker-compose.prod.yml exec -T db mysqldump \
    -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > "./database/backup/${backup_file}"

echo -e "${GREEN}✅ Backup created: ${backup_file}${NC}"

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest images...${NC}"
docker-compose -f docker-compose.prod.yml pull

# Build new images
echo -e "${YELLOW}🔨 Building new images...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Run database migrations
echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
docker-compose -f docker-compose.prod.yml run --rm backend python -m flask db upgrade

# Deploy with zero downtime
echo -e "${YELLOW}🔄 Deploying with zero downtime...${NC}"

# Start new containers
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Health check
echo -e "${YELLOW}🏥 Running health checks...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend health check passed${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
    exit 1
fi

if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    exit 1
fi

# Clean up old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f

# Send notification
echo -e "${YELLOW}📢 Sending deployment notification...${NC}"
curl -X POST "${SLACK_WEBHOOK_URL}" \
    -H 'Content-type: application/json' \
    --data "{
        \"text\": \"🚀 ${PROJECT_NAME} v${VERSION} deployed successfully to ${ENVIRONMENT}\",
        \"username\": \"Deploy Bot\",
        \"icon_emoji\": \":rocket:\"
    }"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Dashboard: https://dashboard.company.com${NC}"
echo -e "${GREEN}🔧 API: https://api.company.com${NC}"
```

### rollback.sh
```bash
#!/bin/bash

# GLPI Dashboard Rollback Script
# Usage: ./rollback.sh [backup_file]

set -e

BACKUP_FILE=${1}

if [[ -z "$BACKUP_FILE" ]]; then
    echo "❌ Error: Please specify backup file"
    echo "Usage: ./rollback.sh backup_20241229_120000.sql"
    exit 1
fi

echo "🔄 Starting rollback process..."

# Stop current services
echo "⏹️ Stopping current services..."
docker-compose -f docker-compose.prod.yml down

# Restore database
echo "💾 Restoring database from backup..."
docker-compose -f docker-compose.prod.yml up -d db
sleep 10

docker-compose -f docker-compose.prod.yml exec -T db mysql \
    -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < "./database/backup/${BACKUP_FILE}"

# Start services with previous version
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback completed successfully!"
```

## 📊 Monitoramento

### Health Check Endpoints
```python
# Backend health check
@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check Redis connection
        redis_client.ping()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', '1.0.0'),
            'environment': app.config.get('ENVIRONMENT', 'unknown'),
            'services': {
                'database': 'healthy',
                'redis': 'healthy'
            }
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }, 503

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    # Return Prometheus formatted metrics
    pass
```

### Monitoring Stack (docker-compose.monitoring.yml)
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

## 💾 Backup e Recovery

### Backup Script
```bash
#!/bin/bash

# backup.sh - Automated backup script

set -e

# Configuration
BACKUP_DIR="/backup"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Database backup
echo "📦 Creating database backup..."
mysqldump -h${DB_HOST} -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} \
    --single-transaction --routines --triggers \
    | gzip > "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"

# Redis backup
echo "📦 Creating Redis backup..."
redis-cli --rdb "${BACKUP_DIR}/redis_backup_${TIMESTAMP}.rdb"

# Application files backup
echo "📦 Creating application backup..."
tar -czf "${BACKUP_DIR}/app_backup_${TIMESTAMP}.tar.gz" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    /app

# Upload to cloud storage (AWS S3)
echo "☁️ Uploading to cloud storage..."
aws s3 cp "${BACKUP_DIR}/" "s3://${S3_BACKUP_BUCKET}/glpi-dashboard/" --recursive

# Clean old backups
echo "🧹 Cleaning old backups..."
find ${BACKUP_DIR} -name "*backup_*.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*backup_*.rdb" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "✅ Backup completed successfully!"
```

### Recovery Script
```bash
#!/bin/bash

# recovery.sh - Database recovery script
# Usage: ./recovery.sh backup_20241229_120000.sql.gz

set -e

BACKUP_FILE=${1}

if [[ -z "$BACKUP_FILE" ]]; then
    echo "❌ Error: Please specify backup file"
    exit 1
fi

echo "🔄 Starting recovery process..."

# Stop application
echo "⏹️ Stopping application..."
docker-compose down

# Start only database
echo "🗄️ Starting database..."
docker-compose up -d db
sleep 10

# Restore database
echo "💾 Restoring database..."
gunzip -c "${BACKUP_FILE}" | docker-compose exec -T db mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME}

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Recovery completed successfully!"
```

---

**Última atualização**: 2024-12-29
**Versão**: 1.0.0