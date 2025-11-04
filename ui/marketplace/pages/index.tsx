import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Rocket, Settings, Download, Star, Package, ShoppingCart, Building, CreditCard } from 'lucide-react'
import Layout from '../components/Layout'

export default function MarketplaceHome() {
  const router = useRouter()
  const [packages, setPackages] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newPackageName, setNewPackageName] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadPackages()
  }, [])

  const loadPackages = async () => {
    setPackages([
      {
        id: 'model_nlp_pro',
        name: 'NLP Pro Analyzer',
        description: 'Advanced natural language processing model',
        category: 'NLP',
        author: 'ATOM AI Labs',
        rating: 4.8,
        downloads: 15420,
        status: 'published'
      },
      {
        id: 'agent_analytics',
        name: 'Analytics Agent Pro',
        description: 'Intelligent data analytics and reporting',
        category: 'Analytics',
        author: 'Data Insights Inc',
        rating: 4.7,
        downloads: 8930,
        status: 'published'
      },
      {
        id: 'model_time_series',
        name: 'Time Series Forecaster',
        description: 'Advanced forecasting for financial data',
        category: 'Analytics',
        author: 'Predictive Analytics Ltd',
        rating: 4.7,
        downloads: 22100,
        status: 'published'
      }
    ])
    setLoading(false)
  }

  const createPackage = async () => {
    if (!newPackageName.trim()) return
    
    const newPackage = {
      id: `pkg-${Date.now()}`,
      name: newPackageName,
      author: 'Your Organization',
      status: 'draft',
      rating: 0,
      downloads: 0,
      description: 'New package description'
    }
    
    setPackages([...packages, newPackage])
    setNewPackageName('')
    setShowCreateModal(false)
  }

  const openPackage = (packageId) => {
    router.push(`/model/${packageId}`)
  }

  const managePackage = (packageId) => {
    router.push(`/model/${packageId}`)
  }

  const filteredPackages = packages.filter(pkg => 
    pkg.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <Layout title="ATOM Marketplace">
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        <div className="relative overflow-hidden bg-gradient-to-r from-teal-500/10 via-primary/5 to-violet-500/10 border-b border-border/50">
          <div className="absolute inset-0 bg-grid-pattern opacity-5" />
          <div className="relative max-w-7xl mx-auto px-6 py-12">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold neural-text mb-4">AI Marketplace</h1>
                <p className="text-xl text-muted-foreground">Discover, deploy, and monetize AI models and agents</p>
              </div>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="atom-gradient text-white px-6 py-3 rounded-lg font-medium hover:opacity-90 flex items-center gap-2"
              >
                <Package className="w-4 h-4" />
                Publish Model
              </button>
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

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
              <div>Loading models...</div>
            </div>
          ) : filteredPackages.length === 0 ? (
            <div className="quantum-card p-12 text-center">
              <Package className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-xl font-bold neural-text mb-2">No Models Found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery ? 'No models match your search.' : 'Publish your first model to get started.'}
              </p>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="atom-gradient text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 mx-auto"
              >
                <Package className="w-4 h-4" />
                Publish Model
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredPackages.map(pkg => (
                <div key={pkg.id} className="quantum-card p-6 hover:scale-105 transition-transform">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-bold text-violet-500">{pkg.name}</h3>
                    <div className="flex items-center gap-1">
                      <span style={{ 
                        padding: '2px 8px', 
                        borderRadius: '12px', 
                        fontSize: '12px',
                        backgroundColor: pkg.status === 'published' ? '#d4edda' : '#f8d7da',
                        color: pkg.status === 'published' ? '#155724' : '#721c24'
                      }}>
                        {pkg.status}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{pkg.description}</p>
                  <div className="text-xs text-muted-foreground mb-4">
                    by {pkg.author}
                  </div>
                  <div className="flex items-center justify-between text-sm mb-4">
                    <span className="bg-primary/10 text-primary px-2 py-1 rounded">
                      {pkg.category}
                    </span>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-500 fill-current" />
                      <span>{pkg.rating}</span>
                    </div>
                  </div>
                  <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
                    <Download className="w-4 h-4" />
                    <span>{pkg.downloads.toLocaleString()} downloads</span>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => openPackage(pkg.id)}
                      className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg font-medium text-sm flex items-center justify-center gap-2"
                    >
                      <Rocket className="w-4 h-4" />
                      Deploy
                    </button>
                    <button 
                      onClick={() => managePackage(pkg.id)}
                      className="flex-1 quantum-card py-2 px-4 rounded-lg font-medium hover:bg-accent text-sm flex items-center justify-center gap-2"
                    >
                      <Settings className="w-4 h-4" />
                      Manage
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
            <button onClick={() => router.push('/browse')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <ShoppingCart className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold text-violet-500">Browse</div>
              </div>
              <div className="text-sm text-muted-foreground">Explore all models</div>
            </button>
            <button onClick={() => router.push('/publish')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <Package className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold text-violet-500">Publish</div>
              </div>
              <div className="text-sm text-muted-foreground">Share your models</div>
            </button>
            <button onClick={() => router.push('/vendor')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <Building className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold text-violet-500">Vendors</div>
              </div>
              <div className="text-sm text-muted-foreground">Partner directory</div>
            </button>
            <button onClick={() => router.push('/checkout')} className="quantum-card p-6 hover:scale-105 transition-transform text-left">
              <div className="flex items-center gap-3 mb-2">
                <CreditCard className="w-5 h-5 text-primary" />
                <div className="text-lg font-semibold text-violet-500">Cart</div>
              </div>
              <div className="text-sm text-muted-foreground">View purchases</div>
            </button>
          </div>
        </div>

        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="quantum-card p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold mb-4">Publish New Model</h2>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Model Name</label>
                <input
                  type="text"
                  value={newPackageName}
                  onChange={(e) => setNewPackageName(e.target.value)}
                  placeholder="e.g., My AI Model"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={createPackage}
                  disabled={!newPackageName.trim()}
                  className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Package className="w-4 h-4" />
                  Publish Model
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