#!/bin/bash
# Simple server startup script for Video Genius

echo "🚀 Starting Video Genius API Server..."

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/walland/credentials.json

# Change to workspace directory
cd /models/workspaces/ai-assistant/video-genius.code-workspace

# Start server
python3 -m uvicorn backend.api.main:create_application --factory --host 0.0.0.0 --port 8080 --log-level info --reload