import Link from 'next/link'

export default function IncidentCard({ incident }) {
  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'status-pending'
      case 'running': return 'status-running'
      case 'completed': return 'status-completed'
      case 'failed': return 'status-failed'
      default: return 'status-pending'
    }
  }
  
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: '600' }}>
            <Link href={`/incidents/${incident.id}`} style={{ textDecoration: 'none', color: '#4f46e5' }}>
              {incident.id}
            </Link>
          </h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            {new Date(incident.created_at).toLocaleString()}
          </p>
        </div>
        <span className={`status-badge ${getStatusClass(incident.status)}`}>
          {incident.status}
        </span>
      </div>
      
      <p style={{ marginBottom: '1rem', color: '#374151' }}>
        {incident.description || 'No description available'}
      </p>
      
      {incident.playbook_id && (
        <div style={{ marginBottom: '1rem' }}>
          <strong>Recommended Playbook:</strong> {incident.playbook_id}
        </div>
      )}
      
      <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
        Last updated: {new Date(incident.updated_at || incident.created_at).toLocaleString()}
      </div>
    </div>
  )
}