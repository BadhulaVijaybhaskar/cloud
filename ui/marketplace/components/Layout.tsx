import Head from 'next/head'
import { useRouter } from 'next/router'
import { useTheme } from '../hooks/useTheme'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

export default function Layout({ children, title = 'ATOM Marketplace' }: LayoutProps) {
  const router = useRouter()
  const { theme, toggleTheme } = useTheme()

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="ATOM AI Marketplace - Discover and deploy AI models and agents" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/atom-favicon.svg" />
      </Head>

      <div className="min-h-screen neural-background">
        {/* Navigation */}
        <nav className="quantum-card border-b border-border/50 sticky top-0 z-40 backdrop-blur-lg">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-8">
                <button 
                  onClick={() => router.push('/')}
                  className="flex items-center gap-3"
                >
                  <div className="relative">
                    <img src="/atom-favicon.svg" alt="ATOM" className="w-8 h-8" />
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold bg-gradient-to-r from-teal-500 via-primary to-violet-500 bg-clip-text text-transparent">
                      ATOM
                    </h1>
                  </div>
                </button>
                
                <div className="hidden md:flex items-center gap-6">
                  <button 
                    onClick={() => router.push('/')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      router.pathname === '/' ? 'bg-primary/10 text-primary' : 'hover:bg-accent'
                    }`}
                  >
                    Browse
                  </button>
                  <button 
                    onClick={() => router.push('/publish')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      router.pathname === '/publish' ? 'bg-primary/10 text-primary' : 'hover:bg-accent'
                    }`}
                  >
                    Publish
                  </button>
                  <button 
                    onClick={() => router.push('/vendor')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      router.pathname === '/vendor' ? 'bg-primary/10 text-primary' : 'hover:bg-accent'
                    }`}
                  >
                    Dashboard
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <button
                  onClick={toggleTheme}
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-10 w-10"
                  title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                >
                  {theme === 'dark' ? '☀️' : '🌙'}
                </button>
                <button className="quantum-card px-4 py-2 rounded-lg text-sm font-medium hover:bg-accent">
                  Sign In
                </button>
                <button className="atom-gradient text-white px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90">
                  Get Started
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main>{children}</main>

        {/* Footer */}
        <footer className="border-t border-border/50 mt-16">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 bg-gradient-to-br from-teal-500 to-violet-500 rounded flex items-center justify-center text-white text-xs font-bold">
                  A
                </div>
                <span className="text-sm text-muted-foreground">© 2024 ATOM Marketplace</span>
              </div>
              <div className="flex items-center gap-6 text-sm text-muted-foreground">
                <button className="hover:text-foreground">Privacy</button>
                <button className="hover:text-foreground">Terms</button>
                <button className="hover:text-foreground">Support</button>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}