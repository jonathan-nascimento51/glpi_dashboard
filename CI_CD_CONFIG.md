# 🔄 Configuração CI/CD - GLPI Dashboard

## 📋 Índice
- [Visão Geral](#-visão-geral)
- [GitHub Actions](#-github-actions)
- [Pipeline Stages](#-pipeline-stages)
- [Quality Gates](#-quality-gates)
- [Security Scanning](#-security-scanning)
- [Deployment Strategies](#-deployment-strategies)
- [Monitoring e Alertas](#-monitoring-e-alertas)

## 🎯 Visão Geral

Este documento define a configuração completa de CI/CD para o GLPI Dashboard, incluindo pipelines automatizados, quality gates, security scanning e deployment strategies.

### Objetivos
- ✅ Automação completa do pipeline
- 🔍 Quality gates rigorosos
- 🛡️ Security scanning integrado
- 🚀 Deploy automático por ambiente
- 📊 Monitoramento e alertas
- 🔄 Rollback automático

## 🔧 GitHub Actions

### .github/workflows/ci.yml
```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ==========================================
  # FRONTEND JOBS
  # ==========================================
  frontend-lint:
    name: 🔍 Frontend Lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 📦 Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: 📥 Install dependencies
        run: npm ci
      
      - name: 🔍 Run ESLint
        run: npm run lint
      
      - name: 🎨 Check Prettier
        run: npm run format:check
      
      - name: 📝 Type check
        run: npm run type-check

  frontend-test:
    name: 🧪 Frontend Tests
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 📦 Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: 📥 Install dependencies
        run: npm ci
      
      - name: 🧪 Run unit tests
        run: npm run test:coverage
      
      - name: 📊 Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/lcov.info
          flags: frontend
          name: frontend-coverage
      
      - name: 📋 Comment coverage on PR
        if: github.event_name == 'pull_request'
        uses: romeovs/lcov-reporter-action@v0.3.1
        with:
          lcov-file: ./frontend/coverage/lcov.info
          github-token: ${{ secrets.GITHUB_TOKEN }}

  frontend-e2e:
    name: 🎭 Frontend E2E Tests
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 📦 Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: 📥 Install dependencies
        run: npm ci
      
      - name: 🏗️ Build application
        run: npm run build
      
      - name: 🎭 Install Playwright
        run: npx playwright install --with-deps
      
      - name: 🎭 Run E2E tests
        run: npm run test:e2e
      
      - name: 📸 Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/

  frontend-build:
    name: 🏗️ Frontend Build
    runs-on: ubuntu-latest
    needs: [frontend-lint, frontend-test]
    defaults:
      run:
        working-directory: ./frontend
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 📦 Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: 📥 Install dependencies
        run: npm ci
      
      - name: 🏗️ Build application
        run: npm run build
      
      - name: 📦 Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/dist/

  # ==========================================
  # BACKEND JOBS
  # ==========================================
  backend-lint:
    name: 🔍 Backend Lint
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: 📥 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: 🔍 Run flake8
        run: flake8 .
      
      - name: 🔍 Run black
        run: black --check .
      
      - name: 🔍 Run isort
        run: isort --check-only .
      
      - name: 🔍 Run mypy
        run: mypy .

  backend-test:
    name: 🧪 Backend Tests
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: 📥 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: 🧪 Run unit tests
        env:
          DATABASE_URL: mysql://root:test_password@localhost:3306/test_db
          REDIS_URL: redis://localhost:6379/0
          FLASK_ENV: testing
        run: |
          pytest --cov=. --cov-report=xml --cov-report=html
      
      - name: 📊 Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: backend
          name: backend-coverage

  # ==========================================
  # SECURITY SCANNING
  # ==========================================
  security-scan:
    name: 🛡️ Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🔍 Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: 📋 Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: 🔍 Frontend security audit
        working-directory: ./frontend
        run: |
          npm audit --audit-level=high
      
      - name: 🔍 Backend security scan
        run: |
          pip install safety
          safety check
      
      - name: 🔍 Run CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: javascript,python

  # ==========================================
  # DOCKER BUILD
  # ==========================================
  docker-build:
    name: 🐳 Docker Build
    runs-on: ubuntu-latest
    needs: [frontend-build, backend-test]
    if: github.event_name != 'pull_request'
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🔐 Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: 📋 Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: 🏗️ Build and push Docker images
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ==========================================
  # QUALITY GATE
  # ==========================================
  quality-gate:
    name: 🚪 Quality Gate
    runs-on: ubuntu-latest
    needs: [frontend-test, backend-test, security-scan]
    if: always()
    
    steps:
      - name: 📊 Check quality gate
        run: |
          if [[ "${{ needs.frontend-test.result }}" != "success" ]]; then
            echo "❌ Frontend tests failed"
            exit 1
          fi
          
          if [[ "${{ needs.backend-test.result }}" != "success" ]]; then
            echo "❌ Backend tests failed"
            exit 1
          fi
          
          if [[ "${{ needs.security-scan.result }}" != "success" ]]; then
            echo "❌ Security scan failed"
            exit 1
          fi
          
          echo "✅ All quality gates passed!"
```

### .github/workflows/deploy.yml
```yaml
name: Deploy Pipeline

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ==========================================
  # STAGING DEPLOYMENT
  # ==========================================
  deploy-staging:
    name: 🚀 Deploy to Staging
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'staging')
    environment:
      name: staging
      url: https://staging-dashboard.company.com
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🔐 Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: 🚀 Deploy to ECS
        run: |
          # Update ECS service with new image
          aws ecs update-service \
            --cluster glpi-dashboard-staging \
            --service glpi-dashboard-staging \
            --force-new-deployment
      
      - name: ⏳ Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster glpi-dashboard-staging \
            --services glpi-dashboard-staging
      
      - name: 🏥 Health check
        run: |
          for i in {1..30}; do
            if curl -f https://staging-api.company.com/health; then
              echo "✅ Health check passed"
              break
            fi
            echo "⏳ Waiting for service to be healthy..."
            sleep 10
          done
      
      - name: 📢 Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          fields: repo,message,commit,author,action,eventName,ref,workflow

  # ==========================================
  # PRODUCTION DEPLOYMENT
  # ==========================================
  deploy-production:
    name: 🚀 Deploy to Production
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v') || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production')
    environment:
      name: production
      url: https://dashboard.company.com
    needs: [deploy-staging]
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🔐 Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: 💾 Create backup
        run: |
          # Create database backup before deployment
          aws rds create-db-snapshot \
            --db-instance-identifier glpi-dashboard-prod \
            --db-snapshot-identifier glpi-dashboard-backup-$(date +%Y%m%d-%H%M%S)
      
      - name: 🚀 Blue-Green Deployment
        run: |
          # Implement blue-green deployment strategy
          ./scripts/blue-green-deploy.sh production
      
      - name: 🏥 Health check
        run: |
          for i in {1..30}; do
            if curl -f https://api.company.com/health; then
              echo "✅ Health check passed"
              break
            fi
            echo "⏳ Waiting for service to be healthy..."
            sleep 10
          done
      
      - name: 🔄 Rollback on failure
        if: failure()
        run: |
          echo "❌ Deployment failed, initiating rollback..."
          ./scripts/rollback.sh production
      
      - name: 📢 Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          fields: repo,message,commit,author,action,eventName,ref,workflow
```

### .github/workflows/security.yml
```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  security-audit:
    name: 🛡️ Security Audit
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🔍 OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'GLPI Dashboard'
          path: '.'
          format: 'ALL'
      
      - name: 📋 Upload OWASP results
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: reports/
      
      - name: 🔍 Snyk Security Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
      
      - name: 🔍 Container Security Scan
        run: |
          docker run --rm -v "$PWD":/app \
            aquasec/trivy:latest fs /app \
            --format sarif \
            --output /app/trivy-results.sarif
      
      - name: 📋 Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

## 🎯 Pipeline Stages

### Stage 1: Code Quality
```yaml
# Executado em paralelo
- Frontend Lint (ESLint, Prettier, TypeScript)
- Backend Lint (Flake8, Black, isort, mypy)
- Security Scan (Trivy, npm audit, safety)
```

### Stage 2: Testing
```yaml
# Executado após Stage 1
- Frontend Unit Tests (Vitest + Coverage)
- Backend Unit Tests (pytest + Coverage)
- Frontend E2E Tests (Playwright)
- Integration Tests
```

### Stage 3: Build
```yaml
# Executado após Stage 2
- Frontend Build (Vite)
- Docker Image Build
- Artifact Upload
```

### Stage 4: Deploy
```yaml
# Executado após Stage 3 (apenas em branches específicas)
- Deploy to Staging (automático em main)
- Deploy to Production (manual ou tags)
- Health Checks
- Rollback (se necessário)
```

## 🚪 Quality Gates

### Frontend Quality Gates
```yaml
requirements:
  - ✅ ESLint: 0 errors
  - ✅ TypeScript: 0 errors
  - ✅ Test Coverage: ≥ 80%
  - ✅ Build: Success
  - ✅ Bundle Size: < 2MB
  - ✅ Performance: Lighthouse Score ≥ 90
```

### Backend Quality Gates
```yaml
requirements:
  - ✅ Flake8: 0 errors
  - ✅ MyPy: 0 errors
  - ✅ Test Coverage: ≥ 85%
  - ✅ Security: 0 high/critical vulnerabilities
  - ✅ Performance: Response time < 200ms
```

### Security Quality Gates
```yaml
requirements:
  - ✅ Dependency Scan: 0 critical vulnerabilities
  - ✅ Container Scan: 0 high/critical vulnerabilities
  - ✅ Code Scan: 0 security issues
  - ✅ License Check: All approved licenses
```

## 🛡️ Security Scanning

### Tools Utilizadas

#### Frontend Security
```bash
# npm audit - Vulnerabilidades em dependências
npm audit --audit-level=high

# Snyk - Análise de vulnerabilidades
snyk test --severity-threshold=high

# ESLint Security Plugin
npm install eslint-plugin-security
```

#### Backend Security
```bash
# Safety - Vulnerabilidades em dependências Python
safety check

# Bandit - Análise de código Python
bandit -r .

# Semgrep - Análise estática de código
semgrep --config=auto .
```

#### Container Security
```bash
# Trivy - Scanner de vulnerabilidades
trivy image glpi-dashboard:latest

# Hadolint - Dockerfile linter
hadolint Dockerfile

# Docker Bench - Security benchmark
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /etc:/etc:ro \
  -v /usr/bin/docker-containerd:/usr/bin/docker-containerd:ro \
  -v /usr/bin/docker-runc:/usr/bin/docker-runc:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --label docker_bench_security \
  docker/docker-bench-security
```

## 🚀 Deployment Strategies

### Blue-Green Deployment
```bash
#!/bin/bash
# blue-green-deploy.sh

ENVIRONMENT=$1
CURRENT_COLOR=$(aws elbv2 describe-target-groups --names "${ENVIRONMENT}-current" --query 'TargetGroups[0].Tags[?Key==`Color`].Value' --output text)

if [ "$CURRENT_COLOR" = "blue" ]; then
    NEW_COLOR="green"
else
    NEW_COLOR="blue"
fi

echo "🔄 Deploying to $NEW_COLOR environment..."

# Deploy to new color
aws ecs update-service \
    --cluster "glpi-dashboard-${ENVIRONMENT}" \
    --service "glpi-dashboard-${ENVIRONMENT}-${NEW_COLOR}" \
    --force-new-deployment

# Wait for deployment
aws ecs wait services-stable \
    --cluster "glpi-dashboard-${ENVIRONMENT}" \
    --services "glpi-dashboard-${ENVIRONMENT}-${NEW_COLOR}"

# Health check
if curl -f "https://${ENVIRONMENT}-api.company.com/health"; then
    echo "✅ Health check passed, switching traffic..."
    
    # Switch load balancer target
    aws elbv2 modify-listener \
        --listener-arn "${LISTENER_ARN}" \
        --default-actions Type=forward,TargetGroupArn="${NEW_COLOR_TARGET_GROUP_ARN}"
    
    echo "🎉 Deployment completed successfully!"
else
    echo "❌ Health check failed, keeping current environment"
    exit 1
fi
```

### Canary Deployment
```bash
#!/bin/bash
# canary-deploy.sh

ENVIRONMENT=$1
CANARY_PERCENTAGE=${2:-10}

echo "🐤 Starting canary deployment with ${CANARY_PERCENTAGE}% traffic..."

# Deploy canary version
aws ecs update-service \
    --cluster "glpi-dashboard-${ENVIRONMENT}" \
    --service "glpi-dashboard-${ENVIRONMENT}-canary" \
    --force-new-deployment

# Configure traffic split
aws elbv2 modify-listener \
    --listener-arn "${LISTENER_ARN}" \
    --default-actions Type=forward,ForwardConfig="{
        \"TargetGroups\": [
            {\"TargetGroupArn\": \"${STABLE_TARGET_GROUP_ARN}\", \"Weight\": $((100-CANARY_PERCENTAGE))},
            {\"TargetGroupArn\": \"${CANARY_TARGET_GROUP_ARN}\", \"Weight\": ${CANARY_PERCENTAGE}}
        ]
    }"

# Monitor metrics for 10 minutes
echo "📊 Monitoring canary metrics..."
sleep 600

# Check error rate
ERROR_RATE=$(aws cloudwatch get-metric-statistics \
    --namespace "AWS/ApplicationELB" \
    --metric-name "HTTPCode_Target_5XX_Count" \
    --dimensions Name=TargetGroup,Value="${CANARY_TARGET_GROUP_ARN}" \
    --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 600 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text)

if [ "$ERROR_RATE" -lt 5 ]; then
    echo "✅ Canary metrics look good, promoting to 100%..."
    
    # Promote canary to 100%
    aws elbv2 modify-listener \
        --listener-arn "${LISTENER_ARN}" \
        --default-actions Type=forward,TargetGroupArn="${CANARY_TARGET_GROUP_ARN}"
    
    echo "🎉 Canary deployment promoted successfully!"
else
    echo "❌ Canary metrics show issues, rolling back..."
    
    # Rollback to stable
    aws elbv2 modify-listener \
        --listener-arn "${LISTENER_ARN}" \
        --default-actions Type=forward,TargetGroupArn="${STABLE_TARGET_GROUP_ARN}"
    
    exit 1
fi
```

## 📊 Monitoring e Alertas

### CloudWatch Alarms
```yaml
# cloudwatch-alarms.yml
Resources:
  HighErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: GLPI-Dashboard-High-Error-Rate
      AlarmDescription: High error rate detected
      MetricName: HTTPCode_Target_5XX_Count
      Namespace: AWS/ApplicationELB
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSTopicArn
  
  HighLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: GLPI-Dashboard-High-Latency
      AlarmDescription: High response latency detected
      MetricName: TargetResponseTime
      Namespace: AWS/ApplicationELB
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 2.0
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSTopicArn
  
  LowHealthyHostsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: GLPI-Dashboard-Low-Healthy-Hosts
      AlarmDescription: Low number of healthy hosts
      MetricName: HealthyHostCount
      Namespace: AWS/ApplicationELB
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: LessThanThreshold
      AlarmActions:
        - !Ref SNSTopicArn
```

### Slack Notifications
```python
# notifications.py
import requests
import json
from datetime import datetime

def send_slack_notification(webhook_url, message, color="good"):
    """Send notification to Slack."""
    payload = {
        "attachments": [{
            "color": color,
            "fields": [
                {
                    "title": "GLPI Dashboard Deployment",
                    "value": message,
                    "short": False
                },
                {
                    "title": "Timestamp",
                    "value": datetime.utcnow().isoformat(),
                    "short": True
                }
            ]
        }]
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

def notify_deployment_success(environment, version):
    """Notify successful deployment."""
    message = f"🚀 Successfully deployed version {version} to {environment}"
    send_slack_notification(SLACK_WEBHOOK_URL, message, "good")

def notify_deployment_failure(environment, error):
    """Notify deployment failure."""
    message = f"❌ Deployment to {environment} failed: {error}"
    send_slack_notification(SLACK_WEBHOOK_URL, message, "danger")

def notify_rollback(environment, version):
    """Notify rollback."""
    message = f"🔄 Rolled back {environment} to version {version}"
    send_slack_notification(SLACK_WEBHOOK_URL, message, "warning")
```

### Performance Monitoring
```javascript
// performance-monitoring.js
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      pageLoadTime: 0,
      apiResponseTime: 0,
      errorRate: 0,
      userSessions: 0
    };
  }
  
  trackPageLoad() {
    window.addEventListener('load', () => {
      const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      this.metrics.pageLoadTime = loadTime;
      this.sendMetric('page_load_time', loadTime);
    });
  }
  
  trackApiCall(url, startTime) {
    return (response) => {
      const responseTime = Date.now() - startTime;
      this.metrics.apiResponseTime = responseTime;
      
      this.sendMetric('api_response_time', responseTime, {
        url,
        status: response.status
      });
      
      if (response.status >= 400) {
        this.metrics.errorRate++;
        this.sendMetric('api_error', 1, {
          url,
          status: response.status
        });
      }
    };
  }
  
  sendMetric(name, value, tags = {}) {
    // Send to monitoring service (DataDog, New Relic, etc.)
    fetch('/api/metrics', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        metric: name,
        value,
        tags,
        timestamp: Date.now()
      })
    });
  }
}

// Initialize monitoring
const monitor = new PerformanceMonitor();
monitor.trackPageLoad();

// Export for use in API calls
export default monitor;
```

---

**Última atualização**: 2024-12-29
**Versão**: 1.0.0