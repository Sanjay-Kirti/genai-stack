import { User, Database, Brain, FileOutput, Globe } from 'lucide-react'
import { WorkflowComponent } from '@/types'

const components: WorkflowComponent[] = [
  {
    id: 'user_query',
    type: 'user_query',
    label: 'User Query',
    icon: 'User',
    description: 'Entry point for user input',
    config: {},
  },
  {
    id: 'knowledge_base',
    type: 'knowledge_base',
    label: 'Knowledge Base',
    icon: 'Database',
    description: 'Let LLM search info in your file',
    config: {
      embeddingProvider: 'openai',
      topK: 5,
    },
  },
  {
    id: 'llm_engine',
    type: 'llm_engine',
    label: 'LLM (OpenAI)',
    icon: 'Brain',
    description: 'Run a query with OpenAI LLM',
    config: {
      model: 'gpt-3.5-turbo',
      provider: 'openai',
      temperature: 0.7,
      maxTokens: 1000,
    },
  },
  {
    id: 'web_search',
    type: 'web_search',
    label: 'Web Search',
    icon: 'Globe',
    description: 'Search the web for information',
    config: {},
  },
  {
    id: 'output',
    type: 'output',
    label: 'Output',
    icon: 'FileOutput',
    description: 'Output of the result nodes as text',
    config: {},
  },
]

const iconMap: { [key: string]: any } = {
  User,
  Database,
  Brain,
  FileOutput,
  Globe,
}

interface ComponentLibraryProps {
  onDragStart: (event: React.DragEvent, component: WorkflowComponent) => void
}

export default function ComponentLibrary({ onDragStart }: ComponentLibraryProps) {
  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-1">
          Components
        </h3>
      </div>
      <div className="p-4 space-y-3">
        {components.map((component) => {
          const Icon = iconMap[component.icon]
          return (
            <div
              key={component.id}
              draggable
              onDragStart={(e) => onDragStart(e, component)}
              className="bg-gray-50 border border-gray-200 rounded-lg p-3 cursor-move hover:bg-gray-100 hover:border-green-300 hover:shadow-sm transition-all group"
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-white border border-gray-200 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:border-green-300">
                  <Icon className="w-4 h-4 text-gray-600 group-hover:text-green-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">{component.label}</h4>
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">{component.description}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
