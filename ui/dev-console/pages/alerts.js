import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadAlerts()
  }, [filter])

  const loadAlerts = async () => {
    setLoading(true)
    
    // Simulate alerts data
    const mockAlerts = [
      {
        id: 'alert-1',
        title: 'High CPU Usage Detected',
        description: 'Project Alpha is experiencing CPU usage above 90% for the last 15 minutes',
        severity: 'high',
        status: 'active',
        project_id: 'p-1',
        project_name: 'Alpha Project',
        created_at: '2024-12-28T10:30:00Z',
        acknowledged_at: null,
        acknowledged_by: null
      },
      {
        id: 'alert-2',
        title: 'API Rate Limit Approaching',
        description: 'Project Beta has used 85% of its daily API quota',
        severity: 'medium',
        status: 'active',
        project_id: 'p-2',
        project_name: 'Beta Project',
        created_at: '2024-12-28T09:45:00Z',
        acknowledged_at: null,
        acknowledged_by: null
      },
      {
        id: 'alert-3',
        title: 'Model Deployment Failed',
        description: 'Neural Optimizer v2.1.0 deployment failed due to insufficient resources',
        severity: 'high',
        status: 'acknowledged',
        project_id: 'p-1',
        project_name: 'Alpha Project',
        created_at: '2024-12-28T08:20:00Z',
        acknowledged_at: '2024-12-28T08:25:00Z',
        acknowledged_by: 'admin@example.com'
      }
    ]

    // Filter alerts
    let filteredAlerts = mockAlerts
    if (filter !== 'all') {
      filteredAlerts = filteredAlerts.filter(alert => alert.status === filter)
    }

    setAlerts(filteredAlerts)
    setLoading(false)
  }

  const acknowledgeAlert = async (alertId) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId 
        ? { 
            ...alert, 
            status: 'acknowledged',
            acknowledged_at: new Date().toISOString(),
            acknowledged_by: 'current-user@example.com'
          }
        : alert
    ))
  }

  const escalateAlert = (alertId) => {
    // Simulate escalation (create support ticket)
    alert('Alert escalated to support team. Ticket #12345 created.')
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-700 bg-red-500/20 border-red-500/30'
      case 'high': return 'text-red-600 bg-red-500/20 border-red-500/30'
      case 'medium': return 'text-yellow-600 bg-yellow-500/20 border-yellow-500/30'
      case 'low': return 'text-blue-600 bg-blue-500/20 border-blue-500/30'
      default: return 'text-gray-600 bg-gray-500/20 border-gray-500/30'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-red-600 bg-red-500/20'
      case 'acknowledged': return 'text-yellow-600 bg-yellow-500/20'
      case 'resolved': return 'text-emerald-600 bg-emerald-500/20'
      default: return 'text-gray-600 bg-gray-500/20'
    }
  }

  return (
    <Layout title="Alerts">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold neural-text">Alert Inbox</h1>
            <p className="text-muted-foreground mt-2">Monitor and manage system alerts</p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Alerts</option>
              <option value="active">Active</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>

        {/* Alert Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-red-500">
              {alerts.filter(a => a.status === 'active').length}
            </div>
            <div className="text-sm text-muted-foreground mt-1">Active Alerts</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-yellow-500">
              {alerts.filter(a => a.status === 'acknowledged').length}
            </div>
            <div className="text-sm text-muted-foreground mt-1">Acknowledged</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-red-600">
              {alerts.filter(a => a.severity === 'high' || a.severity === 'critical').length}
            </div>
            <div className="text-sm text-muted-foreground mt-1">High Priority</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-emerald-500">
              {alerts.filter(a => a.status === 'resolved').length}
            </div>
            <div className="text-sm text-muted-foreground mt-1">Resolved</div>
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
              <div>Loading alerts...</div>
            </div>
          ) : alerts.length === 0 ? (
            <div className="quantum-card p-8 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-bold neural-text mb-2">No Alerts</h3>
              <p className="text-muted-foreground">All systems are running smoothly!</p>
            </div>
          ) : (
            alerts.map(alert => (
              <AlertCard 
                key={alert.id} 
                alert={alert} 
                onAcknowledge={acknowledgeAlert}
                onEscalate={escalateAlert}
                getSeverityColor={getSeverityColor}
                getStatusColor={getStatusColor}
              />
            ))
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <button className="quantum-card p-6 hover:scale-105 transition-transform text-left">
            <div className="text-lg font-semibold neural-text mb-2">🔔 Alert Rules</div>
            <div className="text-sm text-muted-foreground">Configure alert thresholds and conditions</div>
          </button>
          
          <button className="quantum-card p-6 hover:scale-105 transition-transform text-left">
            <div className="text-lg font-semibold neural-text mb-2">📊 Alert Analytics</div>
            <div className="text-sm text-muted-foreground">View alert trends and patterns</div>
          </button>
          
          <button className="quantum-card p-6 hover:scale-105 transition-transform text-left">
            <div className="text-lg font-semibold neural-text mb-2">🔗 Integrations</div>
            <div className="text-sm text-muted-foreground">Connect to Slack, PagerDuty, etc.</div>
          </button>
        </div>
      </div>
    </Layout>
  )
}

function AlertCard({ alert, onAcknowledge, onEscalate, getSeverityColor, getStatusColor }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`quantum-card border-l-4 ${getSeverityColor(alert.severity)}`}>
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(alert.severity)}`}>
                {alert.severity.toUpperCase()}
              </span>
              <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(alert.status)}`}>
                {alert.status.toUpperCase()}
              </span>
              <span className="text-sm text-muted-foreground">
                {alert.project_name}
              </span>
            </div>
            
            <h3 className="text-lg font-bold neural-text mb-2">{alert.title}</h3>
            <p className="text-muted-foreground mb-4">{alert.description}</p>
            
            <div className="text-sm text-muted-foreground">
              Created: {new Date(alert.created_at).toLocaleString()}
              {alert.acknowledged_at && (
                <span className="ml-4">
                  Acknowledged: {new Date(alert.acknowledged_at).toLocaleString()} by {alert.acknowledged_by}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            {alert.status === 'active' && (
              <>
                <button 
                  onClick={() => onAcknowledge(alert.id)}
                  className="quantum-card px-4 py-2 rounded-lg text-sm font-medium hover:bg-accent"
                >
                  ✓ Acknowledge
                </button>
                <button 
                  onClick={() => onEscalate(alert.id)}
                  className="atom-gradient text-white px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90"
                >
                  ⚡ Escalate
                </button>
              </>
            )}
            <button 
              onClick={() => setExpanded(!expanded)}
              className="text-muted-foreground hover:text-foreground"
            >
              {expanded ? '▼' : '▶'}
            </button>
          </div>
        </div>
        
        {expanded && (
          <div className="mt-4 pt-4 border-t border-border/50">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="font-medium mb-1">Alert ID:</div>
                <div className="text-muted-foreground font-mono">{alert.id}</div>
              </div>
              <div>
                <div className="font-medium mb-1">Project ID:</div>
                <div className="text-muted-foreground font-mono">{alert.project_id}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}