import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import AtomTable from '../../components/AtomTable'
import AtomBadge from '../../components/AtomBadge'
import { DollarSign, CreditCard, TrendingUp, Download, Plus } from 'lucide-react'

const mockInvoices = [
  { id: 'INV-001', tenant: 'Acme Corp', amount: '$1,247.50', status: 'paid', date: '2024-01-15', dueDate: '2024-01-30' },
  { id: 'INV-002', tenant: 'Tech Startup', amount: '$599.00', status: 'pending', date: '2024-01-10', dueDate: '2024-01-25' },
  { id: 'INV-003', tenant: 'Global Enterprise', amount: '$2,890.00', status: 'paid', date: '2024-01-05', dueDate: '2024-01-20' },
  { id: 'INV-004', tenant: 'Dev Agency', amount: '$299.00', status: 'overdue', date: '2023-12-28', dueDate: '2024-01-12' }
]

export default function AtomBilling() {
  const columns = [
    { key: 'id', label: 'Invoice ID' },
    { key: 'tenant', label: 'Tenant' },
    { key: 'amount', label: 'Amount' },
    {
      key: 'status',
      label: 'Status',
      render: (value) => (
        <AtomBadge variant={value === 'paid' ? 'success' : value === 'pending' ? 'warning' : 'error'}>
          {value}
        </AtomBadge>
      )
    },
    { key: 'date', label: 'Date' },
    { key: 'dueDate', label: 'Due Date' },
    {
      key: 'actions',
      label: 'Actions',
      render: () => (
        <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
          <Download className="w-4 h-4 text-gray-500" />
        </button>
      )
    }
  ]

  return (
    <AtomLayout title="ATOM Billing - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Billing</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage billing and payment information</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <DollarSign className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">MRR</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">$12,450</div>
            <div className="flex items-center gap-1 text-sm text-green-600">
              <TrendingUp className="w-4 h-4" />
              +8.2%
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <CreditCard className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">This Month</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">$5,236</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Current usage</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <CreditCard className="w-5 h-5 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Outstanding</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">$899</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">2 invoices</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Growth</h2>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">+15%</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">vs last month</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Revenue Trend</h2>
              <div className="text-sm text-gray-500">Stripe Integration: Connected</div>
            </div>
          </div>
          <div className="p-6">
            <div className="h-64 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Monthly Recurring Revenue Chart Placeholder</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Invoices</h2>
              <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Generate Invoice
              </button>
            </div>
          </div>
          <div className="p-6">
            <AtomTable columns={columns} data={mockInvoices} />
          </div>
        </div>
      </div>
    </AtomLayout>
  )
}