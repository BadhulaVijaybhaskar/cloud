import { useState } from 'react';
import Layout from '../components/Layout';

export default function Realtime() {
  const [channels] = useState([
    { name: 'public:messages', connections: 45, messages: 1247, status: 'active' },
    { name: 'public:notifications', connections: 23, messages: 892, status: 'active' }
  ]);

  return (
    <Layout title="Realtime">
      <div className="p-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-normal text-gray-900 mb-2">Realtime</h1>
          <p className="text-gray-600">Listen to database changes in realtime</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Active Connections</p>
              <p className="text-2xl font-semibold text-gray-900">68</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Messages (24h)</p>
              <p className="text-2xl font-semibold text-gray-900">2,139</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Channels</p>
              <p className="text-2xl font-semibold text-gray-900">{channels.length}</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Avg Latency</p>
              <p className="text-2xl font-semibold text-gray-900">45ms</p>
            </div>
          </div>
        </div>

        {/* Channels */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Channels</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Channel</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Connections</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Messages</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {channels.map((channel) => (
                  <tr key={channel.name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center">
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-pulse"></div>
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">{channel.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                        {channel.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{channel.connections}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{channel.messages.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button className="text-gray-400 hover:text-gray-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}