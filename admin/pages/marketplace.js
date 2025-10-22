import { useState } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Card from '../components/Card';

export default function Marketplace() {
  const [activeTab, setActiveTab] = useState('browse');
  const [plugins] = useState([
    { 
      name: 'Stripe Payment Gateway', 
      category: 'Payments', 
      rating: 4.8, 
      downloads: 12456, 
      price: 'Free', 
      author: 'Naksha Team',
      description: 'Complete Stripe integration with webhooks and subscription management',
      installed: false
    },
    { 
      name: 'SendGrid Email Service', 
      category: 'Communication', 
      rating: 4.6, 
      downloads: 8901, 
      price: '$9.99/mo', 
      author: 'SendGrid Inc',
      description: 'Professional email delivery with templates and analytics',
      installed: true
    },
    { 
      name: 'Slack Notifications', 
      category: 'Integrations', 
      rating: 4.9, 
      downloads: 15678, 
      price: 'Free', 
      author: 'Community',
      description: 'Send real-time notifications to Slack channels',
      installed: false
    },
    { 
      name: 'OpenAI GPT Integration', 
      category: 'AI/ML', 
      rating: 4.7, 
      downloads: 23456, 
      price: '$19.99/mo', 
      author: 'AI Labs',
      description: 'Complete OpenAI API integration with prompt management',
      installed: true
    }
  ]);

  const categories = [
    { name: 'All', count: plugins.length },
    { name: 'AI/ML', count: 1 },
    { name: 'Payments', count: 1 },
    { name: 'Communication', count: 1 },
    { name: 'Integrations', count: 1 },
    { name: 'Analytics', count: 0 },
    { name: 'Security', count: 0 }
  ];

  return (
    <Layout title="Marketplace">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">🧩 Marketplace</h1>
            <p className="text-gray-600">Discover and install plugins to extend your project</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="secondary" size="sm">📦 My Plugins</Button>
            <Button size="sm">🚀 Publish Plugin</Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Available Plugins</p>
              <p className="text-2xl font-bold">{plugins.length}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Installed</p>
              <p className="text-2xl font-bold">{plugins.filter(p => p.installed).length}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Categories</p>
              <p className="text-2xl font-bold">{categories.length - 1}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Total Downloads</p>
              <p className="text-2xl font-bold">60K+</p>
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('browse')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'browse'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Browse Plugins
            </button>
            <button
              onClick={() => setActiveTab('installed')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'installed'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Installed ({plugins.filter(p => p.installed).length})
            </button>
            <button
              onClick={() => setActiveTab('develop')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'develop'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Developer Tools
            </button>
          </nav>
        </div>

        {activeTab === 'browse' && (
          <div className="flex space-x-6">
            {/* Categories Sidebar */}
            <div className="w-64 space-y-2">
              <h3 className="font-medium text-gray-900 mb-3">Categories</h3>
              {categories.map((category) => (
                <button
                  key={category.name}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg flex items-center justify-between"
                >
                  <span>{category.name}</span>
                  <span className="text-xs text-gray-500">({category.count})</span>
                </button>
              ))}
            </div>

            {/* Plugins Grid */}
            <div className="flex-1">
              <div className="mb-4 flex items-center justify-between">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search plugins..."
                    className="w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <svg className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <select className="border border-gray-300 rounded px-3 py-2 text-sm">
                  <option>Sort by: Popular</option>
                  <option>Sort by: Newest</option>
                  <option>Sort by: Rating</option>
                  <option>Sort by: Price</option>
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {plugins.map((plugin) => (
                  <Card key={plugin.name} className="hover:shadow-md transition-shadow">
                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold text-gray-900">{plugin.name}</h3>
                            {plugin.installed && (
                              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                                Installed
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{plugin.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>by {plugin.author}</span>
                            <span>•</span>
                            <span>{plugin.downloads.toLocaleString()} downloads</span>
                          </div>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          plugin.category === 'AI/ML' ? 'bg-purple-100 text-purple-800' :
                          plugin.category === 'Payments' ? 'bg-green-100 text-green-800' :
                          plugin.category === 'Communication' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {plugin.category}
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-1">
                            <div className="flex text-yellow-400">
                              {[...Array(5)].map((_, i) => (
                                <svg key={i} className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                              ))}
                            </div>
                            <span className="text-sm text-gray-600">{plugin.rating}</span>
                          </div>
                          <span className="text-sm font-medium text-gray-900">{plugin.price}</span>
                        </div>
                        
                        <div className="flex space-x-2">
                          {plugin.installed ? (
                            <>
                              <Button size="sm" variant="secondary">Configure</Button>
                              <Button size="sm" variant="danger">Uninstall</Button>
                            </>
                          ) : (
                            <>
                              <Button size="sm" variant="secondary">Details</Button>
                              <Button size="sm">Install</Button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'installed' && (
          <Card>
            <div className="space-y-4">
              {plugins.filter(p => p.installed).map((plugin) => (
                <div key={plugin.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-blue-600 text-lg">🔌</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{plugin.name}</h3>
                      <p className="text-sm text-gray-500">{plugin.description}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          Active
                        </span>
                        <span className="text-xs text-gray-500">Version 1.2.3</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button size="sm" variant="secondary">Settings</Button>
                    <Button size="sm" variant="secondary">Update</Button>
                    <Button size="sm" variant="danger">Remove</Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {activeTab === 'develop' && (
          <div className="space-y-6">
            <Card title="🛠️ Plugin Development Kit">
              <div className="space-y-4">
                <p className="text-gray-600">
                  Build and publish your own plugins for the Naksha Cloud marketplace
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">📚 Documentation</h4>
                    <p className="text-sm text-gray-600 mb-3">Complete API reference and guides</p>
                    <Button size="sm" variant="secondary">View Docs</Button>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">🏗️ CLI Tools</h4>
                    <p className="text-sm text-gray-600 mb-3">Command line tools for development</p>
                    <Button size="sm" variant="secondary">Download CLI</Button>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">🎯 Templates</h4>
                    <p className="text-sm text-gray-600 mb-3">Starter templates for common plugins</p>
                    <Button size="sm" variant="secondary">Browse Templates</Button>
                  </div>
                </div>
              </div>
            </Card>

            <Card title="📊 Publisher Analytics">
              <div className="text-center py-8">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No published plugins</h3>
                <p className="mt-1 text-sm text-gray-500">Start building your first plugin to see analytics here</p>
                <Button className="mt-4">Create First Plugin</Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </Layout>
  );
}