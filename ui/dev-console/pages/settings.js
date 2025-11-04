import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function Settings() {
  const [settings, setSettings] = useState({
    notifications: {
      email_alerts: true,
      slack_integration: false,
      webhook_url: ''
    },
    security: {
      two_factor_enabled: true,
      session_timeout: 30,
      ip_whitelist: []
    },
    integrations: {
      github_connected: false,
      ci_cd_enabled: false,
      service_mesh_status: 'active'
    }
  })

  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    // Simulate loading settings
    // In real implementation, fetch from developer-console-core API
  }

  const saveSettings = async () => {
    setLoading(true)
    
    // Simulate saving settings
    setTimeout(() => {
      setLoading(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    }, 1000)
  }

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
  }

  const openLaunchPadAuth = () => {
    // Deep link to LaunchPad Auth UI
    window.open('http://localhost:3000/auth/providers', '_blank')
  }

  const openServiceMeshConfig = () => {
    // Link to infrastructure configuration
    alert('Service mesh configuration is managed through infrastructure. Contact your admin.')
  }

  return (
    <Layout title="Settings">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold neural-text">Console Settings</h1>
            <p className="text-muted-foreground mt-2">Configure your Developer Console preferences</p>
          </div>
          <button 
            onClick={saveSettings}
            disabled={loading}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              saved 
                ? 'bg-emerald-500 text-white' 
                : 'atom-gradient text-white hover:opacity-90'
            } disabled:opacity-50`}
          >
            {loading ? '🔄 Saving...' : saved ? '✅ Saved!' : '💾 Save Settings'}
          </button>
        </div>

        <div className="space-y-8">
          {/* Notifications */}
          <div className="quantum-card p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              🔔 Notifications
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Email Alerts</div>
                  <div className="text-sm text-muted-foreground">Receive alerts via email</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.email_alerts}
                    onChange={(e) => updateSetting('notifications', 'email_alerts', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Slack Integration</div>
                  <div className="text-sm text-muted-foreground">Send alerts to Slack channels</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.slack_integration}
                    onChange={(e) => updateSetting('notifications', 'slack_integration', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              {settings.notifications.slack_integration && (
                <div>
                  <label className="block text-sm font-medium mb-2">Webhook URL</label>
                  <input
                    type="url"
                    value={settings.notifications.webhook_url}
                    onChange={(e) => updateSetting('notifications', 'webhook_url', e.target.value)}
                    placeholder="https://hooks.slack.com/services/..."
                    className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Security */}
          <div className="quantum-card p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              🛡️ Security
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Two-Factor Authentication</div>
                  <div className="text-sm text-muted-foreground">Add extra security to your account</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.security.two_factor_enabled}
                    onChange={(e) => updateSetting('security', 'two_factor_enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Session Timeout (minutes)</label>
                <select
                  value={settings.security.session_timeout}
                  onChange={(e) => updateSetting('security', 'session_timeout', parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                  <option value={120}>2 hours</option>
                </select>
              </div>
            </div>
          </div>

          {/* Integrations */}
          <div className="quantum-card p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              🔗 Integrations
            </h2>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center text-white font-bold">
                    GH
                  </div>
                  <div>
                    <div className="font-medium">GitHub Integration</div>
                    <div className="text-sm text-muted-foreground">
                      {settings.integrations.github_connected ? 'Connected' : 'Connect your GitHub repositories'}
                    </div>
                  </div>
                </div>
                <button 
                  className={`px-4 py-2 rounded-lg font-medium ${
                    settings.integrations.github_connected
                      ? 'bg-red-500/20 text-red-600 hover:bg-red-500/30'
                      : 'atom-gradient text-white hover:opacity-90'
                  }`}
                  onClick={() => updateSetting('integrations', 'github_connected', !settings.integrations.github_connected)}
                >
                  {settings.integrations.github_connected ? 'Disconnect' : 'Connect'}
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                    CI
                  </div>
                  <div>
                    <div className="font-medium">CI/CD Pipeline</div>
                    <div className="text-sm text-muted-foreground">
                      {settings.integrations.ci_cd_enabled ? 'Enabled' : 'Enable automated deployments'}
                    </div>
                  </div>
                </div>
                <button 
                  className={`px-4 py-2 rounded-lg font-medium ${
                    settings.integrations.ci_cd_enabled
                      ? 'bg-red-500/20 text-red-600 hover:bg-red-500/30'
                      : 'atom-gradient text-white hover:opacity-90'
                  }`}
                  onClick={() => updateSetting('integrations', 'ci_cd_enabled', !settings.integrations.ci_cd_enabled)}
                >
                  {settings.integrations.ci_cd_enabled ? 'Disable' : 'Enable'}
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold">
                    SM
                  </div>
                  <div>
                    <div className="font-medium">Service Mesh</div>
                    <div className="text-sm text-muted-foreground">
                      Status: <span className="text-emerald-600 font-medium">{settings.integrations.service_mesh_status}</span>
                    </div>
                  </div>
                </div>
                <button 
                  onClick={openServiceMeshConfig}
                  className="quantum-card px-4 py-2 rounded-lg font-medium hover:bg-accent"
                >
                  Configure
                </button>
              </div>
            </div>
          </div>

          {/* Auth Providers */}
          <div className="quantum-card p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              🔐 Authentication Providers
            </h2>
            
            <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-4">
              <p className="text-sm text-blue-600">
                ℹ️ Authentication provider configuration is managed through LaunchPad Auth UI for consistency across all services.
              </p>
            </div>

            <button 
              onClick={openLaunchPadAuth}
              className="atom-gradient text-white px-6 py-3 rounded-lg font-medium hover:opacity-90"
            >
              🚀 Open LaunchPad Auth Settings
            </button>
          </div>

          {/* Policy Links */}
          <div className="quantum-card p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
              📋 Policies & Compliance
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button className="p-4 border border-border rounded-lg hover:bg-accent text-left">
                <div className="font-medium mb-1">🛡️ Security Policies</div>
                <div className="text-sm text-muted-foreground">View P1-P20 security policies</div>
              </button>
              
              <button className="p-4 border border-border rounded-lg hover:bg-accent text-left">
                <div className="font-medium mb-1">📊 Governance Reports</div>
                <div className="text-sm text-muted-foreground">Access compliance reports</div>
              </button>
              
              <button className="p-4 border border-border rounded-lg hover:bg-accent text-left">
                <div className="font-medium mb-1">🔍 Audit Logs</div>
                <div className="text-sm text-muted-foreground">View system audit trails</div>
              </button>
              
              <button className="p-4 border border-border rounded-lg hover:bg-accent text-left">
                <div className="font-medium mb-1">⚖️ Data Privacy</div>
                <div className="text-sm text-muted-foreground">Review privacy settings</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}