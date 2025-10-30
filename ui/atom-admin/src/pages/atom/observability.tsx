import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { BarChart3, Activity, AlertTriangle } from 'lucide-react'

export default function AtomObservability() {
  return (
    <AtomLayout title="ATOM Observability - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Platform Observability</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor ATOM platform performance, health, and metrics across all regions</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Platform Health</h2>
            </div>
            <div className="text-2xl font-bold text-green-600 mb-2">99.97%</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Global uptime</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">P95 Latency</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">89ms</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Global average</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Error Rate</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">0.03%</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Platform wide</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-5 h-5 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Throughput</h2>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">2.4M</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Requests/hour</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Resource Utilization</h2>
            <div className="h-48 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">CPU, Memory, Storage Usage</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Cost Efficiency</h2>
            <div className="h-48 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Cost per Request Trends</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Regional Performance</h2>
            <button className="text-blue-600 hover:text-blue-800 text-sm">View Grafana Dashboard</button>
          </div>
          <div className="h-64 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500">Embedded Grafana Dashboard Placeholder</p>
              <p className="text-xs text-gray-400">US-East: 45ms | US-West: 52ms | EU: 67ms | APAC: 89ms</p>
            </div>
          </div>
        </div>
      </div>
    </AtomLayout>
  )
}