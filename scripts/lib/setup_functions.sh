#!/bin/bash
# Video Genius - Setup Functions
# Versão: 1.0.0
# Descrição: Funções específicas para setup do ambiente

# Carrega biblioteca comum
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# ============================================================================
# GITHUB CLI SETUP
# ============================================================================

# Setup completo do GitHub CLI
setup_github_cli_complete() {
    log_info "Configurando GitHub CLI..."

    # Verifica se gh está instalado
    if ! command_exists gh; then
        log_warning "GitHub CLI não encontrado. Instalando..."

        # Detecta OS e instala adequadamente
        case "$OS_FAMILY" in
            "linux")
                install_github_cli_linux
                ;;
            "unix")
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    install_github_cli_macos
                else
                    log_error "Sistema Unix não suportado para instalação automática"
                    log_info "Instale GitHub CLI manualmente: https://cli.github.com/"
                    return 1
                fi
                ;;
            *)
                log_error "Sistema operacional não suportado"
                log_info "Instale GitHub CLI manualmente: https://cli.github.com/"
                return 1
                ;;
        esac

        log_success "GitHub CLI instalado"
    else
        log_success "GitHub CLI já instalado"
    fi

    # Verifica autenticação
    if ! gh auth status &> /dev/null; then
        log_info "Autenticando no GitHub..."
        gh auth login

        # Solicita escopos adicionais
        log_info "Solicitando escopos adicionais..."
        gh auth refresh -s copilot,workflow,write:packages
    else
        log_success "Já autenticado no GitHub"
    fi

    # Instala extensões
    install_github_cli_extensions

    # Configura aliases úteis
    setup_github_cli_aliases

    log_success "GitHub CLI configurado completamente"
}

# Instala GitHub CLI no Linux
install_github_cli_linux() {
    log_info "Instalando GitHub CLI no Linux..."

    # Adiciona chave GPG
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg

    # Adiciona repositório
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

    # Atualiza e instala
    sudo apt update
    sudo apt install gh -y
}

# Instala GitHub CLI no macOS
install_github_cli_macos() {
    log_info "Instalando GitHub CLI no macOS..."

    if command_exists brew; then
        brew install gh
    else
        log_error "Homebrew não encontrado. Instale Homebrew primeiro: https://brew.sh/"
        return 1
    fi
}

# Instala extensões do GitHub CLI
install_github_cli_extensions() {
    log_info "Instalando extensões do GitHub CLI..."

    # Instala extensão Copilot
    if ! gh extension list | grep -q "gh-copilot"; then
        log_info "Instalando gh-copilot..."
        gh extension install github/gh-copilot
        log_success "gh-copilot instalado"
    else
        log_success "gh-copilot já instalado"
        gh extension upgrade gh-copilot
    fi

    # Instala outras extensões úteis
    local extensions=("dlvhdr/gh-dash" "seachicken/gh-poi")
    for ext in "${extensions[@]}"; do
        local ext_name=$(basename "$ext")
        if ! gh extension list | grep -q "$ext_name"; then
            log_info "Instalando $ext_name..."
            if gh extension install "$ext" 2>/dev/null; then
                log_success "$ext_name instalado"
            else
                log_warning "Falha ao instalar $ext_name (opcional)"
            fi
        fi
    done
}

# Configura aliases do GitHub CLI
setup_github_cli_aliases() {
    log_info "Configurando aliases do GitHub CLI..."

    # Aliases úteis
    local aliases=(
        "prc:pr create --fill"
        "co:pr checkout"
        "work:issue list --assignee @me"
        "bugs:issue list --label bug"
        "ci:pr checks"
    )

    for alias_def in "${aliases[@]}"; do
        local alias_name="${alias_def%%:*}"
        local alias_expansion="${alias_def#*:}"

        if gh alias set "$alias_name" "$alias_expansion" 2>/dev/null; then
            log_debug "Alias configurado: $alias_name"
        else
            log_debug "Alias já existe ou falhou: $alias_name"
        fi
    done

    log_success "Aliases configurados"
}

# ============================================================================
# PYTHON ENVIRONMENT SETUP
# ============================================================================

# Setup completo do ambiente Python
setup_python_environment_complete() {
    log_info "Configurando ambiente Python..."

    # Cria ambiente virtual
    if ! dir_exists ".venv"; then
        log_info "Criando ambiente virtual..."
        python3 -m venv .venv
        log_success "Ambiente virtual criado"
    else
        log_success "Ambiente virtual já existe"
    fi

    # Ativa ambiente virtual
    source .venv/bin/activate

    # Atualiza pip
    log_info "Atualizando pip..."
    pip install --upgrade pip setuptools wheel

    # Instala dependências de desenvolvimento
    install_python_dependencies "dev"

    # Instala dependências de produção
    install_python_dependencies "prod"

    log_success "Ambiente Python configurado"
}

# Instala dependências Python
install_python_dependencies() {
    local env_type="$1"  # "dev" ou "prod"

    case "$env_type" in
        "dev")
            local req_file="requirements-dev.txt"
            local desc="desenvolvimento"
            ;;
        "prod")
            local req_file="requirements.txt"
            local desc="produção"
            ;;
        *)
            log_error "Tipo de ambiente inválido: $env_type"
            return 1
            ;;
    esac

    if file_exists_and_readable "$req_file"; then
        log_info "Instalando dependências de $desc..."
        pip install -r "$req_file"
        log_success "Dependências de $desc instaladas"
    else
        log_warning "$req_file não encontrado, criando..."
        create_requirements_file "$req_file" "$env_type"
        pip install -r "$req_file"
    fi
}

# Cria arquivo de requirements se não existir
create_requirements_file() {
    local req_file="$1"
    local env_type="$2"

    case "$env_type" in
        "dev")
            cat > "$req_file" << 'EOF'
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
            ;;
        "prod")
            cat > "$req_file" << 'EOF'
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
            ;;
    esac

    log_success "$req_file criado"
}

# ============================================================================
# PRE-COMMIT SETUP
# ============================================================================

# Setup completo do pre-commit
setup_precommit_complete() {
    log_info "Configurando pre-commit hooks..."

    # Cria configuração se não existir
    if ! file_exists_and_readable ".pre-commit-config.yaml"; then
        create_precommit_config
    fi

    # Instala hooks
    source .venv/bin/activate
    pre-commit install
    pre-commit install --hook-type commit-msg

    log_success "Pre-commit hooks configurados"
}

# Cria configuração do pre-commit
create_precommit_config() {
    log_info "Criando configuração do pre-commit..."

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

    log_success "Configuração do pre-commit criada"
}

# ============================================================================
# GOOGLE CLOUD SETUP
# ============================================================================

# Setup do Google Cloud
setup_google_cloud_complete() {
    log_info "Configurando Google Cloud..."

    if ! command_exists gcloud; then
        log_warning "gcloud CLI não encontrado."
        log_info "Instale de: https://cloud.google.com/sdk/docs/install"
        log_info "Pulando configuração do Google Cloud..."
        return 1
    fi

    log_success "gcloud CLI encontrado"

    # Verifica autenticação
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_info "Autenticando no Google Cloud..."
        gcloud auth login
        gcloud auth application-default login
    else
        log_success "Já autenticado no Google Cloud"
    fi

    # Solicita projeto
    setup_google_cloud_project

    log_success "Google Cloud configurado"
}

# Configura projeto do Google Cloud
setup_google_cloud_project() {
    echo ""
    read -p "Digite seu Google Cloud Project ID (ou Enter para pular): " project_id

    if [[ -n "$project_id" ]]; then
        gcloud config set project "$project_id"
        log_success "Projeto definido: $project_id"

        # Habilita APIs necessárias
        log_info "Habilitando APIs do Google Cloud..."
        gcloud services enable \
            aiplatform.googleapis.com \
            bigquery.googleapis.com \
            storage.googleapis.com \
            run.googleapis.com \
            cloudbuild.googleapis.com \
            secretmanager.googleapis.com \
            2>/dev/null || log_warning "Algumas APIs podem já estar habilitadas"

        log_success "APIs do Google Cloud habilitadas"
    fi
}

# ============================================================================
# CONFIGURATION FILES SETUP
# ============================================================================

# Cria arquivos de configuração
create_configuration_files() {
    log_info "Criando arquivos de configuração..."

    # Arquivos de configuração principais
    create_env_files
    create_pyproject_toml
    create_gitignore

    log_success "Arquivos de configuração criados"
}

# Cria arquivos .env
create_env_files() {
    # .env.example
    if ! file_exists_and_readable ".env.example"; then
        cat > .env.example << 'EOF'
# Environment
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
        log_success ".env.example criado"
    fi

    # .env.local
    if ! file_exists_and_readable ".env.local"; then
        log_info "Criando .env.local..."
        cp .env.example .env.local
        log_warning "Atualize .env.local com suas credenciais reais"
    else
        log_success ".env.local já existe"
    fi
}

# Cria pyproject.toml
create_pyproject_toml() {
    if ! file_exists_and_readable "pyproject.toml"; then
        cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "video-genius"
version = "0.1.0"
description = "AI-powered video generation platform"
authors = ["Video Genius Team <team@video-genius.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = {extras = ["settings"], version = "^2.5.0"}
google-cloud-aiplatform = "^1.38.0"
google-cloud-bigquery = "^3.13.0"
google-cloud-storage = "^2.10.0"
python-multipart = "^0.0.6"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
ruff = "^0.1.6"
mypy = "^1.7.1"
pre-commit = "^3.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=backend --cov-report=term-missing"
EOF
        log_success "pyproject.toml criado"
    fi
}

# Cria .gitignore
create_gitignore() {
    if ! file_exists_and_readable ".gitignore"; then
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

# Temporary files
tmp/
temp/
*.tmp
EOF
        log_success ".gitignore criado"
    fi
}

# ============================================================================
# EXECUÇÃO DIRETA
# ============================================================================

# Se executado diretamente, mostra ajuda
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        --help|-h)
            cat << EOF
$SCRIPT_NAME - Video Genius Setup Functions

VERSÃO: $SCRIPT_VERSION

DESCRIÇÃO:
    Funções específicas para setup completo do ambiente Video Genius.

FUNÇÕES DISPONÍVEIS:
    • setup_github_cli_complete     - Setup completo do GitHub CLI
    • setup_python_environment_complete - Setup do ambiente Python
    • setup_precommit_complete      - Setup do pre-commit
    • setup_google_cloud_complete   - Setup do Google Cloud
    • create_configuration_files    - Cria arquivos de configuração

USO:
    source $SCRIPT_NAME
    setup_github_cli_complete

OPÇÕES:
    --help, -h          Mostra esta ajuda
    --version, -v       Mostra versão
EOF
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        *)
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
fi