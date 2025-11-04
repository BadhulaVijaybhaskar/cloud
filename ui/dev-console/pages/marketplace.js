import { useEffect, useState } from 'react'
import Layout from '../components/Layout'

export default function Marketplace() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const response = await fetch('http://localhost:8101/v1/models')
      const data = await response.json()
      setModels(data.models || [])
    } catch (error) {
      console.log('Using simulation data')
      setModels([
        {
          id: 'model-1',
          name: 'ATOM Neural Optimizer',
          description: 'AI-powered performance optimization',
          vendor_id: 'atom-team',
          license: 'MIT',
          tags: ['ai', 'optimization'],
          status: 'active'
        }
      ])
    }
    setLoading(false)
  }

  const publishModel = () => {
    // Deep link to marketplace UI
    window.open('http://localhost:3006', '_blank')
  }

  return (
    <Layout title="Marketplace">
      <div className="min-h-screen neural-background">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold neural-text">AI Marketplace</h1>
              <p className="text-muted-foreground mt-2">Discover and deploy AI models and agents</p>
            </div>
            <button 
              onClick={publishModel}
              className="atom-gradient text-white px-6 py-3 rounded-lg font-medium hover:opacity-90"
            >
              🚀 Publish Model
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
              <div>Loading marketplace...</div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {models.map(model => (
                <div key={model.id} className="quantum-card p-6">
                  <h3 className="font-bold text-lg neural-text mb-2">{model.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{model.description}</p>
                  
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-2 py-1 bg-secondary/50 text-xs rounded-full">{model.license}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      model.status === 'active' ? 'bg-emerald-500/20 text-emerald-600' : 'bg-gray-500/20 text-gray-600'
                    }`}>
                      {model.status}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-4">
                    {model.tags?.map(tag => (
                      <span key={tag} className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <button className="w-full atom-gradient text-white py-2 px-4 rounded-lg font-medium hover:opacity-90">
                    ⚡ Deploy Model
                  </button>
                </div>
              ))}
              
              <div className="quantum-card p-6 border-2 border-dashed border-border/50 hover:border-primary/50 transition-colors cursor-pointer" onClick={publishModel}>
                <div className="text-center">
                  <div className="text-4xl mb-4">➕</div>
                  <h3 className="font-semibold mb-2">Publish Your Model</h3>
                  <p className="text-sm text-muted-foreground">Share your AI models with the community</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}