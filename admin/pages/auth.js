import { useState } from 'react';
import Layout from '../components/Layout';

export default function Auth() {
  const [activeTab, setActiveTab] = useState('users');
  const [users] = useState([
    { id: 1, email: 'john@example.com', provider: 'email', mfa: true, last_sign_in: '2024-01-20T10:30:00Z', status: 'active' },
    { id: 2, email: 'jane@example.com', provider: 'google', mfa: false, last_sign_in: '2024-01-19T15:45:00Z', status: 'active' },
    { id: 3, email: 'bob@example.com', provider: 'github', mfa: true, last_sign_in: '2024-01-18T09:20:00Z', status: 'suspended' }
  ]);

  const tabs = [
    { id: 'users', name: 'Users' },
    { id: 'providers', name: 'Providers' },
    { id: 'policies', name: 'Policies' },
    { id: 'settings', name: 'Settings' }
  ];

  return (
    <Layout title="Authentication">
      <div className="p-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-normal text-gray-900 mb-2">Authentication</h1>
          <p className="text-gray-600">Manage your users and authentication settings</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Total Users</p>
              <p className="text-2xl font-semibold text-gray-900">{users.length}</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Active Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">23</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">MFA Enabled</p>
              <p className="text-2xl font-semibold text-gray-900">67%</p>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">SSO Providers</p>
              <p className="text-2xl font-semibold text-gray-900">4</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-gray-900 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        {activeTab === 'users' && (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Sign In</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-600">
                              {user.email.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-gray-900">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.provider}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Jan 15, 2024</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.last_sign_in).toLocaleDateString()}
                      </td>
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
        )}

        {activeTab === 'providers' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Auth Providers</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded">
                <div>
                  <h4 className="font-medium">Email</h4>
                  <p className="text-sm text-gray-500">Allow users to sign up with email and password</p>
                </div>
                <button className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded">Enabled</button>
              </div>
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded">
                <div>
                  <h4 className="font-medium">Google</h4>
                  <p className="text-sm text-gray-500">Allow users to sign in with Google</p>
                </div>
                <button className="px-3 py-1 text-sm bg-gray-100 text-gray-800 rounded">Disabled</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}