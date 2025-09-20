import { useState, useCallback, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Node } from 'reactflow'
import { Save, MessageSquare, AlertCircle } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'

import WorkflowCanvas from '@/components/WorkflowCanvas'
import ComponentLibrary from '@/components/ComponentLibrary'
import ConfigPanel from '@/components/ConfigPanel'
import ChatModal from '@/components/ChatModal'
import useWorkflowStore from '@/store/workflowStore'
import { workflowAPI, chatAPI } from '@/services/api'
import { WorkflowComponent } from '@/types'

export default function WorkflowBuilder() {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [chatSessionId, setChatSessionId] = useState<string | null>(null)
  
  const {
    nodes,
    edges,
    workflowName,
    workflowDescription,
    setWorkflow,
    setNodes,
    setEdges,
    isDirty,
    setDirty,
  } = useWorkflowStore()

  // Load workflow if ID is provided
  const { data: workflow } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => workflowAPI.get(workflowId!),
    enabled: !!workflowId,
  })

  useEffect(() => {
    if (workflow) {
      setWorkflow(workflow.id, workflow.name, workflow.description || '')
      setNodes(workflow.configuration.nodes)
      setEdges(workflow.configuration.edges)
      setDirty(false)
    }
  }, [workflow, setWorkflow, setNodes, setEdges, setDirty])

  // Save workflow mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        configuration: { nodes, edges },
      }

      if (workflowId) {
        return workflowAPI.update(workflowId, workflowData)
      } else {
        return workflowAPI.create(workflowData)
      }
    },
    onSuccess: (data) => {
      toast.success('Workflow saved successfully!')
      setDirty(false)
      if (!workflowId) {
        navigate(`/builder/${data.id}`)
      }
    },
    onError: () => {
      toast.error('Failed to save workflow')
    },
  })


  // Create chat session mutation
  const createChatMutation = useMutation({
    mutationFn: async () => {
      // First save the workflow if it's dirty or new
      let currentWorkflowId = workflowId
      if (!currentWorkflowId || isDirty) {
        const savedWorkflow = await saveMutation.mutateAsync()
        currentWorkflowId = savedWorkflow.id
      }
      
      // Validate workflow
      const validation = await workflowAPI.validate(currentWorkflowId)
      if (!validation.valid) {
        throw new Error(validation.errors.join(', '))
      }
      
      // Create chat session
      return chatAPI.createSession(currentWorkflowId)
    },
    onSuccess: (session) => {
      setChatSessionId(session.id)
      setIsChatOpen(true)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to start chat session')
    },
  })

  const handleDragStart = useCallback((event: React.DragEvent, component: WorkflowComponent) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(component))
    event.dataTransfer.effectAllowed = 'move'
  }, [])

  const handleNodeClick = useCallback((node: Node) => {
    setSelectedNode(node)
  }, [])

  const handleBuildStack = () => {
    if (nodes.length === 0) {
      toast.error('Please add at least one component to build the stack')
      return
    }
    saveMutation.mutate()
  }

  const handleChatWithStack = () => {
    if (nodes.length === 0) {
      toast.error('Please build a workflow first')
      return
    }
    createChatMutation.mutate()
  }

  return (
    <div className="h-[calc(100vh-64px)] flex bg-gray-50">
      {/* Component Library */}
      <ComponentLibrary onDragStart={handleDragStart} />

      {/* Canvas */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <input
                type="text"
                value={workflowName}
                onChange={(e) => useWorkflowStore.getState().setWorkflow(workflowId || null, e.target.value, workflowDescription)}
                className="bg-gray-50 border border-gray-200 px-4 py-2 rounded-lg text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Untitled Workflow"
              />
              {isDirty && (
                <span className="text-xs text-amber-600 flex items-center gap-1 bg-amber-50 px-2 py-1 rounded-full">
                  <AlertCircle className="w-3 h-3" />
                  Unsaved changes
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleBuildStack}
                disabled={saveMutation.isPending}
                className="btn-secondary flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
              <button
                onClick={handleChatWithStack}
                disabled={createChatMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-5 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md flex items-center gap-2"
              >
                <MessageSquare className="w-4 h-4" />
                Chat with Stack
              </button>
            </div>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-white">
          <WorkflowCanvas onNodeClick={handleNodeClick} />
        </div>
      </div>

      {/* Configuration Panel */}
      <ConfigPanel
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
      />

      {/* Chat Modal */}
      <ChatModal
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        sessionId={chatSessionId}
        workflowName={workflowName}
      />
    </div>
  )
}
