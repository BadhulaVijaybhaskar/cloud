import Layout from '../components/Layout'

export default function Home() {
  return (
    <Layout title="Developer Console">
      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50">
              <div className="text-sm font-medium">Create Project</div>
              <div className="text-xs text-gray-500">Start a new project</div>
            </button>
            <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50">
              <div className="text-sm font-medium">Generate API</div>
              <div className="text-xs text-gray-500">Create SDK from spec</div>
            </button>
            <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50">
              <div className="text-sm font-medium">View Logs</div>
              <div className="text-xs text-gray-500">Monitor activity</div>
            </button>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Projects</h2>
          <div className="text-sm text-gray-500">No projects yet. Create your first project to get started.</div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">System Status</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm">Core Service</span>
              <span className="text-sm text-green-600">●  Running</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">API Gateway</span>
              <span className="text-sm text-green-600">●  Running</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Worker Service</span>
              <span className="text-sm text-green-600">●  Running</span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}