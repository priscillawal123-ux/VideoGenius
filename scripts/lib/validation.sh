#!/bin/bash
# Video Genius - Setup Validation Functions
# Versão: 1.0.0
# Descrição: Funções de validação para o script de setup

# Carrega biblioteca comum
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# ============================================================================
# VALIDAÇÃO DE PRÉ-REQUISITOS
# ============================================================================

# Verifica pré-requisitos do sistema
check_system_prerequisites() {
    log_info "Verificando pré-requisitos do sistema..."

    local missing_deps=()

    # Verifica Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    else
        local python_version
        python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python $python_version encontrado"
    fi

    # Verifica pip
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    fi

    # Verifica git
    if ! command_exists git; then
        missing_deps+=("git")
    else
        log_success "Git encontrado"
    fi

    # Verifica Docker (opcional)
    if ! command_exists docker; then
        log_warning "Docker não encontrado - opcional mas recomendado"
    else
        log_success "Docker encontrado"
    fi

    # Verifica se há dependências críticas faltando
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dependências críticas faltando: ${missing_deps[*]}"
        log_info "Instale-as e execute o setup novamente."
        return 1
    fi

    log_success "Pré-requisitos do sistema OK"
    return 0
}

# Verifica pré-requisitos do GitHub CLI
check_github_cli_prerequisites() {
    log_info "Verificando pré-requisitos do GitHub CLI..."

    # Verifica se gh está instalado
    if ! command_exists gh; then
        log_error "GitHub CLI não encontrado."
        log_info "Instale com: brew install gh (macOS) ou curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && sudo apt update && sudo apt install gh"
        return 1
    fi

    log_success "GitHub CLI encontrado"

    # Verifica autenticação
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI não autenticado."
        log_info "Execute: gh auth login"
        return 1
    fi

    log_success "GitHub CLI autenticado"
    return 0
}

# Verifica pré-requisitos do Google Cloud (opcional)
check_google_cloud_prerequisites() {
    log_info "Verificando pré-requisitos do Google Cloud..."

    if ! command_exists gcloud; then
        log_warning "gcloud CLI não encontrado."
        log_info "Instale de: https://cloud.google.com/sdk/docs/install"
        log_info "Pulando configuração do Google Cloud..."
        return 1
    fi

    log_success "gcloud CLI encontrado"

    # Verifica autenticação
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_warning "Não autenticado no Google Cloud."
        log_info "Será solicitado durante o setup..."
    else
        log_success "Autenticado no Google Cloud"
    fi

    return 0
}

# ============================================================================
# VALIDAÇÃO DE ARQUIVOS E DIRETÓRIOS
# ============================================================================

# Valida estrutura de arquivos existente
validate_existing_structure() {
    log_info "Validando estrutura existente..."

    local issues=0

    # Verifica se já existe um ambiente virtual
    if dir_exists ".venv"; then
        log_success "Ambiente virtual encontrado"
    else
        log_info "Ambiente virtual será criado"
    fi

    # Verifica arquivos de configuração existentes
    local config_files=(".env" ".env.local" "pyproject.toml" "requirements.txt")
    for config_file in "${config_files[@]}"; do
        if file_exists_and_readable "$config_file"; then
            log_success "Arquivo de configuração encontrado: $config_file"
        else
            log_debug "Arquivo de configuração será criado: $config_file"
        fi
    done

    # Verifica estrutura de diretórios
    local required_dirs=("backend" "tests")
    for dir in "${required_dirs[@]}"; do
        if dir_exists "$dir"; then
            log_success "Diretório encontrado: $dir"
        else
            log_debug "Diretório será criado: $dir"
        fi
    done

    return $issues
}

# ============================================================================
# VALIDAÇÃO DE VERSÕES
# ============================================================================

# Valida versão do Python
validate_python_version() {
    local min_version="${1:-3.11}"

    if ! command_exists python3; then
        log_error "Python3 não encontrado"
        return 1
    fi

    local python_version
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)

    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= tuple(map(int, '$min_version'.split('.'))) else 1)" 2>/dev/null; then
        log_error "Python $python_version encontrado, mas $min_version+ é necessário"
        return 1
    fi

    log_success "Python $python_version OK (mínimo: $min_version)"
    return 0
}

# ============================================================================
# VALIDAÇÃO DE PERMISSÕES
# ============================================================================

# Valida permissões de escrita
validate_write_permissions() {
    local test_file=".setup_test_write"

    # Tenta criar arquivo de teste
    if ! echo "test" > "$test_file" 2>/dev/null; then
        log_error "Sem permissões de escrita no diretório atual"
        return 1
    fi

    # Remove arquivo de teste
    rm -f "$test_file"

    log_success "Permissões de escrita OK"
    return 0
}

# ============================================================================
# VALIDAÇÃO DE REDE
# ============================================================================

# Testa conectividade com repositórios externos
test_network_connectivity() {
    log_info "Testando conectividade de rede..."

    local test_urls=("https://pypi.org" "https://github.com" "https://cloud.google.com")
    local failed_tests=0

    for url in "${test_urls[@]}"; do
        if curl -s --head --fail "$url" &> /dev/null; then
            log_debug "Conectividade OK: $url"
        else
            log_warning "Falha na conectividade: $url"
            ((failed_tests++))
        fi
    done

    if [ $failed_tests -gt 0 ]; then
        log_warning "Alguns testes de conectividade falharam. Verifique sua conexão com a internet."
        return 1
    fi

    log_success "Conectividade de rede OK"
    return 0
}

# ============================================================================
# FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ============================================================================

# Executa todas as validações
run_all_validations() {
    log_info "Iniciando validações completas..."

    local validation_errors=0

    # Validações críticas (devem passar)
    if ! validate_write_permissions; then
        ((validation_errors++))
    fi

    if ! check_system_prerequisites; then
        ((validation_errors++))
    fi

    if ! validate_python_version; then
        ((validation_errors++))
    fi

    # Validações importantes (warnings se falharem)
    if ! check_github_cli_prerequisites; then
        log_warning "GitHub CLI não configurado - algumas funcionalidades estarão limitadas"
    fi

    if ! check_google_cloud_prerequisites; then
        log_warning "Google Cloud não configurado - funcionalidades de cloud estarão limitadas"
    fi

    # Validações informativas
    validate_existing_structure
    test_network_connectivity || true  # Não é crítico

    if [ $validation_errors -gt 0 ]; then
        log_error "$validation_errors validação(ões) crítica(s) falhou(aram)"
        return 1
    fi

    log_success "Todas as validações críticas passaram"
    return 0
}

# ============================================================================
# EXECUÇÃO DIRETA
# ============================================================================

# Se executado diretamente, mostra ajuda
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        --help|-h)
            cat << EOF
$SCRIPT_NAME - Video Genius Setup Validation

VERSÃO: $SCRIPT_VERSION

DESCRIÇÃO:
    Executa validações completas do ambiente para setup do Video Genius.

FUNÇÕES:
    • Verifica pré-requisitos do sistema (Python, Git, Docker)
    • Valida GitHub CLI e autenticação
    • Verifica Google Cloud CLI (opcional)
    • Testa permissões de arquivo e rede
    • Valida estrutura existente do projeto

USO:
    source $SCRIPT_NAME
    run_all_validations

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
            run_all_validations
            ;;
    esac
fi