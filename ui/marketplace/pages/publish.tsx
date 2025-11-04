import { useState } from 'react'
import Layout from '../components/Layout'

export default function Publish() {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    version: '1.0.0',
    kind: 'model',
    license: 'MIT',
    tags: '',
    artifact_url: '',
    price: '0'
  })

  const [publishing, setPublishing] = useState(false)
  const [published, setPublished] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setPublishing(true)

    try {
      const publishData = {
        ...formData,
        vendor_id: 'vendor-123',
        tags: formData.tags.split(',').map(t => t.trim()),
        rationale: 'Published via marketplace UI',
        safety_metadata: { ui_published: true }
      }

      console.log('Publishing:', publishData)
      await new Promise(resolve => setTimeout(resolve, 2000))
      setPublished(true)
    } catch (error) {
      console.error('Publish failed:', error)
    } finally {
      setPublishing(false)
    }
  }

  if (published) {
    return (
      <Layout title="Published Successfully - ATOM Marketplace">
        <div className="min-h-screen flex items-center justify-center">
          <div className="quantum-card p-8 text-center max-w-md">
            <div className="text-6xl mb-4 text-emerald-500">✓</div>
            <h2 className="text-2xl font-bold neural-text mb-4">Published Successfully!</h2>
            <p className="text-muted-foreground mb-6">
              Your {formData.kind} "{formData.name}" has been submitted for review.
            </p>
            <button 
              onClick={() => setPublished(false)}
              className="atom-gradient text-white px-6 py-3 rounded-lg font-medium"
            >
              Publish Another
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Publish to Marketplace - ATOM Marketplace">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold neural-text mb-8">Publish to Marketplace</h1>
        
        <form onSubmit={handleSubmit} className="quantum-card p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="My Awesome Model"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Version *</label>
              <input
                type="text"
                required
                value={formData.version}
                onChange={(e) => setFormData({...formData, version: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="1.0.0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Type *</label>
              <select
                value={formData.kind}
                onChange={(e) => setFormData({...formData, kind: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="model">AI Model</option>
                <option value="agent">AI Agent</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">License *</label>
              <select
                value={formData.license}
                onChange={(e) => setFormData({...formData, license: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="MIT">MIT</option>
                <option value="Apache-2.0">Apache 2.0</option>
                <option value="proprietary">Proprietary</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Description *</label>
              <textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Describe what your model/agent does..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Tags</label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({...formData, tags: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="ai, nlp, vision (comma separated)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Price (USD/month)</label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="0.00"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Artifact URL *</label>
              <input
                type="url"
                required
                value={formData.artifact_url}
                onChange={(e) => setFormData({...formData, artifact_url: e.target.value})}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="https://storage.example.com/my-model.tar.gz"
              />
            </div>
          </div>

          <div className="mt-8 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
            <h3 className="font-semibold text-yellow-600 mb-2">Governance Review</h3>
            <p className="text-sm text-muted-foreground">
              Your submission will undergo automated governance checks (P1-P20) including:
              PII scanning, bias validation, security scanning, and license verification.
            </p>
          </div>

          <div className="mt-8 flex gap-4">
            <button
              type="submit"
              disabled={publishing}
              className="atom-gradient text-white px-8 py-3 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
            >
              {publishing ? 'Publishing...' : 'Publish to Marketplace'}
            </button>
            
            <button
              type="button"
              className="quantum-card px-8 py-3 rounded-lg font-medium hover:bg-accent"
            >
              Save Draft
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}