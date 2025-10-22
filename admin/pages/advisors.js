import { useState } from 'react';
import Layout from '../components/Layout';

export default function Advisors() {
  const [issues] = useState([
    { id: 1, title: 'Slow query detected', severity: 'high', table: 'users', description: 'Query taking 2.3s on average' },
    { id: 2, title: 'Missing RLS policy', severity: 'medium', table: 'posts', description: 'Table has no row-level security' },
    { id: 3, title: 'Unused index', severity: 'low', table: 'comments', description: 'Index not being utilized' }
  ]);

  return (
    <Layout title="Advisors">
      <div className="p-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-normal text-gray-900 mb-2">Advisors</h1>
          <p className="text-gray-600">Get recommendations to optimize your project</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Total Issues</p>
              <p className="text-2xl font-semibold text-gray-900">{issues.length}</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">High Priority</p>
              <p className="text-2xl font-semibold text-gray-900">{issues.filter(i => i.severity === 'high').length}</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Security Score</p>
              <p className="text-2xl font-semibold text-gray-900">87%</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Performance Score</p>
              <p className="text-2xl font-semibold text-gray-900">92%</p>
            </div>
          </div>
        </div>

        {/* Issues */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recommendations</h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {issues.map((issue) => (
              <div key={issue.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="text-sm font-medium text-gray-900">{issue.title}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        issue.severity === 'high' ? 'bg-red-100 text-red-800' :
                        issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {issue.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">{issue.description}</p>
                    <p className="text-xs text-gray-500">Table: {issue.table}</p>
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">
                      View Details
                    </button>
                    <button className="px-3 py-1 text-sm bg-gray-900 text-white rounded hover:bg-gray-800">
                      Fix
                    </button>
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