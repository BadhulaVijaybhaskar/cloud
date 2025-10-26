import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const navigation = [
  { name: 'Launchpad', href: '/', icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2z M3 7l9 6 9-6', description: 'AI-powered dashboard' },
  { name: 'Data Studio', href: '/data-studio', icon: 'M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4', description: 'Visual database editor' },
  { name: 'Auth Studio', href: '/auth-studio', icon: 'M12 15v2a3 3 0 11-6 0v-2c0-1.657.895-3 2-3s2 1.343 2 3z M16 12a4 4 0 10-8 0 4 4 0 008 0z', description: 'Identity & access control' },
  { name: 'Edge Runtime', href: '/edge-runtime', icon: 'M13 10V3L4 14h7v7l9-11h-7z', description: 'Serverless functions' },
  { name: 'Neural Ops', href: '/neural-ops', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z', description: 'AI operations center' },
  { name: 'Security Fabric', href: '/security', icon: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z', description: 'Zero-trust security' },
  { name: 'Analytics', href: '/analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', description: 'Real-time insights' },
  { name: 'Marketplace', href: '/marketplace', icon: 'M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4', description: 'Extensions & integrations' },
];

const aiFeatures = [
  { name: 'Neural Assistant', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z', status: 'active' },
  { name: 'Auto Scaling', icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', status: 'active' },
  { name: 'Threat Detection', icon: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z', status: 'active' },
  { name: 'Performance AI', icon: 'M13 10V3L4 14h7v7l9-11h-7z', status: 'learning' },
];

export default function LaunchpadLayout({ children, title }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [aiPanelOpen, setAiPanelOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [showSearchHelp, setShowSearchHelp] = useState(false);
  const [theme, setTheme] = useState('dark');
  const router = useRouter();

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.classList.toggle('dark', savedTheme === 'dark');
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="fixed left-0 top-0 h-full w-80 bg-card border-r border-border">
            <SidebarContent collapsed={false} />
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className={`hidden lg:fixed lg:inset-y-0 lg:flex lg:flex-col transition-all duration-300 ${sidebarCollapsed ? 'lg:w-20' : 'lg:w-80'}`}>
        <div className="flex flex-col flex-grow bg-card/95 backdrop-blur-sm border-r border-border/50">
          <SidebarContent collapsed={sidebarCollapsed} />
        </div>
      </div>

      {/* Main content */}
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-80'}`}>
        {/* Top navigation */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 bg-card/95 backdrop-blur-sm px-2 shadow-sm border-b border-border/50 sm:gap-x-6 sm:px-2 lg:px-2">
          <button
            className="lg:hidden inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10"
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="relative flex flex-1 items-center max-w-md">
              <div className="pointer-events-none absolute left-3 text-muted-foreground">🔍</div>
              <input
                className="block h-full w-full border border-border/50 bg-background/50 backdrop-blur-sm rounded-lg py-0 pl-10 pr-4 text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/20 focus:border-primary sm:text-sm"
                placeholder="Ask ATOM AI anything..."
                type="search"
                onFocus={() => {
                  setSearchFocused(true);
                  setShowSearchHelp(true);
                }}
                onBlur={() => {
                  setSearchFocused(false);
                  setTimeout(() => setShowSearchHelp(false), 200);
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    console.log('AI Command:', e.target.value);
                    setShowSearchHelp(false);
                  }
                }}
              />
              <div className="absolute right-3 text-xs text-muted-foreground">⌘K</div>
              
              {/* Search Help Dropdown */}
              {showSearchHelp && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-card/95 backdrop-blur-sm border border-border/50 rounded-lg shadow-xl z-50 p-4">
                  <div className="text-sm font-medium mb-3 flex items-center gap-2">
                    🤖 Try asking ATOM AI:
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer p-1 rounded hover:bg-accent/20">
                      <span>💡</span>
                      <span>"Show me active users"</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer p-1 rounded hover:bg-accent/20">
                      <span>⚡</span>
                      <span>"Optimize my database"</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer p-1 rounded hover:bg-accent/20">
                      <span>🛡️</span>
                      <span>"Check security status"</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer p-1 rounded hover:bg-accent/20">
                      <span>📊</span>
                      <span>"Go to analytics"</span>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-border/30 text-xs text-muted-foreground">
                    Press <kbd className="px-1 py-0.5 bg-accent rounded text-xs">Enter</kbd> to execute • <kbd className="px-1 py-0.5 bg-accent rounded text-xs">⌘K</kbd> for shortcuts
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-x-4 lg:gap-x-6 ml-auto">
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10"
                title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              >
                {theme === 'dark' ? '☀️' : '🌙'}
              </button>
              
              {/* AI Status */}
              <button 
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-teal-500/10 to-violet-500/10 border border-primary/20 hover:bg-gradient-to-r hover:from-teal-500/20 hover:to-violet-500/20 transition-all"
                onClick={() => setAiPanelOpen(!aiPanelOpen)}
              >
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium">AI Active</span>
              </button>
              
              <button className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10 relative">
                🔔
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              </button>
              
              <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/50 transition-colors cursor-pointer">
                <div className="w-8 h-8 bg-gradient-to-r from-teal-500 to-violet-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  A
                </div>
                <div className="hidden sm:block text-right">
                  <div className="text-sm font-medium">Admin User</div>
                  <div className="text-xs text-muted-foreground">Workspace Owner</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Panel */}
        {aiPanelOpen && (
          <div className="fixed top-16 right-4 w-80 bg-card/95 backdrop-blur-sm border border-border/50 rounded-lg shadow-xl z-50 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2">
                🤖 ATOM AI Status
              </h3>
              <button onClick={() => setAiPanelOpen(false)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>
            <div className="space-y-3">
              {aiFeatures.map((feature) => (
                <div key={feature.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={feature.icon} />
                    </svg>
                    <span className="text-sm">{feature.name}</span>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded-full ${
                    feature.status === 'active' 
                      ? 'bg-emerald-500/20 text-emerald-600' 
                      : 'bg-amber-500/20 text-amber-600'
                  }`}>
                    {feature.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Page content */}
        <main>{children}</main>
      </div>
    </div>
  );

  function SidebarContent({ collapsed }) {
    return (
      <>
        {/* Logo */}
        <div className={`flex shrink-0 items-center transition-all duration-300 ${collapsed ? 'h-16 px-2 justify-center' : 'h-20 px-6'}`}>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="flex items-center gap-4 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="relative">
              <img 
                src="/atom-favicon.svg" 
                alt="ATOM" 
                className={`transition-all duration-300 ${collapsed ? 'w-8 h-8' : 'w-12 h-12'}`} 
              />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-teal-500 via-primary to-violet-500 bg-clip-text text-transparent">
                  ATOM
                </h1>
                <p className="text-xs text-muted-foreground">Neural Cloud Platform</p>
              </div>
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-1 flex-col px-4 py-6">
          <ul role="list" className="flex flex-1 flex-col gap-y-2">
            {navigation.map((item) => {
              const isActive = router.pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={`group flex gap-x-3 rounded-lg p-3 text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-teal-500/10 to-violet-500/10 text-primary border border-primary/20 shadow-sm'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                    } ${collapsed ? 'justify-center' : ''}`}
                    title={collapsed ? `${item.name} - ${item.description}` : ''}
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                    {!collapsed && (
                      <div className="flex-1">
                        <div>{item.name}</div>
                        <div className="text-xs text-muted-foreground">{item.description}</div>
                      </div>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>

          {/* AI Features Section */}
          {!collapsed && (
            <div className="mt-8 pt-6 border-t border-border/50">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                Neural Features
              </h4>
              <div className="space-y-2">
                {aiFeatures.map((feature) => (
                  <div key={feature.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={feature.icon} />
                      </svg>
                      <span className="text-xs">{feature.name}</span>
                    </div>
                    <div className={`w-2 h-2 rounded-full ${
                      feature.status === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500 animate-pulse'
                    }`} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </nav>

        {/* Status indicator */}
        <div className={`px-4 py-4 border-t border-border/50 ${collapsed ? 'text-center' : ''}`}>
          {collapsed ? (
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse mx-auto" />
          ) : (
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-xs text-muted-foreground">Neural network active</span>
              </div>
              <div className="text-xs text-muted-foreground">
                99.7% uptime • Quantum-safe • AI-optimized
              </div>
            </div>
          )}
        </div>
      </>
    );
  }
}