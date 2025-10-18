#!/bin/bash
# Video Genius Production Deployment Script
# Deploys the application to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID="video-genius-prod-v1"
SERVICE_NAME="video-genius-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gcloud is installed and authenticated
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_error "Not authenticated with Google Cloud. Please run 'gcloud auth login' first."
        exit 1
    fi

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi

    # Set project
    log_info "Setting project to ${PROJECT_ID}..."
    gcloud config set project "${PROJECT_ID}"

    log_success "Prerequisites check passed"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building Docker image..."

    # Get current commit SHA for versioning (first 7 chars)
    COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
    
    # Use gcr.io format for GCR with full registry path
    IMAGE_REGISTRY="gcr.io"
    IMAGE_TAG="${IMAGE_REGISTRY}/${PROJECT_ID}/${SERVICE_NAME}:${COMMIT_SHA}"
    IMAGE_LATEST="${IMAGE_REGISTRY}/${PROJECT_ID}/${SERVICE_NAME}:latest"

    log_info "Building Docker image: ${IMAGE_TAG}"

    # Authenticate Docker with GCR first
    log_info "Configuring Docker for GCR..."
    gcloud auth configure-docker "${IMAGE_REGISTRY}" --quiet || {
        log_error "Failed to configure Docker for GCR"
        exit 1
    }

    # Build image using docker buildx (faster and better caching)
    log_info "Building Docker image with buildx (this may take a few minutes)..."
    docker buildx build \
        --push \
        --tag "${IMAGE_TAG}" \
        --tag "${IMAGE_LATEST}" \
        --file Dockerfile \
        --platform linux/amd64 \
        . || {
        log_error "Docker buildx build failed"
        exit 1
    }

    log_success "Docker image built and pushed successfully to GCR"

    # Verify image exists in GCR
    log_info "Verifying image in GCR..."
    gcloud container images describe "${IMAGE_TAG}" --project="${PROJECT_ID}" > /dev/null || {
        log_error "Image not found in GCR after push"
        exit 1
    }

    log_success "Image verified in GCR: ${IMAGE_TAG}"

    # Echo the full image path with registry
    echo "${IMAGE_TAG}"
}

# Setup secrets in Secret Manager
setup_secrets() {
    log_info "Setting up secrets in Google Secret Manager..."

    # JWT Secret Key
    if ! gcloud secrets describe jwt-secret-key &> /dev/null; then
        log_info "Creating JWT secret key..."
        echo -n "$(openssl rand -base64 32)" | gcloud secrets create jwt-secret-key --data-file=-
        log_success "JWT secret key created"
    else
        log_success "JWT secret key already exists"
    fi

    # YouTube API Key
    if ! gcloud secrets describe youtube-api-key &> /dev/null; then
        log_warning "YouTube API key secret not found."
        log_info "Please create it manually:"
        echo "echo -n 'YOUR_YOUTUBE_API_KEY' | gcloud secrets create youtube-api-key --data-file=-"
        echo "Then run this script again."
        exit 1
    else
        log_success "YouTube API key secret exists"
    fi
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    local image_tag=$1

    log_info "Deploying to Google Cloud Run..."

    # Deploy the service
    gcloud run deploy "${SERVICE_NAME}" \
        --image "${image_tag}" \
        --region "${REGION}" \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10 \
        --concurrency 80 \
        --timeout 900 \
        --set-env-vars "ENV=production,GCP_PROJECT_ID=${PROJECT_ID},USE_SECRET_MANAGER=true,SECRET_MANAGER_PROJECT_ID=${PROJECT_ID},LOG_LEVEL=INFO" \
        --set-secrets "JWT_SECRET_KEY=jwt-secret-key:latest,YOUTUBE_API_KEY=youtube-api-key:latest"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format="value(status.url)")

    log_success "Deployment completed!"
    log_info "Service URL: ${SERVICE_URL}"
    log_info "API Documentation: ${SERVICE_URL}/docs"
    log_info "Health Check: ${SERVICE_URL}/health"

    echo "${SERVICE_URL}"
}

# Setup custom domain
setup_custom_domain() {
    local service_url=$1

    log_info "Setting up custom domain videogenius.com.br..."

    # Note: This requires domain ownership verification
    log_warning "Custom domain setup requires manual configuration:"
    echo ""
    echo "1. Go to Cloud Run service in GCP Console"
    echo "2. Click on the service '${SERVICE_NAME}'"
    echo "3. Go to the 'Networking' tab"
    echo "4. Click 'Add mapping'"
    echo "5. Add domain: videogenius.com.br"
    echo "6. Follow the DNS configuration instructions"
    echo ""
    log_info "Current service URL: ${service_url}"
}

# Run health check
run_health_check() {
    local service_url=$1

    log_info "Running health check..."

    # Wait a bit for the service to be ready
    sleep 10

    # Check health endpoint
    if curl -f -s "${service_url}/health" > /dev/null; then
        log_success "Health check passed!"
    else
        log_error "Health check failed. Please check the service logs."
        exit 1
    fi
}

# Main deployment function
main() {
    log_info "🚀 Starting Video Genius production deployment..."
    echo ""

    # Check prerequisites
    check_prerequisites
    echo ""

    # Setup secrets
    setup_secrets
    echo ""

    # Build and push image
    IMAGE_TAG=$(build_and_push_image)
    echo ""

    # Deploy to Cloud Run
    SERVICE_URL=$(deploy_to_cloud_run "${IMAGE_TAG}")
    echo ""

    # Run health check
    run_health_check "${SERVICE_URL}"
    echo ""

    # Setup custom domain
    setup_custom_domain "${SERVICE_URL}"
    echo ""

    log_success "🎉 Deployment completed successfully!"
    log_info "Your Video Genius API is now live at: ${SERVICE_URL}"
}

# Run main function
main