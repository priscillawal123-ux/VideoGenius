#!/bin/bash
# GH Copilot Suggest Wrapper - Resolve problemas de clipboard
# Versão: 1.0.0
# Uso: ./gh-suggest.sh "sua descrição do comando"

# Carrega biblioteca comum
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# ============================================================================
# CONFIGURAÇÃO ESPECÍFICA DO SCRIPT
# ============================================================================

readonly TEMP_FILE="/tmp/gh-copilot-cmd.sh"

# ============================================================================
# FUNÇÕES ESPECÍFICAS
# ============================================================================

# Mostra ajuda específica do script
show_script_help() {
    cat << EOF
$SCRIPT_NAME - GH Copilot Suggest Wrapper

VERSÃO: $SCRIPT_VERSION

DESCRIÇÃO:
    Wrapper inteligente para o GitHub Copilot CLI que detecta automaticamente
    se a tarefa é de geração de código ou comando shell.

USO:
    $SCRIPT_NAME "descrição clara do comando desejado"

EXEMPLOS DE COMANDOS SHELL:
    $SCRIPT_NAME "create python virtual environment"
    $SCRIPT_NAME "install docker and docker-compose"
    $SCRIPT_NAME "setup git repository with main branch"
    $SCRIPT_NAME "run pytest with coverage report"
    $SCRIPT_NAME "start PostgreSQL database"

NOTA SOBRE GERAÇÃO DE CÓDIGO:
    Para geração de código, use o Copilot no VS Code:
    • Abra o arquivo desejado
    • Escreva um comentário descritivo
    • Pressione Ctrl+Enter para gerar código

DICAS PARA COMANDOS SHELL:
    • Seja específico sobre o que quer fazer
    • Use termos técnicos quando possível
    • Descreva o resultado esperado
    • Inclua ferramentas ou tecnologias específicas

OPÇÕES GERAIS:
    --help, -h          Mostra esta ajuda
    --version, -v       Mostra versão
    --debug             Habilita debug mode
EOF
}

# Valida argumentos de entrada
validate_input() {
    local description="$1"

    # Verifica se foi fornecido algum argumento
    if [[ $# -eq 0 ]]; then
        log_error "Nenhum argumento fornecido!"
        echo ""
        show_script_help
        exit 1
    fi

    # Verifica se a descrição não está vazia
    if ! is_not_empty "$description"; then
        log_error "Descrição vazia!"
        log_info "Use: $SCRIPT_NAME \"descrição do comando\""
        exit 1
    fi

    log_debug "Input validado: '$description'"
}

# Detecta se a descrição parece ser uma tarefa de geração de código
is_code_generation_task() {
    local description="$1"

    # Palavras-chave que indicam geração de código
    local code_keywords=(
        "create.*route" "create.*endpoint" "create.*function"
        "create.*class" "create.*model" "create.*api"
        "implement.*route" "implement.*endpoint" "implement.*function"
        "implement.*class" "implement.*model" "implement.*api"
        "build.*route" "build.*endpoint" "build.*function"
        "build.*class" "build.*model" "build.*api"
        "generate.*route" "generate.*endpoint" "generate.*function"
        "generate.*class" "generate.*model" "generate.*api"
        "add.*route" "add.*endpoint" "add.*function"
        "add.*class" "add.*model" "add.*api"
        "write.*route" "write.*endpoint" "write.*function"
        "write.*class" "write.*model" "write.*api"
    )

    # Verifica se a descrição contém alguma palavra-chave de código
    for keyword in "${code_keywords[@]}"; do
        if echo "$description" | grep -qiE "$keyword"; then
            log_debug "Detected code generation keyword: $keyword"
            return 0
        fi
    done

    return 1
}

# Mostra mensagem de orientação para geração de código
show_code_generation_guidance() {
    log_warning "DETECTADO: Esta parece ser uma tarefa de GERAÇÃO DE CÓDIGO"
    echo ""
    log_info "💡 Para geração de código, use o GitHub Copilot no VS Code:"
    echo "   1. Abra o arquivo relevante (ex: backend/api/routes/auth.py)"
    echo "   2. Escreva um comentário descritivo:"
    echo "      # Create FastAPI route for user authentication"
    echo "   3. Pressione Ctrl+Enter ou clique no ícone do Copilot"
    echo ""
    log_info "🔧 Ou use comandos específicos:"
    echo "   $SCRIPT_NAME \"create new python file for authentication\""
    echo "   $SCRIPT_NAME \"setup JWT authentication in FastAPI\""
    echo ""
    log_error "❌ Cancelando geração de comando shell..."
}

# Gera sugestão usando GH Copilot
generate_suggestion() {
    local description="$1"

    log_info "🤖 Gerando comando com GH Copilot..."
    log_info "📝 Descrição: \"$description\""
    echo ""

    # Gera sugestão usando arquivo de saída
    if gh copilot suggest -t shell "$description" -s "$TEMP_FILE"; then
        if file_exists_and_readable "$TEMP_FILE"; then
            log_success "✅ Comando gerado com sucesso!"
            echo "📋 Comando sugerido:"
            echo "----------------------------------------"
            cat "$TEMP_FILE"
            echo "----------------------------------------"
            echo ""
            log_info "💾 Comando salvo em: $TEMP_FILE"
            log_info "📝 Execute manualmente: bash $TEMP_FILE"
        else
            log_error "❌ Arquivo de saída não foi criado"
            show_troubleshooting_tips
            exit 1
        fi
    else
        log_error "❌ Falha ao gerar sugestão."
        show_troubleshooting_tips
        exit 1
    fi
}

# Mostra dicas de resolução de problemas
show_troubleshooting_tips() {
    log_info "💡 Dicas para resolver problemas:"
    echo "   • Certifique-se de que o GitHub CLI está autenticado: gh auth status"
    echo "   • Verifique se a extensão copilot está instalada: gh extension list"
    echo "   • Tente reformular a descrição para ser mais específica"
    echo "   • Use termos técnicos quando possível"
    echo "   • Evite termos de geração de código (create, implement, build)"
    echo "   • Exemplos funcionais: 'install package', 'start service', 'setup database'"
}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

main() {
    local description="$1"

    # Processa argumentos específicos do script
    case "${1:-}" in
        --help|-h)
            show_script_help
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
    esac

    # Valida entrada
    validate_input "$description"

    # Detecta tipo de tarefa
    if is_code_generation_task "$description"; then
        show_code_generation_guidance
        exit 1
    fi

    # Gera sugestão
    generate_suggestion "$description"
}

# ============================================================================
# EXECUÇÃO
# ============================================================================

# Executa função principal com todos os argumentos
main "$@"