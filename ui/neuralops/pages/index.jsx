import Link from 'next/link'

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
          <Link href="/dashboard" className="btn btn-primary">
            View Dashboard
          </Link>
        </div>
        
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            🤖 Automated Response
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            Smart playbook recommendations and automated execution
          </p>
          <Link href="/playbooks" className="btn btn-primary">
            Browse Playbooks
          </Link>
        </div>
        
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            ☁️ Multi-Cloud
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            Bring your own cluster with secure agent deployment
          </p>
          <Link href="/onboard" className="btn btn-primary">
            Onboard Cluster
          </Link>
        </div>
      </div>
      
      <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          Ready to get started?
        </h2>
        <p style={{ fontSize: '1.125rem', marginBottom: '2rem', opacity: 0.9 }}>
          Deploy NeuralOps in your environment and start automating incident response
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/dashboard" className="btn" style={{ background: 'white', color: '#4f46e5' }}>
            View Dashboard
          </Link>
          <Link href="/onboard" className="btn" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid white' }}>
            Onboard Cluster
          </Link>
        </div>
      </div>
    </div>
  )
}