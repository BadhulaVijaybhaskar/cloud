import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '../../components/Layout'

export default function ModelDetail() {
  const router = useRouter()
  const { id } = router.query
  const [model, setModel] = useState(null)
  const [testRunning, setTestRunning] = useState(false)

  useEffect(() => {
    if (id) {
      setModel({
        id: id,
        name: 'ATOM Neural Optimizer',
        vendor: 'ATOM Team',
        description: 'AI-powered performance optimization engine',
        version: '2.1.0',
        price: 29.99,
        rating: 4.8,
        downloads: 15420,
        license: 'MIT',
        tags: ['ai', 'optimization'],
        safety_metadata: {
          governance_status: 'approved'
        }
      })
    }
  }, [id])

  const handleTestRun = async () => {
    setTestRunning(true)
    setTimeout(() => {
      setTestRunning(false)
      alert('Test completed! Performance: +23%')
    }, 3000)
  }

  if (!model) return <div>Loading...</div>

  return (
    <Layout title={`${model.name} - ATOM Marketplace`}>
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="quantum-card p-8 mb-8">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-4xl font-bold neural-text mb-4">{model.name}</h1>
              <p className="text-xl text-muted-foreground mb-6">{model.description}</p>
              
              <div className="flex items-center gap-6 mb-6">
                <div className="flex items-center gap-2">
                  <span className="text-yellow-500">★</span>
                  <span className="font-semibold">{model.rating}</span>
                  <span className="text-muted-foreground">({model.downloads.toLocaleString()} downloads)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">by</span>
                  <span>{model.vendor}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {model.tags.map(tag => (
                  <span key={tag} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="text-right">
              <div className="text-3xl font-bold text-emerald-600 mb-4">
                ${model.price}/month
              </div>
              <div className="space-y-3">
                <button 
                  onClick={handleTestRun}
                  disabled={testRunning}
                  className="w-full quantum-card px-6 py-3 rounded-lg font-medium hover:bg-accent disabled:opacity-50"
                >
                  {testRunning ? 'Testing...' : 'Test Run'}
                </button>
                <button className="w-full atom-gradient text-white px-6 py-3 rounded-lg font-medium">
                  Deploy Model
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="quantum-card p-6">
              <h2 className="text-2xl font-bold mb-6">Safety Report</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-500">✓</span>
                  <div>
                    <div className="font-medium">PII Scanning</div>
                    <div className="text-sm text-muted-foreground">No personal data detected</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-emerald-500">✓</span>
                  <div>
                    <div className="font-medium">Governance Status</div>
                    <div className="text-sm text-emerald-600 font-medium">Approved</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">Statistics</h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Downloads</span>
                  <span className="font-semibold">{model.downloads.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Version</span>
                  <span className="font-semibold">{model.version}</span>
                </div>
                <div className="flex justify-between">
                  <span>License</span>
                  <span className="font-semibold">{model.license}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}