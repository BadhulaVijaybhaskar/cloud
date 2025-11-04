interface Model {
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
}

interface ModelCardProps {
  model: Model
  onDeploy?: (modelId: string) => void
  onViewDetails?: (modelId: string) => void
}

export default function ModelCard({ model, onDeploy, onViewDetails }: ModelCardProps) {
  return (
    <div className="quantum-card p-6 hover:scale-105 transition-transform">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-bold text-lg neural-text mb-1">{model.name}</h3>
          <p className="text-sm text-muted-foreground mb-2">by {model.vendor}</p>
          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{model.description}</p>
        </div>
        <div className="text-right ml-4">
          <div className="text-lg font-bold text-emerald-600">
            {model.price === 0 ? 'Free' : `$${model.price}`}
          </div>
          {model.price > 0 && (
            <div className="text-xs text-muted-foreground">/month</div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 mb-4 text-sm">
        <div className="flex items-center gap-1">
          <span>⭐</span>
          <span>{model.rating}</span>
        </div>
        <div className="flex items-center gap-1">
          <span>📥</span>
          <span>{model.downloads.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <span>⚖️</span>
          <span>{model.license}</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mb-4">
        {model.tags.slice(0, 3).map(tag => (
          <span key={tag} className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
            {tag}
          </span>
        ))}
        {model.tags.length > 3 && (
          <span className="px-2 py-1 bg-secondary/50 text-xs rounded-full">
            +{model.tags.length - 3}
          </span>
        )}
      </div>

      {model.status && (
        <div className="mb-4">
          <span className={`px-2 py-1 text-xs rounded-full ${
            model.status === 'active' 
              ? 'bg-emerald-500/20 text-emerald-600' 
              : 'bg-gray-500/20 text-gray-600'
          }`}>
            {model.status}
          </span>
        </div>
      )}

      <div className="flex gap-2">
        {onViewDetails && (
          <button 
            onClick={() => onViewDetails(model.id)}
            className="flex-1 quantum-card py-2 px-4 rounded-lg text-sm font-medium hover:bg-accent"
          >
            👁️ View Details
          </button>
        )}
        {onDeploy && (
          <button 
            onClick={() => onDeploy(model.id)}
            className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg text-sm font-medium hover:opacity-90"
          >
            ⚡ Deploy
          </button>
        )}
      </div>
    </div>
  )
}