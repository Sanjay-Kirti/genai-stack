# GenAI Stack - Setup Guide

## Prerequisites

- **Docker & Docker Compose** (for containerized deployment)
- **Node.js 18+** and **npm** (for local frontend development)
- **Python 3.10+** (for local backend development)
- **PostgreSQL** (if running locally without Docker)
- **API Keys**:
  - OpenAI API Key (for GPT models)
  - Google Gemini API Key (for Gemini models)

## Quick Start with Docker

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd genai-stack

# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Configure Environment Variables

Edit the `.env` file and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=generate-a-secure-secret-key
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# Or use Make commands
make build
make start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ChromaDB**: http://localhost:8001

## Local Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
createdb genai_stack

# Run migrations (if using Alembic)
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### ChromaDB Setup (Local)

```bash
# Using Docker
docker run -p 8001:8000 chromadb/chroma

# Or install locally
pip install chromadb
chroma run --path ./chroma_data
```

## Usage Guide

### 1. Creating a Workflow

1. Navigate to the **Workflow Builder** page
2. Drag components from the left panel onto the canvas:
   - **User Query**: Entry point for user input
   - **Knowledge Base**: Upload and search documents
   - **LLM Engine**: Configure AI model settings
   - **Output**: Display results

3. Connect components by dragging from output handles to input handles
4. Click on components to configure them in the right panel
5. Click **"Build Stack"** to save your workflow

### 2. Configuring Components

#### Knowledge Base
- Upload PDF, TXT, or MD files
- Select embedding model (OpenAI or Gemini)
- Enter API key for embeddings

#### LLM Engine
- Choose model (GPT-3.5, GPT-4, Gemini Pro)
- Set temperature (0-1 for creativity)
- Add custom prompts
- Enable web search (optional)

### 3. Testing Your Workflow

1. After building your stack, click **"Chat with Stack"**
2. Enter your query in the chat modal
3. The system will process through your workflow and return results

### 4. Managing Workflows

- Go to **"My Stacks"** to view all saved workflows
- Click on a workflow to edit it
- Delete workflows you no longer need

## Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

#### ChromaDB Connection Error
```bash
# Restart ChromaDB
docker-compose restart chromadb

# Check if port 8001 is available
netstat -an | grep 8001
```

#### WebSocket Connection Issues
- Ensure your firewall allows WebSocket connections
- Check that the backend is running and accessible

#### API Key Errors
- Verify API keys are correctly set in `.env` files
- Ensure keys have proper permissions and credits

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access backend shell
docker-compose exec backend /bin/bash

# Access database
docker-compose exec postgres psql -U postgres -d genai_stack
```

## Development Tips

### Hot Reloading
- Backend: Uses `--reload` flag with uvicorn
- Frontend: Vite provides HMR (Hot Module Replacement)

### Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

### Code Quality
```bash
# Backend linting
cd backend && flake8 app/

# Frontend linting
cd frontend && npm run lint
```

## Production Deployment

### Environment Variables
- Use strong, unique SECRET_KEY
- Set DEBUG=False in production
- Use environment-specific API keys
- Configure proper CORS origins

### Security Considerations
- Use HTTPS in production
- Implement rate limiting
- Add authentication/authorization
- Sanitize user inputs
- Use secrets management service

### Scaling
- Use Redis for caching
- Implement horizontal scaling for backend
- Use CDN for static assets
- Consider managed database services

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs for error details
4. Create an issue on GitHub
