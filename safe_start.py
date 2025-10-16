#!/usr/bin/env python3
"""
Simple server startup script that avoids service initialization issues.
"""

import os
import sys

import uvicorn

# Add backend to path
sys.path.insert(0, "/models/workspaces/ai-assistant/video-genius.code-workspace")

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/walland/credentials.json"

if __name__ == "__main__":
    print("🚀 Starting Video Genius API Server (Safe Mode)...")

    # Start server with minimal initialization
    uvicorn.run(
        "backend.api.main:create_application",
        factory=True,
        host="127.0.0.1",
        port=8080,
        log_level="info",
        reload=False,  # Disable reload to avoid re-initialization issues
        access_log=True,
    )
