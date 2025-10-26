import { useState, useEffect } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

export default function AuthStudio() {
  const [users, setUsers] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAuthData();
  }, []);

  const loadAuthData = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/auth/users');
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      // Simulation data
      setUsers([
        { id: 1, email: 'admin@atom.cloud', role: 'admin', status: 'active', lastLogin: '2024-01-20' },
        { id: 2, email: 'user@example.com', role: 'user', status: 'active', lastLogin: '2024-01-19' },
        { id: 3, email: 'dev@company.com', role: 'developer', status: 'pending', lastLogin: null }
      ]);
      
      setPolicies([
        { name: 'users_select', table: 'users', operation: 'SELECT', condition: 'auth.uid() = id' },
        { name: 'projects_insert', table: 'projects', operation: 'INSERT', condition: 'auth.role() = "admin"' },
        { name: 'analytics_read', table: 'analytics', operation: 'SELECT', condition: 'true' }
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
            <h2 className="text-xl font-semibold">Loading Auth Studio...</h2>
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
              <h1 className="text-3xl font-bold neural-text">Auth Studio</h1>
              <p className="text-muted-foreground">Identity & access control with quantum-safe security</p>
            </div>
            <button className="px-4 py-2 bg-gradient-to-r from-teal-500 to-violet-500 text-white rounded-lg">
              🛡️ Security Scan
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Users Management */}
            <div className="quantum-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  👥 Users
                </h3>
                <button className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm">
                  Add User
                </button>
              </div>
              
              <div className="space-y-3">
                {users.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-3 border border-border/50 rounded-lg">
                    <div>
                      <div className="font-medium">{user.email}</div>
                      <div className="text-sm text-muted-foreground">
                        {user.role} • {user.status}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        user.status === 'active' ? 'bg-emerald-500' : 'bg-amber-500'
                      }`} />
                      <button className="text-xs text-muted-foreground hover:text-foreground">
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* RLS Policies */}
            <div className="quantum-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  🔒 RLS Policies
                </h3>
                <button className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm">
                  New Policy
                </button>
              </div>
              
              <div className="space-y-3">
                {policies.map((policy, idx) => (
                  <div key={idx} className="p-3 border border-border/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{policy.name}</div>
                      <span className={`px-2 py-1 text-xs rounded ${
                        policy.operation === 'SELECT' ? 'bg-blue-500/20 text-blue-400' :
                        policy.operation === 'INSERT' ? 'bg-green-500/20 text-green-400' :
                        'bg-orange-500/20 text-orange-400'
                      }`}>
                        {policy.operation}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Table: {policy.table}
                    </div>
                    <div className="text-xs font-mono bg-accent/50 p-2 rounded mt-2">
                      {policy.condition}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Auth Settings */}
          <div className="quantum-card p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              ⚙️ Authentication Settings
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-3">
                <h4 className="font-medium">Providers</h4>
                <div className="space-y-2">
                  {['Email/Password', 'Google OAuth', 'GitHub OAuth', 'Magic Links'].map((provider) => (
                    <div key={provider} className="flex items-center justify-between">
                      <span className="text-sm">{provider}</span>
                      <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium">Security</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">2FA Required</span>
                    <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Password Strength</span>
                    <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Session Timeout</span>
                    <span className="text-xs text-muted-foreground">24h</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium">Quantum Security</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Post-Quantum Crypto</span>
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Neural Threat Detection</span>
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </LaunchpadLayout>
  );
}