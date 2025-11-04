import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'

export default function VendorDashboard() {
  const [vendorData, setVendorData] = useState({
    name: 'ATOM Vendor',
    id: 'vendor-123',
    models: [],
    agents: [],
    revenue: 0,
    downloads: 0
  })

  useEffect(() => {
    loadVendorData()
  }, [])

  const loadVendorData = async () => {
    // Simulate vendor data
    setVendorData({
      name: 'ATOM Vendor',
      id: 'vendor-123',
      models: [
        {
          id: 'model-1',
          name: 'Neural Optimizer',
          version: '2.1.0',
          status: 'published',
          downloads: 15420,
          revenue: 2840.50,
          rating: 4.8
        },
        {
          id: 'model-2', 
          name: 'Text Classifier',
          version: '1.5.0',
          status: 'under_review',
          downloads: 0,
          revenue: 0,
          rating: 0
        }
      ],
      agents: [
        {
          id: 'agent-1',
          name: 'Analytics Agent',
          version: '3.0.0',
          status: 'published',
          downloads: 8930,
          revenue: 1567.80,
          rating: 4.7
        }
      ],
      revenue: 4408.30,
      downloads: 24350
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'text-emerald-600 bg-emerald-500/20'
      case 'under_review': return 'text-yellow-600 bg-yellow-500/20'
      case 'rejected': return 'text-red-600 bg-red-500/20'
      default: return 'text-gray-600 bg-gray-500/20'
    }
  }

  return (
    <Layout title="Vendor Dashboard - ATOM Marketplace">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold neural-text">Vendor Dashboard</h1>
            <p className="text-muted-foreground mt-2">Welcome back, {vendorData.name}</p>
          </div>
          <button className="atom-gradient text-white px-6 py-3 rounded-lg font-medium">
            Publish New Item
          </button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-emerald-500">${vendorData.revenue.toFixed(2)}</div>
            <div className="text-sm text-muted-foreground mt-1">Total Revenue</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-violet-500">{vendorData.downloads.toLocaleString()}</div>
            <div className="text-sm text-muted-foreground mt-1">Total Downloads</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-teal-500">{vendorData.models.length}</div>
            <div className="text-sm text-muted-foreground mt-1">Published Models</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-orange-500">{vendorData.agents.length}</div>
            <div className="text-sm text-muted-foreground mt-1">Published Agents</div>
          </div>
        </div>

        {/* Models Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-6">Your Models</h2>
          <div className="quantum-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-secondary/20">
                  <tr>
                    <th className="text-left p-4">Name</th>
                    <th className="text-left p-4">Version</th>
                    <th className="text-left p-4">Status</th>
                    <th className="text-left p-4">Downloads</th>
                    <th className="text-left p-4">Revenue</th>
                    <th className="text-left p-4">Rating</th>
                    <th className="text-left p-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {vendorData.models.map(model => (
                    <tr key={model.id} className="border-t border-border/50">
                      <td className="p-4 font-medium">{model.name}</td>
                      <td className="p-4 text-muted-foreground">{model.version}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(model.status)}`}>
                          {model.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-4">{model.downloads.toLocaleString()}</td>
                      <td className="p-4 font-semibold text-emerald-600">${model.revenue.toFixed(2)}</td>
                      <td className="p-4">
                        {model.rating > 0 ? (
                          <div className="flex items-center gap-1">
                            <span>⭐</span>
                            <span>{model.rating}</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="p-4">
                        <button className="text-primary hover:text-primary/80 text-sm font-medium">
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Agents Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-6">Your Agents</h2>
          <div className="quantum-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-secondary/20">
                  <tr>
                    <th className="text-left p-4">Name</th>
                    <th className="text-left p-4">Version</th>
                    <th className="text-left p-4">Status</th>
                    <th className="text-left p-4">Downloads</th>
                    <th className="text-left p-4">Revenue</th>
                    <th className="text-left p-4">Rating</th>
                    <th className="text-left p-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {vendorData.agents.map(agent => (
                    <tr key={agent.id} className="border-t border-border/50">
                      <td className="p-4 font-medium">{agent.name}</td>
                      <td className="p-4 text-muted-foreground">{agent.version}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(agent.status)}`}>
                          {agent.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-4">{agent.downloads.toLocaleString()}</td>
                      <td className="p-4 font-semibold text-emerald-600">${agent.revenue.toFixed(2)}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-1">
                          <span>⭐</span>
                          <span>{agent.rating}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <button className="text-primary hover:text-primary/80 text-sm font-medium">
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Revenue Chart Placeholder */}
        <div className="quantum-card p-6">
          <h3 className="text-xl font-bold mb-4">Revenue Analytics</h3>
          <div className="h-64 bg-secondary/20 rounded-lg flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <div className="text-4xl mb-2 text-emerald-500">↗</div>
              <div>Revenue chart would be displayed here</div>
              <div className="text-sm mt-1">(Integration with analytics service)</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}