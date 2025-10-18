#!/bin/bash

################################################################################
# Final Deployment Script - Video Genius Production
# Deploys to Cloud Run with proper environment configuration
################################################################################

set -euo pipefail

PROJECT_ID="video-genius-prod-v1"
REGION="us-central1"
BACKEND_SERVICE="video-genius-backend"
FRONTEND_SERVICE="video-genius-frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Video Genius - Cloud Run Deployment                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Load environment variables
if [ -f .env.prod ]; then
    echo -e "\n${YELLOW}Loading .env.prod...${NC}"
    export $(grep -v '^#' .env.prod | xargs)
else
    echo -e "${YELLOW}⚠️  .env.prod not found, using defaults${NC}"
fi

# Verify authentication
echo -e "\n${YELLOW}[1/4] Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not authenticated${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Authenticated${NC}"

# Set project
echo -e "\n${YELLOW}[2/4] Setting GCP project...${NC}"
gcloud config set project "$PROJECT_ID"
echo -e "${GREEN}✅ Project set to $PROJECT_ID${NC}"

# Deploy Backend
echo -e "\n${YELLOW}[3/4] Deploying Backend Service...${NC}"
gcloud run deploy "$BACKEND_SERVICE" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 60s \
    --max-instances 100 \
    --min-instances 1 \
    --set-env-vars \
        SUPABASE_URL="${SUPABASE_URL:-https://db.khkiebkjaqncqpjsknup.supabase.co}",\
        SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9}",\
        SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9}",\
        ENVIRONMENT="production" \
    2>&1 | tail -20

BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format='value(status.url)')
echo -e "\n${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"

# Deploy Frontend
echo -e "\n${YELLOW}[4/4] Deploying Frontend Service...${NC}"
# Navigate to frontend directory
cd frontend || { echo -e "${RED}❌ frontend directory not found${NC}"; exit 1; }

# Build frontend
npm run build 2>&1 | tail -10

# Deploy to Cloud Run
cd .. && gcloud run deploy "$FRONTEND_SERVICE" \
    --source ./frontend \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --timeout 30s \
    --max-instances 50 \
    --min-instances 1 \
    --set-env-vars \
        REACT_APP_API_URL="${BACKEND_URL}" \
    2>&1 | tail -20

FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region "$REGION" --format='value(status.url)')
echo -e "\n${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"

# Final Status
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              ✅ DEPLOYMENT COMPLETE                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}Services Running:${NC}"
echo -e "  Backend:   ${BACKEND_URL}"
echo -e "  Frontend:  ${FRONTEND_URL}"
echo -e "  Domain:    https://videogenius.com.br"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Verify SSL certificate: https://videogenius.com.br"
echo -e "  2. Check monitoring: gcloud logging read --limit 50"
echo -e "  3. Test endpoints: curl ${BACKEND_URL}/health"
echo -e "  4. Monitor: https://console.cloud.google.com/run?project=${PROJECT_ID}"

echo -e "\n${GREEN}✨ Production is LIVE! ✨${NC}\n"
