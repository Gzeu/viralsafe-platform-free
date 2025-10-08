#!/bin/bash
# Script de start pentru Render.com
echo "🚀 Starting ViralSafe API on Render.com..."
echo "Port: $PORT"
echo "Environment: $ENVIRONMENT"

# Start aplicația
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1