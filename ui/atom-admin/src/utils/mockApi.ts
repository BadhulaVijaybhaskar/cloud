// ATOM Admin Console - Mock API Utilities

export interface AtomTenant {
  id: string
  name: string
  email: string
  plan: 'starter' | 'pro' | 'enterprise'
  status: 'active' | 'trial' | 'suspended'
  createdAt: string
  lastActive: string
  deployments: number
  monthlyUsage: number
  region: string
  features: string[]
}

export interface AtomDashboardStats {
  totalTenants: number
  activeTenants: number
  activeDeployments: number
  monthlyRevenue: number
  systemHealth: number
  totalRequests: number
  avgResponseTime: number
  criticalIssues: number
}

export interface AtomActivity {
  id: number
  type: 'deployment' | 'tenant' | 'alert' | 'approval'
  message: string
  time: string
  status: 'success' | 'warning' | 'info' | 'error'
  tenant: string
  user: string
}

// Mock API functions
export const atomApi = {
  // Dashboard
  async getDashboardStats(): Promise<AtomDashboardStats> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const response = await fetch('/mock/api/dashboard.json')
    const data = await response.json()
    return data.stats
  },

  async getRecentActivity(): Promise<AtomActivity[]> {
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const response = await fetch('/mock/api/dashboard.json')
    const data = await response.json()
    return data.recentActivity
  },

  // Tenants
  async getTenants(): Promise<AtomTenant[]> {
    await new Promise(resolve => setTimeout(resolve, 400))
    
    const response = await fetch('/mock/api/tenants.json')
    const data = await response.json()
    return data.tenants
  },

  async getTenant(id: string): Promise<AtomTenant | null> {
    const tenants = await this.getTenants()
    return tenants.find(tenant => tenant.id === id) || null
  },

  // Plans
  async getPlans() {
    await new Promise(resolve => setTimeout(resolve, 200))
    
    const response = await fetch('/mock/api/tenants.json')
    const data = await response.json()
    return data.plans
  }
}

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

export const formatDate = (dateString: string): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(dateString))
}

export const getRelativeTime = (dateString: string): string => {
  const now = new Date()
  const date = new Date(dateString)
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`
  return `${Math.floor(diffInSeconds / 86400)} days ago`
}

export default atomApi