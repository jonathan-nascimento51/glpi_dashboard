# GLPI Dashboard - Makefile for Development Tasks
# ===============================================

# Variables
PYTHON := python
PIP := pip
NPM := npm
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
BANDIT := bandit
SAFETY := safety
PRECOMMIT := pre-commit

# Directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend
TESTS_DIR := tests
SCRIPTS_DIR := scripts
DOCS_DIR := docs
COVERAGE_DIR := coverage_html_report

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)GLPI Dashboard - Development Commands$(RESET)"
	@echo "====================================="
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(install|setup|init)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Development Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(dev|run|serve|watch)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(test|coverage)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quality Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(lint|format|check|security)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Build & Deploy Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(build|deploy|docker|release)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Cleanup Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(clean|reset)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# SETUP COMMANDS
# =============================================================================

.PHONY: install
install: install-backend install-frontend ## Install all dependencies

.PHONY: install-backend
install-backend: ## Install Python backend dependencies
	@echo "$(BLUE)Installing Python backend dependencies...$(RESET)"
	$(PIP) install -e .[dev,testing,linting,docs]
	@echo "$(GREEN)Backend dependencies installed successfully!$(RESET)"

.PHONY: install-frontend
install-frontend: ## Install Node.js frontend dependencies
	@echo "$(BLUE)Installing Node.js frontend dependencies...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) ci
	@echo "$(GREEN)Frontend dependencies installed successfully!$(RESET)"

.PHONY: setup
setup: install setup-pre-commit setup-env ## Complete project setup
	@echo "$(GREEN)Project setup completed successfully!$(RESET)"

.PHONY: setup-pre-commit
setup-pre-commit: ## Install and setup pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(RESET)"
	$(PRECOMMIT) install
	$(PRECOMMIT) install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed successfully!$(RESET)"

.PHONY: setup-env
setup-env: ## Setup environment files
	@echo "$(BLUE)Setting up environment files...$(RESET)"
	@if [ ! -f .env ]; then \
		cp .env.example .env 2>/dev/null || echo "# Environment variables\nFLASK_ENV=development\nFLASK_DEBUG=True" > .env; \
		echo "$(YELLOW)Created .env file. Please update it with your configuration.$(RESET)"; \
	else \
		echo "$(GREEN).env file already exists.$(RESET)"; \
	fi

.PHONY: init
init: clean install setup ## Initialize project from scratch
	@echo "$(GREEN)Project initialized successfully!$(RESET)"

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

.PHONY: dev
dev: ## Start development servers (backend and frontend)
	@echo "$(BLUE)Starting development servers...$(RESET)"
	@echo "$(YELLOW)Backend will run on http://localhost:5000$(RESET)"
	@echo "$(YELLOW)Frontend will run on http://localhost:3001$(RESET)"
	@echo "$(MAGENTA)Press Ctrl+C to stop both servers$(RESET)"
	@trap 'kill %1 %2 2>/dev/null; exit' INT; \
	$(MAKE) run-backend & \
	$(MAKE) run-frontend & \
	wait

.PHONY: run-backend
run-backend: ## Start backend development server
	@echo "$(BLUE)Starting backend server...$(RESET)"
	cd $(BACKEND_DIR) && $(PYTHON) app.py

.PHONY: run-frontend
run-frontend: ## Start frontend development server
	@echo "$(BLUE)Starting frontend server...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) run dev

.PHONY: watch
watch: ## Start development with file watching
	@echo "$(BLUE)Starting development with file watching...$(RESET)"
	@$(MAKE) dev

# =============================================================================
# TESTING COMMANDS
# =============================================================================

.PHONY: test
test: test-backend test-frontend ## Run all tests

.PHONY: test-backend
test-backend: ## Run Python backend tests
	@echo "$(BLUE)Running backend tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR) -v --tb=short
	@echo "$(GREEN)Backend tests completed!$(RESET)"

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) run test:ci
	@echo "$(GREEN)Frontend tests completed!$(RESET)"

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	@echo "$(YELLOW)Backend tests: $(RESET)$(PYTEST) $(TESTS_DIR) --watch"
	@echo "$(YELLOW)Frontend tests: $(RESET)cd $(FRONTEND_DIR) && $(NPM) run test:watch"
	@echo "$(MAGENTA)Choose which tests to watch:$(RESET)"
	@echo "  1) Backend tests"
	@echo "  2) Frontend tests"
	@read -p "Enter choice [1-2]: " choice; \
	case $$choice in \
		1) $(PYTEST) $(TESTS_DIR) -f ;; \
		2) cd $(FRONTEND_DIR) && $(NPM) run test:watch ;; \
		*) echo "$(RED)Invalid choice$(RESET)" ;; \
	esac

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTEST) $(TESTS_DIR) --cov=$(BACKEND_DIR) --cov=$(SCRIPTS_DIR) --cov-report=html --cov-report=term-missing --cov-report=xml
	cd $(FRONTEND_DIR) && $(NPM) run test:coverage
	@echo "$(GREEN)Coverage reports generated!$(RESET)"
	@echo "$(YELLOW)Backend coverage: $(RESET)file://$(PWD)/$(COVERAGE_DIR)/index.html"
	@echo "$(YELLOW)Frontend coverage: $(RESET)file://$(PWD)/$(FRONTEND_DIR)/coverage/index.html"

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR) -m integration -v
	@echo "$(GREEN)Integration tests completed!$(RESET)"

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR) -m "not integration" -v
	@echo "$(GREEN)Unit tests completed!$(RESET)"

.PHONY: test-slow
test-slow: ## Run slow tests
	@echo "$(BLUE)Running slow tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR) -m slow -v
	@echo "$(GREEN)Slow tests completed!$(RESET)"

.PHONY: test-fast
test-fast: ## Run fast tests only
	@echo "$(BLUE)Running fast tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR) -m "not slow" -v
	@echo "$(GREEN)Fast tests completed!$(RESET)"

# =============================================================================
# CODE QUALITY COMMANDS
# =============================================================================

.PHONY: lint
lint: lint-backend lint-frontend ## Run all linting

.PHONY: lint-backend
lint-backend: ## Run Python linting
	@echo "$(BLUE)Running Python linting...$(RESET)"
	$(FLAKE8) $(BACKEND_DIR) $(SCRIPTS_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Python linting completed!$(RESET)"

.PHONY: lint-frontend
lint-frontend: ## Run frontend linting
	@echo "$(BLUE)Running frontend linting...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) run lint
	@echo "$(GREEN)Frontend linting completed!$(RESET)"

.PHONY: format
format: format-backend format-frontend ## Format all code

.PHONY: format-backend
format-backend: ## Format Python code
	@echo "$(BLUE)Formatting Python code...$(RESET)"
	$(BLACK) $(BACKEND_DIR) $(SCRIPTS_DIR) $(TESTS_DIR)
	$(ISORT) $(BACKEND_DIR) $(SCRIPTS_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Python code formatted!$(RESET)"

.PHONY: format-frontend
format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend code...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) run format
	@echo "$(GREEN)Frontend code formatted!$(RESET)"

.PHONY: check
check: check-backend check-frontend ## Run all code checks

.PHONY: check-backend
check-backend: ## Run Python code checks
	@echo "$(BLUE)Running Python code checks...$(RESET)"
	$(BLACK) --check $(BACKEND_DIR) $(SCRIPTS_DIR) $(TESTS_DIR)
	$(ISORT) --check-only $(BACKEND_DIR) $(SCRIPTS_DIR) $(TESTS_DIR)
	$(FLAKE8) $(BACKEND_DIR) $(SCRIPTS_DIR) $(TESTS_DIR)
	$(MYPY) $(BACKEND_DIR) $(SCRIPTS_DIR)
	@echo "$(GREEN)Python code checks passed!$(RESET)"

.PHONY: check-frontend
check-frontend: ## Run frontend code checks
	@echo "$(BLUE)Running frontend code checks...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) run lint
	cd $(FRONTEND_DIR) && $(NPM) run type-check
	@echo "$(GREEN)Frontend code checks passed!$(RESET)"

.PHONY: security
security: security-backend security-frontend ## Run security checks

.PHONY: security-backend
security-backend: ## Run Python security checks
	@echo "$(BLUE)Running Python security checks...$(RESET)"
	$(BANDIT) -r $(BACKEND_DIR) $(SCRIPTS_DIR) --skip B101,B601
	$(SAFETY) check
	@echo "$(GREEN)Python security checks completed!$(RESET)"

.PHONY: security-frontend
security-frontend: ## Run frontend security checks
	@echo "$(BLUE)Running frontend security checks...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) audit --audit-level=moderate
	@echo "$(GREEN)Frontend security checks completed!$(RESET)"

.PHONY: type-check
type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(RESET)"
	$(MYPY) $(BACKEND_DIR) $(SCRIPTS_DIR)
	cd $(FRONTEND_DIR) && $(NPM) run type-check
	@echo "$(GREEN)Type checking completed!$(RESET)"

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(PRECOMMIT) run --all-files
	@echo "$(GREEN)Pre-commit hooks completed!$(RESET)"

# =============================================================================
# BUILD & DEPLOY COMMANDS
# =============================================================================

.PHONY: build
build: build-frontend ## Build production assets

.PHONY: build-frontend
build-frontend: ## Build frontend for production
	@echo "$(BLUE)Building frontend for production...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) run build
	@echo "$(GREEN)Frontend built successfully!$(RESET)"

.PHONY: build-docker
build-docker: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(RESET)"
	docker-compose build
	@echo "$(GREEN)Docker images built successfully!$(RESET)"

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(RESET)"
	@echo "$(YELLOW)This would deploy to staging environment$(RESET)"
	@echo "$(RED)Not implemented yet$(RESET)"

.PHONY: deploy-production
deploy-production: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(RESET)"
	@echo "$(YELLOW)This would deploy to production environment$(RESET)"
	@echo "$(RED)Not implemented yet$(RESET)"

.PHONY: release
release: ## Create a new release
	@echo "$(BLUE)Creating new release...$(RESET)"
	@echo "$(YELLOW)This would create a new release$(RESET)"
	@echo "$(RED)Not implemented yet$(RESET)"

# =============================================================================
# CLEANUP COMMANDS
# =============================================================================

.PHONY: clean
clean: clean-python clean-frontend clean-coverage clean-logs ## Clean all generated files

.PHONY: clean-python
clean-python: ## Clean Python cache files
	@echo "$(BLUE)Cleaning Python cache files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/
	@echo "$(GREEN)Python cache files cleaned!$(RESET)"

.PHONY: clean-frontend
clean-frontend: ## Clean frontend build files
	@echo "$(BLUE)Cleaning frontend build files...$(RESET)"
	cd $(FRONTEND_DIR) && rm -rf dist/ build/ node_modules/.cache/
	@echo "$(GREEN)Frontend build files cleaned!$(RESET)"

.PHONY: clean-coverage
clean-coverage: ## Clean coverage reports
	@echo "$(BLUE)Cleaning coverage reports...$(RESET)"
	rm -rf $(COVERAGE_DIR)/ .coverage coverage.xml
	cd $(FRONTEND_DIR) && rm -rf coverage/
	@echo "$(GREEN)Coverage reports cleaned!$(RESET)"

.PHONY: clean-logs
clean-logs: ## Clean log files
	@echo "$(BLUE)Cleaning log files...$(RESET)"
	find . -name "*.log" -type f -delete
	@echo "$(GREEN)Log files cleaned!$(RESET)"

.PHONY: clean-all
clean-all: clean reset-deps ## Clean everything including dependencies

.PHONY: reset-deps
reset-deps: ## Reset all dependencies
	@echo "$(BLUE)Resetting dependencies...$(RESET)"
	rm -rf $(FRONTEND_DIR)/node_modules/
	@echo "$(YELLOW)Run 'make install' to reinstall dependencies$(RESET)"

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

.PHONY: info
info: ## Show project information
	@echo "$(CYAN)GLPI Dashboard Project Information$(RESET)"
	@echo "================================="
	@echo "$(YELLOW)Python Version:$(RESET) $$($(PYTHON) --version)"
	@echo "$(YELLOW)Node Version:$(RESET) $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo "$(YELLOW)NPM Version:$(RESET) $$($(NPM) --version 2>/dev/null || echo 'Not installed')"
	@echo "$(YELLOW)Project Root:$(RESET) $(PWD)"
	@echo "$(YELLOW)Backend Dir:$(RESET) $(BACKEND_DIR)"
	@echo "$(YELLOW)Frontend Dir:$(RESET) $(FRONTEND_DIR)"
	@echo "$(YELLOW)Tests Dir:$(RESET) $(TESTS_DIR)"
	@echo ""
	@echo "$(YELLOW)Available Make Targets:$(RESET)"
	@$(MAKE) help

.PHONY: deps-check
deps-check: ## Check for dependency updates
	@echo "$(BLUE)Checking for dependency updates...$(RESET)"
	@echo "$(YELLOW)Python dependencies:$(RESET)"
	$(PIP) list --outdated
	@echo "$(YELLOW)Frontend dependencies:$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) outdated

.PHONY: deps-update
deps-update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	@echo "$(YELLOW)Updating Python dependencies...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	@echo "$(YELLOW)Updating frontend dependencies...$(RESET)"
	cd $(FRONTEND_DIR) && $(NPM) update
	@echo "$(GREEN)Dependencies updated!$(RESET)"

.PHONY: logs
logs: ## Show application logs
	@echo "$(BLUE)Showing recent logs...$(RESET)"
	@find . -name "*.log" -type f -exec echo "$(YELLOW){}:$(RESET)" \; -exec tail -n 20 {} \; -exec echo "" \;

.PHONY: status
status: ## Show project status
	@echo "$(CYAN)Project Status$(RESET)"
	@echo "=============="
	@echo "$(YELLOW)Git Status:$(RESET)"
	@git status --short 2>/dev/null || echo "Not a git repository"
	@echo ""
	@echo "$(YELLOW)Git Branch:$(RESET)"
	@git branch --show-current 2>/dev/null || echo "Not a git repository"
	@echo ""
	@echo "$(YELLOW)Last Commit:$(RESET)"
	@git log -1 --oneline 2>/dev/null || echo "No commits found"
	@echo ""
	@echo "$(YELLOW)Uncommitted Changes:$(RESET)"
	@git diff --stat 2>/dev/null || echo "Not a git repository"

# =============================================================================
# DOCKER COMMANDS
# =============================================================================

.PHONY: docker-up
docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)Docker containers started!$(RESET)"

.PHONY: docker-down
docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(RESET)"
	docker-compose down
	@echo "$(GREEN)Docker containers stopped!$(RESET)"

.PHONY: docker-logs
docker-logs: ## Show Docker container logs
	@echo "$(BLUE)Showing Docker logs...$(RESET)"
	docker-compose logs -f

.PHONY: docker-clean
docker-clean: ## Clean Docker resources
	@echo "$(BLUE)Cleaning Docker resources...$(RESET)"
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Docker resources cleaned!$(RESET)"

# =============================================================================
# DOCUMENTATION COMMANDS
# =============================================================================

.PHONY: docs
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(RESET)"
	@if [ -d "$(DOCS_DIR)" ]; then \
		cd $(DOCS_DIR) && make html; \
		echo "$(GREEN)Documentation built successfully!$(RESET)"; \
		echo "$(YELLOW)Open: $(RESET)file://$(PWD)/$(DOCS_DIR)/_build/html/index.html"; \
	else \
		echo "$(YELLOW)Documentation directory not found. Creating basic docs...$(RESET)"; \
		mkdir -p $(DOCS_DIR); \
		echo "# GLPI Dashboard Documentation" > $(DOCS_DIR)/README.md; \
		echo "$(GREEN)Basic documentation created!$(RESET)"; \
	fi

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(RESET)"
	@if [ -d "$(DOCS_DIR)/_build/html" ]; then \
		cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8080; \
	else \
		echo "$(RED)Documentation not built. Run 'make docs' first.$(RESET)"; \
	fi

# =============================================================================
# SPECIAL TARGETS
# =============================================================================

# Prevent make from deleting intermediate files
.SECONDARY:

# Declare phony targets
.PHONY: all install setup dev test lint format check security build deploy clean help info