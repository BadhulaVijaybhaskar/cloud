import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function ApiKeys() {
  const [keys, setKeys] = useState([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [createdKey, setCreatedKey] = useState(null)

  useEffect(() => {
    loadApiKeys()
  }, [])

  const loadApiKeys = () => {
    // Simulate API keys data
    setKeys([
      {
        id: 'key-1',
        name: 'Production API Key',
        masked_key: 'ak_**********************abc123',
        created_at: '2024-12-01T10:00:00Z',
        last_used: '2024-12-28T09:30:00Z',
        status: 'active'
      },
      {
        id: 'key-2', 
        name: 'Development Key',
        masked_key: 'ak_**********************def456',
        created_at: '2024-11-15T14:20:00Z',
        last_used: '2024-12-27T16:45:00Z',
        status: 'active'
      }
    ])
  }

  const createApiKey = async () => {
    if (!newKeyName.trim()) return

    // Simulate API key creation
    const newKey = {
      id: `key-${Date.now()}`,
      name: newKeyName,
      masked_key: 'ak_**********************xyz789',
      full_key: 'ak_1234567890abcdef1234567890abcdef1234567890xyz789', // Only shown once
      created_at: new Date().toISOString(),
      last_used: null,
      status: 'active'
    }

    setKeys([...keys, newKey])
    setCreatedKey(newKey)
    setNewKeyName('')
    setShowCreateModal(false)
  }

  const revokeKey = (keyId) => {
    if (confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      setKeys(keys.filter(key => key.id !== keyId))
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  return (
    <Layout title="API Keys">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold neural-text">API Keys</h1>
            <p className="text-muted-foreground mt-2">Manage your project and global API keys</p>
          </div>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="atom-gradient text-white px-6 py-3 rounded-lg font-medium hover:opacity-90"
          >
            🔑 Create API Key
          </button>
        </div>

        {/* Created Key Display */}
        {createdKey && (
          <div className="quantum-card p-6 mb-8 border-emerald-500/20 bg-emerald-500/5">
            <h2 className="text-xl font-bold text-emerald-600 mb-4">🎉 API Key Created Successfully!</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Copy this key now - it won't be shown again for security reasons.
            </p>
            <div className="flex items-center gap-3 p-4 bg-background border rounded-lg">
              <code className="flex-1 font-mono text-sm">{createdKey.full_key}</code>
              <button 
                onClick={() => copyToClipboard(createdKey.full_key)}
                className="quantum-card px-3 py-2 rounded text-sm hover:bg-accent"
              >
                📋 Copy
              </button>
            </div>
            <button 
              onClick={() => setCreatedKey(null)}
              className="mt-4 text-sm text-muted-foreground hover:text-foreground"
            >
              ✕ Dismiss
            </button>
          </div>
        )}

        {/* API Keys Table */}
        <div className="quantum-card overflow-hidden">
          <div className="p-6 border-b border-border/50">
            <h2 className="text-xl font-bold">Your API Keys</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/20">
                <tr>
                  <th className="text-left p-4">Name</th>
                  <th className="text-left p-4">Key</th>
                  <th className="text-left p-4">Created</th>
                  <th className="text-left p-4">Last Used</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {keys.map(key => (
                  <tr key={key.id} className="border-t border-border/50">
                    <td className="p-4 font-medium">{key.name}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <code className="font-mono text-sm">{key.masked_key}</code>
                        <button 
                          onClick={() => copyToClipboard(key.masked_key)}
                          className="text-muted-foreground hover:text-foreground"
                        >
                          📋
                        </button>
                      </div>
                    </td>
                    <td className="p-4 text-sm text-muted-foreground">
                      {new Date(key.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-sm text-muted-foreground">
                      {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        key.status === 'active' 
                          ? 'bg-emerald-500/20 text-emerald-600' 
                          : 'bg-gray-500/20 text-gray-600'
                      }`}>
                        {key.status}
                      </span>
                    </td>
                    <td className="p-4">
                      <button 
                        onClick={() => revokeKey(key.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Revoke
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Create Key Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="quantum-card p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold mb-4">Create New API Key</h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Key Name</label>
                <input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g., Production API Key"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <p className="text-sm text-yellow-600">
                  ⚠️ The API key will only be shown once. Make sure to copy and store it securely.
                </p>
              </div>

              <div className="flex gap-3">
                <button 
                  onClick={createApiKey}
                  disabled={!newKeyName.trim()}
                  className="flex-1 atom-gradient text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
                >
                  Create Key
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