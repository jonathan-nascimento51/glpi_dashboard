# GLPI Dashboard Development Tools
# ================================

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=development

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    jq \
    unzip \
    zip \
    # Build tools
    build-essential \
    pkg-config \
    # Python dependencies
    python3.11 \
    python3.11-dev \
    python3-pip \
    python3.11-venv \
    # Node.js dependencies
    nodejs \
    npm \
    # Database tools
    postgresql-client \
    redis-tools \
    # Network tools
    netcat \
    telnet \
    nmap \
    # Development tools
    make \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools
RUN python3.11 -m pip install --upgrade pip setuptools wheel && \
    python3.11 -m pip install \
    # Code quality
    black \
    isort \
    flake8 \
    mypy \
    bandit \
    safety \
    # Testing
    pytest \
    pytest-cov \
    pytest-xdist \
    pytest-mock \
    # Development
    ipython \
    jupyter \
    pre-commit \
    # Debugging
    pdb++ \
    ipdb \
    # Documentation
    sphinx \
    mkdocs \
    # Utilities
    requests \
    python-dotenv

# Install Node.js tools
RUN npm install -g \
    # Package managers
    yarn \
    pnpm \
    # Code quality
    eslint \
    prettier \
    # Testing
    jest \
    # Build tools
    vite \
    webpack \
    # Development
    nodemon \
    concurrently \
    # Utilities
    http-server \
    json-server \
    # Documentation
    jsdoc

# Install Docker CLI (for Docker-in-Docker scenarios)
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Create development user
RUN groupadd -r devuser && useradd -r -g devuser -s /bin/bash devuser && \
    mkdir -p /home/devuser && \
    chown -R devuser:devuser /home/devuser

# Install Oh My Bash for better shell experience
RUN git clone --depth=1 https://github.com/ohmybash/oh-my-bash.git /home/devuser/.oh-my-bash && \
    chown -R devuser:devuser /home/devuser/.oh-my-bash

# Create useful aliases and functions
RUN echo 'alias ll="ls -alF"' >> /home/devuser/.bashrc && \
    echo 'alias la="ls -A"' >> /home/devuser/.bashrc && \
    echo 'alias l="ls -CF"' >> /home/devuser/.bashrc && \
    echo 'alias ..="cd .."' >> /home/devuser/.bashrc && \
    echo 'alias ...="cd ../.."' >> /home/devuser/.bashrc && \
    echo 'alias grep="grep --color=auto"' >> /home/devuser/.bashrc && \
    echo 'alias fgrep="fgrep --color=auto"' >> /home/devuser/.bashrc && \
    echo 'alias egrep="egrep --color=auto"' >> /home/devuser/.bashrc && \
    echo 'export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /home/devuser/.bashrc

# Add development functions
RUN echo 'function run_tests() { python -m pytest tests/ -v --cov=backend --cov=scripts; }' >> /home/devuser/.bashrc && \
    echo 'function run_frontend_tests() { cd frontend && npm test; }' >> /home/devuser/.bashrc && \
    echo 'function lint_python() { black . && isort . && flake8 .; }' >> /home/devuser/.bashrc && \
    echo 'function lint_frontend() { cd frontend && npm run lint && npm run format; }' >> /home/devuser/.bashrc && \
    echo 'function check_security() { safety check && bandit -r backend/ scripts/; }' >> /home/devuser/.bashrc && \
    echo 'function dev_setup() { pip install -e .[dev] && cd frontend && npm install; }' >> /home/devuser/.bashrc

# Set up Git configuration template
RUN echo '[user]' > /home/devuser/.gitconfig.template && \
    echo '    name = Developer' >> /home/devuser/.gitconfig.template && \
    echo '    email = dev@example.com' >> /home/devuser/.gitconfig.template && \
    echo '[core]' >> /home/devuser/.gitconfig.template && \
    echo '    editor = vim' >> /home/devuser/.gitconfig.template && \
    echo '    autocrlf = input' >> /home/devuser/.gitconfig.template && \
    echo '[push]' >> /home/devuser/.gitconfig.template && \
    echo '    default = simple' >> /home/devuser/.gitconfig.template && \
    echo '[pull]' >> /home/devuser/.gitconfig.template && \
    echo '    rebase = false' >> /home/devuser/.gitconfig.template && \
    chown devuser:devuser /home/devuser/.gitconfig.template

# Create workspace directory
RUN mkdir -p /workspace && chown -R devuser:devuser /workspace

# Switch to development user
USER devuser
WORKDIR /workspace

# Set up Python virtual environment
RUN python3.11 -m venv /home/devuser/.venv && \
    echo 'source /home/devuser/.venv/bin/activate' >> /home/devuser/.bashrc

# Create development scripts
RUN mkdir -p /home/devuser/scripts

# Script to initialize project
RUN echo '#!/bin/bash' > /home/devuser/scripts/init-project.sh && \
    echo 'echo "Initializing GLPI Dashboard development environment..."' >> /home/devuser/scripts/init-project.sh && \
    echo 'source /home/devuser/.venv/bin/activate' >> /home/devuser/scripts/init-project.sh && \
    echo 'pip install -e .[dev]' >> /home/devuser/scripts/init-project.sh && \
    echo 'cd frontend && npm install' >> /home/devuser/scripts/init-project.sh && \
    echo 'cd ..' >> /home/devuser/scripts/init-project.sh && \
    echo 'pre-commit install' >> /home/devuser/scripts/init-project.sh && \
    echo 'echo "Development environment ready!"' >> /home/devuser/scripts/init-project.sh && \
    chmod +x /home/devuser/scripts/init-project.sh

# Script to run full test suite
RUN echo '#!/bin/bash' > /home/devuser/scripts/run-all-tests.sh && \
    echo 'echo "Running backend tests..."' >> /home/devuser/scripts/run-all-tests.sh && \
    echo 'source /home/devuser/.venv/bin/activate' >> /home/devuser/scripts/run-all-tests.sh && \
    echo 'python -m pytest tests/ -v --cov=backend --cov=scripts --cov-report=html' >> /home/devuser/scripts/run-all-tests.sh && \
    echo 'echo "Running frontend tests..."' >> /home/devuser/scripts/run-all-tests.sh && \
    echo 'cd frontend && npm test' >> /home/devuser/scripts/run-all-tests.sh && \
    echo 'echo "All tests completed!"' >> /home/devuser/scripts/run-all-tests.sh && \
    chmod +x /home/devuser/scripts/run-all-tests.sh

# Add scripts to PATH
RUN echo 'export PATH="/home/devuser/scripts:$PATH"' >> /home/devuser/.bashrc

# Default command
CMD ["/bin/bash"]