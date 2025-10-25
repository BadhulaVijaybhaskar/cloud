import { useState, useEffect } from 'react'
import PlaybookCard from '../components/PlaybookCard'
import Toast from '../components/Toast'

export default function Playbooks() {
  const [playbooks, setPlaybooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState(null)
  
  useEffect(() => {
    fetchPlaybooks()
  }, [])
  
  const fetchPlaybooks = async () => {
    try {
      // Try real API first, fallback to mock
      let response
      try {
        response = await fetch('/api/recommender/playbooks')
      } catch (error) {
        response = await fetch('/api/mock/playbooks')
      }
      
      if (response.ok) {
        const data = await response.json()
        setPlaybooks(Array.isArray(data) ? data : data.playbooks || [])
      } else {
        throw new Error('Failed to fetch playbooks')
      }
    } catch (error) {
      console.error('Error fetching playbooks:', error)
      setToast({ message: 'Failed to load playbooks', type: 'error' })
      // Use fallback data
      setPlaybooks([
        {
          id: 'restart-unhealthy',
          description: 'Restart unhealthy pods in deployment',
          safety_mode: 'manual',
          success_rate: 95,
          tags: ['kubernetes', 'restart', 'health']
        },
        {
          id: 'scale-deployment',
          description: 'Scale deployment based on resource usage',
          safety_mode: 'auto',
          success_rate: 88,
          tags: ['kubernetes', 'scaling', 'performance']
        }
      ])
    } finally {
      setLoading(false)
    }
  }
  
  const handleDryRun = async (playbookId) => {
    try {
      const response = await fetch(`/api/registry/workflows/${playbookId}/dry-run`, {
        method: 'POST'
      })
      
      if (response.ok) {
        setToast({ message: `Dry-run initiated for ${playbookId}`, type: 'success' })
      } else {
        throw new Error('Dry-run failed')
      }
    } catch (error) {
      console.error('Dry-run error:', error)
      setToast({ message: `Dry-run failed for ${playbookId}`, type: 'error' })
    }
  }
  
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>Loading playbooks...</div>
      </div>
    )
  }
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>
          Playbook Catalog
        </h1>
        <button 
          className="btn btn-primary"
          onClick={fetchPlaybooks}
        >
          Refresh
        </button>
      </div>
      
      <div style={{ marginBottom: '2rem' }}>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Browse and test available automation playbooks
        </p>
      </div>
      
      {/* Playbooks Grid */}
      <div className="grid grid-2">
        {playbooks.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem', gridColumn: '1 / -1' }}>
            <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>
              No playbooks available
            </div>
          </div>
        ) : (
          playbooks.map(playbook => (
            <PlaybookCard 
              key={playbook.id} 
              playbook={playbook} 
              onDryRun={handleDryRun}
            />
          ))
        )}
      </div>
      
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}