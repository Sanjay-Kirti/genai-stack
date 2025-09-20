import { useCallback, useRef } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  useReactFlow,
} from 'reactflow'
import useWorkflowStore from '@/store/workflowStore'
import CustomNode from './CustomNode'
import { WorkflowComponent } from '@/types'
import { generateId } from '@/lib/utils'

const nodeTypes = {
  custom: CustomNode,
}

interface WorkflowCanvasProps {
  onNodeClick: (node: Node) => void
}

export default function WorkflowCanvas({ onNodeClick }: WorkflowCanvasProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const { project } = useReactFlow()
  
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    selectNode,
  } = useWorkflowStore()

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect()
      const componentData = event.dataTransfer.getData('application/reactflow')

      if (!componentData || !reactFlowBounds) {
        return
      }

      const component: WorkflowComponent = JSON.parse(componentData)
      const position = project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      })

      const newNode: Node = {
        id: generateId(),
        type: 'custom',
        position,
        data: {
          label: component.label,
          icon: component.icon,
          type: component.type,
          config: component.config,
        },
      }

      addNode(newNode)
    },
    [project, addNode]
  )

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      selectNode(node)
      onNodeClick(node)
    },
    [selectNode, onNodeClick]
  )

  return (
    <div className="flex-1 h-full" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        className="bg-dark-900"
      >
        <Background color="#334155" gap={16} />
        <Controls className="!bg-dark-800 !border-dark-700 !shadow-xl">
          <style>{`
            .react-flow__controls-button {
              background: #1e293b !important;
              border-color: #334155 !important;
              color: #e2e8f0 !important;
            }
            .react-flow__controls-button:hover {
              background: #334155 !important;
            }
            .react-flow__controls-button svg {
              fill: currentColor;
            }
          `}</style>
        </Controls>
        <MiniMap 
          className="!bg-dark-800 !border-dark-700"
          nodeColor="#4ade80"
          maskColor="rgba(15, 23, 42, 0.8)"
        />
      </ReactFlow>
    </div>
  )
}
