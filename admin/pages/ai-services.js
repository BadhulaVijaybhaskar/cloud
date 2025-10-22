import { useState } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Card from '../components/Card';

export default function AIServices() {
  const [models] = useState([
    { name: 'text-embedding-ada-002', provider: 'OpenAI', tokens: 2456789, cost: '$24.57', status: 'active' },
    { name: 'all-MiniLM-L6-v2', provider: 'HuggingFace', tokens: 1234567, cost: '$0.00', status: 'active' },
    { name: 'gpt-4-turbo', provider: 'OpenAI', tokens: 89012, cost: '$89.01', status: 'active' }
  ]);

  const [pipelines] = useState([
    { name: 'content-embeddings', status: 'running', processed: 12456, errors: 3, lastRun: '2024-01-20T10:30:00Z' },
    { name: 'user-classification', status: 'completed', processed: 8901, errors: 0, lastRun: '2024-01-20T09:15:00Z' },
    { name: 'document-analysis', status: 'failed', processed: 234, errors: 12, lastRun: '2024-01-20T08:45:00Z' }
  ]);

  return (
    <Layout title="AI Services">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">🧠 AI Services</h1>
            <p className="text-gray-600">Manage embeddings, orchestration, and AI model integrations</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="secondary" size="sm">📊 Usage Analytics</Button>
            <Button size="sm">+ New Pipeline</Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Total Embeddings</p>
              <p className="text-2xl font-bold">2.4M</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Active Models</p>
              <p className="text-2xl font-bold">{models.length}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Monthly Cost</p>
              <p className="text-2xl font-bold">$113.58</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Pipelines</p>
              <p className="text-2xl font-bold">{pipelines.length}</p>
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button className="py-2 px-1 border-b-2 border-purple-500 font-medium text-sm text-purple-600">
              Embeddings Dashboard
            </button>
            <button className="py-2 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700">
              Orchestration Monitor
            </button>
            <button className="py-2 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700">
              Vector Inspector
            </button>
            <button className="py-2 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700">
              Prompt Templates
            </button>
          </nav>
        </div>

        {/* Models Overview */}
        <Card title="🤖 Model Usage & Token Consumption">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tokens Used</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost (30d)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {models.map((model) => (
                  <tr key={model.name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                          <span className="text-purple-600 text-sm">🧠</span>
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">{model.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        model.provider === 'OpenAI' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {model.provider}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {model.tokens.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.cost}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                        {model.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-800">Configure</button>
                        <button className="text-gray-600 hover:text-gray-800">Analytics</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* AI Pipelines */}
        <Card title="🔄 AI Pipeline Status">
          <div className="space-y-4">
            {pipelines.map((pipeline) => (
              <div key={pipeline.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${
                    pipeline.status === 'running' ? 'bg-green-500 animate-pulse' :
                    pipeline.status === 'completed' ? 'bg-blue-500' :
                    'bg-red-500'
                  }`}></div>
                  <div>
                    <h3 className="font-medium text-gray-900">{pipeline.name}</h3>
                    <p className="text-sm text-gray-500">
                      Processed: {pipeline.processed.toLocaleString()} • Errors: {pipeline.errors} • 
                      Last run: {new Date(pipeline.lastRun).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    pipeline.status === 'running' ? 'bg-green-100 text-green-800' :
                    pipeline.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {pipeline.status}
                  </span>
                  <Button size="sm" variant="secondary">View Details</Button>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Vector Index Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="📊 Vector Index Coverage">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Embeddings Coverage</span>
                <span className="text-sm text-gray-500">94.2%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '94.2%' }}></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Index Freshness</span>
                <span className="text-sm text-gray-500">2 hours ago</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '78%' }}></div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Drift Detection</span>
                <span className="text-sm text-green-600">Normal</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '92%' }}></div>
              </div>
            </div>
          </Card>

          <Card title="🎯 Prompt Templates">
            <div className="space-y-3">
              {[
                { name: 'Content Summarization', usage: 234, category: 'Text Processing' },
                { name: 'User Intent Classification', usage: 156, category: 'Analysis' },
                { name: 'Document Q&A', usage: 89, category: 'Retrieval' },
                { name: 'Code Generation', usage: 67, category: 'Development' }
              ].map((template) => (
                <div key={template.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-sm text-gray-900">{template.name}</div>
                    <div className="text-xs text-gray-500">{template.category} • {template.usage} uses</div>
                  </div>
                  <Button size="sm" variant="secondary">Edit</Button>
                </div>
              ))}
            </div>
            <Button className="w-full mt-4" size="sm" variant="secondary">+ New Template</Button>
          </Card>
        </div>
      </div>
    </Layout>
  );
}