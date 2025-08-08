#!/bin/bash
# GLPI Dashboard Development Environment Initialization
# ====================================================

set -e

echo "🚀 Initializing GLPI Dashboard Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "/workspace/pyproject.toml" ] && [ ! -f "/workspace/package.json" ]; then
    print_error "Not in GLPI Dashboard workspace directory!"
    exit 1
fi

cd /workspace

# Create necessary directories
print_status "Creating development directories..."
mkdir -p {
    logs/{backend,frontend,nginx,redis},
    data/{redis,postgres},
    uploads,
    cache,
    .pytest_cache,
    .coverage,
    node_modules/.cache
}

# Set up Python virtual environment
if [ ! -d ".venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip setuptools wheel
else
    print_status "Activating existing Python virtual environment..."
    source .venv/bin/activate
fi

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    print_status "Installing Python development dependencies..."
    pip install -r requirements-dev.txt
fi

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    print_status "Installing pre-commit hooks..."
    pre-commit install
    pre-commit install --hook-type commit-msg
fi

# Set up Node.js environment
if [ -f "frontend/package.json" ]; then
    print_status "Installing Node.js dependencies..."
    cd frontend
    
    # Use npm ci for faster, reliable, reproducible builds
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    
    cd ..
fi

# Create environment files if they don't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
# GLPI Dashboard Environment Configuration
# =======================================

# Environment
ENVIRONMENT=development
DEBUG=true

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///glpi_dashboard.db

# Redis
REDIS_URL=redis://localhost:6379/0

# GLPI API
GLPI_URL=http://your-glpi-instance.com
GLPI_APP_TOKEN=your-app-token
GLPI_USER_TOKEN=your-user-token

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# Frontend
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=GLPI Dashboard
EOF
    fi
    print_warning "Please update .env file with your configuration!"
fi

if [ ! -f "frontend/.env.local" ]; then
    print_status "Creating frontend .env.local file..."
    cat > frontend/.env.local << EOF
# Frontend Development Configuration
# =================================

VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=GLPI Dashboard - Development
VITE_APP_VERSION=dev
VITE_NODE_ENV=development
EOF
fi

# Initialize database (if using SQLite)
if [ -f "backend/app.py" ] && grep -q "sqlite" .env; then
    print_status "Initializing database..."
    cd backend
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
    cd ..
fi

# Run initial tests to ensure everything is working
print_status "Running initial health checks..."

# Check Python environment
if python --version &> /dev/null; then
    print_success "Python environment: $(python --version)"
else
    print_error "Python environment check failed!"
fi

# Check Node.js environment
if node --version &> /dev/null; then
    print_success "Node.js environment: $(node --version)"
else
    print_error "Node.js environment check failed!"
fi

# Check if ports are available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use (needed for $service)"
    else
        print_success "Port $port is available for $service"
    fi
}

check_port 5000 "Backend API"
check_port 3000 "Frontend Dev Server"
check_port 6379 "Redis"
check_port 5432 "PostgreSQL"

# Create useful aliases
print_status "Creating development aliases..."
cat >> ~/.bashrc << 'EOF'

# GLPI Dashboard Development Aliases
# =================================
alias glpi-backend="cd /workspace && source .venv/bin/activate && cd backend && python app.py"
alias glpi-frontend="cd /workspace/frontend && npm run dev"
alias glpi-test="cd /workspace && source .venv/bin/activate && pytest"
alias glpi-lint="cd /workspace && source .venv/bin/activate && flake8 backend/ && cd frontend && npm run lint"
alias glpi-format="cd /workspace && source .venv/bin/activate && black backend/ && isort backend/ && cd frontend && npm run format"
alias glpi-logs="tail -f /workspace/logs/*.log"
alias glpi-clean="cd /workspace && rm -rf .pytest_cache __pycache__ .coverage && cd frontend && rm -rf node_modules/.cache"
EOF

# Create development scripts
print_status "Creating development scripts..."

# Backend development script
cat > run-backend.sh << 'EOF'
#!/bin/bash
cd /workspace
source .venv/bin/activate
cd backend
export FLASK_ENV=development
export FLASK_DEBUG=true
python app.py
EOF
chmod +x run-backend.sh

# Frontend development script
cat > run-frontend.sh << 'EOF'
#!/bin/bash
cd /workspace/frontend
npm run dev
EOF
chmod +x run-frontend.sh

# Test runner script
cat > run-tests.sh << 'EOF'
#!/bin/bash
cd /workspace
source .venv/bin/activate

echo "Running backend tests..."
pytest backend/tests/ -v

echo "Running frontend tests..."
cd frontend
npm run test:ci
EOF
chmod +x run-tests.sh

print_success "Development environment initialized successfully!"
print_status "Available commands:"
echo "  - glpi-backend    : Start backend development server"
echo "  - glpi-frontend   : Start frontend development server"
echo "  - glpi-test       : Run all tests"
echo "  - glpi-lint       : Run linting"
echo "  - glpi-format     : Format code"
echo "  - glpi-logs       : View application logs"
echo "  - glpi-clean      : Clean cache files"
echo ""
print_status "Development scripts:"
echo "  - ./run-backend.sh  : Start backend server"
echo "  - ./run-frontend.sh : Start frontend server"
echo "  - ./run-tests.sh    : Run all tests"
echo ""
print_warning "Don't forget to:"
echo "  1. Update .env file with your GLPI configuration"
echo "  2. Update frontend/.env.local if needed"
echo "  3. Start Redis and PostgreSQL services"
echo "  4. Run 'source ~/.bashrc' to load new aliases"

print_success "🎉 Happy coding!"