# 🤖 GenAI Stack - No-Code/Low-Code Workflow Builder

A comprehensive, production-ready workflow builder for creating AI-powered applications without coding. Built with modern technologies and designed for scalability.

## 🌟 Overview

GenAI Stack enables users to visually create complex AI workflows by dragging and connecting components. Perfect for building chatbots, document analysis systems, and AI-powered applications without writing code.

## ✨ Key Features

### 🎨 **Visual Workflow Builder**
- **Drag & Drop Interface**: Intuitive React Flow-based canvas
- **Real-time Validation**: Instant feedback on workflow configuration
- **Component Library**: 4 core components + extensible architecture

### 🧠 **Multi-LLM Support**
- **OpenAI Integration**: GPT-3.5, GPT-4, GPT-4 Vision
- **Google Gemini**: Gemini Pro with multimodal capabilities
- **Flexible Configuration**: Easy switching between providers

### 📚 **Knowledge Base**
- **Document Processing**: PDF, TXT, MD, DOC, DOCX support
- **Vector Embeddings**: ChromaDB for semantic search
- **Smart Retrieval**: Context-aware document querying

### 💬 **Real-time Chat**
- **WebSocket Integration**: Live chat interface
- **Session Management**: Persistent chat history
- **Streaming Responses**: Real-time AI responses

### 🏗️ **Enterprise Ready**
- **Docker Containerization**: Production deployment ready
- **PostgreSQL Database**: Reliable data persistence
- **RESTful APIs**: Comprehensive backend services
- **Modern Architecture**: Scalable and maintainable

## Tech Stack

- **Frontend**: React.js with TypeScript, React Flow, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Vector Store**: ChromaDB
- **Containerization**: Docker & Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/genai-stack.git
cd genai-stack

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create `.env` files in both frontend and backend directories:

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@localhost/genai_stack
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
CHROMA_HOST=localhost
CHROMA_PORT=8001
SECRET_KEY=your_secret_key
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Project Structure

```
genai-stack/
├── frontend/           # React TypeScript application
├── backend/           # FastAPI Python backend
├── docker-compose.yml # Docker orchestration
└── k8s/              # Kubernetes manifests
```

## License

MIT
