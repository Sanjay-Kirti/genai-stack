#!/bin/bash

# GenAI Stack - Docker Build Script

set -e

echo "🐳 Building GenAI Stack Docker Images..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Build backend image
echo "📦 Building backend image..."
docker build -t genai-stack/backend:latest ./backend

# Build frontend image
echo "📦 Building frontend image..."
docker build -t genai-stack/frontend:latest ./frontend

# Build production images
echo "📦 Building production images..."
docker build -f ./backend/Dockerfile.prod -t genai-stack/backend:prod ./backend
docker build -f ./frontend/Dockerfile.prod -t genai-stack/frontend:prod \
    --build-arg VITE_API_URL=${VITE_API_URL:-http://localhost:8000} \
    --build-arg VITE_WS_URL=${VITE_WS_URL:-ws://localhost:8000} \
    ./frontend

echo "✅ All images built successfully!"

# List built images
echo "📋 Built images:"
docker images | grep genai-stack
