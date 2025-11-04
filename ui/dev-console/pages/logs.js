import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState('all')

  useEffect(() => {
    loadLogs()
  }, [selectedProject, searchQuery])

  const loadLogs = async () => {
    setLoading(true)
    
    // Simulate logs data
    const mockLogs = [
      {
        id: 'log-1',
        timestamp: '2024-12-28T10:30:00Z',
        level: 'INFO',
        service: 'auth-service',
        project_id: 'p-1',
        message: 'User authentication successful',
        details: { user_id: 'user-123', ip: '192.168.1.100' }
      },
      {
        id: 'log-2',
        timestamp: '2024-12-28T10:25:00Z',
        level: 'ERROR',
        service: 'api-gateway',
        project_id: 'p-1',
        message: 'Rate limit exceeded for API key',
        details: { api_key: 'ak_****abc123', endpoint: '/v1/models' }
      },
      {
        id: 'log-3',
        timestamp: '2024-12-28T10:20:00Z',
        level: 'WARN',
        service: 'marketplace-core',
        project_id: 'p-2',
        message: 'Model deployment taking longer than expected',
        details: { model_id: 'model-123', duration: '45s' }
      }
    ]

    // Filter by project and search
    let filteredLogs = mockLogs
    if (selectedProject !== 'all') {
      filteredLogs = filteredLogs.filter(log => log.project_id === selectedProject)
    }
    if (searchQuery) {
      filteredLogs = filteredLogs.filter(log => 
        log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
        log.service.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setLogs(filteredLogs)
    setLoading(false)
  }

  const getLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'text-red-600 bg-red-500/20'
      case 'WARN': return 'text-yellow-600 bg-yellow-500/20'
      case 'INFO': return 'text-blue-600 bg-blue-500/20'
      default: return 'text-gray-600 bg-gray-500/20'
    }
  }

  const openFullLogs = () => {
    // Link to full logging console
    window.open('http://localhost:3001/logs', '_blank')
  }

  return (
    <Layout title="Logs">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold neural-text">Logs Viewer</h1>
            <p className="text-muted-foreground mt-2">Aggregated logs and quick search</p>
          </div>
          <button 
            onClick={openFullLogs}
            className="atom-gradient text-white px-6 py-3 rounded-lg font-medium hover:opacity-90"
          >
            🔍 Open Full Logs Console
          </button>
        </div>

        {/* Search and Filters */}
        <div className="quantum-card p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search Logs</label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search messages, services..."
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Project Filter</label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Projects</option>
                <option value="p-1">Alpha Project</option>
                <option value="p-2">Beta Project</option>
              </select>
            </div>
          </div>
        </div>

        {/* Logs List */}
        <div className="quantum-card">
          <div className="p-6 border-b border-border/50">
            <h2 className="text-xl font-bold flex items-center gap-3">
              📋 Recent Logs
              {loading && <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full"></div>}
            </h2>
          </div>

          <div className="divide-y divide-border/50">
            {logs.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                {loading ? 'Loading logs...' : 'No logs found matching your criteria'}
              </div>
            ) : (
              logs.map(log => (
                <LogEntry key={log.id} log={log} getLevelColor={getLevelColor} />
              ))
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <button 
            onClick={openFullLogs}
            className="quantum-card p-6 hover:scale-105 transition-transform text-left"
          >
            <div className="text-lg font-semibold neural-text mb-2">🔍 Advanced Search</div>
            <div className="text-sm text-muted-foreground">Use full logging console for complex queries</div>
          </button>
          
          <button className="quantum-card p-6 hover:scale-105 transition-transform text-left">
            <div className="text-lg font-semibold neural-text mb-2">📊 Log Analytics</div>
            <div className="text-sm text-muted-foreground">View patterns and trends</div>
          </button>
          
          <button className="quantum-card p-6 hover:scale-105 transition-transform text-left">
            <div className="text-lg font-semibold neural-text mb-2">🚨 Set Alerts</div>
            <div className="text-sm text-muted-foreground">Create log-based alerts</div>
          </button>
        </div>
      </div>
    </Layout>
  )
}

function LogEntry({ log, getLevelColor }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="p-4 hover:bg-accent/50">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className={`px-2 py-1 text-xs rounded-full ${getLevelColor(log.level)}`}>
              {log.level}
            </span>
            <span className="text-sm text-muted-foreground">
              {new Date(log.timestamp).toLocaleString()}
            </span>
            <span className="text-sm font-medium text-primary">{log.service}</span>
          </div>
          
          <div className="font-medium mb-2">{log.message}</div>
          
          {expanded && (
            <div className="mt-3 p-3 bg-secondary/20 rounded-lg">
              <div className="text-sm font-medium mb-2">Details:</div>
              <pre className="text-xs text-muted-foreground overflow-x-auto">
                {JSON.stringify(log.details, null, 2)}
              </pre>
            </div>
          )}
        </div>
        
        <button 
          onClick={() => setExpanded(!expanded)}
          className="text-muted-foreground hover:text-foreground ml-4"
        >
          {expanded ? '▼' : '▶'}
        </button>
      </div>
    </div>
  )
}