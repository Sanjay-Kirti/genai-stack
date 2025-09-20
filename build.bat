@echo off
REM GenAI Stack - Docker Build Script for Windows

echo 🐳 Building GenAI Stack Docker Images...

REM Build backend image
echo 📦 Building backend image...
docker build -t genai-stack/backend:latest ./backend
if %ERRORLEVEL% neq 0 (
    echo ❌ Backend build failed!
    exit /b 1
)

REM Build frontend image
echo 📦 Building frontend image...
docker build -t genai-stack/frontend:latest ./frontend
if %ERRORLEVEL% neq 0 (
    echo ❌ Frontend build failed!
    exit /b 1
)

REM Build production images
echo 📦 Building production images...
docker build -f ./backend/Dockerfile.prod -t genai-stack/backend:prod ./backend
if %ERRORLEVEL% neq 0 (
    echo ❌ Production backend build failed!
    exit /b 1
)

docker build -f ./frontend/Dockerfile.prod -t genai-stack/frontend:prod ^
    --build-arg VITE_API_URL=http://localhost:8000 ^
    --build-arg VITE_WS_URL=ws://localhost:8000 ^
    ./frontend
if %ERRORLEVEL% neq 0 (
    echo ❌ Production frontend build failed!
    exit /b 1
)

echo ✅ All images built successfully!

REM List built images
echo 📋 Built images:
docker images | findstr genai-stack
