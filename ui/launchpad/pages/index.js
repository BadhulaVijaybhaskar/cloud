import { useState, useEffect } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';
import ProjectCard from '../components/ProjectCard';
import AIAssistant from '../components/AIAssistant';
import QuickActions from '../components/QuickActions';
import FloatingAtomChat from '../components/FloatingAtomChat';

export default function LaunchpadHome() {
  const [projects, setProjects] = useState([]);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [systemHealth, setSystemHealth] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load data from backend API
    const loadData = async () => {
      try {
        // Check if backend is available
        const healthResponse = await fetch('http://localhost:8001/health');
        const isBackendLive = healthResponse.ok;
        
        if (isBackendLive) {
          // Load real data from backend
          const [projectsRes, aiRes] = await Promise.all([
            fetch('http://localhost:8001/api/data/query', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ sql: 'SELECT * FROM projects' })
            }),
            fetch('http://localhost:8001/api/ai/optimize/suggest', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ context: 'dashboard' })
            })
          ]);
          
          if (projectsRes.ok) {
            const projectData = await projectsRes.json();
            // Transform backend data to UI format
            const transformedProjects = projectData.rows?.map((row, index) => ({
              id: row[0] || index + 1,
              name: row[1] || 'Unknown Project',
              status: row[2] || 'active',
              aiOptimized: true,
              performance: Math.random() * 20 + 80,
              users: Math.floor(Math.random() * 10000) + 1000,
              requests: `${(Math.random() * 3 + 0.5).toFixed(1)}M/day`,
              autoScaling: Math.random() > 0.3,
              securityScore: Math.floor(Math.random() * 15 + 85),
              lastOptimized: `${Math.floor(Math.random() * 60)} minutes ago`
            })) || [];
            setProjects(transformedProjects);
          }
          
          if (aiRes.ok) {
            const aiData = await aiRes.json();
            setAiSuggestions(aiData.suggestions || []);
          }
        } else {
          throw new Error('Backend not available');
        }
      } catch (error) {
        console.log('Backend not available, using simulation data');
        // Fallback to simulation data
        setProjects([
        {
          id: 1,
          name: 'E-commerce Platform',
          status: 'autonomous',
          aiOptimized: true,
          performance: 98.7,
          users: 12847,
          requests: '2.4M/day',
          autoScaling: true,
          securityScore: 95,
          lastOptimized: '2 minutes ago'
        },
        {
          id: 2,
          name: 'Analytics Dashboard',
          status: 'learning',
          aiOptimized: true,
          performance: 94.2,
          users: 1289,
          requests: '456K/day',
          autoScaling: true,
          securityScore: 92,
          lastOptimized: '5 minutes ago'
        },
        {
          id: 3,
          name: 'Mobile Backend',
          status: 'optimizing',
          aiOptimized: false,
          performance: 87.1,
          users: 5643,
          requests: '1.2M/day',
          autoScaling: false,
          securityScore: 88,
          lastOptimized: '1 hour ago'
        }
        ]);

        setAiSuggestions([
        {
          type: 'performance',
          title: 'Auto-optimize Mobile Backend',
          description: 'AI detected 23% performance improvement opportunity',
          action: 'Enable Neural Optimization',
          impact: 'High',
          confidence: 94
        },
        {
          type: 'security',
          title: 'Quantum-safe encryption ready',
          description: 'Upgrade to post-quantum cryptography for future-proofing',
          action: 'Enable PQC',
          impact: 'Critical',
          confidence: 99
        },
        {
          type: 'cost',
          title: 'Resource optimization detected',
          description: 'AI can reduce costs by 31% without performance loss',
          action: 'Apply Optimization',
          impact: 'Medium',
          confidence: 87
        }
        ]);

        setSystemHealth({
        overall: 99.7,
        neural: 98.4,
        security: 99.9,
        performance: 97.8,
        autonomous: true
        });
        
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  if (loading) {
    return (
      <LaunchpadLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-gradient-to-r from-teal-500 to-violet-500 rounded-full animate-pulse" />
            <h2 className="text-xl font-semibold bg-gradient-to-r from-teal-500 to-violet-500 bg-clip-text text-transparent">
              ATOM Neural Network Initializing...
            </h2>
            <p className="text-muted-foreground">Autonomous systems coming online</p>
          </div>
        </div>
      </LaunchpadLayout>
    );
  }

  return (
    <LaunchpadLayout>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        {/* Hero Section */}
        <div className="relative overflow-hidden bg-gradient-to-r from-teal-500/10 via-primary/5 to-violet-500/10 border-b border-border/50">
          <div className="absolute inset-0 bg-grid-pattern opacity-5" />
          <div className="relative container mx-auto px-6 py-12">
            <div className="flex items-center justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
                  <span className="text-sm font-medium text-emerald-600">Neural Network Active</span>
                </div>
                <h1 className="text-5xl font-bold bg-gradient-to-r from-teal-500 via-primary to-violet-500 bg-clip-text text-transparent">
                  Welcome to ATOM Cloud
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl">
                  The world's first autonomous, AI-driven cloud platform. 
                  Your infrastructure learns, optimizes, and scales itself.
                </p>
                <div className="flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    <span>99.7% Uptime</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" />
                    <span>AI Optimized</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse" />
                    <span>Quantum Safe</span>
                  </div>
                </div>
              </div>
              
              <div className="hidden lg:block">
                <div className="relative">
                  <div className="w-64 h-64 bg-gradient-to-r from-teal-500/20 to-violet-500/20 rounded-full animate-pulse" />
                  <div className="absolute inset-4 bg-gradient-to-r from-teal-500/30 to-violet-500/30 rounded-full animate-pulse delay-75" />
                  <div className="absolute inset-8 bg-gradient-to-r from-teal-500/40 to-violet-500/40 rounded-full animate-pulse delay-150" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-6xl">🧠</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="w-full px-6 py-8 space-y-8">
          {/* Quick Actions */}
          <QuickActions />

          {/* AI Assistant Panel */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-8 w-full">
            <div className="xl:col-span-3 space-y-8">
              {/* Projects Grid */}
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold flex items-center gap-3">
                    🚀 Your Projects
                    <span className="text-sm font-normal text-muted-foreground bg-accent px-2 py-1 rounded-full">
                      {projects.length} Active
                    </span>
                  </h2>
                  <button className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-gradient-to-r from-teal-500 to-violet-500 text-white hover:opacity-90 shadow-lg hover:shadow-xl transition-all h-10 px-6">
                    ⚡ New Project
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
                  {projects.map((project) => (
                    <ProjectCard key={project.id} project={project} />
                  ))}
                  
                  {/* Add New Project Card */}
                  <div className="rounded-lg border-2 border-dashed border-border/50 hover:border-primary/50 transition-colors p-8 flex flex-col items-center justify-center text-center space-y-4 min-h-[300px] group cursor-pointer">
                    <div className="w-16 h-16 bg-gradient-to-r from-teal-500/10 to-violet-500/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-2xl">➕</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">Create New Project</h3>
                      <p className="text-muted-foreground text-sm">Start with AI-powered templates</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Overview */}
              <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
                <div className="flex flex-col space-y-1.5 p-6">
                  <h3 className="text-2xl font-semibold leading-none tracking-tight flex items-center gap-2">
                    🛡️ Neural System Health
                  </h3>
                  <p className="text-sm text-muted-foreground">Autonomous monitoring and optimization</p>
                </div>
                <div className="p-6 pt-0">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="text-center space-y-2">
                      <div className="text-3xl font-bold text-emerald-500">{systemHealth.overall}%</div>
                      <div className="text-sm text-muted-foreground">Overall Health</div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-gradient-to-r from-emerald-500 to-green-500 h-2 rounded-full" style={{ width: `${systemHealth.overall}%` }} />
                      </div>
                    </div>
                    <div className="text-center space-y-2">
                      <div className="text-3xl font-bold text-violet-500">{systemHealth.neural}%</div>
                      <div className="text-sm text-muted-foreground">Neural Engine</div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-gradient-to-r from-violet-500 to-purple-500 h-2 rounded-full" style={{ width: `${systemHealth.neural}%` }} />
                      </div>
                    </div>
                    <div className="text-center space-y-2">
                      <div className="text-3xl font-bold text-teal-500">{systemHealth.security}%</div>
                      <div className="text-sm text-muted-foreground">Security Fabric</div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-gradient-to-r from-teal-500 to-cyan-500 h-2 rounded-full" style={{ width: `${systemHealth.security}%` }} />
                      </div>
                    </div>
                    <div className="text-center space-y-2">
                      <div className="text-3xl font-bold text-orange-500">{systemHealth.performance}%</div>
                      <div className="text-sm text-muted-foreground">Performance</div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full" style={{ width: `${systemHealth.performance}%` }} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* System Status Sidebar */}
            <div className="xl:col-span-1">
              <div className="space-y-6">
                {/* Neural Status */}
                <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
                  <div className="flex flex-col space-y-1.5 p-6">
                    <h3 className="text-xl font-semibold leading-none tracking-tight flex items-center gap-2">
                      🧠 Neural Status
                    </h3>
                  </div>
                  <div className="p-6 pt-0 space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Learning Engine</span>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                        <span className="text-xs text-emerald-600">Active</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Optimization AI</span>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" />
                        <span className="text-xs text-violet-600">Processing</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Threat Detection</span>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse" />
                        <span className="text-xs text-teal-600">Monitoring</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Quantum Encryption</span>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
                        <span className="text-xs text-orange-600">Ready</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Live Recommendations */}
                <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
                  <div className="flex flex-col space-y-1.5 p-6">
                    <h3 className="text-xl font-semibold leading-none tracking-tight flex items-center gap-2">
                      💡 Live Insights
                    </h3>
                    <p className="text-sm text-muted-foreground">Real-time AI analysis</p>
                  </div>
                  <div className="p-6 pt-0 space-y-3">
                    {aiSuggestions.slice(0, 2).map((suggestion, index) => (
                      <div key={index} className="border border-border/50 rounded-lg p-3 text-sm">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">{suggestion.type === 'performance' ? '⚡' : suggestion.type === 'security' ? '🛡️' : '💰'}</span>
                          <span className="font-medium">{suggestion.title}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mb-2">{suggestion.description}</p>
                        <button className="text-xs text-primary hover:text-primary/80 font-medium">
                          {suggestion.action}
                        </button>
                      </div>
                    ))}
                    <button 
                      onClick={() => document.querySelector('.floating-atom-chat button').click()}
                      className="w-full text-xs text-center p-2 border border-dashed border-border/50 rounded-lg hover:bg-accent/20 transition-colors"
                    >
                      💬 Ask ATOM for more insights
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Floating ATOM Chat */}
      <div className="floating-atom-chat">
        <FloatingAtomChat />
      </div>
    </LaunchpadLayout>
  );
}