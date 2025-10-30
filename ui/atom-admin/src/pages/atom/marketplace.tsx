import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { Store, Download } from 'lucide-react'

const apps = [
  { name: 'Analytics Pro', description: 'Advanced analytics dashboard', downloads: '1.2k' },
  { name: 'Security Scanner', description: 'Automated security scanning', downloads: '856' },
  { name: 'Backup Manager', description: 'Automated backup solution', downloads: '2.1k' }
]

export default function AtomMarketplace() {
  return (
    <AtomLayout title="ATOM Marketplace - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Marketplace</h1>
          <p className="text-gray-600 dark:text-gray-400">Discover and install applications</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {apps.map((app) => (
            <div key={app.name} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center gap-3 mb-4">
                <Store className="w-8 h-8 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{app.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{app.description}</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                  <Download className="w-4 h-4" />
                  {app.downloads}
                </div>
                <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg text-sm">
                  Install
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AtomLayout>
  )
}