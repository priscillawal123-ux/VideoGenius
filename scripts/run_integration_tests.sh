#!/bin/bash
# Run integration tests

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run integration tests
pytest tests/integration/ -v --tb=short