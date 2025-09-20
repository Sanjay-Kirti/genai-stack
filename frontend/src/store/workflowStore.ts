import { create } from 'zustand'
import { Node, Edge, Connection, addEdge, applyNodeChanges, applyEdgeChanges } from 'reactflow'
import { ComponentConfig } from '@/types'

interface WorkflowState {
  nodes: Node[]
  edges: Edge[]
  selectedNode: Node | null
  workflowId: string | null
  workflowName: string
  workflowDescription: string
  isDirty: boolean
  
  // Actions
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
  onNodesChange: (changes: any) => void
  onEdgesChange: (changes: any) => void
  onConnect: (connection: Connection) => void
  addNode: (node: Node) => void
  updateNodeConfig: (nodeId: string, config: ComponentConfig) => void
  deleteNode: (nodeId: string) => void
  selectNode: (node: Node | null) => void
  setWorkflow: (id: string | null, name: string, description: string) => void
  resetWorkflow: () => void
  setDirty: (isDirty: boolean) => void
}

const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  workflowId: null,
  workflowName: 'Untitled Workflow',
  workflowDescription: '',
  isDirty: false,

  setNodes: (nodes) => {
    set({ nodes, isDirty: true })
  },

  setEdges: (edges) => {
    set({ edges, isDirty: true })
  },

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
      isDirty: true,
    })
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
      isDirty: true,
    })
  },

  onConnect: (connection) => {
    set({
      edges: addEdge(connection, get().edges),
      isDirty: true,
    })
  },

  addNode: (node) => {
    set({
      nodes: [...get().nodes, node],
      isDirty: true,
    })
  },

  updateNodeConfig: (nodeId, config) => {
    const nodes = get().nodes.map((node) => {
      if (node.id === nodeId) {
        return {
          ...node,
          data: {
            ...node.data,
            config,
          },
        }
      }
      return node
    })
    set({ nodes, isDirty: true })
  },

  deleteNode: (nodeId) => {
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      ),
      selectedNode: get().selectedNode?.id === nodeId ? null : get().selectedNode,
      isDirty: true,
    })
  },

  selectNode: (node) => {
    set({ selectedNode: node })
  },

  setWorkflow: (id, name, description) => {
    set({
      workflowId: id,
      workflowName: name,
      workflowDescription: description,
      isDirty: false,
    })
  },

  resetWorkflow: () => {
    set({
      nodes: [],
      edges: [],
      selectedNode: null,
      workflowId: null,
      workflowName: 'Untitled Workflow',
      workflowDescription: '',
      isDirty: false,
    })
  },

  setDirty: (isDirty) => {
    set({ isDirty })
  },
}))

export default useWorkflowStore
