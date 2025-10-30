import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import {
  LayoutDashboard,
  Users,
  CreditCard,
  DollarSign,
  Rocket,
  CheckCircle,
  Shield,
  BarChart3,
  Store,
  Users as Partnership,
  HelpCircle,
  Settings
} from 'lucide-react'

const navItems = [
  { href: '/atom/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/atom/tenants', label: 'Tenants', icon: Users },
  { href: '/atom/plans', label: 'Plans', icon: CreditCard },
  { href: '/atom/billing', label: 'Billing', icon: DollarSign },
  { href: '/atom/deployments', label: 'Deployments', icon: Rocket },
  { href: '/atom/approvals', label: 'Approvals', icon: CheckCircle },
  { href: '/atom/vault', label: 'Vault', icon: Shield },
  { href: '/atom/observability', label: 'Observability', icon: BarChart3 },
  { href: '/atom/marketplace', label: 'Marketplace', icon: Store },
  { href: '/atom/partner', label: 'Partner', icon: Partnership },
  { href: '/atom/support', label: 'Support', icon: HelpCircle },
  { href: '/atom/settings', label: 'Settings', icon: Settings }
]

export function AtomSidebar() {
  const router = useRouter()

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 h-screen">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="font-bold text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          ATOM
        </h1>
        <p className="text-xs text-gray-500">Admin Console</p>
      </div>

      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = router.pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}

export default AtomSidebar