# 🐳 Docker Deployment Guide

This guide covers containerization and deployment of the GenAI Stack application.

## 📋 Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- At least 4GB RAM available for containers

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.docker .env

# Edit .env file with your API keys
# OPENAI_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
```

### 2. Development Deployment

```bash
# Start all services
docker compose up --build

# Or run in background
docker compose up --build -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### 3. Production Deployment

```bash
# Build production images
./build.sh  # Linux/Mac
# OR
build.bat   # Windows

# Start production stack
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

## 🏗️ Container Architecture

### Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **frontend** | 3000 | React.js application with Nginx |
| **backend** | 8000 | FastAPI Python backend |
| **postgres** | 5432 | PostgreSQL database |
| **chromadb** | 8001 | ChromaDB vector database |

### Network Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   (Nginx)       │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼─────────────────┐
                                 │                 │
                    ┌─────────────────┐  ┌─────────────────┐
                    │   PostgreSQL    │  │   ChromaDB      │
                    │   Port: 5432    │  │   Port: 8001    │
                    └─────────────────┘  └─────────────────┘
```

## 🔧 Docker Files

### Backend Dockerfile
- **Base**: `python:3.10-slim`
- **Features**: Multi-stage build, non-root user, health checks
- **Production**: 4 workers, optimized for performance

### Frontend Dockerfile
- **Build Stage**: `node:18-alpine` for building React app
- **Runtime Stage**: `nginx:alpine` for serving static files
- **Features**: Gzip compression, security headers, API proxy

## 📝 Build Commands

### Individual Service Builds

```bash
# Backend only
docker build -t genai-stack/backend ./backend

# Frontend only
docker build -t genai-stack/frontend ./frontend

# Production builds
docker build -f backend/Dockerfile.prod -t genai-stack/backend:prod ./backend
docker build -f frontend/Dockerfile.prod -t genai-stack/frontend:prod ./frontend
```

### Custom Build Arguments

```bash
# Frontend with custom API URL
docker build -f frontend/Dockerfile.prod \
  --build-arg VITE_API_URL=https://api.example.com \
  --build-arg VITE_WS_URL=wss://api.example.com \
  -t genai-stack/frontend:prod ./frontend
```

## 🔍 Monitoring & Debugging

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 frontend
```

### Container Status

```bash
# List running containers
docker compose ps

# Container resource usage
docker stats

# Execute commands in container
docker compose exec backend bash
docker compose exec frontend sh
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/health

# Database connection
docker compose exec postgres pg_isready -U postgres
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "3001:80"  # Frontend on port 3001
     - "8001:8000"  # Backend on port 8001
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit to 4GB+
   # Check Docker Desktop settings
   ```

3. **Build Failures**
   ```bash
   # Clean build cache
   docker system prune -a
   
   # Rebuild without cache
   docker compose build --no-cache
   ```

4. **Database Connection Issues**
   ```bash
   # Reset database
   docker compose down -v
   docker compose up --build
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_DB` | Database name | `genai_stack` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `FRONTEND_PORT` | Frontend port | `3000` |

## 🚀 Production Deployment

### Security Considerations

1. **Environment Variables**
   - Use strong passwords
   - Rotate API keys regularly
   - Use secrets management in production

2. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Use private networks

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 1G
       reservations:
         cpus: '0.5'
         memory: 512M
   ```

### Scaling

```bash
# Scale backend service
docker compose up --scale backend=3

# Use load balancer (nginx, traefik, etc.)
# Configure database connection pooling
```

## 📊 Performance Optimization

### Frontend
- Static asset caching
- Gzip compression
- CDN integration

### Backend
- Multiple workers
- Connection pooling
- Redis caching (optional)

### Database
- Connection limits
- Query optimization
- Regular backups

## 🔄 Updates & Maintenance

```bash
# Update images
docker compose pull
docker compose up -d

# Backup database
docker compose exec postgres pg_dump -U postgres genai_stack > backup.sql

# Restore database
docker compose exec -T postgres psql -U postgres genai_stack < backup.sql
```
