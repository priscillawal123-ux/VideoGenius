#!/bin/bash
# Video Genius - Complete Environment Setup Script
# Versão: 1.0.0
# Descrição: Script completo para setup do ambiente de desenvolvimento

# Carrega bibliotecas comuns
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/validation.sh"
source "$SCRIPT_DIR/lib/setup_functions.sh"

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

# Função principal de setup
main() {
    log_info "🚀 Iniciando setup completo do ambiente Video Genius..."
    echo ""

    # Passo 1: Validar pré-requisitos
    run_all_validations

    # Passo 2: Setup GitHub CLI
    setup_github_cli_complete

    # Passo 3: Setup ambiente Python
    setup_python_environment_complete

    # Passo 4: Setup pre-commit
    setup_precommit_complete

    # Passo 5: Setup Google Cloud
    setup_google_cloud_complete

    # Passo 6: Criar arquivos de configuração
    create_configuration_files

    # Passo 7: Setup Docker (opcional)
    setup_docker_config

    # Passo 8: Verificar instalação
    verify_complete_setup

    echo ""
    log_success "🎉 Setup completo! Você está pronto para desenvolver."
    print_setup_next_steps
}

# ============================================================================
# SETUP DOCKER (CONFIGURAÇÃO BÁSICA)
# ============================================================================

# Setup configuração Docker
setup_docker_config() {
    log_info "Configurando Docker..."

    if ! command_exists docker; then
        log_warning "Docker não encontrado - opcional mas recomendado"
        log_info "Instale Docker de: https://docs.docker.com/get-docker/"
        return 1
    fi

    # Criar Dockerfile se não existir
    create_dockerfile

    # Criar docker-compose.yml
    create_docker_compose

    log_success "Docker configurado"
}

# Criar Dockerfile
create_dockerfile() {
    if ! file_exists_and_readable "Dockerfile"; then
        cat > Dockerfile << 'EOF'
# Multi-stage build for Cloud Run optimization
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Development stage
FROM base as development

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Production stage
FROM base as production

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
EOF
        log_success "Dockerfile criado"
    fi

    # Criar .dockerignore
    if ! file_exists_and_readable ".dockerignore"; then
        cat > .dockerignore << 'EOF'
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
.pytest_cache
.coverage
htmlcov
.env
.env.local
*.log
.DS_Store
README.md
tests/
docs/
.github/
EOF
        log_success ".dockerignore criado"
    fi
}

# Criar docker-compose.yml
create_docker_compose() {
    if ! file_exists_and_readable "docker-compose.yml"; then
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    ports:
      - "8080:8080"
    volumes:
      - .:/app
      - /app/.venv
    env_file:
      - .env.local
    environment:
      - ENV=development
      - DEBUG=true
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
EOF
        log_success "docker-compose.yml criado"
    fi
}

# ============================================================================
# VERIFICAÇÃO FINAL
# ============================================================================

# Verificar setup completo
verify_complete_setup() {
    log_info "Verificando instalação completa..."
    echo ""

    local errors=0

    # Verificar Python e dependências
    if verify_python_setup; then
        log_success "✓ Ambiente Python"
    else
        log_error "✗ Ambiente Python"
        errors=$((errors + 1))
    fi

    # Verificar GitHub CLI
    if verify_github_cli_setup; then
        log_success "✓ GitHub CLI com Copilot"
    else
        log_error "✗ GitHub CLI ou Copilot"
        errors=$((errors + 1))
    fi

    # Verificar pre-commit
    if verify_precommit_setup; then
        log_success "✓ Pre-commit hooks"
    else
        log_error "✗ Pre-commit hooks"
        errors=$((errors + 1))
    fi

    # Verificar arquivos de configuração
    if verify_config_files; then
        log_success "✓ Arquivos de configuração"
    else
        log_error "✗ Arquivos de configuração"
        errors=$((errors + 1))
    fi

    # Verificar Google Cloud (opcional)
    if command_exists gcloud && gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_success "✓ Google Cloud CLI"
    else
        log_warning "⚠ Google Cloud CLI não configurado (opcional)"
    fi

    # Verificar Docker (opcional)
    if command_exists docker; then
        log_success "✓ Docker"
    else
        log_warning "⚠ Docker não encontrado (opcional)"
    fi

    echo ""

    if [ $errors -eq 0 ]; then
        log_success "Todas as verificações passaram!"
        return 0
    else
        log_error "$errors verificação(ões) falhou(aram). Reveja os erros acima."
        return 1
    fi
}

# Verificar setup do Python
verify_python_setup() {
    source .venv/bin/activate 2>/dev/null || return 1

    # Verificar imports principais
    python3 -c "
import sys
try:
    import fastapi
    import uvicorn
    import pydantic
    import google.cloud.aiplatform
    import google.cloud.bigquery
    import google.cloud.storage
    print('SUCCESS')
except ImportError as e:
    print(f'FAILED: {e}')
    sys.exit(1)
" 2>/dev/null | grep -q "SUCCESS"
}

# Verificar setup do GitHub CLI
verify_github_cli_setup() {
    gh --version &>/dev/null || return 1
    gh extension list | grep -q "gh-copilot" || return 1
    gh auth status &>/dev/null || return 1
}

# Verificar setup do pre-commit
verify_precommit_setup() {
    source .venv/bin/activate 2>/dev/null || return 1
    pre-commit --version &>/dev/null
}

# Verificar arquivos de configuração
verify_config_files() {

        # Enable required APIs
        log_info "Enabling required Google Cloud APIs..."
        gcloud services enable \
            aiplatform.googleapis.com \
            bigquery.googleapis.com \
            storage.googleapis.com \
            run.googleapis.com \
            cloudbuild.googleapis.com \
            secretmanager.googleapis.com \
            2>/dev/null || log_warning "Some APIs may already be enabled"

        log_success "Google Cloud APIs enabled"
    fi

    echo ""
}

# Create environment files
create_environment_files() {
    log_info "Creating environment files..."

    # Create .env.example
    if [ ! -f ".env.example" ]; then
        cat > .env.example << 'EOF'
# Application
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Google Cloud
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1
BIGQUERY_DATASET=video_data
CLOUD_STORAGE_BUCKET=video-genius-assets

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
API_WORKERS=4

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# YouTube API (optional)
YOUTUBE_API_KEY=your-youtube-api-key

# Feature Flags
ENABLE_CACHING=true
ENABLE_MONITORING=true
EOF
        log_success "Created .env.example"
    fi

    # Create .env.local if not exists
    if [ ! -f ".env.local" ]; then
        log_info "Creating .env.local from template..."
        cp .env.example .env.local
        log_warning "Please update .env.local with your actual credentials"
    else
        log_success ".env.local already exists"
    fi

    # Create .gitignore if not exists
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.ruff_cache/

# Environment
.env
.env.local
.env.*.local
*.env

# Google Cloud
service-account-key.json
*-key.json

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Temporary files
tmp/
temp/
*.tmp
EOF
        log_success "Created .gitignore"
    fi

    # Create pyproject.toml for tool configurations
    if [ ! -f "pyproject.toml" ]; then
        cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python $python_version found"
    fi

    # Check pip
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    fi

    # Check git
    if ! command_exists git; then
        missing_deps+=("git")
    else
        log_success "Git found"
    fi

    # Check Docker
    if ! command_exists docker; then
        log_warning "Docker not found - optional but recommended"
    else
        log_success "Docker found"
    fi

    # Check if any critical dependencies are missing
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install them and run setup again."
        exit 1
    fi

    echo ""
}

# Setup GitHub CLI
setup_github_cli() {
    log_info "Setting up GitHub CLI..."

    if ! command_exists gh; then
        log_warning "GitHub CLI not found. Installing..."

        # Detect OS and install accordingly
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update
            sudo apt install gh -y
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install gh
        else
            log_error "Unsupported OS. Please install GitHub CLI manually: https://cli.github.com/"
            exit 1
        fi

        log_success "GitHub CLI installed"
    else
        log_success "GitHub CLI already installed"
    fi

    # Check authentication
    if ! gh auth status &> /dev/null; then
        log_info "Authenticating with GitHub..."
        gh auth login

        # Refresh token with required scopes
        log_info "Requesting additional scopes..."
        gh auth refresh -s copilot,workflow,write:packages
    else

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["backend"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
EOF
        log_success "Created pyproject.toml"
    fi

    echo ""
}

# Setup Docker
setup_docker() {
    log_info "Setting up Docker configuration..."

    if ! command_exists docker; then
        log_warning "Docker not found, skipping Docker setup"
        echo ""
        return
    fi

    # Create Dockerfile if not exists
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << 'EOF'
# Multi-stage build for Cloud Run optimization
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Development stage
FROM base as development

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Production stage
FROM base as production

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
EOF
        log_success "Created Dockerfile"
    fi

    # Create .dockerignore
    if [ ! -f ".dockerignore" ]; then
        cat > .dockerignore << 'EOF'
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
.pytest_cache
.coverage
htmlcov
.env
.env.local
*.log
.DS_Store
README.md
tests/
docs/
.github/
EOF
        log_success "Created .dockerignore"
    fi

    # Create docker-compose.yml for local development
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    ports:
      - "8080:8080"
    volumes:
      - .:/app
      - /app/.venv
    env_file:
      - .env.local
    environment:
      - ENV=development
      - DEBUG=true
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
EOF
        log_success "Created docker-compose.yml"
    fi

    echo ""
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    echo ""

    local errors=0

    # Check Python
    if source .venv/bin/activate && python -c "import fastapi, google.cloud.aiplatform" 2>/dev/null; then
        log_success "✓ Python dependencies"
    else
        log_error "✗ Python dependencies"
        errors=$((errors + 1))
    fi

    # Check GitHub CLI
    if gh --version &>/dev/null && gh extension list | grep -q "gh-copilot"; then
        log_success "✓ GitHub CLI with Copilot"
    else
        log_error "✗ GitHub CLI or Copilot extension"
        errors=$((errors + 1))
    fi

    # Check pre-commit
    if pre-commit --version &>/dev/null; then
        log_success "✓ Pre-commit hooks"
    else
        log_error "✗ Pre-commit hooks"
        errors=$((errors + 1))
    fi

    # Check environment files
    if [ -f ".env.local" ] && [ -f "pyproject.toml" ]; then
        log_success "✓ Configuration files"
    else
        log_error "✗ Configuration files"
        errors=$((errors + 1))
    fi

    # Check gcloud (optional)
    if command_exists gcloud; then
        log_success "✓ Google Cloud CLI (optional)"
    else
        log_warning "⚠ Google Cloud CLI not found (optional)"
    fi

    # Check Docker (optional)
    if command_exists docker; then
        log_success "✓ Docker (optional)"
    else
        log_warning "⚠ Docker not found (optional)"
    fi

    echo ""

    if [ $errors -eq 0 ]; then
        log_success "All checks passed!"
    else
        log_error "$errors check(s) failed. Please review the errors above."
        exit 1
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_info "📝 Next Steps:"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   ${GREEN}source .venv/bin/activate${NC}"
    echo ""
    echo "2. Update your credentials in .env.local"
    echo ""
    echo "3. Create project directories:"
    echo "   ${GREEN}mkdir -p backend/{api,services,models,database,storage}${NC}"
    echo "   ${GREEN}mkdir -p tests scripts${NC}"
    echo ""
    echo "4. Test GitHub Copilot CLI:"
    echo "   ${GREEN}gh copilot suggest -t shell \"list files\"${NC}"
    echo ""
    echo "5. Start development:"
    echo "   ${GREEN}uvicorn backend.api.main:app --reload${NC}"
    echo ""
    echo "6. Useful commands:"
    echo "   ${GREEN}gh work${NC}          # See your assigned issues"
    echo "   ${GREEN}gh prc${NC}           # Create PR quickly"
    echo "   ${GREEN}gh ci${NC}            # Check CI status"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Run main function
main
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python $python_version found"
    fi

    # Check pip
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    fi

    # Check git
    if ! command_exists git; then
        missing_deps+=("git")
    else
        log_success "Git found"
    fi

    # Check Docker
    if ! command_exists docker; then
        log_warning "Docker not found - optional but recommended"
    else
        log_success "Docker found"
    fi

    # Check if any critical dependencies are missing
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install them and run setup again."
        exit 1
    fi

    echo ""
}

# Setup GitHub CLI
setup_github_cli() {
    log_info "Setting up GitHub CLI..."

    if ! command_exists gh; then
        log_warning "GitHub CLI not found. Installing..."

        # Detect OS and install accordingly
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update
            sudo apt install gh -y
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install gh
        else
            log_error "Unsupported OS. Please install GitHub CLI manually: https://cli.github.com/"
            exit 1
        fi

        log_success "GitHub CLI installed"
    else
        log_success "GitHub CLI already installed"
    fi

    # Check authentication
    if ! gh auth status &> /dev/null; then
        log_info "Authenticating with GitHub..."
        gh auth login

        # Refresh token with required scopes
        log_info "Requesting additional scopes..."
        gh auth refresh -s copilot,workflow,write:packages
    else
