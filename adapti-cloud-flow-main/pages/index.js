import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>Adapti Cloud Flow - AI Infrastructure Platform</title>
        <meta name="description" content="Modern cloud infrastructure platform with adaptive workflows and intelligent automation" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </Head>
      
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 font-['Inter']">
        {/* Navigation */}
        <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-200/50">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <div>
                <div className="text-xl font-bold tracking-tight text-gray-900">Adapti Flow</div>
                <div className="text-xs text-gray-500 -mt-1">Cloud Platform</div>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#platform" className="text-gray-600 hover:text-gray-900 transition-colors">Platform</a>
              <a href="#docs" className="text-gray-600 hover:text-gray-900 transition-colors">Docs</a>
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-full font-medium hover:shadow-lg transition-all">
                Get Started
              </button>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="pt-32 pb-20 px-6">
          <div className="max-w-7xl mx-auto text-center">
            <div className="space-y-8">
              <div className="inline-flex items-center space-x-2 bg-blue-100 rounded-full px-4 py-2 text-sm text-blue-800">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Next-Gen Cloud • Adaptive • Intelligent</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold leading-tight text-gray-900">
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  Adapti Flow
                </span>
                <br />
                <span className="text-gray-700">intelligent cloud</span>
                <br />
                <span className="text-gray-500 text-3xl md:text-5xl">infrastructure</span>
              </h1>
              
              <p className="text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
                Build, deploy, and scale modern applications with our adaptive cloud platform. 
                Intelligent automation meets enterprise-grade infrastructure.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="group bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl hover:shadow-blue-500/25 transition-all transform hover:scale-105">
                  <span className="flex items-center justify-center space-x-2">
                    <span>Start Building</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </span>
                </button>
                <button className="border border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all">
                  View Platform
                </button>
              </div>

              {/* Floating Cards Animation */}
              <div className="relative mt-16 h-96">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="grid grid-cols-3 gap-8 opacity-20">
                    {[...Array(9)].map((_, i) => (
                      <div key={i} className={`w-16 h-16 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-lg animate-pulse`} 
                           style={{animationDelay: `${i * 0.2}s`}}></div>
                    ))}
                  </div>
                </div>
                
                {/* Central Flow Visualization */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative">
                    <div className="w-32 h-32 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center animate-pulse">
                      <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    
                    {/* Orbiting Elements */}
                    <div className="absolute inset-0 animate-spin" style={{animationDuration: '20s'}}>
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-blue-400 rounded-full"></div>
                      <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-indigo-400 rounded-full"></div>
                      <div className="absolute top-1/2 -left-8 transform -translate-y-1/2 w-4 h-4 bg-purple-400 rounded-full"></div>
                      <div className="absolute top-1/2 -right-8 transform -translate-y-1/2 w-4 h-4 bg-cyan-400 rounded-full"></div>
                    </div>
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
              <h2 className="text-4xl font-bold mb-4 text-gray-900">Platform Features</h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Everything you need to build, deploy, and scale modern cloud applications 
                with intelligent automation and enterprise-grade reliability.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: "⚡",
                  title: "Instant Deploy",
                  description: "Deploy applications in seconds with our optimized build pipeline"
                },
                {
                  icon: "🔄",
                  title: "Auto Scaling",
                  description: "Intelligent scaling based on traffic patterns and resource usage"
                },
                {
                  icon: "🛡️",
                  title: "Enterprise Security",
                  description: "Built-in security with encryption, compliance, and access controls"
                },
                {
                  icon: "📊",
                  title: "Real-time Analytics",
                  description: "Monitor performance, usage, and costs with detailed insights"
                },
                {
                  icon: "🌐",
                  title: "Global CDN",
                  description: "Worldwide content delivery for optimal user experience"
                },
                {
                  icon: "🔧",
                  title: "DevOps Tools",
                  description: "Integrated CI/CD, monitoring, and collaboration tools"
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
                Ready to build the future?
              </h2>
              <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                Join thousands of developers building next-generation applications 
                with Adapti Flow's intelligent cloud platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl hover:shadow-blue-500/25 transition-all">
                  Start Free Trial
                </button>
                <button className="border border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all">
                  View Documentation
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 px-6 border-t border-gray-200 bg-white/50">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <div>
                <div className="font-bold text-gray-900">Adapti Flow</div>
                <div className="text-xs text-gray-500">Cloud Platform</div>
              </div>
            </div>
            <div className="text-gray-500 text-sm">
              © 2025 Adapti Flow — Intelligent Cloud Infrastructure.
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}