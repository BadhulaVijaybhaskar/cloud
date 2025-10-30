import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { Users, Globe, Building } from 'lucide-react'

export default function AtomPartner() {
  return (
    <AtomLayout title="ATOM Partner - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Partner Program</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage partnerships and integrations</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Building className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Partners</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">12</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Verified partners</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Integrations</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">28</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Active integrations</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Globe className="w-5 h-5 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">API Calls</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">1.2M</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">This month</p>
          </div>
        </div>
      </div>
    </AtomLayout>
  )
}