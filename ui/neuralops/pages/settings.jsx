import { useState } from 'react'
import Toast from '../components/Toast'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('tenant')
  const [toast, setToast] = useState(null)
  
  const renderTenantSettings = () => (
    <div className="card">
      <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
        Tenant Configuration
      </h2>
      
      <div className="form-group">
        <label className="form-label">Tenant ID</label>
        <input
          type="text"
          className="form-input"
          value="tenant-12345"
          disabled
          style={{ background: '#f9fafb' }}
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Organization Name</label>
        <input
          type="text"
          className="form-input"
          defaultValue="ATOM Corporation"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">RLS Policy Status</label>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="status-badge status-completed">Active</span>
          <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Row-level security is enabled
          </span>
        </div>
      </div>
      
      <div className="form-group">
        <label className="form-label">Cosign Public Key</label>
        <textarea
          className="form-textarea"
          defaultValue="-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE..."
          disabled
          style={{ background: '#f9fafb', minHeight: '100px' }}
        />
        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
          Used for verifying WPK signatures
        </div>
      </div>
      
      <button className="btn btn-primary">
        Save Changes
      </button>
    </div>
  )
  
  const renderBillingSettings = () => (
    <div className="card">
      <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
        Billing & Usage
      </h2>
      
      <div className="grid grid-3" style={{ marginBottom: '2rem' }}>
        <div style={{ textAlign: 'center', padding: '1rem', background: '#f9fafb', borderRadius: '6px' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4f46e5' }}>
            142
          </div>
          <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Incidents This Month
          </div>
        </div>
        
        <div style={{ textAlign: 'center', padding: '1rem', background: '#f9fafb', borderRadius: '6px' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
            89
          </div>
          <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Executions This Month
          </div>
        </div>
        
        <div style={{ textAlign: 'center', padding: '1rem', background: '#f9fafb', borderRadius: '6px' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
            3
          </div>
          <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Connected Clusters
          </div>
        </div>
      </div>
      
      <div style={{ background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '6px', padding: '1rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>⚠️</span>
          <strong>Billing Placeholder</strong>
        </div>
        <p style={{ color: '#92400e', fontSize: '0.875rem', margin: 0 }}>
          Billing integration is not yet implemented. Usage metrics are collected for future billing setup.
        </p>
      </div>
      
      <div>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
          Current Plan: Development
        </h3>
        <ul style={{ paddingLeft: '1.5rem', color: '#374151' }}>
          <li>Unlimited incidents</li>
          <li>Up to 5 clusters</li>
          <li>Basic support</li>
          <li>30-day audit retention</li>
        </ul>
      </div>
    </div>
  )
  
  const renderAPISettings = () => (
    <div className="card">
      <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
        API Configuration
      </h2>
      
      <div className="form-group">
        <label className="form-label">API Base URL</label>
        <input
          type="text"
          className="form-input"
          defaultValue="http://localhost:8080"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Orchestrator URL</label>
        <input
          type="text"
          className="form-input"
          defaultValue="http://localhost:8004"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">API Key</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="password"
            className="form-input"
            defaultValue="sk-1234567890abcdef"
            style={{ flex: 1 }}
          />
          <button className="btn btn-secondary">
            Regenerate
          </button>
        </div>
      </div>
      
      <div style={{ background: '#dbeafe', border: '1px solid #3b82f6', borderRadius: '6px', padding: '1rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>ℹ️</span>
          <strong>Service Status</strong>
        </div>
        <div style={{ fontSize: '0.875rem', color: '#1e40af' }}>
          <p>✅ Orchestrator: Connected</p>
          <p>✅ Recommender: Connected</p>
          <p>⚠️ Insight Engine: Simulation Mode</p>
          <p>⚠️ Registry: Simulation Mode</p>
        </div>
      </div>
      
      <button 
        className="btn btn-primary"
        onClick={() => setToast({ message: 'API settings saved', type: 'success' })}
      >
        Save Configuration
      </button>
    </div>
  )
  
  return (
    <div>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '2rem' }}>
        Settings
      </h1>
      
      {/* Tabs */}
      <div style={{ borderBottom: '1px solid #e5e7eb', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '2rem' }}>
          {[
            { id: 'tenant', label: 'Tenant' },
            { id: 'billing', label: 'Billing' },
            { id: 'api', label: 'API' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '1rem 0',
                border: 'none',
                background: 'none',
                borderBottom: activeTab === tab.id ? '2px solid #4f46e5' : '2px solid transparent',
                color: activeTab === tab.id ? '#4f46e5' : '#6b7280',
                fontWeight: activeTab === tab.id ? '600' : '400',
                cursor: 'pointer'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Tab Content */}
      {activeTab === 'tenant' && renderTenantSettings()}
      {activeTab === 'billing' && renderBillingSettings()}
      {activeTab === 'api' && renderAPISettings()}
      
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