import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ReactFlowProvider } from 'reactflow'
import Layout from '@/components/Layout'
import WorkflowBuilder from '@/pages/WorkflowBuilder'
import MyStacks from '@/pages/MyStacks'
import 'reactflow/dist/style.css'

function App() {
  return (
    <ReactFlowProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/builder" replace />} />
            <Route path="/builder" element={<WorkflowBuilder />} />
            <Route path="/builder/:workflowId" element={<WorkflowBuilder />} />
            <Route path="/stacks" element={<MyStacks />} />
          </Routes>
        </Layout>
      </Router>
    </ReactFlowProvider>
  )
}

export default App
