import Layout from '../components/Layout'

export default function Home() {
  return (
    <Layout title="Developer Console">
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        {/* Hero Section */}
        <div className="relative overflow-hidden bg-gradient-to-r from-teal-500/10 via-primary/5 to-violet-500/10 border-b border-border/50">
          <div className="absolute inset-0 bg-grid-pattern opacity-5" />
          <div className="relative max-w-7xl mx-auto px-6 py-12">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-emerald-600">Developer Console Active</span>
              </div>
              <h1 className="text-4xl font-bold neural-text">
                ATOM Developer Console
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl">
                Build, deploy, and manage your applications with AI-powered development tools.
              </p>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
          {/* Quick Actions */}
          <div className="quantum-card p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              ⚡ Quick Actions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <button className="quantum-card p-6 hover:scale-105 transition-transform neural-glow">
                <div className="text-lg font-semibold neural-text">🚀 Create Project</div>
                <div className="text-sm text-muted-foreground mt-2">Start with AI-powered templates</div>
              </button>
              <button className="quantum-card p-6 hover:scale-105 transition-transform neural-glow">
                <div className="text-lg font-semibold neural-text">🔧 Generate API</div>
                <div className="text-sm text-muted-foreground mt-2">Auto-generate from specifications</div>
              </button>
              <button className="quantum-card p-6 hover:scale-105 transition-transform neural-glow">
                <div className="text-lg font-semibold neural-text">📊 View Analytics</div>
                <div className="text-sm text-muted-foreground mt-2">Real-time performance insights</div>
              </button>
            </div>
          </div>

          {/* Development Tools */}
          <div className="quantum-card p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              🛠️ Development Tools
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="quantum-card p-4">
                <h3 className="font-semibold mb-2 neural-text">Code Assistant</h3>
                <p className="text-sm text-muted-foreground mb-4">AI-powered code generation and optimization</p>
                <button className="atom-gradient text-white px-4 py-2 rounded-lg text-sm font-medium">
                  Launch Assistant
                </button>
              </div>
              <div className="quantum-card p-4">
                <h3 className="font-semibold mb-2 neural-text">Database Studio</h3>
                <p className="text-sm text-muted-foreground mb-4">Visual database design and management</p>
                <button className="atom-gradient text-white px-4 py-2 rounded-lg text-sm font-medium">
                  Open Studio
                </button>
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="quantum-card p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              🛡️ System Status
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center space-y-2">
                <div className="text-3xl font-bold text-emerald-500">99.9%</div>
                <div className="text-sm text-muted-foreground">API Uptime</div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-gradient-to-r from-emerald-500 to-green-500 h-2 rounded-full" style={{ width: '99.9%' }} />
                </div>
              </div>
              <div className="text-center space-y-2">
                <div className="text-3xl font-bold text-violet-500">98.7%</div>
                <div className="text-sm text-muted-foreground">AI Engine</div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-gradient-to-r from-violet-500 to-purple-500 h-2 rounded-full" style={{ width: '98.7%' }} />
                </div>
              </div>
              <div className="text-center space-y-2">
                <div className="text-3xl font-bold text-teal-500">100%</div>
                <div className="text-sm text-muted-foreground">Security</div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-gradient-to-r from-teal-500 to-cyan-500 h-2 rounded-full" style={{ width: '100%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}