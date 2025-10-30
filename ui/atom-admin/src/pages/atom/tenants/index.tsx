import React, { useState } from 'react'
import AtomLayout from '../../../components/Layout/AtomLayout'
import AtomTable from '../../../components/AtomTable'
import AtomBadge from '../../../components/AtomBadge'
import AtomModal from '../../../components/AtomModal'
import { Users, Search, Plus, MoreHorizontal, Eye } from 'lucide-react'

const mockTenants = [
  { id: 'acme-corp', name: 'Acme Corporation', email: 'admin@acme.com', plan: 'enterprise', status: 'active', usage: '89.5 GB', region: 'us-east-1', nodes: 12, lastActive: '2 min ago' },
  { id: 'tech-startup', name: 'Tech Startup Inc', email: 'ops@techstartup.com', plan: 'pro', status: 'active', usage: '34.2 GB', region: 'us-west-2', nodes: 8, lastActive: '5 min ago' },
  { id: 'dev-agency', name: 'Development Agency', email: 'team@devagency.io', plan: 'starter', status: 'trial', usage: '8.9 GB', region: 'us-east-1', nodes: 3, lastActive: '1 hour ago' },
  { id: 'global-ent', name: 'Global Enterprise Ltd', email: 'devops@global.com', plan: 'enterprise', status: 'active', usage: '156.8 GB', region: 'eu-west-1', nodes: 25, lastActive: '1 min ago' },
  { id: 'fintech-co', name: 'FinTech Solutions Co', email: 'infra@fintech.co', plan: 'pro', status: 'suspended', usage: '0 GB', region: 'us-east-1', nodes: 0, lastActive: '2 days ago' },
  { id: 'ai-startup', name: 'AI Startup Labs', email: 'platform@ai-labs.com', plan: 'enterprise', status: 'active', usage: '234.1 GB', region: 'us-west-2', nodes: 18, lastActive: '30 sec ago' },
  { id: 'media-corp', name: 'Media Corporation', email: 'tech@media-corp.com', plan: 'pro', status: 'active', usage: '67.3 GB', region: 'eu-west-1', nodes: 14, lastActive: '3 min ago' },
  { id: 'retail-giant', name: 'Retail Giant Inc', email: 'cloud@retail-giant.com', plan: 'enterprise', status: 'active', usage: '445.7 GB', region: 'us-east-1', nodes: 42, lastActive: '1 min ago' }
]

export default function AtomTenants() {
  const [selectedTenant, setSelectedTenant] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const columns = [
    {
      key: 'name',
      label: 'Tenant',
      render: (value, row) => (
        <div>
          <div className="font-medium text-gray-900 dark:text-white">{value}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">{row.email}</div>
        </div>
      )
    },
    {
      key: 'plan',
      label: 'Plan',
      render: (value) => (
        <AtomBadge variant={value === 'enterprise' ? 'info' : value === 'pro' ? 'success' : 'default'}>
          {value}
        </AtomBadge>
      )
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => (
        <AtomBadge variant={value === 'active' ? 'success' : value === 'trial' ? 'warning' : 'error'}>
          {value}
        </AtomBadge>
      )
    },
    { key: 'usage', label: 'Usage' },
    { key: 'nodes', label: 'Nodes' },
    { key: 'region', label: 'Region' },
    { key: 'lastActive', label: 'Last Active' },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setSelectedTenant(row)
              setIsModalOpen(true)
            }}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
            <MoreHorizontal className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      )
    }
  ]

  return (
    <AtomLayout title="ATOM Tenants - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Platform Tenants</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage and monitor all tenants across ATOM Cloud platform</p>
        </div>

        <div className="flex items-center justify-between mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search tenants..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button className="ml-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Provision Tenant
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Tenant Overview</h2>
              <span className="text-sm text-gray-500">({mockTenants.length} tenants)</span>
            </div>
          </div>
          
          <div className="p-6">
            <AtomTable columns={columns} data={mockTenants} />
          </div>
        </div>

        <AtomModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Tenant Details"
          size="lg"
        >
          {selectedTenant && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
                  <p className="text-gray-900 dark:text-white">{selectedTenant.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
                  <p className="text-gray-900 dark:text-white">{selectedTenant.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Plan</label>
                  <AtomBadge variant="info">{selectedTenant.plan}</AtomBadge>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
                  <AtomBadge variant="success">{selectedTenant.status}</AtomBadge>
                </div>
              </div>
              <div className="flex gap-2 pt-4">
                <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg">
                  Edit Tenant
                </button>
                <button className="bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded-lg">
                  Suspend
                </button>
              </div>
            </div>
          )}
        </AtomModal>
      </div>
    </AtomLayout>
  )
}