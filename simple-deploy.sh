#!/bin/bash

# Simple Cloud Run deploy script
set -e

PROJECT_ID="video-genius-prod-v1"
SERVICE_NAME="video-genius-api"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "🚀 Deploying Video Genius API to Cloud Run"
echo "Image: ${IMAGE}"
echo ""

# Deploy
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --project "${PROJECT_ID}" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10

echo ""
echo "✅ Deployment initiated"
echo "View service: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}?project=${PROJECT_ID}"
