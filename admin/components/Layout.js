import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: '📊' },
  { name: 'Database', href: '/database', icon: '🗄️' },
  { name: 'Auth', href: '/auth', icon: '👥' },
  { name: 'Storage', href: '/storage', icon: '📦' },
  { name: 'Functions', href: '/functions', icon: '⚡' },
  { name: 'Realtime', href: '/realtime', icon: '💬' },
  { name: 'AI Services', href: '/ai-services', icon: '🧠' },
  { name: 'Analytics', href: '/reports', icon: '📈' },
  { name: 'Logs', href: '/logs', icon: '📄' },
  { name: 'Marketplace', href: '/marketplace', icon: '🧩' },
];

export default function Layout({ children, title }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const router = useRouter();

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="fixed left-0 top-0 h-full w-64 bg-card border-r border-border">
            <SidebarContent collapsed={false} />
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className={`hidden lg:fixed lg:inset-y-0 lg:flex lg:flex-col transition-all duration-300 ${sidebarCollapsed ? 'lg:w-16' : 'lg:w-64'}`}>
        <div className="flex flex-col flex-grow bg-card border-r border-border">
          <SidebarContent collapsed={sidebarCollapsed} />
        </div>
      </div>

      {/* Main content */}
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'lg:pl-16' : 'lg:pl-64'}`}>
        {/* Top navigation */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 bg-card/95 backdrop-blur-sm px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            className="lg:hidden inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10"
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="relative flex flex-1 items-center">
              <div className="pointer-events-none absolute left-3 text-muted-foreground">🔍</div>
              <input
                className="block h-full w-full border-0 bg-transparent py-0 pl-10 pr-0 text-foreground placeholder:text-muted-foreground focus:ring-0 sm:text-sm"
                placeholder="Search..."
                type="search"
              />
            </div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <button className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10">
                🔔
              </button>
              <button className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10">
                👤
              </button>
            </div>
          </div>
        </div>

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
            <img 
              src="/atom-favicon.svg" 
              alt="ATOM" 
              className={`transition-all duration-300 ${collapsed ? 'w-8 h-8' : 'w-12 h-12'}`} 
            />
            {!collapsed && (
              <h1 className="text-4xl font-bold bg-gradient-to-r from-teal-500 via-primary to-violet-500 bg-clip-text text-transparent">
                ATOM
              </h1>
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
                    className={`group flex gap-x-3 rounded-md p-3 text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-teal-500/10 to-violet-500/10 text-primary border border-primary/20'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                    } ${collapsed ? 'justify-center' : ''}`}
                    title={collapsed ? item.name : ''}
                  >
                    <span className="text-lg">{item.icon}</span>
                    {!collapsed && <span>{item.name}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Status indicator */}
        {!collapsed && (
          <div className="px-6 py-4 border-t border-border">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-xs text-muted-foreground">All systems operational</span>
            </div>
          </div>
        )}
      </>
    );
  }
}