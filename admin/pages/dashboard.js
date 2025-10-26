import { useState } from 'react';
import Layout from '../components/Layout';

export default function Dashboard() {
  const [projects] = useState([
    { id: 1, name: 'E-commerce API', status: 'active', users: 1247, requests: '2.4M' },
    { id: 2, name: 'Analytics Dashboard', status: 'building', users: 89, requests: '156K' },
    { id: 3, name: 'Mobile Backend', status: 'paused', users: 456, requests: '890K' }
  ]);

  const stats = [
    { title: 'Total Projects', value: '12', change: '+2.1%', color: 'from-teal-500 to-cyan-500' },
    { title: 'Active Users', value: '1,247', change: '+12.5%', color: 'from-violet-500 to-purple-500' },
    { title: 'API Requests', value: '2.4M', change: '+8.2%', color: 'from-emerald-500 to-green-500' },
    { title: 'Uptime', value: '99.9%', change: '+0.1%', color: 'from-orange-500 to-red-500' }
  ];

  return (
    <Layout title="Dashboard">
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary">
        {/* Header */}
        <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm">
          <div className="container mx-auto px-6 py-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-teal-500 via-primary to-violet-500 bg-clip-text text-transparent">
                  Dashboard
                </h1>
                <p className="text-muted-foreground mt-2">Welcome back to ATOM Cloud</p>
              </div>
              <div className="flex items-center gap-3">
                <button className="inline-flex items-center justify-center rounded-md text-sm font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-3">
                  📊 Analytics
                </button>
                <button className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-gradient-to-r from-teal-500 to-violet-500 text-white hover:opacity-90 shadow-lg hover:shadow-xl transition-all h-9 px-3">
                  ⚡ New Project
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-6 py-8 space-y-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm hover:shadow-lg transition-all duration-300 group p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                    <p className="text-2xl font-bold mt-2">{stat.value}</p>
                    <p className="text-xs text-emerald-600 mt-1">{stat.change} from last month</p>
                  </div>
                  <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.color} group-hover:scale-110 transition-transform`}>
                    <div className="w-6 h-6 text-white">📊</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Projects Overview */}
            <div className="lg:col-span-2">
              <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
                <div className="flex flex-col space-y-1.5 p-6">
                  <h3 className="text-2xl font-semibold leading-none tracking-tight flex items-center gap-2">
                    🗄️ Recent Projects
                  </h3>
                  <p className="text-sm text-muted-foreground">Your latest project activity</p>
                </div>
                <div className="p-6 pt-0">
                  <div className="space-y-4">
                    {projects.map((project) => (
                      <div key={project.id} className="flex items-center justify-between p-4 rounded-lg border border-border/50 hover:bg-accent/50 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className={`w-3 h-3 rounded-full ${
                            project.status === 'active' ? 'bg-emerald-500 animate-pulse' :
                            project.status === 'building' ? 'bg-amber-500 animate-pulse' :
                            'bg-gray-400'
                          }`} />
                          <div>
                            <h4 className="font-medium">{project.name}</h4>
                            <p className="text-sm text-muted-foreground capitalize">{project.status}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">{project.users} users</p>
                          <p className="text-xs text-muted-foreground">{project.requests} requests</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="space-y-6">
              <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
                <div className="flex flex-col space-y-1.5 p-6">
                  <h3 className="text-2xl font-semibold leading-none tracking-tight flex items-center gap-2">
                    🛡️ System Status
                  </h3>
                </div>
                <div className="p-6 pt-0 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">API Gateway</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                      <span className="text-xs text-emerald-600">Operational</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Database</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                      <span className="text-xs text-emerald-600">Healthy</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Vector Store</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                      <span className="text-xs text-amber-600">Syncing</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
                <div className="flex flex-col space-y-1.5 p-6">
                  <h3 className="text-2xl font-semibold leading-none tracking-tight flex items-center gap-2">
                    💻 Resource Usage
                  </h3>
                </div>
                <div className="p-6 pt-0 space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>CPU</span>
                      <span>67%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-gradient-to-r from-teal-500 to-violet-500 h-2 rounded-full" style={{ width: '67%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Memory</span>
                      <span>45%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-gradient-to-r from-emerald-500 to-green-500 h-2 rounded-full" style={{ width: '45%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Storage</span>
                      <span>23%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full" style={{ width: '23%' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}