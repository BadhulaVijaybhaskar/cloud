import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { Shield, Key, Lock } from 'lucide-react'

export default function AtomVault() {
  return (
    <AtomLayout title="ATOM Vault - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Platform Vault</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage platform-wide secrets, keys, and security policies</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Key className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Platform Keys</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">247</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Active across regions</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Lock className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Secrets</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">1,567</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Platform secrets</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-5 h-5 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Policies</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">23</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Security policies</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-5 h-5 text-red-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Rotations</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">12</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Due this week</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Secret Bindings</h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Namespace</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Key Count</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Last Rotation</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Sync Status</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-4 px-4 font-medium text-gray-900 dark:text-white">atom-core</td>
                    <td className="py-4 px-4 text-gray-600 dark:text-gray-400">47</td>
                    <td className="py-4 px-4 text-gray-600 dark:text-gray-400">2 days ago</td>
                    <td className="py-4 px-4"><span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">synced</span></td>
                    <td className="py-4 px-4"><button className="text-blue-600 hover:text-blue-800 text-sm">Rotate</button></td>
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-4 px-4 font-medium text-gray-900 dark:text-white">atom-auth</td>
                    <td className="py-4 px-4 text-gray-600 dark:text-gray-400">23</td>
                    <td className="py-4 px-4 text-gray-600 dark:text-gray-400">1 week ago</td>
                    <td className="py-4 px-4"><span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">synced</span></td>
                    <td className="py-4 px-4"><button className="text-blue-600 hover:text-blue-800 text-sm">Rotate</button></td>
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-4 px-4 font-medium text-gray-900 dark:text-white">atom-storage</td>
                    <td className="py-4 px-4 text-gray-600 dark:text-gray-400">31</td>
                    <td className="py-4 px-4 text-gray-600 dark:text-gray-400">3 days ago</td>
                    <td className="py-4 px-4"><span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">pending</span></td>
                    <td className="py-4 px-4"><button className="text-green-600 hover:text-green-800 text-sm">Sync</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </AtomLayout>
  )
}