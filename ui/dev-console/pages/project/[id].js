import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '../../components/Layout'

export default function ProjectOverview() {
  const router = useRouter()
  const { id } = router.query
  const [project, setProject] = useState(null)
  const [usage, setUsage] = useState(null)

  useEffect(() => {
    if (id) {
      // Simulate project data
      setProject({
        id: id,
        name: `Project ${id}`,
        status: 'running',
        owner: 'org-1'
      })
      
      setUsage({
        cpu: 35,
        memory: 60,
        storage: 25,
        requests_today: 15420
      })
    }
  }, [id])

  const openLaunchPad = async () => {
    const launchUrl = `http://localhost:3000?projectId=${id}&scopedToken=sim_token_123`
    window.open(launchUrl, '_blank')
  }

  if (!project) {
    return <Layout title="Loading..."><div>Loading...</div></Layout>
  }

  return (
    <Layout title={project.name}>
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold neural-text">{project.name}</h1>
            <span className={`px-2 py-1 text-xs rounded-full ${
              project.status === 'running' 
                ? 'bg-emerald-500/20 text-emerald-600' 
                : 'bg-gray-500/20 text-gray-600'
            }`}>
              {project.status}
            </span>
          </div>
          
          <button 
            onClick={openLaunchPad}
            className="atom-gradient text-white px-6 py-3 rounded-lg font-medium"
          >
            🚀 Open LaunchPad
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="quantum-card p-6">
              <h2 className="text-xl font-bold mb-4">📊 Usage</h2>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-emerald-500">{usage.cpu}%</div>
                  <div className="text-sm text-muted-foreground">CPU</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-violet-500">{usage.memory}%</div>
                  <div className="text-sm text-muted-foreground">Memory</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-teal-500">{usage.storage}%</div>
                  <div className="text-sm text-muted-foreground">Storage</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-500">{usage.requests_today.toLocaleString()}</div>
                  <div className="text-sm text-muted-foreground">Requests</div>
                </div>
              </div>
            </div>

            <div className="quantum-card p-6">
              <h2 className="text-xl font-bold mb-4">⚡ Quick Links</h2>
              <div className="grid grid-cols-3 gap-4">
                <button 
                  onClick={openLaunchPad}
                  className="p-4 border border-border rounded-lg hover:bg-accent text-left"
                >
                  <div className="font-medium">🚀 LaunchPad</div>
                  <div className="text-xs text-muted-foreground">Full environment</div>
                </button>
                
                <button 
                  onClick={() => router.push('/marketplace')}
                  className="p-4 border border-border rounded-lg hover:bg-accent text-left"
                >
                  <div className="font-medium">🛒 Marketplace</div>
                  <div className="text-xs text-muted-foreground">AI models</div>
                </button>
                
                <button 
                  onClick={() => router.push('/api-keys')}
                  className="p-4 border border-border rounded-lg hover:bg-accent text-left"
                >
                  <div className="font-medium">🔑 API Keys</div>
                  <div className="text-xs text-muted-foreground">Access tokens</div>
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">🚨 Alerts</h3>
              <div className="space-y-3">
                <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <div className="font-medium text-yellow-600">High CPU Usage</div>
                  <div className="text-xs text-muted-foreground">2 min ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}