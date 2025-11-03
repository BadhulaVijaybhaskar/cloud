import { useState, useEffect } from 'react'

export default function MarketplaceHome() {
  const [packages, setPackages] = useState([])
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    // Simulate package data
    setPackages([
      {
        id: 'auth-service-1.0.0',
        name: 'ATOM Auth Service',
        description: 'Complete authentication service with JWT and OAuth2',
        category: 'Authentication',
        author: 'ATOM Team',
        rating: 4.8,
        downloads: 15420,
        quality_score: 96
      },
      {
        id: 'neural-optimizer-2.1.0',
        name: 'Neural Performance Optimizer',
        description: 'AI-powered performance optimization engine',
        category: 'AI/ML',
        author: 'Neural Labs',
        rating: 4.9,
        downloads: 8930,
        quality_score: 94
      }
    ])
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
      <div className="bg-gradient-to-r from-teal-500/10 via-primary/5 to-violet-500/10 border-b border-border/50">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <h1 className="text-4xl font-bold neural-text mb-4">
            ATOM Marketplace
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Discover, deploy, and monetize AI-powered cloud solutions
          </p>
          
          <div className="max-w-2xl">
            <input
              type="text"
              placeholder="Search packages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 border border-border rounded-lg bg-background/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {packages.map(pkg => (
            <div key={pkg.id} className="quantum-card p-6 hover:scale-105 transition-transform">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-bold text-lg neural-text">{pkg.name}</h3>
                  <p className="text-sm text-muted-foreground">by {pkg.author}</p>
                </div>
                <div className="text-sm font-semibold text-emerald-500">
                  {pkg.quality_score}
                </div>
              </div>

              <p className="text-sm text-muted-foreground mb-4">
                {pkg.description}
              </p>

              <div className="flex items-center gap-4 mb-4 text-sm">
                <span>⭐ {pkg.rating}</span>
                <span>📥 {pkg.downloads.toLocaleString()}</span>
              </div>

              <button className="w-full atom-gradient text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity">
                ⚡ Install Package
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}