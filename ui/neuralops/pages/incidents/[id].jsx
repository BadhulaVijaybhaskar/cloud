import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import ApproveModal from '../../components/ApproveModal'
import Toast from '../../components/Toast'

export default function IncidentDetail() {
  const router = useRouter()
  const { id } = router.query
  
  const [incident, setIncident] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [toast, setToast] = useState(null)
  
  useEffect(() => {
    if (id) {
      fetchIncident()
    }
  }, [id])
  
  const fetchIncident = async () => {
    try {
      // Try real API first, fallback to mock
      let response
      try {
        response = await fetch(`/api/orchestrator/orchestrations/${id}`)
      } catch (error) {
        // Mock incident data
        setIncident({
          id,
          status: 'pending',
          stage: 'suggest',
          playbook_id: 'restart-unhealthy',
          description: 'High CPU usage detected on production cluster',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          updated_at: new Date().toISOString(),
          audit_trail: [
            {
              stage: 'suggest',
              action: 'create_incident',
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              details: { playbook_id: 'restart-unhealthy' }
            }
          ]
        })
        setLoading(false)
        return
      }
      
      if (response.ok) {
        const data = await response.json()
        setIncident(data)
      } else {
        throw new Error('Failed to fetch incident')
      }
    } catch (error) {
      console.error('Error fetching incident:', error)
      setToast({ message: 'Failed to load incident details', type: 'error' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleDryRun = async () => {
    try {
      const response = await fetch(`/api/orchestrator/orchestrations/${id}/dry-run`, {
        method: 'POST'
      })
      
      if (response.ok) {
        setToast({ message: 'Dry-run initiated successfully', type: 'success' })
        fetchIncident() // Refresh data
      } else {
        throw new Error('Dry-run failed')
      }
    } catch (error) {
      console.error('Dry-run error:', error)
      setToast({ message: 'Dry-run request failed', type: 'error' })
    }
  }
  
  const handleApprove = async (approvalData) => {
    try {
      const response = await fetch(`/api/orchestrator/orchestrations/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(approvalData)
      })
      
      if (response.ok) {
        setToast({ message: 'Incident approved successfully', type: 'success' })
        fetchIncident() // Refresh data
      } else {
        throw new Error('Approval failed')
      }
    } catch (error) {
      console.error('Approval error:', error)
      setToast({ message: 'Approval request failed', type: 'error' })
    }
  }
  
  const handleExecute = async () => {
    try {
      const response = await fetch(`/api/orchestrator/orchestrations/${id}/execute`, {
        method: 'POST'
      })
      
      if (response.ok) {
        setToast({ message: 'Execution initiated successfully', type: 'success' })
        fetchIncident() // Refresh data
      } else {
        throw new Error('Execution failed')
      }
    } catch (error) {
      console.error('Execution error:', error)
      setToast({ message: 'Execution request failed', type: 'error' })
    }
  }
  
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>Loading incident details...</div>
      </div>
    )
  }
  
  if (!incident) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '1.125rem', color: '#ef4444' }}>Incident not found</div>
      </div>
    )
  }
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>
          Incident {incident.id}
        </h1>
        <span className={`status-badge status-${incident.status}`}>
          {incident.status}
        </span>
      </div>
      
      {/* Incident Overview */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Overview
        </h2>
        <div className="grid grid-2">
          <div>
            <p><strong>Playbook:</strong> {incident.playbook_id}</p>
            <p><strong>Stage:</strong> {incident.stage}</p>
            <p><strong>Created:</strong> {new Date(incident.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p><strong>Status:</strong> {incident.status}</p>
            <p><strong>Updated:</strong> {new Date(incident.updated_at).toLocaleString()}</p>
          </div>
        </div>
        {incident.description && (
          <div style={{ marginTop: '1rem' }}>
            <p><strong>Description:</strong> {incident.description}</p>
          </div>
        )}
      </div>
      
      {/* Timeline */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Timeline
        </h2>
        <div className="timeline">
          {incident.audit_trail?.map((entry, index) => (
            <div key={index} className={`timeline-item ${entry.stage === incident.stage ? 'active' : 'completed'}`}>
              <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                {entry.stage.charAt(0).toUpperCase() + entry.stage.slice(1)} - {entry.action}
              </h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                {new Date(entry.timestamp).toLocaleString()}
              </p>
              {entry.details && (
                <pre style={{ fontSize: '0.75rem', color: '#374151', background: '#f9fafb', padding: '0.5rem', borderRadius: '4px' }}>
                  {JSON.stringify(entry.details, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Actions */}
      <div className="card">
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Actions
        </h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {incident.stage === 'suggest' && (
            <button className="btn btn-primary" onClick={handleDryRun}>
              Request Dry-Run
            </button>
          )}
          
          {incident.stage === 'dry_run' && incident.status === 'completed' && (
            <button className="btn btn-success" onClick={() => setShowApproveModal(true)}>
              Request Approval
            </button>
          )}
          
          {incident.stage === 'approved' && (
            <button className="btn btn-danger" onClick={handleExecute}>
              Execute Playbook
            </button>
          )}
          
          <button className="btn btn-secondary" onClick={fetchIncident}>
            Refresh
          </button>
        </div>
      </div>
      
      {showApproveModal && (
        <ApproveModal
          incident={incident}
          onApprove={handleApprove}
          onClose={() => setShowApproveModal(false)}
        />
      )}
      
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