interface Agent {
  id: string
  name: string
  description: string
  vendor: string
  price: number
  rating: number
  downloads: number
  tags: string[]
  license: string
  status?: string
  capabilities?: string[]
}

interface AgentCardProps {
  agent: Agent
  onDeploy?: (agentId: string) => void
  onViewDetails?: (agentId: string) => void
}

export default function AgentCard({ agent, onDeploy, onViewDetails }: AgentCardProps) {
  return (
    <div className="quantum-card p-6 hover:scale-105 transition-transform">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-violet-500 rounded-lg flex items-center justify-center text-white font-bold">
            🤖
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg neural-text mb-1">{agent.name}</h3>
            <p className="text-sm text-muted-foreground mb-2">by {agent.vendor}</p>
          </div>
        </div>
        <div className="text-right ml-4">
          <div className="text-lg font-bold text-emerald-600">
            {agent.price === 0 ? 'Free' : `$${agent.price}`}
          </div>
          {agent.price > 0 && (
            <div className="text-xs text-muted-foreground">/month</div>
          )}
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{agent.description}</p>

      <div className="flex items-center gap-4 mb-4 text-sm">
        <div className="flex items-center gap-1">
          <span>⭐</span>
          <span>{agent.rating}</span>
        </div>
        <div className="flex items-center gap-1">
          <span>🚀</span>
          <span>{agent.downloads.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <span>⚖️</span>
          <span>{agent.license}</span>
        </div>
      </div>

      {agent.capabilities && agent.capabilities.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-muted-foreground mb-2">Capabilities:</div>
          <div className="flex flex-wrap gap-1">
            {agent.capabilities.slice(0, 2).map(cap => (
              <span key={cap} className="px-2 py-1 bg-secondary/50 text-xs rounded-full">
                {cap.replace('_', ' ')}
              </span>
            ))}
            {agent.capabilities.length > 2 && (
              <span className="px-2 py-1 bg-secondary/50 text-xs rounded-full">
                +{agent.capabilities.length - 2}
              </span>
            )}
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-1 mb-4">
        {agent.tags.slice(0, 3).map(tag => (
          <span key={tag} className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
            {tag}
          </span>
        ))}
        {agent.tags.length > 3 && (
          <span className="px-2 py-1 bg-secondary/50 text-xs rounded-full">
            +{agent.tags.length - 3}
          </span>
        )}
      </div>

      {agent.status && (
        <div className="mb-4">
          <span className={`px-2 py-1 text-xs rounded-full ${
            agent.status === 'active' 
              ? 'bg-emerald-500/20 text-emerald-600' 
              : 'bg-gray-500/20 text-gray-600'
          }`}>
            {agent.status}
          </span>
        </div>
      )}

      <div className="flex gap-2">
        {onViewDetails && (
          <button 
            onClick={() => onViewDetails(agent.id)}
            className="flex-1 quantum-card py-2 px-4 rounded-lg text-sm font-medium hover:bg-accent"
          >
            👁️ View Details
          </button>
        )}
        {onDeploy && (
          <button 
            onClick={() => onDeploy(agent.id)}
            className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg text-sm font-medium hover:opacity-90"
          >
            🚀 Deploy
          </button>
        )}
      </div>
    </div>
  )
}