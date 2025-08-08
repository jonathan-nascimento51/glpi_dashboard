#!/bin/bash
# GLPI Dashboard Test Runner
# =========================

set -e

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

# Default values
TEST_TYPE="all"
VERBOSE=false
COVERAGE=false
WATCH=false
FAST=false
SLOW=false
PARALLEL=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -f|--fast)
            FAST=true
            shift
            ;;
        -s|--slow)
            SLOW=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -h|--help)
            echo "GLPI Dashboard Test Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -t, --type TYPE     Test type: all, backend, frontend, unit, integration, e2e"
            echo "  -v, --verbose       Verbose output"
            echo "  -c, --coverage      Generate coverage report"
            echo "  -w, --watch         Watch mode (for frontend tests)"
            echo "  -f, --fast          Run only fast tests"
            echo "  -s, --slow          Run only slow tests"
            echo "  -p, --parallel      Run tests in parallel"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run all tests"
            echo "  $0 -t backend -c            # Run backend tests with coverage"
            echo "  $0 -t frontend -w           # Run frontend tests in watch mode"
            echo "  $0 -t unit -f               # Run only fast unit tests"
            echo "  $0 -t integration -s        # Run only slow integration tests"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to workspace directory
cd /workspace

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Build pytest command
    local pytest_cmd="pytest"
    local pytest_args=""
    
    if [ "$VERBOSE" = true ]; then
        pytest_args="$pytest_args -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        pytest_args="$pytest_args --cov=backend --cov-report=html --cov-report=term-missing"
    fi
    
    if [ "$PARALLEL" = true ]; then
        pytest_args="$pytest_args -n auto"
    fi
    
    if [ "$FAST" = true ]; then
        pytest_args="$pytest_args -m 'not slow'"
    elif [ "$SLOW" = true ]; then
        pytest_args="$pytest_args -m slow"
    fi
    
    # Set test directory based on test type
    local test_dir="backend/tests/"
    case $TEST_TYPE in
        unit)
            test_dir="backend/tests/unit/"
            ;;
        integration)
            test_dir="backend/tests/integration/"
            ;;
        e2e)
            test_dir="backend/tests/e2e/"
            ;;
    esac
    
    # Run tests
    print_status "Executing: $pytest_cmd $pytest_args $test_dir"
    $pytest_cmd $pytest_args $test_dir
    
    if [ $? -eq 0 ]; then
        print_success "Backend tests passed!"
    else
        print_error "Backend tests failed!"
        return 1
    fi
    
    # Generate coverage report if requested
    if [ "$COVERAGE" = true ]; then
        print_status "Coverage report generated in htmlcov/"
        if command -v xdg-open &> /dev/null; then
            xdg-open htmlcov/index.html &
        fi
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests..."
    
    cd frontend
    
    # Build npm test command
    local npm_cmd="npm run"
    local test_script="test"
    
    if [ "$WATCH" = true ]; then
        test_script="test:watch"
    elif [ "$COVERAGE" = true ]; then
        test_script="test:coverage"
    else
        test_script="test:ci"
    fi
    
    # Set environment variables
    if [ "$VERBOSE" = true ]; then
        export CI=true
        export VERBOSE=true
    fi
    
    # Run tests
    print_status "Executing: $npm_cmd $test_script"
    $npm_cmd $test_script
    
    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed!"
    else
        print_error "Frontend tests failed!"
        cd ..
        return 1
    fi
    
    cd ..
}

# Function to run linting
run_linting() {
    print_status "Running code quality checks..."
    
    # Backend linting
    print_status "Checking backend code quality..."
    source .venv/bin/activate
    
    # Run flake8
    if command -v flake8 &> /dev/null; then
        print_status "Running flake8..."
        flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 backend/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    fi
    
    # Run black check
    if command -v black &> /dev/null; then
        print_status "Checking code formatting with black..."
        black --check backend/
    fi
    
    # Run isort check
    if command -v isort &> /dev/null; then
        print_status "Checking import sorting with isort..."
        isort --check-only backend/
    fi
    
    # Run mypy
    if command -v mypy &> /dev/null; then
        print_status "Running type checking with mypy..."
        mypy backend/ --ignore-missing-imports
    fi
    
    # Frontend linting
    print_status "Checking frontend code quality..."
    cd frontend
    
    # Run ESLint
    if [ -f "package.json" ] && npm list eslint &> /dev/null; then
        print_status "Running ESLint..."
        npm run lint
    fi
    
    # Run Prettier check
    if [ -f "package.json" ] && npm list prettier &> /dev/null; then
        print_status "Checking code formatting with Prettier..."
        npm run format:check
    fi
    
    cd ..
    
    print_success "Code quality checks completed!"
}

# Function to run security checks
run_security_checks() {
    print_status "Running security checks..."
    
    # Backend security
    source .venv/bin/activate
    
    # Run safety check
    if command -v safety &> /dev/null; then
        print_status "Checking for known security vulnerabilities with safety..."
        safety check
    fi
    
    # Run bandit
    if command -v bandit &> /dev/null; then
        print_status "Running security linting with bandit..."
        bandit -r backend/ -f json -o bandit-report.json || true
        bandit -r backend/
    fi
    
    # Frontend security
    cd frontend
    
    # Run npm audit
    if [ -f "package.json" ]; then
        print_status "Running npm security audit..."
        npm audit --audit-level moderate
    fi
    
    cd ..
    
    print_success "Security checks completed!"
}

# Main execution
print_status "Starting GLPI Dashboard test suite..."
print_status "Test type: $TEST_TYPE"
print_status "Verbose: $VERBOSE"
print_status "Coverage: $COVERAGE"
print_status "Watch: $WATCH"
print_status "Fast: $FAST"
print_status "Slow: $SLOW"
print_status "Parallel: $PARALLEL"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "package.json" ]; then
    print_error "Not in GLPI Dashboard workspace directory!"
    exit 1
fi

# Run tests based on type
case $TEST_TYPE in
    all)
        run_linting
        run_security_checks
        run_backend_tests
        run_frontend_tests
        ;;
    backend)
        run_backend_tests
        ;;
    frontend)
        run_frontend_tests
        ;;
    unit|integration|e2e)
        run_backend_tests
        ;;
    lint)
        run_linting
        ;;
    security)
        run_security_checks
        ;;
    *)
        print_error "Unknown test type: $TEST_TYPE"
        print_error "Valid types: all, backend, frontend, unit, integration, e2e, lint, security"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    print_success "🎉 All tests completed successfully!"
else
    print_error "❌ Some tests failed!"
    exit 1
fi