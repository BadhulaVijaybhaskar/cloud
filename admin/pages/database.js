import { useState } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';

export default function Database() {
  const [activeTab, setActiveTab] = useState('tables');
  const [tables] = useState([
    { name: 'users', rows: 1247, size: '2.4 MB', type: 'table' },
    { name: 'posts', rows: 3421, size: '5.1 MB', type: 'table' },
    { name: 'embeddings', rows: 8932, size: '45.2 MB', type: 'vector' },
    { name: 'user_stats', rows: 1247, size: '890 KB', type: 'view' }
  ]);

  const tabs = [
    { id: 'tables', name: 'Tables', count: tables.filter(t => t.type === 'table').length },
    { id: 'views', name: 'Views', count: tables.filter(t => t.type === 'view').length },
    { id: 'vectors', name: 'Vector Indexes', count: tables.filter(t => t.type === 'vector').length },
    { id: 'functions', name: 'Functions', count: 12 },
    { id: 'triggers', name: 'Triggers', count: 5 }
  ];

  return (
    <Layout title="Database">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Schema Designer</h2>
              <Button size="sm">🧠 AI Assistant</Button>
            </div>
            
            {/* Engine Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Database Engine</label>
              <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
                <option>PostgreSQL (Primary)</option>
                <option>SQLite (Local)</option>
                <option>DuckDB (Analytics)</option>
                <option>VectorDB (Embeddings)</option>
              </select>
            </div>

            {/* Tabs */}
            <div className="flex flex-wrap gap-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1 text-xs font-medium rounded ${
                    activeTab === tab.id
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {tab.name} ({tab.count})
                </button>
              ))}
            </div>
          </div>
          
          {/* Tables List */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {tables.filter(t => activeTab === 'tables' ? t.type === 'table' : activeTab === 'vectors' ? t.type === 'vector' : activeTab === 'views' ? t.type === 'view' : true).map((table) => (
                <div key={table.name} className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${table.type === 'vector' ? 'bg-purple-500' : table.type === 'view' ? 'bg-blue-500' : 'bg-green-500'}`}></div>
                    <span className="font-medium text-sm">{table.name}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1 ml-4">
                    {table.rows.toLocaleString()} rows • {table.size}
                  </div>
                </div>
              ))}
            </div>
            
            <Button className="w-full mt-4" size="sm">
              + Create {activeTab === 'tables' ? 'Table' : activeTab === 'vectors' ? 'Vector Index' : 'View'}
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold text-gray-900">users</h1>
                <p className="text-sm text-gray-500">PostgreSQL table • 1,247 rows • 2.4 MB</p>
              </div>
              <div className="flex space-x-3">
                <Button variant="secondary" size="sm">🔍 Query</Button>
                <Button variant="secondary" size="sm">📊 Analytics</Button>
                <Button size="sm">✏️ Edit Schema</Button>
              </div>
            </div>
          </div>

          {/* Content Tabs */}
          <div className="bg-white border-b border-gray-200">
            <div className="flex">
              <button className="px-4 py-2 text-sm font-medium text-green-600 border-b-2 border-green-600">
                Data
              </button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700">
                Schema
              </button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700">
                Indexes
              </button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700">
                Policies (RLS)
              </button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700">
                Relationships
              </button>
            </div>
          </div>

          {/* AI Suggestions Bar */}
          <div className="bg-blue-50 border-b border-blue-200 p-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600">🧠</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900">AI Suggestions</p>
                <p className="text-xs text-blue-700">Add UUID primary key • Create email unique index • Generate RLS policy for user isolation</p>
              </div>
              <Button size="sm" variant="secondary">Apply All</Button>
            </div>
          </div>

          {/* Data Grid */}
          <div className="flex-1 bg-gray-50 p-6">
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        id <span className="text-blue-500">(int8)</span>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        email <span className="text-green-500">(text)</span>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        name <span className="text-green-500">(text)</span>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        created_at <span className="text-purple-500">(timestamptz)</span>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {[
                      { id: 1, email: 'john@example.com', name: 'John Doe', created_at: '2024-01-15T10:30:00Z' },
                      { id: 2, email: 'jane@example.com', name: 'Jane Smith', created_at: '2024-01-14T15:45:00Z' },
                      { id: 3, email: 'bob@example.com', name: 'Bob Johnson', created_at: '2024-01-13T09:20:00Z' }
                    ].map((row) => (
                      <tr key={row.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(row.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex space-x-2">
                            <button className="text-blue-600 hover:text-blue-800">Edit</button>
                            <button className="text-red-600 hover:text-red-800">Delete</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}