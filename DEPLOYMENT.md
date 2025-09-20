# 🚀 GenAI Stack - Railway Deployment Guide

## 📋 **Complete Railway Deployment (Frontend + Backend)**

### **Step 1: Push to GitHub**

1. **Initialize Git Repository**
   ```bash
   cd genai-stack
   git init
   git add .
   git commit -m "GenAI Stack - Ready for Railway deployment"
   ```

2. **Create GitHub Repository**
   - Go to https://github.com/new
   - Name: `genai-stack`
   - Make it **Public**
   - Don't initialize with README

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/genai-stack.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Deploy Backend on Railway**

1. **Go to Railway**
   - Visit https://railway.app
   - Click "Login" → Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `genai-stack` repository

3. **Configure Backend Service**
   - Railway will detect the Python backend
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** (in Railway dashboard):
   ```
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   SECRET_KEY=your_secret_key_here
   CHROMA_HOST=localhost
   CHROMA_PORT=8001
   CHROMA_COLLECTION_NAME=genai_stack_docs
   BACKEND_CORS_ORIGINS=["https://your-frontend-url.railway.app"]
   ```

### **Step 3: Add PostgreSQL Database**

1. **In Railway Dashboard**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will create a PostgreSQL instance

2. **Get Database URL**
   - Go to PostgreSQL service → "Connect"
   - Copy the `DATABASE_URL`

3. **Add to Backend Environment Variables**
   ```
   DATABASE_URL=postgresql://postgres:password@host:port/railway
   ```

### **Step 4: Deploy Frontend on Railway**

1. **Add Frontend Service**
   - In same Railway project, click "New Service"
   - Select "GitHub Repo" → Choose same repository
   - **Root Directory**: `frontend`

2. **Configure Frontend Build**
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

3. **Add Frontend Environment Variables**
   ```
   VITE_API_URL=https://your-backend-service.railway.app
   VITE_WS_URL=wss://your-backend-service.railway.app
   ```

### **Step 5: Update CORS Settings**

After frontend is deployed, update backend CORS:
```
BACKEND_CORS_ORIGINS=["https://your-frontend-service.railway.app"]
```

## ✅ **Final Steps**

### **Step 6: Test Your Deployment**

1. **Access Your Application**
   - Frontend: `https://your-frontend-service.railway.app`
   - Backend API: `https://your-backend-service.railway.app/docs`

2. **Test Core Features**
   - Create a workflow
   - Upload a document
   - Test chat functionality

### **Step 7: Custom Domain (Optional)**

1. **In Railway Dashboard**
   - Go to Frontend service → "Settings" → "Domains"
   - Add your custom domain
   - Update DNS records as instructed

## 📋 **Pre-Deployment Checklist**

- ✅ All environment variables configured
- ✅ Database connection string ready
- ✅ API keys available
- ✅ Frontend build working locally
- ✅ Backend running locally
- ✅ CORS configured for production URLs

## 🚨 **Important Notes**

1. **Database**: You'll need a cloud PostgreSQL instance
2. **ChromaDB**: Will run in-memory mode (perfect for demo)
3. **File Uploads**: Configure cloud storage for production
4. **WebSocket**: Ensure your hosting supports WebSocket connections
5. **CORS**: Update CORS origins in backend for production URLs

## 🎯 **Quick Deploy Commands**

```bash
# 1. Prepare for deployment
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Deploy frontend (Vercel CLI - optional)
npm i -g vercel
cd frontend
vercel --prod

# 3. Deploy backend (Railway CLI - optional)
npm i -g @railway/cli
cd backend
railway login
railway deploy
```

## 🔗 **Final URLs**

After deployment, you'll have:
- **Frontend**: https://genai-stack.vercel.app
- **Backend**: https://genai-stack-backend.railway.app
- **API Docs**: https://genai-stack-backend.railway.app/docs

Your GenAI Stack will be live and accessible worldwide! 🌍
