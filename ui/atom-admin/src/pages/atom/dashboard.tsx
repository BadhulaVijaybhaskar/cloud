import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { Users, Server, Activity, Clock, Plus, AlertTriangle, TrendingUp, BarChart3, PieChart, Database, Shield } from 'lucide-react'

export default function AtomDashboard() {
  return (
    <AtomLayout title="ATOM Platform Dashboard - Admin Console">
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            ATOM Platform Operations
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Platform-wide metrics and operational controls for ATOM Cloud infrastructure
          </p>
        </div>

        {/* Platform Health Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Total Tenants</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Platform-wide</p>
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">1,247</div>
            <div className="flex items-center gap-1 text-sm text-green-600 mt-2">
              <TrendingUp className="w-4 h-4" />
              +12% this month
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Platform Approvals</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pending review</p>
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">7</div>
            <div className="flex items-center gap-1 text-sm text-yellow-600 mt-2">
              <AlertTriangle className="w-4 h-4" />
              2 high-risk deployments
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Platform Uptime</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Global SLA</p>
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">99.97%</div>
            <div className="flex items-center gap-1 text-sm text-green-600 mt-2">
              <Activity className="w-4 h-4" />
              Above SLA target
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Server className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Global Latency</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">P95 response time</p>
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">89ms</div>
            <div className="flex items-center gap-1 text-sm text-blue-600 mt-2">
              <TrendingUp className="w-4 h-4" />
              -12ms improvement
            </div>
          </div>
        </div>

        {/* Platform Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Regional Infrastructure Load */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Regional Load Distribution</h3>
            </div>
            <div className="h-48 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Infrastructure Load by Region</p>
                <p className="text-xs text-gray-400">US-East: 2.1K nodes, EU: 1.8K nodes, APAC: 1.2K nodes</p>
              </div>
            </div>
          </div>

          {/* Platform Revenue */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Platform Revenue</h3>
            </div>
            <div className="h-48 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Monthly Platform Revenue</p>
                <p className="text-xs text-gray-400">ARR: $2.4M (+18% YoY)</p>
              </div>
            </div>
          </div>

          {/* Security & Compliance */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Security Status</h3>
            </div>
            <div className="h-48 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Platform Security Overview</p>
                <p className="text-xs text-gray-400">Policies: 94% compliant, Secrets: Rotated</p>
              </div>
            </div>
          </div>
        </div>

        {/* Platform Operations - Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Operations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button 
              onClick={() => console.log('Create Tenant clicked')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-lg font-medium hover:shadow-lg transition-all flex items-center gap-3"
            >
              <Plus className="w-5 h-5" />
              Provision Tenant
            </button>
            
            <button 
              onClick={() => console.log('Manage Plans clicked')}
              className="bg-white dark:bg-gray-700 border-2 border-blue-600 text-blue-600 dark:text-blue-400 p-4 rounded-lg font-medium hover:bg-blue-50 dark:hover:bg-gray-600 transition-all flex items-center gap-3"
            >
              <Database className="w-5 h-5" />
              Manage Platform Plans
            </button>
            
            <button 
              onClick={() => console.log('View Platform Alerts clicked')}
              className="bg-white dark:bg-gray-700 border-2 border-yellow-500 text-yellow-600 dark:text-yellow-400 p-4 rounded-lg font-medium hover:bg-yellow-50 dark:hover:bg-gray-600 transition-all flex items-center gap-3"
            >
              <AlertTriangle className="w-5 h-5" />
              Platform Alerts
            </button>
            
            <button 
              onClick={() => console.log('Toggle Simulation Mode clicked')}
              className="bg-white dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 p-4 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-600 transition-all flex items-center gap-3"
            >
              <Activity className="w-5 h-5" />
              Simulation Mode
            </button>
          </div>
        </div>

        {/* Platform Status Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-lg text-white">
          <h2 className="text-xl font-semibold mb-4">ATOM Platform Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold mb-2">5.1K</div>
              <div className="text-white/80">Active Nodes</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-2">89ms</div>
              <div className="text-white/80">Global P95</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-2">0</div>
              <div className="text-white/80">Critical Issues</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-2">99.97%</div>
              <div className="text-white/80">Platform SLA</div>
            </div>
          </div>
        </div>
      </div>
    </AtomLayout>
  )
}