import { useState } from 'react';
import Layout from '../components/Layout';

export default function Logs() {
  const [logs] = useState([
    { timestamp: '2024-01-20 10:30:15', level: 'INFO', service: 'api', message: 'GET /api/users - 200 OK' },
    { timestamp: '2024-01-20 10:30:12', level: 'ERROR', service: 'auth', message: 'Authentication failed for user' },
    { timestamp: '2024-01-20 10:30:10', level: 'INFO', service: 'db', message: 'Query executed successfully' }
  ]);

  return (
    <Layout title="Logs">
      <div className="p-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-normal text-gray-900 mb-2">Logs</h1>
          <p className="text-gray-600">Monitor your application logs and events</p>
        </div>

        {/* Filters */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Level</label>
              <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
                <option>All levels</option>
                <option>ERROR</option>
                <option>WARN</option>
                <option>INFO</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service</label>
              <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
                <option>All services</option>
                <option>API</option>
                <option>Auth</option>
                <option>Database</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
              <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
                <option>Last hour</option>
                <option>Last 24 hours</option>
                <option>Last 7 days</option>
              </select>
            </div>
            <div className="flex items-end">
              <button className="w-full px-4 py-2 bg-gray-900 text-white rounded text-sm hover:bg-gray-800">
                Apply Filters
              </button>
            </div>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Logs</h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {logs.map((log, index) => (
              <div key={index} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      log.level === 'ERROR' ? 'bg-red-100 text-red-800' :
                      log.level === 'WARN' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {log.level}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-sm font-medium text-gray-900">{log.service}</span>
                      <span className="text-xs text-gray-500">{log.timestamp}</span>
                    </div>
                    <p className="text-sm text-gray-700">{log.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}