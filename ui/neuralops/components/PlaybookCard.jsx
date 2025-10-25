export default function PlaybookCard({ playbook, onDryRun }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: '600' }}>
          {playbook.id}
        </h3>
        <span className={`status-badge ${playbook.safety_mode === 'auto' ? 'status-completed' : 'status-pending'}`}>
          {playbook.safety_mode || 'manual'}
        </span>
      </div>
      
      <p style={{ marginBottom: '1rem', color: '#374151' }}>
        {playbook.description || 'No description available'}
      </p>
      
      {playbook.tags && (
        <div style={{ marginBottom: '1rem' }}>
          {playbook.tags.map(tag => (
            <span key={tag} style={{
              display: 'inline-block',
              background: '#f3f4f6',
              color: '#374151',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              marginRight: '0.5rem'
            }}>
              {tag}
            </span>
          ))}
        </div>
      )}
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
          Success Rate: {playbook.success_rate || 'N/A'}%
        </div>
        <button 
          className="btn btn-secondary"
          onClick={() => onDryRun(playbook.id)}
        >
          Dry Run
        </button>
      </div>
    </div>
  )
}