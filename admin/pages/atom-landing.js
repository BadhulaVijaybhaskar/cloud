import Head from 'next/head';

export default function AtomLanding() {
  return (
    <>
      <Head>
        <title>ATOM — the Self-Adapting AI Cloud</title>
        <meta name="description" content="Automate workflows, scale vectors, and deploy RAG pipelines with an intelligent, autonomous control plane. ATOM — Adaptive Topology Orchestration Module for AI infrastructure." />
        <meta name="keywords" content="AI cloud, RAG, vector search, orchestration, LangGraph, MLOps, adaptive infrastructure, self-healing cloud, observability, Kubernetes AI" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </Head>
      
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Navigation */}
        <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-200/50">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="3" fill="#1f2937" />
                  <g stroke="rgba(31,41,55,0.7)" strokeWidth="1.5" strokeLinecap="round">
                    <ellipse cx="12" cy="12" rx="8" ry="3" />
                    <ellipse cx="12" cy="12" rx="8" ry="3" transform="rotate(60 12 12)" />
                    <ellipse cx="12" cy="12" rx="8" ry="3" transform="rotate(120 12 12)" />
                  </g>
                </svg>
              </div>
              <div>
                <div className="text-xl font-bold tracking-tight text-gray-900">ATOM</div>
                <div className="text-xs text-gray-500 -mt-1">Orchestration Platform</div>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#architecture" className="text-gray-600 hover:text-gray-900 transition-colors">Architecture</a>
              <a href="#docs" className="text-gray-600 hover:text-gray-900 transition-colors">Docs</a>
              <a href="/dashboard" className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-full font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all">
                Launch Platform
              </a>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="pt-32 pb-20 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="text-center space-y-8">
              <div className="space-y-6">
                <div className="inline-flex items-center space-x-2 bg-blue-100 rounded-full px-4 py-2 text-sm text-blue-800">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Global Cloud • Multi-Region • Auto-Scale</span>
                </div>
                
                <h1 className="text-5xl md:text-7xl font-bold leading-tight text-gray-900">
                  <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                    ATOM
                  </span>
                  <br />
                  <span className="text-gray-700">the self-adapting</span>
                  <br />
                  <span className="text-gray-500 text-3xl md:text-5xl">AI cloud</span>
                </h1>
                
                <p className="text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
                  ATOM — the self-adapting AI cloud. Automate workflows, scale vectors, 
                  and deploy RAG pipelines with an intelligent, autonomous control plane.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="/dashboard" className="group bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl hover:shadow-blue-500/25 transition-all transform hover:scale-105">
                  <span className="flex items-center justify-center space-x-2">
                    <span>Deploy ATOM</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </span>
                </a>
                <a href="#architecture" className="border border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all">
                  View Architecture
                </a>
              </div>

              <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>99.99% Uptime</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span>SOC2 Compliant</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span>Open Source</span>
                </div>
              </div>

              {/* Animated Atom Visualization */}
              <div className="flex justify-center mt-16">
                <div className="relative">
                  <div className="w-[400px] h-[400px] relative">
                    <svg viewBox="0 0 400 400" className="w-full h-full">
                      <defs>
                        <radialGradient id="nucleus" cx="50%" cy="50%" r="50%">
                          <stop offset="0%" stopColor="#3b82f6" />
                          <stop offset="100%" stopColor="#6366f1" />
                        </radialGradient>
                        <linearGradient id="orbit1" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.6" />
                          <stop offset="100%" stopColor="#6366f1" stopOpacity="0.3" />
                        </linearGradient>
                        <linearGradient id="orbit2" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.4" />
                          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.2" />
                        </linearGradient>
                      </defs>
                      
                      <g transform="translate(200,200)">
                        {/* Outer orbit */}
                        <g className="animate-spin" style={{animationDuration: '20s', transformOrigin: 'center'}}>
                          <ellipse rx="150" ry="60" fill="none" stroke="url(#orbit1)" strokeWidth="2" />
                          <circle cx="150" cy="0" r="8" fill="#3b82f6" className="animate-pulse" />
                          <circle cx="-150" cy="0" r="6" fill="#6366f1" className="animate-pulse" />
                        </g>
                        
                        {/* Middle orbit */}
                        <g className="animate-spin" style={{animationDuration: '15s', transformOrigin: 'center'}} transform="rotate(60)">
                          <ellipse rx="120" ry="45" fill="none" stroke="url(#orbit2)" strokeWidth="2" />
                          <circle cx="120" cy="0" r="7" fill="#8b5cf6" className="animate-pulse" />
                          <circle cx="-120" cy="0" r="5" fill="#3b82f6" className="animate-pulse" />
                        </g>
                        
                        {/* Inner orbit */}
                        <g className="animate-spin" style={{animationDuration: '10s', transformOrigin: 'center'}} transform="rotate(120)">
                          <ellipse rx="90" ry="30" fill="none" stroke="url(#orbit1)" strokeWidth="1.5" />
                          <circle cx="90" cy="0" r="6" fill="#6366f1" className="animate-pulse" />
                          <circle cx="-90" cy="0" r="4" fill="#8b5cf6" className="animate-pulse" />
                        </g>
                        
                        {/* Nucleus */}
                        <circle r="20" fill="url(#nucleus)" className="animate-pulse" />
                        <circle r="12" fill="white" opacity="0.9" className="animate-pulse" />
                        <circle r="6" fill="url(#nucleus)" />
                      </g>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section id="features" className="py-20 px-6 bg-white/50">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4 text-gray-900">Core Modules</h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Built on open-source foundations, ATOM combines LangGraph orchestration, 
                Vector Engine, Vault security, and Observability — all managed under a single, autonomous control layer.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {[
                {
                  icon: "🧩",
                  title: "Adaptive Orchestration",
                  description: "Self-adjusting topology and autoscaling for compute, vector, and AI tasks"
                },
                {
                  icon: "🧠",
                  title: "AI-Integrated Workflows",
                  description: "Natively integrates LangGraph for RAG and LLM pipelines"
                },
                {
                  icon: "🔐",
                  title: "Security by Design",
                  description: "Vault-based secret management, signed containers, and RBAC"
                },
                {
                  icon: "📊",
                  title: "Built-in Observability",
                  description: "Prometheus, Grafana, Loki integrated for metrics and tracing"
                }
              ].map((feature, index) => (
                <div key={index} className="group p-8 bg-white rounded-2xl border border-gray-200 hover:shadow-xl transition-all hover:scale-105">
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-semibold mb-3 text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl p-12 border border-blue-200">
              <h2 className="text-4xl font-bold mb-6 text-gray-900">
                Deploy ATOM in your environment in minutes
              </h2>
              <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                ATOM turns infrastructure into intelligence — a self-driving AI cloud 
                that runs, scales, and heals itself while you focus on building.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="/dashboard" className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl hover:shadow-blue-500/25 transition-all">
                  Start Free Trial
                </a>
                <a href="#docs" className="border border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all">
                  Enterprise Demo
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 px-6 border-t border-gray-200 bg-white/50">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="3" fill="#1f2937" />
                <g stroke="rgba(31,41,55,0.7)" strokeWidth="1.5" strokeLinecap="round">
                  <ellipse cx="12" cy="12" rx="8" ry="3" />
                  <ellipse cx="12" cy="12" rx="8" ry="3" transform="rotate(60 12 12)" />
                  <ellipse cx="12" cy="12" rx="8" ry="3" transform="rotate(120 12 12)" />
                </g>
              </svg>
              <div>
                <div className="font-bold text-gray-900">ATOM</div>
                <div className="text-xs text-gray-500">Orchestration Platform</div>
              </div>
            </div>
            <div className="text-gray-500 text-sm">
              © 2025 ATOM — The Self-Adapting AI Cloud.
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}