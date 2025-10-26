export default function ProjectCard({ project }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'autonomous': return 'from-emerald-500 to-green-500';
      case 'learning': return 'from-violet-500 to-purple-500';
      case 'optimizing': return 'from-amber-500 to-orange-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'autonomous': return '🤖';
      case 'learning': return '🧠';
      case 'optimizing': return '⚡';
      default: return '⏸️';
    }
  };

  return (
    <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm hover:shadow-lg transition-all duration-300 group overflow-hidden">
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2 group-hover:text-primary transition-colors">
              {project.name}
            </h3>
            <div className="flex items-center gap-2 mb-3">
              <div className={`px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getStatusColor(project.status)} text-white flex items-center gap-1`}>
                <span>{getStatusIcon(project.status)}</span>
                <span className="capitalize">{project.status}</span>
              </div>
              {project.aiOptimized && (
                <div className="px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-teal-500/20 to-violet-500/20 text-primary border border-primary/20">
                  🧠 AI Optimized
                </div>
              )}
            </div>
          </div>
          <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-accent rounded-lg">
            ⚙️
          </button>
        </div>
      </div>

      {/* Metrics */}
      <div className="px-6 pb-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="text-2xl font-bold text-emerald-500">{project.performance}%</div>
            <div className="text-xs text-muted-foreground">Performance</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-violet-500">{project.securityScore}%</div>
            <div className="text-xs text-muted-foreground">Security Score</div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Users</span>
            <span className="font-medium">{project.users.toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Requests</span>
            <span className="font-medium">{project.requests}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Auto Scaling</span>
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${project.autoScaling ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'}`} />
              <span className="text-xs">{project.autoScaling ? 'Active' : 'Disabled'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Bar */}
      <div className="px-6 pb-4">
        <div className="flex justify-between text-xs mb-2">
          <span className="text-muted-foreground">Overall Health</span>
          <span className="font-medium">{project.performance}%</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div 
            className={`bg-gradient-to-r ${getStatusColor(project.status)} h-2 rounded-full transition-all duration-500`}
            style={{ width: `${project.performance}%` }}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 bg-accent/20 border-t border-border/50">
        <div className="flex items-center justify-between">
          <div className="text-xs text-muted-foreground">
            Last optimized: {project.lastOptimized}
          </div>
          <div className="flex items-center gap-2">
            <button className="text-xs text-primary hover:text-primary/80 font-medium">
              View Details
            </button>
            <span className="text-muted-foreground">→</span>
          </div>
        </div>
      </div>

      {/* AI Optimization Indicator */}
      {project.status === 'learning' && (
        <div className="absolute top-2 right-2">
          <div className="w-3 h-3 bg-gradient-to-r from-violet-500 to-purple-500 rounded-full animate-pulse" />
        </div>
      )}
    </div>
  );
}