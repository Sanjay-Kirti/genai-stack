import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { User, Database, Brain, FileOutput, Globe, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import useWorkflowStore from '@/store/workflowStore'

const iconMap: { [key: string]: any } = {
  user_query: User,
  knowledge_base: Database,
  llm_engine: Brain,
  output: FileOutput,
  web_search: Globe,
}

function CustomNode({ data, selected, id }: NodeProps) {
  const Icon = iconMap[data.type] || Brain
  const { deleteNode } = useWorkflowStore()

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    deleteNode(id)
  }

  return (
    <div
      className={cn(
        'bg-dark-800 border-2 rounded-lg p-3 min-w-[180px] transition-all',
        selected ? 'border-primary-500 shadow-lg shadow-primary-500/20' : 'border-dark-600'
      )}
    >
      {data.type !== 'user_query' && (
        <Handle
          type="target"
          position={Position.Left}
          className="!bg-primary-500 !w-3 !h-3 !border-2 !border-dark-800"
        />
      )}
      
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-dark-700 rounded flex items-center justify-center">
            <Icon className="w-4 h-4 text-primary-400" />
          </div>
          <span className="text-sm font-medium text-gray-100">{data.label}</span>
        </div>
        <button
          onClick={handleDelete}
          className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-400"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {data.config && Object.keys(data.config).length > 0 && (
        <div className="text-xs text-gray-400 space-y-1">
          {data.config.model && (
            <div>Model: {data.config.model}</div>
          )}
          {data.config.temperature !== undefined && (
            <div>Temp: {data.config.temperature}</div>
          )}
          {data.config.topK && (
            <div>Top K: {data.config.topK}</div>
          )}
        </div>
      )}

      {data.type !== 'output' && (
        <Handle
          type="source"
          position={Position.Right}
          className="!bg-primary-500 !w-3 !h-3 !border-2 !border-dark-800"
        />
      )}
    </div>
  )
}

export default memo(CustomNode)
