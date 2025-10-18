#!/bin/bash
# Run the video generation worker locally

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the worker
uvicorn backend.worker.main:app --host 0.0.0.0 --port 8081 --reload