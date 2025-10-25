import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    // Mock data for demonstration
    setTimeout(() => {
      setIncidents([
        {
          id: 'inc-001',
          status: 'pending',
          playbook_id: 'restart-unhealthy',
          description: 'High CPU usage detected on production cluster',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'inc-002', 
          status: 'completed',
          playbook_id: 'scale-deployment',
          description: 'Memory pressure on web servers',
          created_at: new Date(Date.now() - 7200000).toISOString(),
          updated_at: new Date(Date.now() - 1800000).toISOString()
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])
  
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
        <button className="btn btn-primary">
          Refresh
        </button>
      </div>
      
      <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>1</div>
          <div style={{ color: '#6b7280' }}>Pending</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3b82f6' }}>0</div>
          <div style={{ color: '#6b7280' }}>Running</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>1</div>
          <div style={{ color: '#6b7280' }}>Completed</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>0</div>
          <div style={{ color: '#6b7280' }}>Failed</div>
        </div>
      </div>
      
      <div>
        {incidents.map(incident => (
          <div key={incident.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
              <div>
                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: '600' }}>
                  <a href={`/incidents/${incident.id}`} style={{ textDecoration: 'none', color: '#4f46e5' }}>
                    {incident.id}
                  </a>
                </h3>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  {new Date(incident.created_at).toLocaleString()}
                </p>
              </div>
              <span className={`status-badge status-${incident.status}`}>
                {incident.status}
              </span>
            </div>
            
            <p style={{ marginBottom: '1rem', color: '#374151' }}>
              {incident.description}
            </p>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Recommended Playbook:</strong> {incident.playbook_id}
            </div>
            
            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
              Last updated: {new Date(incident.updated_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}