#!/bin/bash
# Video Genius - Migrate GitHub Secrets to GCP Secret Manager
# This script migrates secrets from GitHub to Google Cloud Secret Manager

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

# Check prerequisites
check_prerequisites() {
    if ! command_exists gh; then
        log_error "GitHub CLI not found. Please install it first."
        exit 1
    fi

    if ! command_exists gcloud; then
        log_error "Google Cloud CLI not found. Please install it first."
        exit 1
    fi

    if ! gh auth status &>/dev/null; then
        log_error "Not authenticated with GitHub. Run: gh auth login"
        exit 1
    fi

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with Google Cloud. Run: gcloud auth login"
        exit 1
    fi
}

# Get project ID
get_project_id() {
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        log_error "No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    echo "$PROJECT_ID"
}

# Migrate a secret from GitHub to GCP
migrate_secret() {
    local secret_name=$1
    local description=${2:-"Migrated from GitHub"}

    log_info "Migrating secret: $secret_name"

    # Get secret value from GitHub
    local secret_value
    if ! secret_value=$(gh secret view "$secret_name" 2>/dev/null); then
        log_warning "Secret $secret_name not found in GitHub"
        return 1
    fi

    # Create secret in GCP Secret Manager
    PROJECT_ID=$(get_project_id)

    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        log_warning "Secret $secret_name already exists in GCP Secret Manager"
        return 0
    fi

    echo -n "$secret_value" | gcloud secrets create "$secret_name" \
        --project="$PROJECT_ID" \
        --data-file=- \
        --description="$description"

    log_success "Migrated $secret_name to GCP Secret Manager"
}

# Main migration function
main() {
    log_info "Starting migration from GitHub Secrets to GCP Secret Manager..."

    check_prerequisites

    PROJECT_ID=$(get_project_id)
    log_info "Using GCP project: $PROJECT_ID"

    # Enable Secret Manager API
    log_info "Enabling Secret Manager API..."
    gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"

    # List of secrets to migrate
    secrets_to_migrate=(
        "GOOGLE_PROJECT_ID"
        "CLOUD_STORAGE_BUCKET"
        "YOUTUBE_API_KEY"
        "BIGQUERY_DATASET"
        "VERTEX_AI_LOCATION"
        "USE_SECRET_MANAGER"
    )

    log_info "Migrating secrets..."
    for secret in "${secrets_to_migrate[@]}"; do
        migrate_secret "$secret" "Video Genius configuration - migrated from GitHub"
    done

    # Create additional secrets that might be needed
    log_info "Creating additional secrets..."

    # JWT Secret Key (generate new one)
    if ! gcloud secrets describe jwt-secret-key --project="$PROJECT_ID" &>/dev/null; then
        log_info "Creating JWT secret key..."
        openssl rand -hex 32 | gcloud secrets create jwt-secret-key \
            --project="$PROJECT_ID" \
            --data-file=- \
            --description="JWT signing key for Video Genius"
        log_success "JWT secret key created"
    fi

    log_success "Migration complete!"
    echo ""
    echo "Next steps:"
    echo "1. Update your .env file: USE_SECRET_MANAGER=true"
    echo "2. Remove sensitive secrets from GitHub if desired"
    echo "3. Test your application with Secret Manager"
    echo ""
    echo "To list secrets in GCP:"
    echo "  gcloud secrets list --project=$PROJECT_ID"
    echo ""
    echo "To access a secret:"
    echo "  gcloud secrets versions access latest --secret=jwt-secret-key --project=$PROJECT_ID"
}

main "$@"