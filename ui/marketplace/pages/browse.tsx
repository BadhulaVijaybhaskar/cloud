import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function Browse() {
  const [models, setModels] = useState([])
  const [agents, setAgents] = useState([])
  const [activeTab, setActiveTab] = useState('models')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadMarketplaceData()
  }, [])

  const loadMarketplaceData = async () => {
    setModels([
      {
        id: 'model-1',
        name: 'ATOM Neural Optimizer',
        description: 'AI-powered performance optimization engine',
        vendor: 'ATOM Team',
        price: '$29.99/month',
        downloads: 15420,
        rating: 4.8,
        tags: ['ai', 'optimization']
      },
      {
        id: 'model-2', 
        name: 'Quantum Crypto Engine',
        description: 'Post-quantum cryptography implementation',
        vendor: 'CryptoCore',
        price: '$49.99/month',
        downloads: 8930,
        rating: 4.9,
        tags: ['security', 'quantum']
      }
    ])

    setAgents([
      {
        id: 'agent-1',
        name: 'Smart Analytics Agent',
        description: 'Autonomous data analysis and insights',
        vendor: 'DataLabs',
        price: '$19.99/month',
        downloads: 5670,
        rating: 4.7,
        capabilities: ['data_analysis', 'reporting']
      }
    ])
  }

  const filteredModels = models.filter(model => 
    model.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <Layout title="Browse Marketplace">
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        <div className="relative overflow-hidden bg-gradient-to-r from-teal-500/10 via-primary/5 to-violet-500/10 border-b border-border/50">
          <div className="absolute inset-0 bg-grid-pattern opacity-5" />
          <div className="relative max-w-7xl mx-auto px-6 py-12">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold neural-text mb-4">Browse Marketplace</h1>
                <p className="text-xl text-muted-foreground">Discover AI models and agents for your projects</p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="quantum-card p-6 mb-8">
            <input
              type="text"
              placeholder="Search models and agents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        
          <div className="flex gap-4 mb-8">
            <button 
              onClick={() => setActiveTab('models')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'models' 
                  ? 'atom-gradient text-white' 
                  : 'quantum-card hover:bg-accent'
              }`}
            >
              🧠 AI Models ({filteredModels.length})
            </button>
            <button 
              onClick={() => setActiveTab('agents')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'agents' 
                  ? 'atom-gradient text-white' 
                  : 'quantum-card hover:bg-accent'
              }`}
            >
              🤖 AI Agents ({filteredAgents.length})
            </button>
          </div>

          {activeTab === 'models' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredModels.map(model => (
                <div key={model.id} className="quantum-card p-6 hover:scale-105 transition-transform">
                  <h3 className="font-bold text-lg neural-text mb-2">{model.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{model.description}</p>
                  <div className="text-xs text-muted-foreground mb-4">
                    by {model.vendor}
                  </div>
                  
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-semibold text-emerald-600">{model.price}</span>
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">⭐</span>
                      <span className="text-sm">{model.rating}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-4">
                    {model.tags.map(tag => (
                      <span key={tag} className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="mb-4">
                    <div>Downloads: 📥 {model.downloads.toLocaleString()}</div>
                  </div>

                  <button className="w-full atom-gradient text-white py-2 px-4 rounded-lg font-medium">
                    🚀 Deploy Model
                  </button>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'agents' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAgents.map(agent => (
                <div key={agent.id} className="quantum-card p-6 hover:scale-105 transition-transform">
                  <h3 className="font-bold text-lg neural-text mb-2">{agent.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{agent.description}</p>
                  <div className="text-xs text-muted-foreground mb-4">
                    by {agent.vendor}
                  </div>
                  
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-semibold text-emerald-600">{agent.price}</span>
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">⭐</span>
                      <span className="text-sm">{agent.rating}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-4">
                    {agent.capabilities.map(cap => (
                      <span key={cap} className="px-2 py-1 bg-violet-500/10 text-violet-600 text-xs rounded-full">
                        {cap}
                      </span>
                    ))}
                  </div>

                  <div className="mb-4">
                    <div>Downloads: 📥 {agent.downloads.toLocaleString()}</div>
                  </div>

                  <button className="w-full atom-gradient text-white py-2 px-4 rounded-lg font-medium">
                    🚀 Deploy Agent
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}