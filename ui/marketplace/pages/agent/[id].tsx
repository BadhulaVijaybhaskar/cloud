import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '../../components/Layout'

export default function AgentDetail() {
  const router = useRouter()
  const { id } = router.query
  const [agent, setAgent] = useState(null)
  const [testRunning, setTestRunning] = useState(false)
  const [manifest, setManifest] = useState(null)

  useEffect(() => {
    if (id) {
      setAgent({
        id: id,
        name: 'ATOM Analytics Agent',
        vendor: 'ATOM Team',
        description: 'Intelligent data analytics and reporting agent',
        version: '3.0.0',
        price: 49.99,
        rating: 4.7,
        downloads: 8930,
        license: 'Apache-2.0',
        tags: ['analytics', 'reporting', 'ai'],
        safety_metadata: {
          governance_status: 'approved',
          pii_scan: 'passed',
          security_scan: 'passed'
        },
        execution_policy: {
          max_runtime: '30m',
          memory_limit: '2GB',
          network_access: 'restricted',
          file_access: 'read-only'
        }
      })

      setManifest({
        name: 'analytics-agent',
        version: '3.0.0',
        runtime: 'python:3.11',
        entrypoint: 'main.py',
        dependencies: [
          'pandas>=2.0.0',
          'numpy>=1.24.0',
          'plotly>=5.0.0'
        ],
        capabilities: [
          'data_analysis',
          'visualization',
          'report_generation'
        ],
        inputs: {
          data_source: { type: 'string', required: true },
          analysis_type: { type: 'enum', values: ['summary', 'trend', 'correlation'] },
          output_format: { type: 'enum', values: ['json', 'html', 'pdf'] }
        },
        outputs: {
          report: { type: 'file', format: 'varies' },
          metrics: { type: 'json' }
        }
      })
    }
  }, [id])

  const handleTestRun = async () => {
    setTestRunning(true)
    
    // Simulate test run
    setTimeout(() => {
      setTestRunning(false)
      alert('Test completed! Generated sample analytics report in 12.3s')
    }, 3000)
  }

  const handleDeploy = () => {
    // Navigate to checkout
    router.push(`/checkout?agent=${id}&project=${router.query.project || 'p-1'}`)
  }

  if (!agent) return <div>Loading...</div>

  return (
    <Layout title={`${agent.name} - ATOM Marketplace`}>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="quantum-card p-8 mb-8">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-violet-500 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                  A
                </div>
                <div>
                  <h1 className="text-4xl font-bold neural-text">{agent.name}</h1>
                  <p className="text-muted-foreground">by {agent.vendor}</p>
                </div>
              </div>
              
              <p className="text-xl text-muted-foreground mb-6">{agent.description}</p>
              
              <div className="flex items-center gap-6 mb-6">
                <div className="flex items-center gap-2">
                  <span className="text-yellow-500">★</span>
                  <span className="font-semibold">{agent.rating}</span>
                  <span className="text-muted-foreground">({agent.downloads.toLocaleString()} deployments)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Version:</span>
                  <span>v{agent.version}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">License:</span>
                  <span>{agent.license}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {agent.tags.map(tag => (
                  <span key={tag} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="text-right ml-8">
              <div className="text-3xl font-bold text-emerald-600 mb-4">
                ${agent.price}/month
              </div>
              <div className="space-y-3">
                <button 
                  onClick={handleTestRun}
                  disabled={testRunning}
                  className="w-full quantum-card px-6 py-3 rounded-lg font-medium hover:bg-accent disabled:opacity-50"
                >
                  {testRunning ? 'Testing...' : 'Test Run'}
                </button>
                <button 
                  onClick={handleDeploy}
                  className="w-full atom-gradient text-white px-6 py-3 rounded-lg font-medium"
                >
                  Deploy Agent
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Agent Manifest */}
            <div className="quantum-card p-6">
              <h2 className="text-2xl font-bold mb-6">Agent Manifest</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Runtime</div>
                    <div className="font-mono text-sm">{manifest.runtime}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Entrypoint</div>
                    <div className="font-mono text-sm">{manifest.entrypoint}</div>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-muted-foreground mb-2">Capabilities</div>
                  <div className="flex flex-wrap gap-2">
                    {manifest.capabilities.map(cap => (
                      <span key={cap} className="px-2 py-1 bg-secondary/50 text-xs rounded-full">
                        {cap.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-muted-foreground mb-2">Dependencies</div>
                  <div className="bg-secondary/20 rounded-lg p-3">
                    <pre className="text-xs font-mono">
                      {manifest.dependencies.join('\n')}
                    </pre>
                  </div>
                </div>
              </div>
            </div>

            {/* Execution Policy */}
            <div className="quantum-card p-6">
              <h2 className="text-2xl font-bold mb-6">Execution Policy</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">Runtime:</span>
                  <div>
                    <div className="font-medium">Max Runtime</div>
                    <div className="text-sm text-muted-foreground">{agent.execution_policy.max_runtime}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">Memory:</span>
                  <div>
                    <div className="font-medium">Memory Limit</div>
                    <div className="text-sm text-muted-foreground">{agent.execution_policy.memory_limit}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">Network:</span>
                  <div>
                    <div className="font-medium">Network Access</div>
                    <div className="text-sm text-muted-foreground">{agent.execution_policy.network_access}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">Files:</span>
                  <div>
                    <div className="font-medium">File Access</div>
                    <div className="text-sm text-muted-foreground">{agent.execution_policy.file_access}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Input/Output Schema */}
            <div className="quantum-card p-6">
              <h2 className="text-2xl font-bold mb-6">Input/Output Schema</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-3">Inputs</h3>
                  <div className="space-y-3">
                    {Object.entries(manifest.inputs).map(([key, schema]) => (
                      <div key={key} className="p-3 bg-secondary/20 rounded-lg">
                        <div className="font-medium text-sm">{key}</div>
                        <div className="text-xs text-muted-foreground">
                          Type: {schema.type}
                          {schema.required && <span className="text-red-500 ml-1">*</span>}
                        </div>
                        {schema.values && (
                          <div className="text-xs text-muted-foreground">
                            Values: {schema.values.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-3">Outputs</h3>
                  <div className="space-y-3">
                    {Object.entries(manifest.outputs).map(([key, schema]) => (
                      <div key={key} className="p-3 bg-secondary/20 rounded-lg">
                        <div className="font-medium text-sm">{key}</div>
                        <div className="text-xs text-muted-foreground">
                          Type: {schema.type}
                          {schema.format && ` (${schema.format})`}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Safety Report */}
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">Safety Report</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-500">✓</span>
                  <div>
                    <div className="font-medium text-sm">Governance Status</div>
                    <div className="text-xs text-emerald-600 font-medium">
                      {agent.safety_metadata.governance_status}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-emerald-500">✓</span>
                  <div>
                    <div className="font-medium text-sm">PII Scanning</div>
                    <div className="text-xs text-emerald-600 font-medium">
                      {agent.safety_metadata.pii_scan}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-emerald-500">✓</span>
                  <div>
                    <div className="font-medium text-sm">Security Scan</div>
                    <div className="text-xs text-emerald-600 font-medium">
                      {agent.safety_metadata.security_scan}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">Statistics</h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Deployments</span>
                  <span className="font-semibold">{agent.downloads.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Version</span>
                  <span className="font-semibold">v{agent.version}</span>
                </div>
                <div className="flex justify-between">
                  <span>License</span>
                  <span className="font-semibold">{agent.license}</span>
                </div>
                <div className="flex justify-between">
                  <span>Rating</span>
                  <span className="font-semibold">{agent.rating}</span>
                </div>
              </div>
            </div>

            {/* Sandbox Configuration */}
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">Sandbox Config</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Test Data Source</label>
                  <select className="w-full px-3 py-2 border border-border rounded text-sm bg-background">
                    <option>Sample Dataset</option>
                    <option>Upload CSV</option>
                    <option>Connect Database</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Analysis Type</label>
                  <select className="w-full px-3 py-2 border border-border rounded text-sm bg-background">
                    <option>Summary</option>
                    <option>Trend Analysis</option>
                    <option>Correlation</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Output Format</label>
                  <select className="w-full px-3 py-2 border border-border rounded text-sm bg-background">
                    <option>JSON</option>
                    <option>HTML Report</option>
                    <option>PDF Report</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
} bg-secondary/20 rounded-lg">
                        <div className="font-medium text-sm">{key}</div>
                        <div className="text-xs text-muted-foreground">
                          Type: {schema.type}
                          {schema.required && <span className="text-red-500 ml-1">*</span>}
                        </div>
                        {schema.values && (
                          <div className="text-xs text-muted-foreground">
                            Values: {schema.values.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-3">📤 Outputs</h3>
                  <div className="space-y-3">
                    {Object.entries(manifest.outputs).map(([key, schema]) => (
                      <div key={key} className="p-3 bg-secondary/20 rounded-lg">
                        <div className="font-medium text-sm">{key}</div>
                        <div className="text-xs text-muted-foreground">
                          Type: {schema.type}
                          {schema.format && ` (${schema.format})`}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Safety Report */}
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">🛡️ Safety Report</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span>✅</span>
                  <div>
                    <div className="font-medium text-sm">Governance Status</div>
                    <div className="text-xs text-emerald-600 font-medium">
                      {agent.safety_metadata.governance_status}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span>✅</span>
                  <div>
                    <div className="font-medium text-sm">PII Scanning</div>
                    <div className="text-xs text-emerald-600 font-medium">
                      {agent.safety_metadata.pii_scan}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span>✅</span>
                  <div>
                    <div className="font-medium text-sm">Security Scan</div>
                    <div className="text-xs text-emerald-600 font-medium">
                      {agent.safety_metadata.security_scan}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">📊 Statistics</h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Deployments</span>
                  <span className="font-semibold">{agent.downloads.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Version</span>
                  <span className="font-semibold">v{agent.version}</span>
                </div>
                <div className="flex justify-between">
                  <span>License</span>
                  <span className="font-semibold">{agent.license}</span>
                </div>
                <div className="flex justify-between">
                  <span>Rating</span>
                  <span className="font-semibold">⭐ {agent.rating}</span>
                </div>
              </div>
            </div>

            {/* Sandbox Configuration */}
            <div className="quantum-card p-6">
              <h3 className="text-lg font-bold mb-4">⚙️ Sandbox Config</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Test Data Source</label>
                  <select className="w-full px-3 py-2 border border-border rounded text-sm bg-background">
                    <option>Sample Dataset</option>
                    <option>Upload CSV</option>
                    <option>Connect Database</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Analysis Type</label>
                  <select className="w-full px-3 py-2 border border-border rounded text-sm bg-background">
                    <option>Summary</option>
                    <option>Trend Analysis</option>
                    <option>Correlation</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Output Format</label>
                  <select className="w-full px-3 py-2 border border-border rounded text-sm bg-background">
                    <option>JSON</option>
                    <option>HTML Report</option>
                    <option>PDF Report</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}