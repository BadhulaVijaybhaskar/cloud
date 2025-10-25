export default function Home() {
  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 'bold', marginBottom: '1rem', color: '#4f46e5' }}>
          ⚛️ NeuralOps
        </h1>
        <p style={{ fontSize: '1.25rem', color: '#6b7280', maxWidth: '600px', margin: '0 auto' }}>
          Intelligent incident response and automation platform powered by AI
        </p>
      </div>
      
      <div className="grid grid-3" style={{ marginBottom: '3rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            🔍 Intelligent Detection
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            AI-powered anomaly detection and incident classification
          </p>
          <a href="/dashboard" className="btn btn-primary">
            View Dashboard
          </a>
        </div>
        
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            🤖 Automated Response
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            Smart playbook recommendations and automated execution
          </p>
          <a href="/playbooks" className="btn btn-primary">
            Browse Playbooks
          </a>
        </div>
        
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            ☁️ Multi-Cloud
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            Bring your own cluster with secure agent deployment
          </p>
          <a href="/onboard" className="btn btn-primary">
            Onboard Cluster
          </a>
        </div>
      </div>
    </div>
  )
}