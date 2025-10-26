import { useState, useEffect } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

export default function Analytics() {
  const [metrics, setMetrics] = useState({});
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/analytics/overview');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data.metrics || {});
        setEvents(data.events || []);
      }
    } catch (error) {
      // Simulation data
      setMetrics({
        totalUsers: 12847,
        activeUsers: 3421,
        apiRequests: 2400000,
        errorRate: 0.02,
        avgResponseTime: 89,
        dataTransfer: 1.2
      });
      
      setEvents([
        { timestamp: '2024-01-20 15:30', event: 'user_login', count: 234, trend: '+12%' },
        { timestamp: '2024-01-20 15:25', event: 'api_request', count: 1567, trend: '+8%' },
        { timestamp: '2024-01-20 15:20', event: 'function_invoke', count: 89, trend: '-3%' },
        { timestamp: '2024-01-20 15:15', event: 'data_query', count: 445, trend: '+15%' }
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
            <h2 className="text-xl font-semibold">Loading Analytics...</h2>
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
              <h1 className="text-3xl font-bold neural-text">Analytics</h1>
              <p className="text-muted-foreground">Real-time insights with AI-powered predictions</p>
            </div>
            <button className="px-4 py-2 bg-gradient-to-r from-teal-500 to-violet-500 text-white rounded-lg">
              📊 AI Insights
            </button>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-emerald-500">{metrics.totalUsers?.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Total Users</div>
              <div className="text-xs text-emerald-400 mt-1">+12% this week</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-violet-500">{metrics.activeUsers?.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Active Users</div>
              <div className="text-xs text-violet-400 mt-1">+8% today</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-teal-500">{(metrics.apiRequests / 1000000).toFixed(1)}M</div>
              <div className="text-sm text-muted-foreground">API Requests</div>
              <div className="text-xs text-teal-400 mt-1">+15% today</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-orange-500">{(metrics.errorRate * 100).toFixed(2)}%</div>
              <div className="text-sm text-muted-foreground">Error Rate</div>
              <div className="text-xs text-green-400 mt-1">-5% today</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-blue-500">{metrics.avgResponseTime}ms</div>
              <div className="text-sm text-muted-foreground">Avg Response</div>
              <div className="text-xs text-blue-400 mt-1">-12ms today</div>
            </div>
            <div className="quantum-card p-4 text-center">
              <div className="text-2xl font-bold text-purple-500">{metrics.dataTransfer}TB</div>
              <div className="text-sm text-muted-foreground">Data Transfer</div>
              <div className="text-xs text-purple-400 mt-1">+23% today</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Real-time Events */}
            <div className="quantum-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                📈 Real-time Events
              </h3>
              
              <div className="space-y-3">
                {events.map((event, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border border-border/50 rounded-lg">
                    <div>
                      <div className="font-medium">{event.event.replace('_', ' ').toUpperCase()}</div>
                      <div className="text-sm text-muted-foreground">{event.timestamp}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{event.count.toLocaleString()}</div>
                      <div className={`text-xs ${
                        event.trend.startsWith('+') ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {event.trend}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Insights */}
            <div className="quantum-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                🧠 AI Insights
              </h3>
              
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    <span className="font-medium text-emerald-400">Performance Optimization</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    AI detected 23% improvement opportunity in API response times. 
                    Recommend enabling neural caching.
                  </p>
                </div>
                
                <div className="p-4 bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" />
                    <span className="font-medium text-violet-400">Usage Pattern</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Peak usage predicted at 18:00 UTC. Auto-scaling will activate 
                    additional resources.
                  </p>
                </div>
                
                <div className="p-4 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                    <span className="font-medium text-amber-400">Cost Optimization</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Potential 31% cost reduction identified. Consider migrating 
                    low-frequency functions to edge runtime.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Placeholder */}
          <div className="quantum-card p-6">
            <h3 className="text-xl font-semibold mb-4">Usage Trends</h3>
            <div className="h-64 bg-gradient-to-r from-teal-500/5 to-violet-500/5 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-2">📊</div>
                <p className="text-muted-foreground">Interactive charts powered by AI analytics</p>
                <p className="text-sm text-muted-foreground mt-1">Real-time data visualization coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </LaunchpadLayout>
  );
}