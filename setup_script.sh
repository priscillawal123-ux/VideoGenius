#!/bin/bash
# Video Genius - Complete Environment Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
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
        log_success "Already authenticated with GitHub"
    fi

    # Install GitHub CLI extensions
    log_info "Installing GitHub CLI extensions..."

    # Install Copilot extension
    if ! gh extension list | grep -q "gh-copilot"; then
        log_info "Installing gh-copilot extension..."
        gh extension install github/gh-copilot
        log_success "gh-copilot installed"
    else
        log_success "gh-copilot already installed"
        gh extension upgrade gh-copilot
    fi

    # Install other useful extensions
    local extensions=("dlvhdr/gh-dash" "seachicken/gh-poi")
    for ext in "${extensions[@]}"; do
        local ext_name=$(basename "$ext")
        if ! gh extension list | grep -q "$ext_name"; then
            log_info "Installing $ext_name..."
            gh extension install "$ext" || log_warning "Failed to install $ext_name (optional)"
        fi
    done

    # Setup useful aliases
    log_info "Setting up GitHub CLI aliases..."
    gh alias set prc 'pr create --fill' 2>/dev/null || true
    gh alias set co 'pr checkout' 2>/dev/null || true
    gh alias set work 'issue list --assignee @me' 2>/dev/null || true
    gh alias set bugs 'issue list --label bug' 2>/dev/null || true
    gh alias set ci 'pr checks' 2>/dev/null || true
    log_success "Aliases configured"

    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    # Check Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    else
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

# Setup Python environment
setup_python_environment() {
    log_info "Setting up Python environment..."

    # Create virtual environment
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel

    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        log_info "Installing development dependencies..."
        pip install -r requirements-dev.txt
        log_success "Development dependencies installed"
    else
        log_warning "requirements-dev.txt not found, creating..."
        cat > requirements-dev.txt << 'EOF'
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Google Cloud
google-cloud-aiplatform==1.38.0
google-cloud-bigquery==3.13.0
google-cloud-storage==2.10.0
google-auth==2.23.4

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.25.1

# Linting & Formatting
ruff==0.1.6
black==23.11.0
mypy==1.7.1
isort==5.12.0

# Pre-commit
pre-commit==3.5.0

# Development tools
ipython==8.17.2
python-dotenv==1.0.0

# Type stubs
types-requests==2.31.0
EOF
        pip install -r requirements-dev.txt
    fi

    # Install production dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing production dependencies..."
        pip install -r requirements.txt
    else
        log_warning "requirements.txt not found, creating basic version..."
        cat > requirements.txt << 'EOF'
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Google Cloud
google-cloud-aiplatform==1.38.0
google-cloud-bigquery==3.13.0
google-cloud-storage==2.10.0
google-auth==2.23.4

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
EOF
        pip install -r requirements.txt
    fi

    log_success "Python environment ready"
    echo ""
}

# Setup pre-commit hooks
setup_precommit_hooks() {
    log_info "Setting up pre-commit hooks..."

    # Create .pre-commit-config.yaml if not exists
    if [ ! -f ".pre-commit-config.yaml" ]; then
        log_info "Creating pre-commit configuration..."
        cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        args: [--ignore-missing-imports]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
EOF
        log_success "Pre-commit configuration created"
    fi

    # Install pre-commit hooks
    source .venv/bin/activate
    pre-commit install
    pre-commit install --hook-type commit-msg

    log_success "Pre-commit hooks installed"
    echo ""
}

# Setup Google Cloud
setup_google_cloud() {
    log_info "Setting up Google Cloud..."

    if ! command_exists gcloud; then
        log_warning "gcloud CLI not found."
        log_info "Please install from: https://cloud.google.com/sdk/docs/install"
        log_info "Skipping Google Cloud setup..."
        echo ""
        return
    fi

    log_success "gcloud CLI found"

    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_info "Please authenticate with Google Cloud..."
        gcloud auth login
        gcloud auth application-default login
    else
        log_success "Already authenticated with Google Cloud"
    fi

    # Prompt for project ID
    read -p "Enter your Google Cloud Project ID (or press Enter to skip): " project_id

    if [ ! -z "$project_id" ]; then
        gcloud config set project "$project_id"
        log_success "Project set to: $project_id"

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

# Setup Google Cloud Secret Manager
setup_secret_manager() {
    log_info "Setting up Google Cloud Secret Manager..."

    if ! command_exists gcloud; then
        log_error "gcloud CLI not found. Please install it first."
        return 1
    fi

    # Enable Secret Manager API
    log_info "Enabling Secret Manager API..."
    gcloud services enable secretmanager.googleapis.com

    # Create initial secrets if they don't exist
    PROJECT_ID=$(gcloud config get-value project)

    # JWT Secret Key
    if ! gcloud secrets describe jwt-secret-key --project="$PROJECT_ID" &>/dev/null; then
        log_info "Creating JWT secret key..."
        echo -n "$(openssl rand -hex 32)" | gcloud secrets create jwt-secret-key \
            --project="$PROJECT_ID" --data-file=-
        log_success "JWT secret key created"
    else
        log_success "JWT secret key already exists"
    fi

    # YouTube API Key (if provided)
    if [ ! -z "$YOUTUBE_API_KEY" ]; then
        if ! gcloud secrets describe youtube-api-key --project="$PROJECT_ID" &>/dev/null; then
            log_info "Creating YouTube API key secret..."
            echo -n "$YOUTUBE_API_KEY" | gcloud secrets create youtube-api-key \
                --project="$PROJECT_ID" --data-file=-
            log_success "YouTube API key secret created"
        else
            log_success "YouTube API key secret already exists"
        fi
    fi

    # YouTube Client Secrets (if file exists)
    if [ -f "client_secrets.json" ]; then
        if ! gcloud secrets describe youtube-client-secrets --project="$PROJECT_ID" &>/dev/null; then
            log_info "Creating YouTube client secrets..."
            gcloud secrets create youtube-client-secrets \
                --project="$PROJECT_ID" --data-file=client_secrets.json
            log_success "YouTube client secrets created"
        else
            log_success "YouTube client secrets already exist"
        fi
    fi

    log_success "Secret Manager setup complete"
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
include = '\.pyi?$'

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

# Setup YouTube API
setup_youtube_api() {
    log_info "Setting up YouTube API configuration..."

    # Check if YouTube API key is configured
    if ! gh secret list | grep -q "YOUTUBE_API_KEY"; then
        log_warning "YouTube API key not configured in GitHub secrets"
        log_info "To configure:"
        echo "  1. Get API key from: https://console.developers.google.com/"
        echo "  2. Run: gh secret set YOUTUBE_API_KEY"
        echo "  3. For OAuth credentials: gh secret set YOUTUBE_CREDENTIALS < client_secret.json"
    else
        log_success "YouTube API key configured"
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

# Main setup function
main() {
    log_info "Starting Video Genius environment setup..."
    echo ""

    # Step 1: Check prerequisites
    check_prerequisites

    # Step 2: Setup GitHub CLI
    setup_github_cli

    # Step 3: Setup Python environment
    setup_python_environment

    # Step 4: Setup pre-commit hooks
    setup_precommit_hooks

    # Step 5: Setup Google Cloud
    setup_google_cloud

    # Step 6: Setup Secret Manager
    setup_secret_manager

    # Step 7: Setup YouTube API
    setup_youtube_api

    # Step 8: Create environment files
    create_environment_files

    # Step 9: Setup Docker
    setup_docker

    # Step 10: Verify installation
    verify_installation

    echo ""
    log_success "🎉 Setup complete! You're ready to start developing."
    print_next_steps
}

# Run main function
main
