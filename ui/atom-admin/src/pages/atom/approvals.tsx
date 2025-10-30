import React, { useState } from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import AtomTable from '../../components/AtomTable'
import AtomBadge from '../../components/AtomBadge'
import AtomModal from '../../components/AtomModal'
import { CheckCircle, Clock, AlertTriangle, Eye, ThumbsUp, ThumbsDown } from 'lucide-react'

const mockApprovals = [
  { id: 'APP-001', type: 'deployment', title: 'Deploy to Production', target: 'prod-api-v2.1.0', risk: 'medium', requester: 'john.doe@acme.com', status: 'pending', confidence: 0.83, rollback: true },
  { id: 'APP-002', type: 'policy', title: 'Update Security Policy', target: 'P3-execution-safety', risk: 'high', requester: 'jane.smith@tech.com', status: 'approved', confidence: 0.91, rollback: false },
  { id: 'APP-003', type: 'tenant', title: 'Suspend Tenant', target: 'fintech-co', risk: 'low', requester: 'admin@global.com', status: 'pending', confidence: 0.95, rollback: true },
  { id: 'APP-004', type: 'vault', title: 'Rotate API Keys', target: 'production-keys', risk: 'medium', requester: 'security@atom.cloud', status: 'rejected', confidence: 0.67, rollback: true }
]

export default function AtomApprovals() {
  const [selectedApproval, setSelectedApproval] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const columns = [
    { key: 'id', label: 'ID' },
    {
      key: 'type',
      label: 'Type',
      render: (value) => (
        <AtomBadge variant="info">{value}</AtomBadge>
      )
    },
    { key: 'title', label: 'Title' },
    { key: 'target', label: 'Target' },
    {
      key: 'risk',
      label: 'Risk',
      render: (value) => (
        <AtomBadge variant={value === 'high' ? 'error' : value === 'medium' ? 'warning' : 'success'}>
          {value}
        </AtomBadge>
      )
    },
    { key: 'requester', label: 'Requested By' },
    {
      key: 'status',
      label: 'Status',
      render: (value) => (
        <AtomBadge variant={value === 'approved' ? 'success' : value === 'rejected' ? 'error' : 'warning'}>
          {value}
        </AtomBadge>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setSelectedApproval(row)
              setIsModalOpen(true)
            }}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          {row.status === 'pending' && (
            <>
              <button className="p-1 hover:bg-green-100 dark:hover:bg-green-900 rounded">
                <ThumbsUp className="w-4 h-4 text-green-600" />
              </button>
              <button className="p-1 hover:bg-red-100 dark:hover:bg-red-900 rounded">
                <ThumbsDown className="w-4 h-4 text-red-600" />
              </button>
            </>
          )}
        </div>
      )
    }
  ]

  return (
    <AtomLayout title="ATOM Approvals - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Approvals</h1>
          <p className="text-gray-600 dark:text-gray-400">Review and approve pending requests</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-5 h-5 text-yellow-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Pending</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">2</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Awaiting review</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Approved</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">1</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">This week</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">High Risk</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">1</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Requires MFA</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Avg Time</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">4.2h</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">To approval</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Approval Queue</h2>
              <span className="text-sm text-gray-500">({mockApprovals.length} total)</span>
            </div>
          </div>
          
          <div className="p-6">
            <AtomTable columns={columns} data={mockApprovals} />
          </div>
        </div>

        <AtomModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Approval Details"
          size="lg"
        >
          {selectedApproval && (
            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Dry-run Preview</h4>
                <pre className="text-sm text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-800 p-3 rounded border">
{JSON.stringify({
  impact: selectedApproval.risk,
  rollback_available: selectedApproval.rollback,
  confidence: selectedApproval.confidence
}, null, 2)}
                </pre>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Type</label>
                  <AtomBadge variant="info">{selectedApproval.type}</AtomBadge>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Risk Level</label>
                  <AtomBadge variant={selectedApproval.risk === 'high' ? 'error' : 'warning'}>{selectedApproval.risk}</AtomBadge>
                </div>
              </div>
              {selectedApproval.status === 'pending' && (
                <div className="flex gap-2 pt-4">
                  <button className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <ThumbsUp className="w-4 h-4" />
                    Approve
                  </button>
                  <button className="bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <ThumbsDown className="w-4 h-4" />
                    Reject
                  </button>
                </div>
              )}
            </div>
          )}
        </AtomModal>
      </div>
    </AtomLayout>
  )
}