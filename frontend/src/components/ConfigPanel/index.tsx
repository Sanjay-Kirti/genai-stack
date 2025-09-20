import { useState, useEffect } from 'react'
import { Node } from 'reactflow'
import { X, Upload, Trash2 } from 'lucide-react'
import useWorkflowStore from '@/store/workflowStore'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'

interface ConfigPanelProps {
  node: Node | null
  onClose: () => void
}

export default function ConfigPanel({ node, onClose }: ConfigPanelProps) {
  const { updateNodeConfig } = useWorkflowStore()
  const [config, setConfig] = useState<any>({})
  const [files, setFiles] = useState<File[]>([])

  useEffect(() => {
    if (node?.data?.config) {
      setConfig(node.data.config)
      setFiles(node.data.config.files || [])
    }
  }, [node])

  const handleConfigChange = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value }
    setConfig(newConfig)
    if (node) {
      updateNodeConfig(node.id, newConfig)
    }
  }

  const onDrop = (acceptedFiles: File[]) => {
    const newFiles = [...files, ...acceptedFiles]
    setFiles(newFiles)
    handleConfigChange('files', newFiles)
  }

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    setFiles(newFiles)
    handleConfigChange('files', newFiles)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
  })

  if (!node) return null

  const nodeType = node.data.type

  return (
    <div className="w-80 bg-white border-l border-gray-200 h-full overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Configuration</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="p-4 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Component Type
          </label>
          <div className="bg-gray-50 border border-gray-200 px-3 py-2 rounded-lg text-gray-900 font-medium">
            {node.data.label}
          </div>
        </div>

        {/* Knowledge Base Configuration */}
        {nodeType === 'knowledge_base' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                File for Knowledge Base
              </label>
              <div
                {...getRootProps()}
                className={cn(
                  'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
                  isDragActive
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 hover:border-green-400 bg-gray-50'
                )}
              >
                <input {...getInputProps()} />
                <Upload className="w-8 h-8 mx-auto mb-3 text-gray-400" />
                <p className="text-sm text-gray-600">
                  {isDragActive
                    ? 'Drop the files here...'
                    : 'Drag & drop files here, or click to select'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supports PDF, TXT, MD files
                </p>
              </div>
              {files.length > 0 && (
                <div className="mt-3 space-y-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-white border border-gray-200 px-3 py-2 rounded-lg"
                    >
                      <span className="text-sm text-gray-700 truncate">
                        {file.name}
                      </span>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Embedding Model
              </label>
              <select
                value={config.embeddingProvider || 'openai'}
                onChange={(e) => handleConfigChange('embeddingProvider', e.target.value)}
                className="w-full select"
              >
                <option value="openai">text-embedding-3-large</option>
                <option value="gemini">Gemini Embeddings</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                API Key
              </label>
              <input
                type="password"
                value={config.apiKey || ''}
                onChange={(e) => handleConfigChange('apiKey', e.target.value)}
                placeholder="Enter API key"
                className="w-full input"
              />
            </div>
          </>
        )}

        {/* LLM Engine Configuration */}
        {nodeType === 'llm_engine' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Model
              </label>
              <select
                value={config.model || 'gpt-3.5-turbo'}
                onChange={(e) => handleConfigChange('model', e.target.value)}
                className="w-full input"
              >
                <optgroup label="OpenAI">
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </optgroup>
                <optgroup label="Google">
                  <option value="gemini-pro">Gemini Pro</option>
                  <option value="gemini-pro-vision">Gemini Pro Vision</option>
                </optgroup>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                API Key
              </label>
              <input
                type="password"
                value={config.apiKey || ''}
                onChange={(e) => handleConfigChange('apiKey', e.target.value)}
                placeholder="Enter API key"
                className="w-full input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Prompt
              </label>
              <textarea
                value={config.prompt || ''}
                onChange={(e) => handleConfigChange('prompt', e.target.value)}
                placeholder="You are a helpful PDF assistant. Use web search if the PDF lacks context.\n\nCONTEXT: {context}\nUSER QUERY: {query}"
                rows={4}
                className="w-full input resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Temperature: {config.temperature || 0.7}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.temperature || 0.7}
                onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-300">
                WebSearch Tool
              </label>
              <button
                onClick={() => handleConfigChange('webSearch', !config.webSearch)}
                className={cn(
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  config.webSearch ? 'bg-primary-500' : 'bg-dark-600'
                )}
              >
                <span
                  className={cn(
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    config.webSearch ? 'translate-x-6' : 'translate-x-1'
                  )}
                />
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                SERP API Key
              </label>
              <input
                type="password"
                value={config.serpApiKey || ''}
                onChange={(e) => handleConfigChange('serpApiKey', e.target.value)}
                placeholder="Enter SERP API key"
                className="w-full input"
                disabled={!config.webSearch}
              />
            </div>
          </>
        )}

        {/* User Query Configuration */}
        {nodeType === 'user_query' && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Query
            </label>
            <input
              type="text"
              value={config.placeholder || ''}
              onChange={(e) => handleConfigChange('placeholder', e.target.value)}
              placeholder="Write your query here..."
              className="w-full input"
            />
          </div>
        )}

        {/* Output Configuration */}
        {nodeType === 'output' && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Output Text
            </label>
            <textarea
              value={config.outputText || ''}
              onChange={(e) => handleConfigChange('outputText', e.target.value)}
              placeholder="Output will be generated based on query"
              rows={4}
              className="w-full input resize-none"
              readOnly
            />
          </div>
        )}
      </div>
    </div>
  )
}
