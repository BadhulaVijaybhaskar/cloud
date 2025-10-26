import { useState, useEffect } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

export default function EdgeRuntime() {
  const [functions, setFunctions] = useState([]);
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRuntimeData();
  }, []);

  const loadRuntimeData = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/runtime/functions');
      if (response.ok) {
        const data = await response.json();
        setFunctions(data.functions || []);
      }
    } catch (error) {
      // Simulation data
      setFunctions([
        { 
          name: 'user-auth', 
          status: 'deployed', 
          runtime: 'nodejs18', 
          invocations: '1.2M', 
          avgDuration: '45ms',
          memory: '128MB'
        },
        { 
          name: 'data-processor', 
          status: 'building', 
          runtime: 'python39', 
          invocations: '856K', 
          avgDuration: '120ms',
          memory: '256MB'
        },
        { 
          name: 'ai-optimizer', 
          status: 'deployed', 
          runtime: 'nodejs18', 
          invocations: '2.4M', 
          avgDuration: '89ms',
          memory: '512MB'
        }
      ]);
      
      setDeployments([
        { id: 1, function: 'user-auth', version: 'v1.2.3', status: 'success', deployedAt: '2024-01-20 14:30' },
        { id: 2, function: 'ai-optimizer', version: 'v2.1.0', status: 'success', deployedAt: '2024-01-20 12:15' },
        { id: 3, function: 'data-processor', version: 'v1.0.1', status: 'building', deployedAt: '2024-01-20 15:45' }
      ]);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <LaunchpadLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-gradient-to-r from-teal-500 to-violet-500 rounded-full animate-pulse" />
            <h2 className="text-xl font-semibold">Loading Edge Runtime...</h2>
          </div>
        </div>
      </LaunchpadLayout>
    );
  }

  return (
    <LaunchpadLayout>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold neural-text">Edge Runtime</h1>
              <p className="text-muted-foreground">Serverless functions with AI-powered optimization</p>
            </div>
            <button className="px-4 py-2 bg-gradient-to-r from-teal-500 to-violet-500 text-white rounded-lg">
              ⚡ Deploy Function
            </button>
          </div>

          {/* Functions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {functions.map((func) => (
              <div key={func.name} className="quantum-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">{func.name}</h3>
                  <div className={`px-2 py-1 text-xs rounded-full ${
                    func.status === 'deployed' ? 'bg-emerald-500/20 text-emerald-400' :
                    func.status === 'building' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {func.status}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Runtime</span>
                    <span>{func.runtime}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Invocations</span>
                    <span>{func.invocations}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Avg Duration</span>
                    <span>{func.avgDuration}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Memory</span>
                    <span>{func.memory}</span>
                  </div>
                </div>
                
                <div className="flex gap-2 mt-4">
                  <button className="flex-1 px-3 py-1 bg-accent rounded text-sm">Logs</button>
                  <button className="flex-1 px-3 py-1 bg-accent rounded text-sm">Metrics</button>
                  <button className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm">Edit</button>
                </div>
              </div>
            ))}
            
            {/* Add Function Card */}
            <div className="border-2 border-dashed border-border/50 rounded-lg p-6 flex flex-col items-center justify-center text-center hover:border-primary/50 transition-colors cursor-pointer">
              <div className="text-4xl mb-2">⚡</div>
              <h3 className="font-semibold mb-1">New Function</h3>
              <p className="text-sm text-muted-foreground">Deploy serverless code</p>
            </div>
          </div>

          {/* Recent Deployments */}
          <div className="quantum-card p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              🚀 Recent Deployments
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left p-2">Function</th>
                    <th className="text-left p-2">Version</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-left p-2">Deployed At</th>
                    <th className="text-left p-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {deployments.map((deployment) => (
                    <tr key={deployment.id} className="border-b border-border/50 hover:bg-accent/20">
                      <td className="p-2 font-medium">{deployment.function}</td>
                      <td className="p-2">{deployment.version}</td>
                      <td className="p-2">
                        <div className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full ${
                          deployment.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' :
                          deployment.status === 'building' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          <div className="w-1 h-1 rounded-full bg-current" />
                          {deployment.status}
                        </div>
                      </td>
                      <td className="p-2 text-muted-foreground">{deployment.deployedAt}</td>
                      <td className="p-2">
                        <button className="text-xs text-primary hover:text-primary/80">
                          View Logs
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Runtime Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-emerald-500">99.9%</div>
              <div className="text-sm text-muted-foreground">Uptime</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-violet-500">4.5M</div>
              <div className="text-sm text-muted-foreground">Total Invocations</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-teal-500">67ms</div>
              <div className="text-sm text-muted-foreground">Avg Cold Start</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-orange-500">$12.34</div>
              <div className="text-sm text-muted-foreground">Monthly Cost</div>
            </div>
          </div>
        </div>
      </div>
    </LaunchpadLayout>
  );
}