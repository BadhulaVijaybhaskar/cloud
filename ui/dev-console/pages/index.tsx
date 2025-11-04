import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Rocket, FolderOpen, CreditCard, ShoppingCart, Key, FileText } from 'lucide-react'
import Layout from '../components/Layout'
import ProjectCard from '../components/ProjectCard'

export default function Home() {
  const router = useRouter()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    setProjects([
      {
        id: 'p-1',
        name: 'Alpha Project',
        owner: 'org-1',
        status: 'running',
        quota: { cpu: 35, memory: 60 },
        last_activity: '2024-12-28T10:30:00Z'
      },
      {
        id: 'p-2',
        name: 'Beta Project',
        owner: 'org-1',
        status: 'suspended',
        quota: { cpu: 0, memory: 0 },
        last_activity: '2024-12-27T15:20:00Z'
      }
    ])
    setLoading(false)
  }

  const createProject = async () => {
    if (!newProjectName.trim()) return
    
    const newProject = {
      id: `p-${Date.now()}`,
      name: newProjectName,
      owner: 'org-1',
      status: 'running',
      quota: { cpu: 0, memory: 0 },
      last_activity: new Date().toISOString()
    }
    
    setProjects([...projects, newProject])
    setNewProjectName('')
    setShowCreateModal(false)
  }

  const openProject = (projectId) => {
    router.push(`/project/${projectId}`)
  }

  const manageProject = (projectId) => {
    router.push(`/project/${projectId}`)
  }

  const filteredProjects = projects.filter(project => 
    project.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <Layout title="Developer Console">
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        <div className="relative overflow-hidden bg-gradient-to-r from-teal-500/10 via-primary/5 to-violet-500/10 border-b border-border/50">
          <div className="absolute inset-0 bg-grid-pattern opacity-5" />
          <div className="relative max-w-7xl mx-auto px-6 py-12">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold neural-text mb-4">Projects</h1>
                <p className="text-xl text-muted-foreground">Manage your organization projects</p>
              </div>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="atom-gradient text-white px-6 py-3 rounded-lg font-medium hover:opacity-90 flex items-center gap-2"
              >
                <Rocket className="w-4 h-4" />
                Create Project
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="quantum-card p-6 mb-8">
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
              <div>Loading projects...</div>
            </div>
          ) : filteredProjects.length === 0 ? (
            <div className="quantum-card p-12 text-center">
              <FolderOpen className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-xl font-bold neural-text mb-2">No Projects Found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery ? 'No projects match your search.' : 'Create your first project to get started.'}
              </p>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="atom-gradient text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 mx-auto"
              >
                <Rocket className="w-4 h-4" />
                Create Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProjects.map(project => (
                <ProjectCard 
                  key={project.id} 
                  project={project} 
                  onOpen={openProject}
                  onManage={manageProject}
                />
              ))}
            </div>
          )}

          <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
            <button onClick={() => router.push('/billing')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <CreditCard className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold neural-text">Billing</div>
              </div>
              <div className="text-sm text-muted-foreground">View costs and invoices</div>
            </button>
            <button onClick={() => router.push('/marketplace')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <ShoppingCart className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold neural-text">Marketplace</div>
              </div>
              <div className="text-sm text-muted-foreground">Browse AI models</div>
            </button>
            <button onClick={() => router.push('/api-keys')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <Key className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold neural-text">API Keys</div>
              </div>
              <div className="text-sm text-muted-foreground">Manage access tokens</div>
            </button>
            <button onClick={() => router.push('/logs')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold neural-text">Logs</div>
              </div>
              <div className="text-sm text-muted-foreground">View system logs</div>
            </button>
          </div>
        </div>

        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="quantum-card p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold mb-4">Create New Project</h2>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Project Name</label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="e.g., My Awesome Project"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={createProject}
                  disabled={!newProjectName.trim()}
                  className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Rocket className="w-4 h-4" />
                  Create Project
                </button>
                <button 
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 quantum-card py-2 px-4 rounded-lg font-medium hover:bg-accent"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}