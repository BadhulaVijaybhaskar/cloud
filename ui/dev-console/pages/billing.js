import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function Billing() {
  const [billingData, setBillingData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBillingData()
  }, [])

  const loadBillingData = async () => {
    // Simulate billing data
    setBillingData({
      total_mtd: 1250.50,
      forecast: 1800.00,
      projects: [
        { id: 'p-1', name: 'Alpha Project', cost: 850.25 },
        { id: 'p-2', name: 'Beta Project', cost: 400.25 }
      ],
      invoices: [
        { id: 'inv-1', date: '2024-12-01', amount: 1150.00, status: 'paid' },
        { id: 'inv-2', date: '2024-11-01', amount: 980.50, status: 'paid' }
      ]
    })
    setLoading(false)
  }

  const exportCSV = () => {
    // Simulate CSV export
    const csvData = 'Project,Cost\nAlpha Project,850.25\nBeta Project,400.25'
    const blob = new Blob([csvData], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'billing-report.csv'
    a.click()
  }

  if (loading) {
    return (
      <Layout title="Billing">
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Billing Dashboard">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold neural-text">Billing Dashboard</h1>
          <button 
            onClick={exportCSV}
            className="quantum-card px-6 py-3 rounded-lg font-medium hover:bg-accent"
          >
            📊 Export CSV
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-emerald-500">${billingData.total_mtd.toFixed(2)}</div>
            <div className="text-sm text-muted-foreground mt-1">Month to Date</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-violet-500">${billingData.forecast.toFixed(2)}</div>
            <div className="text-sm text-muted-foreground mt-1">Forecast</div>
          </div>
          <div className="quantum-card p-6 text-center">
            <div className="text-3xl font-bold text-teal-500">{billingData.projects.length}</div>
            <div className="text-sm text-muted-foreground mt-1">Active Projects</div>
          </div>
        </div>

        {/* Project Spend Breakdown */}
        <div className="quantum-card p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6">💰 Project Spend Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/20">
                <tr>
                  <th className="text-left p-4">Project</th>
                  <th className="text-left p-4">Current Cost</th>
                  <th className="text-left p-4">Trend</th>
                  <th className="text-left p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {billingData.projects.map(project => (
                  <tr key={project.id} className="border-t border-border/50">
                    <td className="p-4 font-medium">{project.name}</td>
                    <td className="p-4 font-semibold text-emerald-600">${project.cost.toFixed(2)}</td>
                    <td className="p-4">
                      <div className="w-20 h-8 bg-gradient-to-r from-emerald-500/20 to-emerald-500/40 rounded flex items-center justify-center text-xs">
                        📈 +12%
                      </div>
                    </td>
                    <td className="p-4">
                      <button className="text-primary hover:text-primary/80 text-sm font-medium">
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Invoices */}
        <div className="quantum-card p-6">
          <h2 className="text-2xl font-bold mb-6">🧾 Recent Invoices</h2>
          <div className="space-y-4">
            {billingData.invoices.map(invoice => (
              <div key={invoice.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div>
                  <div className="font-medium">Invoice #{invoice.id}</div>
                  <div className="text-sm text-muted-foreground">{invoice.date}</div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">${invoice.amount.toFixed(2)}</div>
                  <span className="px-2 py-1 bg-emerald-500/20 text-emerald-600 text-xs rounded-full">
                    {invoice.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}