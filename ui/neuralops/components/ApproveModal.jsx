import { useState } from 'react'

export default function ApproveModal({ incident, onApprove, onClose }) {
  const [justification, setJustification] = useState('')
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!justification.trim()) return
    
    setLoading(true)
    try {
      await onApprove({
        orchestration_id: incident.id,
        approver_id: 'admin', // In production, get from JWT
        justification: justification.trim()
      })
      onClose()
    } catch (error) {
      console.error('Approval failed:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: '600' }}>
          Approve Execution
        </h2>
        
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f9fafb', borderRadius: '6px' }}>
          <p><strong>Incident ID:</strong> {incident.id}</p>
          <p><strong>Playbook:</strong> {incident.playbook_id}</p>
          <p><strong>Status:</strong> {incident.status}</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              Justification <span style={{ color: '#ef4444' }}>*</span>
            </label>
            <textarea
              className="form-textarea"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Provide justification for approving this execution..."
              required
            />
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !justification.trim()}
            >
              {loading ? 'Approving...' : 'Approve Execution'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}