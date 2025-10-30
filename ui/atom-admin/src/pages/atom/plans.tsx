import React from 'react'
import AtomLayout from '../../components/Layout/AtomLayout'
import { CreditCard, Check } from 'lucide-react'

const platformPlans = [
  {
    name: 'Starter',
    price: 29,
    tenants: 156,
    revenue: '$4,524',
    features: ['Basic Auth', '5GB Storage', 'Community Support']
  },
  {
    name: 'Professional', 
    price: 99,
    tenants: 423,
    revenue: '$41,877',
    features: ['Advanced Auth', '50GB Storage', 'Email Support']
  },
  {
    name: 'Enterprise',
    price: 299,
    tenants: 668,
    revenue: '$199,732',
    features: ['Enterprise Auth', 'Unlimited Storage', 'Priority Support']
  }
]

export default function AtomPlans() {
  return (
    <AtomLayout title="ATOM Plans - Admin Console">
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            ATOM Cloud Plans
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Choose the perfect plan for your organization's needs
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {platformPlans.map((plan) => (
            <div key={plan.name} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{plan.name}</h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    ${plan.price}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">/month</span>
                </div>
              </div>

              <div className="space-y-3 mb-6">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-500" />
                    <span className="text-gray-900 dark:text-white">{feature}</span>
                  </div>
                ))}
              </div>

              <div className="text-center mb-4">
                <div className="text-lg font-semibold text-gray-900 dark:text-white">{plan.tenants} tenants</div>
                <div className="text-sm text-green-600">{plan.revenue} MRR</div>
              </div>
              <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:shadow-lg transition-all">
                Edit Plan
              </button>
            </div>
          ))}
        </div>
      </div>
    </AtomLayout>
  )
}