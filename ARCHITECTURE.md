# 🏗️ GenAI Stack - Architecture Documentation

## 🌟 System Architecture Overview

GenAI Stack follows a modern, microservices-inspired architecture with clear separation of concerns and scalable design patterns.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Workflow │  │Component │  │   Chat   │  │    My    │   │
│  │  Canvas  │  │ Library  │  │  Modal   │  │  Stacks  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────┬───────────────────────────┬───────────────┘
                  │ HTTP/REST API              │ WebSocket
┌─────────────────▼───────────────────────────▼───────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Workflow │  │ Document │  │   Chat   │  │WebSocket │   │
│  │Endpoints │  │Endpoints │  │Endpoints │  │ Handler  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Service Layer                       │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │   │
│  │  │   LLM   │ │Embedding│ │Document │ │ Workflow │  │   │
│  │  │ Service │ │ Service │ │ Service │ │  Engine  │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬──────────────┬──────────────┬────────────────────┘
           │              │              │
    ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼─────┐
    │ PostgreSQL │ │  ChromaDB  │ │ External │
    │  Database  │ │Vector Store│ │   APIs   │
    └────────────┘ └────────────┘ └──────────┘
```

## Component Details

### Frontend Architecture

#### Technology Stack
- **React 18** with TypeScript
- **React Flow** for workflow visualization
- **Zustand** for state management
- **React Query** for server state
- **Tailwind CSS** for styling
- **Vite** for build tooling

#### Key Components

1. **WorkflowCanvas**
   - Drag-and-drop interface using React Flow
   - Custom node components
   - Connection validation
   - Real-time updates

2. **ComponentLibrary**
   - Draggable workflow components
   - Component metadata
   - Visual indicators

3. **ConfigPanel**
   - Dynamic form generation
   - Component-specific configurations
   - File upload handling
   - API key management

4. **ChatModal**
   - WebSocket connection
   - Real-time messaging
   - Message history
   - Thinking indicators

### Backend Architecture

#### Technology Stack
- **FastAPI** for REST API
- **SQLAlchemy** for ORM
- **PostgreSQL** for data persistence
- **ChromaDB** for vector storage
- **WebSockets** for real-time communication

#### Service Layer

1. **LLM Service**
   ```python
   - OpenAI GPT integration
   - Google Gemini integration
   - Streaming support
   - Error handling and retries
   ```

2. **Embedding Service**
   ```python
   - Text embedding generation
   - Multiple provider support
   - Batch processing
   - Similarity calculations
   ```

3. **Vector Store Service**
   ```python
   - ChromaDB integration
   - Document indexing
   - Similarity search
   - Metadata filtering
   ```

4. **Document Service**
   ```python
   - PDF text extraction
   - Text chunking
   - Metadata extraction
   - File validation
   ```

5. **Workflow Engine**
   ```python
   - Workflow validation
   - Node execution orchestration
   - Data flow management
   - Error handling
   ```

### Database Schema

#### Workflows Table
```sql
- id: UUID (Primary Key)
- name: VARCHAR(255)
- description: TEXT
- configuration: JSONB
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### Documents Table
```sql
- id: UUID (Primary Key)
- workflow_id: UUID (Foreign Key)
- filename: VARCHAR(255)
- content: TEXT
- metadata: JSONB
- created_at: TIMESTAMP
```

#### Chat Sessions Table
```sql
- id: UUID (Primary Key)
- workflow_id: UUID (Foreign Key)
- created_at: TIMESTAMP
```

#### Chat Messages Table
```sql
- id: UUID (Primary Key)
- session_id: UUID (Foreign Key)
- role: VARCHAR(50)
- content: TEXT
- metadata: JSONB
- created_at: TIMESTAMP
```

## Data Flow

### Workflow Execution Flow

1. **User Input** → User Query Node
2. **Document Search** → Knowledge Base Node
3. **Context Preparation** → Combine user input with retrieved documents
4. **LLM Processing** → Send to configured LLM with context
5. **Response Generation** → Format and return response
6. **Output Display** → Show in chat interface

### WebSocket Communication

```
Client                    Server
  │                         │
  ├──── Connect ──────────► │
  │                         │
  ├──── Send Message ─────► │
  │                         ├──── Process Workflow
  │ ◄─── User Message ──────┤
  │ ◄─── Thinking Status ───┤
  │                         ├──── Execute LLM
  │ ◄─── AI Response ───────┤
  │                         │
```

## Security Considerations

### API Security
- JWT authentication (optional)
- Rate limiting
- Input validation
- CORS configuration
- API key encryption

### Data Security
- Encrypted API keys storage
- Secure WebSocket connections
- SQL injection prevention
- XSS protection
- CSRF protection

## Performance Optimizations

### Frontend
- Code splitting
- Lazy loading
- Memoization
- Virtual scrolling
- Optimistic updates

### Backend
- Connection pooling
- Async operations
- Caching strategies
- Batch processing
- Query optimization

### Vector Store
- Indexed searches
- Embedding caching
- Batch operations
- Metadata filtering

## Deployment Architecture

### Docker Deployment
```yaml
Services:
  - PostgreSQL (Database)
  - ChromaDB (Vector Store)
  - Backend (FastAPI)
  - Frontend (Nginx)
  - Redis (Optional - Caching)
```

### Kubernetes Deployment
```yaml
Deployments:
  - backend-deployment
  - frontend-deployment
  - postgres-statefulset
  - chromadb-statefulset
  
Services:
  - backend-service
  - frontend-service
  - postgres-service
  - chromadb-service
  
Ingress:
  - api.domain.com → backend
  - app.domain.com → frontend
```

## Monitoring and Logging

### Metrics to Track
- API response times
- WebSocket connection count
- LLM API usage
- Vector store query performance
- Error rates

### Logging Strategy
- Structured logging
- Log aggregation
- Error tracking
- Performance monitoring
- Audit trails

## Scalability Considerations

### Horizontal Scaling
- Stateless backend services
- Load balancing
- Database replication
- Distributed caching

### Vertical Scaling
- Resource optimization
- Query optimization
- Caching strategies
- Connection pooling

## Future Enhancements

1. **Authentication & Authorization**
   - User management
   - Role-based access
   - OAuth integration

2. **Advanced Features**
   - Workflow versioning
   - Collaborative editing
   - Custom components
   - Workflow templates

3. **Integrations**
   - More LLM providers
   - External data sources
   - Webhook support
   - API marketplace

4. **Analytics**
   - Usage analytics
   - Performance metrics
   - Cost tracking
   - User insights
