import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { Rocket, CheckCircle } from 'lucide-react'

const platformDeployments = [
  { id: 1, name: 'atom-core-v3.2.1', service: 'Core Platform', environment: 'production', version: 'v3.2.1', status: 'running', region: 'us-east-1', created: '2 hours ago', health: 'healthy' },
  { id: 2, name: 'atom-auth-v2.8.4', service: 'Auth Service', environment: 'production', version: 'v2.8.4', status: 'running', region: 'global', created: '1 day ago', health: 'healthy' },
  { id: 3, name: 'atom-storage-v1.9.2', service: 'Storage API', environment: 'production', version: 'v1.9.2', status: 'running', region: 'us-west-2', created: '3 days ago', health: 'healthy' },
  { id: 4, name: 'atom-realtime-v2.1.0', service: 'Realtime Service', environment: 'staging', version: 'v2.1.0', status: 'deploying', region: 'eu-west-1', created: '30 min ago', health: 'deploying' },
  { id: 5, name: 'atom-graphql-v4.0.0-rc1', service: 'GraphQL Gateway', environment: 'canary', version: 'v4.0.0-rc1', status: 'canary', region: 'us-east-1', created: '1 hour ago', health: 'monitoring' }
]

export default function AtomDeployments() {
  return (
    <AtomLayout title="ATOM Deployments - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Platform Deployments</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor and manage ATOM platform deployments across all regions</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <Rocket className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Deployments</h2>
            </div>
          </div>
          
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Service</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Environment</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Version</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Status</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Region</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Health</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {platformDeployments.map((deployment) => (
                    <tr key={deployment.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">{deployment.service}</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">{deployment.name}</div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          deployment.environment === 'production' ? 'bg-green-100 text-green-800' :
                          deployment.environment === 'staging' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {deployment.environment}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-900 dark:text-white">{deployment.version}</td>
                      <td className="py-4 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          deployment.status === 'running' ? 'bg-green-100 text-green-800' :
                          deployment.status === 'deploying' ? 'bg-blue-100 text-blue-800' :
                          deployment.status === 'canary' ? 'bg-purple-100 text-purple-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {deployment.status}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600 dark:text-gray-400">{deployment.region}</td>
                      <td className="py-4 px-4">
                        <CheckCircle className={`w-5 h-5 ${
                          deployment.health === 'healthy' ? 'text-green-500' :
                          deployment.health === 'monitoring' ? 'text-yellow-500' :
                          'text-blue-500'
                        }`} />
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex gap-2">
                          <button className="text-blue-600 hover:text-blue-800 text-sm">Logs</button>
                          <button className="text-green-600 hover:text-green-800 text-sm">Rollback</button>
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
    </AtomLayout>
  )
}