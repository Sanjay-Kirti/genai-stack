import axios from 'axios'
import { Workflow, ChatSession, ChatMessage, Document, WorkflowValidation, WorkflowExecutionResult } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_V1 = `${API_BASE_URL}/api/v1`

const api = axios.create({
  baseURL: API_V1,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Workflow APIs
export const workflowAPI = {
  list: async (): Promise<Workflow[]> => {
    const { data } = await api.get('/workflows')
    return data
  },

  get: async (id: string): Promise<Workflow> => {
    const { data } = await api.get(`/workflows/${id}`)
    return data
  },

  create: async (workflow: Partial<Workflow>): Promise<Workflow> => {
    const { data } = await api.post('/workflows', workflow)
    return data
  },

  update: async (id: string, workflow: Partial<Workflow>): Promise<Workflow> => {
    const { data } = await api.put(`/workflows/${id}`, workflow)
    return data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/workflows/${id}`)
  },

  validate: async (id: string): Promise<WorkflowValidation> => {
    const { data } = await api.post(`/workflows/${id}/validate`)
    return data
  },

  execute: async (id: string, userInput: string, sessionId?: string): Promise<WorkflowExecutionResult> => {
    const { data } = await api.post(`/workflows/${id}/execute`, {
      user_input: userInput,
      session_id: sessionId,
    })
    return data
  },
}

// Document APIs
export const documentAPI = {
  upload: async (file: File, workflowId?: string, embeddingProvider: string = 'openai') => {
    const formData = new FormData()
    formData.append('file', file)
    if (workflowId) {
      formData.append('workflow_id', workflowId)
    }
    formData.append('embedding_provider', embeddingProvider)

    const { data } = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },

  get: async (id: string): Promise<Document> => {
    const { data } = await api.get(`/documents/${id}`)
    return data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`)
  },

  search: async (query: string, workflowId?: string, nResults: number = 5) => {
    const { data } = await api.post('/documents/search', {
      query,
      workflow_id: workflowId,
      n_results: nResults,
    })
    return data
  },

  extractText: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await api.post('/documents/extract-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },
}

// Chat APIs
export const chatAPI = {
  createSession: async (workflowId: string): Promise<ChatSession> => {
    const { data } = await api.post('/chat/sessions', {
      workflow_id: workflowId,
    })
    return data
  },

  getSession: async (sessionId: string): Promise<ChatSession> => {
    const { data } = await api.get(`/chat/sessions/${sessionId}`)
    return data
  },

  getMessages: async (sessionId: string): Promise<ChatMessage[]> => {
    const { data } = await api.get(`/chat/sessions/${sessionId}/messages`)
    return data
  },

  sendMessage: async (sessionId: string, message: string): Promise<ChatMessage> => {
    const { data } = await api.post(`/chat/sessions/${sessionId}/messages`, {
      message,
      session_id: sessionId,
    })
    return data
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/sessions/${sessionId}`)
  },
}

// WebSocket connection for chat
export const createWebSocketConnection = (sessionId: string) => {
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  return new WebSocket(`${WS_URL}/ws/chat/${sessionId}`)
}

export default api
