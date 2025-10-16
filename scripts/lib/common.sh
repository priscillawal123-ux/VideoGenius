#!/bin/bash
# Video Genius - Common Library Functions
# Versão: 1.0.0
# Descrição: Funções utilitárias compartilhadas por todos os scripts

# Configurações globais
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_NAME="$(basename "$0")"

# Cores para output (compatível com diferentes terminais)
if [[ -t 1 ]]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly BLUE='\033[0;34m'
    readonly PURPLE='\033[0;35m'
    readonly CYAN='\033[0;36m'
    readonly NC='\033[0m' # No Color
else
    readonly RED=''
    readonly GREEN=''
    readonly YELLOW=''
    readonly BLUE=''
    readonly PURPLE=''
    readonly CYAN=''
    readonly NC=''
fi

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

# Função de logging principal
# Uso: log <level> <message>
# Exemplo: log "INFO" "Operação realizada com sucesso"
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        "INFO")
            echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $message" >&2
            ;;
        "WARNING")
            echo -e "${YELLOW}[${timestamp}] [WARNING]${NC} $message" >&2
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] [ERROR]${NC} $message" >&2
            ;;
        "DEBUG")
            if [[ "${DEBUG:-false}" == "true" ]]; then
                echo -e "${PURPLE}[${timestamp}] [DEBUG]${NC} $message" >&2
            fi
            ;;
        *)
            echo -e "${CYAN}[${timestamp}] [${level}]${NC} $message" >&2
            ;;
    esac
}

# Funções de logging específicas para conveniência
log_info() {
    log "INFO" "$1"
}

log_success() {
    log "SUCCESS" "$1"
}

log_warning() {
    log "WARNING" "$1"
}

log_error() {
    log "ERROR" "$1"
}

log_debug() {
    log "DEBUG" "$1"
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

# Verifica se comando existe
# Uso: command_exists <command>
# Retorno: 0 se existe, 1 se não existe
command_exists() {
    local cmd="$1"
    if command -v "$cmd" &> /dev/null; then
        log_debug "Command '$cmd' found"
        return 0
    else
        log_debug "Command '$cmd' not found"
        return 1
    fi
}

# Verifica se arquivo existe e é legível
# Uso: file_exists_and_readable <filepath>
# Retorno: 0 se existe e é legível, 1 caso contrário
file_exists_and_readable() {
    local file="$1"
    if [[ -f "$file" && -r "$file" ]]; then
        log_debug "File '$file' exists and is readable"
        return 0
    else
        log_debug "File '$file' does not exist or is not readable"
        return 1
    fi
}

# Verifica se diretório existe
# Uso: dir_exists <dirpath>
# Retorno: 0 se existe, 1 caso contrário
dir_exists() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        log_debug "Directory '$dir' exists"
        return 0
    else
        log_debug "Directory '$dir' does not exist"
        return 1
    fi
}

# Valida se string não está vazia
# Uso: is_not_empty <string>
# Retorno: 0 se não vazia, 1 se vazia
is_not_empty() {
    local str="$1"
    if [[ -n "$str" ]]; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# FILE OPERATIONS
# ============================================================================

# Cria diretório se não existir
# Uso: ensure_dir <dirpath>
ensure_dir() {
    local dir="$1"
    if ! dir_exists "$dir"; then
        log_debug "Creating directory: $dir"
        mkdir -p "$dir" || {
            log_error "Failed to create directory: $dir"
            return 1
        }
    else
        log_debug "Directory already exists: $dir"
    fi
}

# Cria arquivo com conteúdo se não existir
# Uso: create_file_if_not_exists <filepath> <content>
create_file_if_not_exists() {
    local file="$1"
    local content="$2"

    if ! file_exists_and_readable "$file"; then
        log_debug "Creating file: $file"
        echo "$content" > "$file" || {
            log_error "Failed to create file: $file"
            return 1
        }
    else
        log_debug "File already exists: $file"
    fi
}

# Backup de arquivo existente
# Uso: backup_file <filepath>
backup_file() {
    local file="$1"
    if file_exists_and_readable "$file"; then
        local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
        log_debug "Creating backup: $file -> $backup"
        cp "$file" "$backup" || {
            log_error "Failed to backup file: $file"
            return 1
        }
    fi
}

# ============================================================================
# SYSTEM DETECTION
# ============================================================================

# Detecta sistema operacional
# Uso: detect_os
# Define variáveis: OS_TYPE, OS_FAMILY
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
        OS_FAMILY="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        OS_FAMILY="unix"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS_TYPE="windows"
        OS_FAMILY="windows"
    else
        OS_TYPE="unknown"
        OS_FAMILY="unknown"
    fi

    log_debug "Detected OS: $OS_TYPE ($OS_FAMILY)"
}

# Verifica se está rodando como root/admin
# Uso: is_root
# Retorno: 0 se root, 1 se não
is_root() {
    if [[ $EUID -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Converte string para lowercase
# Uso: to_lower <string>
# Output: string em lowercase
to_lower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Converte string para uppercase
# Uso: to_upper <string>
# Output: string em uppercase
to_upper() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Remove espaços do início e fim da string
# Uso: trim <string>
# Output: string sem espaços
trim() {
    local str="$1"
    # Remove leading whitespace
    str="${str#"${str%%[![:space:]]*}"}"
    # Remove trailing whitespace
    str="${str%"${str##*[![:space:]]}"}"
    echo "$str"
}

# Gera string aleatória
# Uso: random_string <length>
# Output: string aleatória
random_string() {
    local length="${1:-32}"
    openssl rand -hex "$length" 2>/dev/null || {
        # Fallback se openssl não estiver disponível
        tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c "$length" 2>/dev/null || {
            # Último fallback
            echo "fallback_random_$(date +%s)_$RANDOM"
        }
    }
}

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Função para tratamento de erros
# Uso: error_exit <message> [exit_code]
error_exit() {
    local message="$1"
    local exit_code="${2:-1}"

    log_error "$message"
    echo "" >&2
    echo "💡 Para ajuda, execute: $SCRIPT_NAME --help" >&2
    exit "$exit_code"
}

# Trap para cleanup em caso de erro
# Uso: setup_error_trap
setup_error_trap() {
    trap 'error_exit "Script interrompido pelo usuário"' INT TERM
}

# ============================================================================
# VERSION & HELP
# ============================================================================

# Mostra versão do script
# Uso: show_version
show_version() {
    echo "$SCRIPT_NAME versão $SCRIPT_VERSION"
    echo "Video Genius - Common Library Functions"
}

# Mostra ajuda genérica
# Uso: show_help
show_help() {
    cat << EOF
$SCRIPT_NAME - Video Genius Script Library

VERSÃO: $SCRIPT_VERSION

DESCRIÇÃO:
    Biblioteca de funções utilitárias compartilhadas por todos os scripts
    do projeto Video Genius.

FUNÇÕES DISPONÍVEIS:
    Logging: log_info, log_success, log_warning, log_error, log_debug
    Validação: command_exists, file_exists_and_readable, dir_exists
    Arquivos: ensure_dir, create_file_if_not_exists, backup_file
    Sistema: detect_os, is_root
    Utilitários: to_lower, to_upper, trim, random_string

OPÇÕES:
    --help, -h          Mostra esta ajuda
    --version, -v       Mostra versão
    --debug             Habilita debug mode

EXEMPLOS:
    source lib/common.sh
    log_info "Operação iniciada"
    ensure_dir "caminho/para/diretorio"
    command_exists "docker" && log_success "Docker encontrado"

Para mais informações, consulte a documentação do projeto.
EOF
}

# ============================================================================
# INITIALIZATION
# ============================================================================

# Inicialização da biblioteca
init_common() {
    # Detecta sistema operacional
    detect_os

    # Setup error trap
    setup_error_trap

    # Processa argumentos se for executado diretamente
    if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
        case "${1:-}" in
            --help|-h)
                show_help
                exit 0
                ;;
            --version|-v)
                show_version
                exit 0
                ;;
            --debug)
                export DEBUG=true
                log_debug "Debug mode enabled"
                ;;
            "")
                show_help
                exit 0
                ;;
            *)
                error_exit "Opção desconhecida: $1"
                ;;
        esac
    fi
}

# Executa inicialização
init_common