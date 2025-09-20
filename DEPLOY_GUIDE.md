# 🚀 GenAI Stack - Complete Deployment Guide

## 🔑 **Step 1: Get API Keys (Do This First!)**

### **OpenAI API Key**
1. Go to https://platform.openai.com
2. Sign up or log in
3. Click your profile → "View API keys"
4. Click "Create new secret key"
5. Copy and save the key (starts with `sk-`)
6. **Cost**: Pay-per-use (starts around $0.002/1K tokens)

### **Google Gemini API Key**
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Select existing project or create new one
5. Copy and save the key
6. **Cost**: Free tier available (60 requests/minute)

### **Secret Key for Backend**
Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📦 **Step 2: Prepare for Deployment**

### **Terminal Commands (You'll run these):**
```bash
# 1. Remove unnecessary files
cd genai-stack
rm railway.json
rm -rf api/

# 2. Initialize Git
git init
git add .
git commit -m "GenAI Stack - Ready for Render deployment"

# 3. Create GitHub repository (go to github.com/new)
# Name: genai-stack
# Make it Public

# 4. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/genai-stack.git
git branch -M main
git push -u origin main
```

---

## 🌐 **Step 3: Deploy on Render.com**

### **3.1: Sign Up**
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub
4. Verify your email

### **3.2: Deploy Backend**
1. In Render dashboard, click "New +" → "Web Service"
2. Click "Connect account" → Authorize GitHub
3. Select your `genai-stack` repository
4. Configure Backend:
   ```
   Name: genai-backend
   Environment: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### **3.3: Add Backend Environment Variables**
In the backend service, go to "Environment" and add:
```
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
SECRET_KEY=your_generated_secret_key
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION_NAME=genai_stack_docs
BACKEND_CORS_ORIGINS=["*"]
```

### **3.4: Deploy PostgreSQL Database**
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   ```
   Name: genai-database
   Database: genaidb
   User: genaiuser
   Region: Same as your backend
   ```
3. After creation, go to "Connect" tab
4. Copy the "External Database URL"
5. Add to backend environment variables:
   ```
   DATABASE_URL=your_copied_database_url
   ```

### **3.5: Deploy Frontend**
1. In Render dashboard, click "New +" → "Static Site"
2. Select your `genai-stack` repository
3. Configure Frontend:
   ```
   Name: genai-frontend
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

### **3.6: Add Frontend Environment Variables**
After backend is deployed, get its URL and add to frontend:
```
VITE_API_URL=https://genai-backend-xxx.onrender.com
VITE_WS_URL=wss://genai-backend-xxx.onrender.com
```

### **3.7: Update CORS Settings**
After frontend is deployed, update backend environment:
```
BACKEND_CORS_ORIGINS=["https://genai-frontend-xxx.onrender.com"]
```

---

## ✅ **Step 4: Test Your Deployment**

### **Your Live URLs:**
- **Frontend**: https://genai-frontend-xxx.onrender.com
- **Backend API**: https://genai-backend-xxx.onrender.com/docs
- **Health Check**: https://genai-backend-xxx.onrender.com/health

### **Test Checklist:**
- [ ] Frontend loads without errors
- [ ] Can create a new workflow
- [ ] Can upload documents to Knowledge Base
- [ ] Chat functionality works
- [ ] LLM switching works (OpenAI ↔ Gemini)

---

## 🚨 **Important Notes**

### **Free Tier Limitations:**
- Services sleep after 15 minutes of inactivity
- 750 hours/month of usage
- Slower cold starts
- Limited to 1 concurrent build

### **Costs:**
- **Render**: Free tier available
- **OpenAI API**: ~$0.002/1K tokens
- **Gemini API**: Free tier (60 req/min)

### **Production Considerations:**
- Upgrade to paid plans for 24/7 uptime
- Add custom domain
- Set up monitoring
- Configure proper logging

---

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Build Fails**
   - Check build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt/package.json

2. **Database Connection Error**
   - Verify DATABASE_URL is correct
   - Check if database service is running

3. **CORS Errors**
   - Update BACKEND_CORS_ORIGINS with correct frontend URL
   - Redeploy backend after changes

4. **API Key Errors**
   - Verify API keys are correctly set
   - Check if keys have sufficient credits/quota

### **Getting Help:**
- Check Render logs: Service → "Logs" tab
- Monitor resource usage: Service → "Metrics" tab
- Render documentation: https://render.com/docs

---

## 🎉 **Congratulations!**

Your GenAI Stack is now live and accessible worldwide! 🌍

**Next Steps:**
- Share your live demo URL
- Add custom domain (optional)
- Monitor usage and costs
- Consider upgrading for production use

**Demo URLs to share:**
- **App**: https://genai-frontend-xxx.onrender.com
- **API**: https://genai-backend-xxx.onrender.com/docs
