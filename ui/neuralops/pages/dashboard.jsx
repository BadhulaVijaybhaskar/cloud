import { useState, useEffect } from 'react'
import IncidentCard from '../components/IncidentCard'
import Toast from '../components/Toast'

export default function Dashboard() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [toast, setToast] = useState(null)
  
  useEffect(() => {
    fetchIncidents()
  }, [])
  
  const fetchIncidents = async () => {
    try {
      // Try real API first, fallback to mock
      let response
      try {
        response = await fetch('/api/orchestrator/incidents')
      } catch (error) {
        response = await fetch('/api/mock/incidents')
      }
      
      if (response.ok) {
        const data = await response.json()
        setIncidents(Array.isArray(data) ? data : data.incidents || [])
      } else {
        throw new Error('Failed to fetch incidents')
      }
    } catch (error) {
      console.error('Error fetching incidents:', error)
      setToast({ message: 'Failed to load incidents', type: 'error' })
      // Use fallback data
      setIncidents([
        {
          id: 'inc-001',
          status: 'pending',
          playbook_id: 'restart-unhealthy',
          description: 'High CPU usage detected on production cluster',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          updated_at: new Date().toISOString()
        }
      ])
    } finally {
      setLoading(false)
    }
  }
  
  const filteredIncidents = incidents.filter(incident => {
    if (filter === 'all') return true
    return incident.status === filter
  })
  
  const statusCounts = incidents.reduce((acc, incident) => {
    acc[incident.status] = (acc[incident.status] || 0) + 1
    return acc
  }, {})
  
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>Loading incidents...</div>
      </div>
    )
  }
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>
          Incident Dashboard
        </h1>
        <button 
          className="btn btn-primary"
          onClick={fetchIncidents}
        >
          Refresh
        </button>
      </div>
      
      {/* Status Summary */}
      <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
            {statusCounts.pending || 0}
          </div>
          <div style={{ color: '#6b7280' }}>Pending</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3b82f6' }}>
            {statusCounts.running || 0}
          </div>
          <div style={{ color: '#6b7280' }}>Running</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
            {statusCounts.completed || 0}
          </div>
          <div style={{ color: '#6b7280' }}>Completed</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>
            {statusCounts.failed || 0}
          </div>
          <div style={{ color: '#6b7280' }}>Failed</div>
        </div>
      </div>
      
      {/* Filters */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {['all', 'pending', 'running', 'completed', 'failed'].map(status => (
            <button
              key={status}
              className={`btn ${filter === status ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilter(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>
      
      {/* Incidents List */}
      <div>
        {filteredIncidents.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>
              No incidents found
            </div>
          </div>
        ) : (
          filteredIncidents.map(incident => (
            <IncidentCard key={incident.id} incident={incident} />
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