import { useState } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Card from '../components/Card';

export default function QueryAI() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [queryHistory] = useState([
    { query: 'Show me all users who signed up last week', timestamp: '2024-01-20T10:30:00Z', type: 'sql' },
    { query: 'Find similar documents to "AI in healthcare"', timestamp: '2024-01-20T09:15:00Z', type: 'semantic' },
    { query: 'What are the top performing posts by engagement?', timestamp: '2024-01-19T16:45:00Z', type: 'analytics' }
  ]);

  const handleQuery = async () => {
    setLoading(true);
    // Simulate AI query processing
    setTimeout(() => {
      setResults({
        type: 'table',
        sql: 'SELECT * FROM users WHERE created_at >= NOW() - INTERVAL \'7 days\' ORDER BY created_at DESC;',
        data: [
          { id: 1, email: 'john@example.com', name: 'John Doe', created_at: '2024-01-18T10:30:00Z' },
          { id: 2, email: 'jane@example.com', name: 'Jane Smith', created_at: '2024-01-17T15:45:00Z' },
          { id: 3, email: 'bob@example.com', name: 'Bob Johnson', created_at: '2024-01-16T09:20:00Z' }
        ],
        explanation: 'I found 3 users who signed up in the last 7 days. The query filters users by creation date and orders them by most recent first.'
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <Layout title="Query AI">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">🔍 Query AI</h1>
            <p className="text-gray-600">Natural language interface for your data with semantic search</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="secondary" size="sm">📚 Examples</Button>
            <Button variant="secondary" size="sm">🔗 Chain Mode</Button>
          </div>
        </div>

        {/* Query Interface */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ask anything about your data
              </label>
              <div className="relative">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-12"
                  rows={3}
                  placeholder="Example: Show me all users who signed up last week and have made at least one purchase..."
                />
                <div className="absolute bottom-3 right-3">
                  <Button 
                    onClick={handleQuery} 
                    loading={loading}
                    disabled={!query.trim()}
                    size="sm"
                  >
                    {loading ? 'Processing...' : 'Ask AI'}
                  </Button>
                </div>
              </div>
            </div>
            
            {/* Query Type Selector */}
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2">
                <input type="radio" name="queryType" defaultChecked className="text-blue-600" />
                <span className="text-sm text-gray-700">🗄️ SQL + Vector Search</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="radio" name="queryType" className="text-blue-600" />
                <span className="text-sm text-gray-700">📊 Analytics Only</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="radio" name="queryType" className="text-blue-600" />
                <span className="text-sm text-gray-700">🔍 Semantic Search</span>
              </label>
            </div>
          </div>
        </Card>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* AI Explanation */}
            <Card title="🧠 AI Analysis">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-900">{results.explanation}</p>
              </div>
            </Card>

            {/* Generated SQL */}
            <Card title="🔧 Generated Query">
              <div className="bg-gray-900 rounded-lg p-4">
                <code className="text-green-400 text-sm font-mono">{results.sql}</code>
              </div>
              <div className="mt-3 flex space-x-2">
                <Button size="sm" variant="secondary">Copy SQL</Button>
                <Button size="sm" variant="secondary">Optimize</Button>
                <Button size="sm" variant="secondary">Explain Plan</Button>
              </div>
            </Card>

            {/* Results Visualization */}
            <Card title="📊 Results" action={
              <div className="flex space-x-2">
                <Button size="sm" variant="secondary">📋 Table</Button>
                <Button size="sm" variant="secondary">📈 Chart</Button>
                <Button size="sm" variant="secondary">📄 JSON</Button>
              </div>
            }>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(results.data[0] || {}).map((key) => (
                        <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.data.map((row, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        {Object.values(row).map((value, i) => (
                          <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {typeof value === 'string' && value.includes('T') ? 
                              new Date(value).toLocaleString() : 
                              String(value)
                            }
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="mt-4 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Showing {results.data.length} results • Query executed in 0.23s
                </p>
                <div className="flex space-x-2">
                  <Button size="sm" variant="secondary">Export CSV</Button>
                  <Button size="sm" variant="secondary">Save Query</Button>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Query History & Examples */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="📚 Query History">
            <div className="space-y-3">
              {queryHistory.map((item, index) => (
                <div key={index} className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{item.query}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          item.type === 'sql' ? 'bg-blue-100 text-blue-800' :
                          item.type === 'semantic' ? 'bg-purple-100 text-purple-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {item.type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <Button size="sm" variant="secondary">Rerun</Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card title="💡 Example Queries">
            <div className="space-y-3">
              {[
                { query: 'Show me users with the highest engagement scores', category: 'Analytics' },
                { query: 'Find documents similar to "machine learning best practices"', category: 'Semantic' },
                { query: 'What are the most common error patterns in logs?', category: 'Logs' },
                { query: 'Compare revenue by month for the last year', category: 'Business' }
              ].map((example, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                     onClick={() => setQuery(example.query)}>
                  <p className="text-sm font-medium text-gray-900">{example.query}</p>
                  <span className="text-xs text-gray-500">{example.category}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Chain Mode Preview */}
        <Card title="🔗 Chain Mode" className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
          <div className="space-y-4">
            <p className="text-sm text-gray-700">
              Chain multiple queries together for complex analysis workflows
            </p>
            <div className="flex items-center space-x-2">
              <div className="px-3 py-2 bg-white border border-gray-300 rounded text-sm">
                1. Find top users
              </div>
              <span className="text-gray-400">→</span>
              <div className="px-3 py-2 bg-white border border-gray-300 rounded text-sm">
                2. Analyze their behavior
              </div>
              <span className="text-gray-400">→</span>
              <div className="px-3 py-2 bg-white border border-gray-300 rounded text-sm">
                3. Generate insights
              </div>
            </div>
            <Button variant="secondary" size="sm">Try Chain Mode</Button>
          </div>
        </Card>
      </div>
    </Layout>
  );
}