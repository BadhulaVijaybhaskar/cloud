import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { HelpCircle, MessageCircle, Mail, Phone } from 'lucide-react'

export default function AtomSupport() {
  return (
    <AtomLayout title="ATOM Support - Admin Console">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Support</h1>
          <p className="text-gray-600 dark:text-gray-400">Get help and contact support</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <MessageCircle className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Live Chat</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">Get instant help from our support team</p>
            <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg">
              Start Chat
            </button>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Mail className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Email Support</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">Send us an email for detailed assistance</p>
            <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg">
              Send Email
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <HelpCircle className="w-5 h-5 text-purple-600" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Frequently Asked Questions</h2>
          </div>
          <div className="space-y-4">
            <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">How do I create a new tenant?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Navigate to the Tenants page and click the "Create Tenant" button.</p>
            </div>
            <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">How do I upgrade a plan?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Go to the Plans page and select the desired plan for upgrade.</p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">Where can I view system logs?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">System logs are available in the Observability section.</p>
            </div>
          </div>
        </div>
      </div>
    </AtomLayout>
  )
}