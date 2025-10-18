#!/bin/bash
# Deploy script for Video Genius to Google Cloud Run
# Usage: ./deploy-cloud-run.sh [backend|frontend|both]

set -e

PROJECT_ID="video-genius-prod-v1"
REGION="us-central1"
BACKEND_SERVICE="video-genius-backend"
FRONTEND_SERVICE="video-genius-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check gcloud is authenticated
check_auth() {
    log_info "Checking Google Cloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated to Google Cloud"
        log_info "Run: gcloud auth login"
        exit 1
    fi
    log_success "Authenticated"
}

# Set project
set_project() {
    log_info "Setting project to $PROJECT_ID..."
    gcloud config set project $PROJECT_ID
    log_success "Project set"
}

# Deploy Backend
deploy_backend() {
    log_info "Deploying Backend..."
    
    gcloud run deploy $BACKEND_SERVICE \
        --source . \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --timeout 60s \
        --max-instances 100 \
        --min-instances 1 \
        --no-gen2 \
        --set-env-vars \
            SUPABASE_URL=${SUPABASE_URL:-},\
            SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-},\
            SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY:-} \
        --service-account video-genius-sa@${PROJECT_ID}.iam.gserviceaccount.com

    log_success "Backend deployed"
    
    # Get service URL
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format='value(status.url)')
    echo -e "${GREEN}Backend URL: $BACKEND_URL${NC}"
}

# Deploy Frontend
deploy_frontend() {
    log_info "Deploying Frontend..."
    
    # Build frontend first
    log_info "Building frontend..."
    cd frontend
    npm ci
    npm run build
    cd ..
    
    gcloud run deploy $FRONTEND_SERVICE \
        --source ./frontend \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 0.5 \
        --timeout 60s \
        --max-instances 50 \
        --min-instances 1 \
        --no-gen2 \
        --set-env-vars \
            VITE_API_URL=${BACKEND_URL:-http://localhost:8000} \
        --service-account video-genius-sa@${PROJECT_ID}.iam.gserviceaccount.com

    log_success "Frontend deployed"
    
    # Get service URL
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --format='value(status.url)')
    echo -e "${GREEN}Frontend URL: $FRONTEND_URL${NC}"
}

# Main
main() {
    local target=${1:-both}
    
    log_info "Starting deployment process..."
    check_auth
    set_project
    
    case $target in
        backend)
            deploy_backend
            ;;
        frontend)
            deploy_frontend
            ;;
        both)
            deploy_backend
            deploy_frontend
            ;;
        *)
            log_error "Invalid target: $target"
            log_info "Usage: ./deploy-cloud-run.sh [backend|frontend|both]"
            exit 1
            ;;
    esac
    
    log_success "Deployment complete!"
}

# Run main
main "$@"
