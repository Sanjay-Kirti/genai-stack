import { useNavigate } from 'react-router-dom'
import { Plus, Edit2 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { workflowAPI } from '@/services/api'

export default function MyStacks() {
  const navigate = useNavigate()

  // Fetch workflows
  const { data: workflows = [], isLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: workflowAPI.list,
  })


  const handleCreateNew = () => {
    navigate('/builder')
  }

  const handleEdit = (workflowId: string) => {
    navigate(`/builder/${workflowId}`)
  }


  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="text-gray-500">Loading workflows...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">My Stacks</h1>
        </div>
        <button
          onClick={handleCreateNew}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Stack
        </button>
      </div>

      {/* Workflows Grid */}
      {workflows.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="text-center max-w-md">
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Create New Stack
            </h3>
            <p className="text-gray-500 mb-6">
              Start building your generative AI apps with our essential tools and frameworks
            </p>
            <button
              onClick={handleCreateNew}
              className="btn-primary mx-auto flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Stack
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleEdit(workflow.id)}
            >
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {workflow.name}
                </h3>
                {workflow.description && (
                  <p className="text-sm text-gray-500 line-clamp-2">
                    {workflow.description}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit(workflow.id);
                  }}
                  className="text-sm text-gray-600 hover:text-gray-900 font-medium flex items-center gap-1"
                >
                  <Edit2 className="w-3 h-3" />
                  Edit Stack
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
