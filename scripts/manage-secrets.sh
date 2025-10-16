#!/bin/bash
# Video Genius - Secret Manager CLI Tool
# Manage secrets using Google Cloud Secret Manager

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
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
    command -v "$1" >/dev/null 2>&1
}

# Check if gcloud is available
check_gcloud() {
    if ! command_exists gcloud; then
        log_error "gcloud CLI not found. Please install the Google Cloud SDK (gcloud)."
        echo ""
        echo "Helpful install commands (choose one based on your OS):"
        echo "  Debian / Ubuntu:" 
        echo "    sudo apt-get update && sudo apt-get install -y ca-certificates gnupg"
        echo "    echo 'deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main' | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list"
        echo "    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -"
        echo "    sudo apt-get update && sudo apt-get install -y google-cloud-sdk"
        echo "  macOS (Homebrew):"
        echo "    brew install --cask google-cloud-sdk"
        echo "  Alternative (interactive installer):"
        echo "    curl https://sdk.cloud.google.com | bash && exec -l \$SHELL && gcloud init"
        echo ""
        echo "Or follow: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with Google Cloud. Run: gcloud auth login"
        exit 1
    fi
}

# Get current project
get_project() {
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        log_error "No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    echo "$PROJECT_ID"
}

# List all secrets
list_secrets() {
    PROJECT_ID=$(get_project)
    log_info "Listing secrets in project: $PROJECT_ID"
    
    gcloud secrets list --project="$PROJECT_ID" \
        --format="table(name.basename():label=NAME,createTime.date('%Y-%m-%d %H:%M:%S'))"
}

# Create or update a secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_name" ] || [ -z "$secret_value" ]; then
        log_error "Usage: $0 create <secret-name> <secret-value>"
        exit 1
    fi
    
    PROJECT_ID=$(get_project)
    
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        log_info "Updating existing secret: $secret_name"
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --project="$PROJECT_ID" --data-file=-
    else
        log_info "Creating new secret: $secret_name"
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --project="$PROJECT_ID" --data-file=-
    fi
    
    log_success "Secret $secret_name updated"
}

# Get a secret value
get_secret() {
    local secret_name=$1
    local version=${2:-latest}
    
    if [ -z "$secret_name" ]; then
        log_error "Usage: $0 get <secret-name> [version]"
        exit 1
    fi
    
    PROJECT_ID=$(get_project)
    
    log_info "Retrieving secret: $secret_name (version: $version)"
    gcloud secrets versions access "$version" \
        --secret="$secret_name" --project="$PROJECT_ID"
}

# Delete a secret
delete_secret() {
    local secret_name=$1
    
    if [ -z "$secret_name" ]; then
        log_error "Usage: $0 delete <secret-name>"
        exit 1
    fi
    
    PROJECT_ID=$(get_project)
    
    if ! gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        log_error "Secret $secret_name does not exist"
        exit 1
    fi
    
    read -p "Are you sure you want to delete secret '$secret_name'? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        gcloud secrets delete "$secret_name" --project="$PROJECT_ID" --quiet
        log_success "Secret $secret_name deleted"
    else
        log_info "Operation cancelled"
    fi
}

# Setup initial secrets for Video Genius
setup_initial_secrets() {
    PROJECT_ID=$(get_project)
    log_info "Setting up initial secrets for Video Genius..."
    
    # JWT Secret Key
    if ! gcloud secrets describe jwt-secret-key --project="$PROJECT_ID" &>/dev/null; then
        log_info "Creating JWT secret key..."
        openssl rand -hex 32 | create_secret "jwt-secret-key" "$(cat)"
        log_success "JWT secret key created"
    else
        log_success "JWT secret key already exists"
    fi
    
    # Check for YouTube API key in environment
    if [ ! -z "$YOUTUBE_API_KEY" ]; then
        if ! gcloud secrets describe youtube-api-key --project="$PROJECT_ID" &>/dev/null; then
            log_info "Creating YouTube API key secret..."
            create_secret "youtube-api-key" "$YOUTUBE_API_KEY"
            log_success "YouTube API key secret created"
        fi
    else
        log_warning "YOUTUBE_API_KEY not set. Run: export YOUTUBE_API_KEY=your-key"
    fi
    
    # Check for client_secrets.json
    if [ -f "client_secrets.json" ]; then
        if ! gcloud secrets describe youtube-client-secrets --project="$PROJECT_ID" &>/dev/null; then
            log_info "Creating YouTube client secrets..."
            create_secret "youtube-client-secrets" "$(cat client_secrets.json)"
            log_success "YouTube client secrets created"
        fi
    else
        log_warning "client_secrets.json not found. Download from Google Cloud Console."
    fi
}

# Show usage
usage() {
    echo "Video Genius - Secret Manager CLI Tool"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list                    List all secrets"
    echo "  create <name> <value>   Create or update a secret"
    echo "  get <name> [version]    Get secret value"
    echo "  delete <name>           Delete a secret"
    echo "  setup                   Setup initial secrets for Video Genius"
    echo "  help                    Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 create my-secret 'secret-value'"
    echo "  $0 get my-secret"
    echo "  $0 setup"
}

# Main script
main() {
    check_gcloud
    
    case "${1:-help}" in
        list)
            list_secrets
            ;;
        create)
            create_secret "$2" "$3"
            ;;
        get)
            get_secret "$2" "$3"
            ;;
        delete)
            delete_secret "$2"
            ;;
        setup)
            setup_initial_secrets
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"