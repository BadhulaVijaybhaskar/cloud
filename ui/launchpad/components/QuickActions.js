export default function QuickActions() {
  const actions = [
    {
      title: 'Create Project',
      description: 'Start with AI-powered templates',
      icon: '🚀',
      gradient: 'from-teal-500 to-cyan-500',
      action: () => console.log('Create project'),
      featured: true
    },
    {
      title: 'Deploy Function',
      description: 'Serverless edge computing',
      icon: '⚡',
      gradient: 'from-violet-500 to-purple-500',
      action: () => console.log('Deploy function')
    },
    {
      title: 'Setup Database',
      description: 'Multi-tenant Postgres',
      icon: '🗄️',
      gradient: 'from-emerald-500 to-green-500',
      action: () => console.log('Setup database')
    },
    {
      title: 'Configure Auth',
      description: 'Identity & access control',
      icon: '🛡️',
      gradient: 'from-orange-500 to-red-500',
      action: () => console.log('Configure auth')
    },
    {
      title: 'AI Optimization',
      description: 'Neural performance tuning',
      icon: '🧠',
      gradient: 'from-pink-500 to-rose-500',
      action: () => console.log('AI optimization')
    },
    {
      title: 'Security Scan',
      description: 'Quantum-safe analysis',
      icon: '🔒',
      gradient: 'from-indigo-500 to-blue-500',
      action: () => console.log('Security scan')
    }
  ];

  return (
    <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
      <div className="flex flex-col space-y-1.5 p-6">
        <h2 className="text-2xl font-semibold leading-none tracking-tight flex items-center gap-2">
          ⚡ Quick Actions
        </h2>
        <p className="text-sm text-muted-foreground">Get started with ATOM's autonomous features</p>
      </div>
      <div className="p-6 pt-0">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className={`group relative overflow-hidden rounded-lg p-4 text-center transition-all duration-300 hover:scale-105 hover:shadow-lg ${
                action.featured 
                  ? 'bg-gradient-to-br from-teal-500/10 to-violet-500/10 border-2 border-primary/20' 
                  : 'bg-accent/20 hover:bg-accent/40 border border-border/50'
              }`}
            >
              {/* Background gradient on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${action.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
              
              <div className="relative space-y-3">
                <div className={`w-12 h-12 mx-auto rounded-lg bg-gradient-to-br ${action.gradient} flex items-center justify-center text-white text-xl group-hover:scale-110 transition-transform`}>
                  {action.icon}
                </div>
                <div>
                  <h3 className="font-medium text-sm mb-1">{action.title}</h3>
                  <p className="text-xs text-muted-foreground">{action.description}</p>
                </div>
              </div>

              {/* Featured badge */}
              {action.featured && (
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-teal-500 to-violet-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✨</span>
                </div>
              )}
            </button>
          ))}
        </div>

        {/* AI Suggestions */}
        <div className="mt-6 p-4 rounded-lg bg-gradient-to-r from-teal-500/5 to-violet-500/5 border border-primary/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-teal-500 to-violet-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm">🤖</span>
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-sm">AI Recommendation</h4>
              <p className="text-xs text-muted-foreground">
                Based on your usage patterns, I suggest starting with a new project using our e-commerce template.
              </p>
            </div>
            <button className="px-3 py-1 bg-gradient-to-r from-teal-500 to-violet-500 text-white text-xs rounded-full hover:opacity-90 transition-opacity">
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}