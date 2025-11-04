import { Rocket, Settings, Play, Pause, AlertTriangle } from 'lucide-react'

interface Project {
  id: string
  name: string
  status: 'running' | 'suspended' | 'needs-attention'
  owner: string
  quota?: {
    cpu: number
    memory?: number
  }
  last_activity?: string
}

interface ProjectCardProps {
  project: Project
  onOpen: (projectId: string) => void
  onManage: (projectId: string) => void
}

export default function ProjectCard({ project, onOpen, onManage }: ProjectCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-emerald-600 bg-emerald-500/20'
      case 'suspended': return 'text-yellow-600 bg-yellow-500/20'
      case 'needs-attention': return 'text-red-600 bg-red-500/20'
      default: return 'text-gray-600 bg-gray-500/20'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Play className="w-4 h-4 text-emerald-600" />
      case 'suspended': return <Pause className="w-4 h-4 text-yellow-600" />
      case 'needs-attention': return <AlertTriangle className="w-4 h-4 text-red-600" />
      default: return <Play className="w-4 h-4 text-gray-600" />
    }
  }

  return (
    <div className="quantum-card p-6 hover:scale-105 transition-transform cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-bold text-lg text-violet-500 mb-2">{project.name}</h3>
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon(project.status)}
            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(project.status)}`}>
              {project.status.replace('-', ' ')}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">Owner: {project.owner}</p>
        </div>
      </div>

      {project.quota && (
        <div className="mb-4">
          <div className="text-sm text-muted-foreground mb-2">Resource Usage</div>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span>CPU</span>
              <span>{project.quota.cpu}%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-1">
              <div 
                className="bg-gradient-to-r from-teal-500 to-violet-500 h-1 rounded-full" 
                style={{ width: `${project.quota.cpu}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {project.last_activity && (
        <div className="text-xs text-muted-foreground mb-4">
          Last activity: {new Date(project.last_activity).toLocaleDateString()}
        </div>
      )}

      <div className="flex gap-2">
        <button 
          onClick={() => onOpen(project.id)}
          className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg text-sm font-medium hover:opacity-90 flex items-center justify-center gap-2"
        >
          <Rocket className="w-4 h-4" />
          Open
        </button>
        <button 
          onClick={() => onManage(project.id)}
          className="quantum-card py-2 px-4 rounded-lg text-sm font-medium hover:bg-accent flex items-center justify-center gap-2"
        >
          <Settings className="w-4 h-4" />
          Manage
        </button>
      </div>
    </div>
  )
}