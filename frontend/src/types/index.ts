import { Node, Edge, Connection } from 'reactflow'

export interface WorkflowComponent {
  id: string
  type: 'user_query' | 'knowledge_base' | 'llm_engine' | 'output' | 'web_search'
  label: string
  icon: string
  description: string
  config: ComponentConfig
}

export interface ComponentConfig {
  [key: string]: any
}

export interface UserQueryConfig {
  placeholder?: string
}

export interface KnowledgeBaseConfig {
  embeddingProvider?: 'openai' | 'gemini'
  apiKey?: string
  topK?: number
  files?: File[]
}

export interface LLMEngineConfig {
  model?: string
  provider?: 'openai' | 'gemini'
  apiKey?: string
  temperature?: number
  maxTokens?: number
  prompt?: string
  systemPrompt?: string
  webSearch?: boolean
}

export interface OutputConfig {
  format?: 'text' | 'json' | 'markdown'
}

export interface WorkflowNode extends Node {
  data: {
    label: string
    icon: string
    config: ComponentConfig
    type: WorkflowComponent['type']
  }
}

export interface Workflow {
  id: string
  name: string
  description?: string
  configuration: {
    nodes: WorkflowNode[]
    edges: Edge[]
  }
  created_at: string
  updated_at: string
}

export interface ChatSession {
  id: string
  workflow_id: string
  created_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: any
  created_at: string
}

export interface Document {
  id: string
  workflow_id?: string
  filename: string
  content?: string
  metadata?: any
  created_at: string
}

export interface WorkflowValidation {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface WorkflowExecutionResult {
  output: any[]
  context: any
  execution_summary: {
    total_nodes: number
    executed_nodes: number
    errors: number
  }
}
