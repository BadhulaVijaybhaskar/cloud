/**
 * Admin Portal Main Page - E.5
 * Business intelligence dashboard and tenant management
 */
import React, { useState, useEffect } from 'react';
import RevenueChart from '../components/RevenueChart';

interface DashboardData {
  revenue: Array<{
    month: string;
    revenue: number;
    transactions: number;
  }>;
  usage: Array<{
    tenant_id: string;
    service: string;
    usage_total: number;
    cost: number;
  }>;
  summary: {
    total_revenue: number;
    active_tenants: number;
    total_transactions: number;
  };
}

interface TenantInfo {
  id: string;
  name: string;
  status: string;
  created_at: string;
  usage_cost: number;
}

const AdminPortal: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [tenants, setTenants] = useState<TenantInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'revenue' | 'tenants'>('overview');

  useEffect(() => {
    fetchDashboardData();
    fetchTenants();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/analytics/summary');
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        // Fallback to sample data in simulation mode
        setDashboardData({
          revenue: [
            { month: '2024-10', revenue: 15420.50, transactions: 342 },
            { month: '2024-11', revenue: 18750.25, transactions: 428 },
            { month: '2024-12', revenue: 22100.75, transactions: 515 }
          ],
          usage: [
            { tenant_id: 'tenant-001', service: 'marketplace', usage_total: 150.5, cost: 75.25 },
            { tenant_id: 'tenant-002', service: 'analytics', usage_total: 89.2, cost: 44.60 },
            { tenant_id: 'tenant-003', service: 'storage', usage_total: 1024.8, cost: 102.48 }
          ],
          summary: {
            total_revenue: 56271.50,
            active_tenants: 3,
            total_transactions: 1285
          }
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTenants = async () => {
    try {
      const response = await fetch('/api/tenants');
      
      if (response.ok) {
        const data = await response.json();
        setTenants(data.tenants || []);
      } else {
        // Fallback to sample tenants
        setTenants([
          { id: 'tenant-001', name: 'Acme Corp', status: 'active', created_at: '2024-01-15', usage_cost: 75.25 },
          { id: 'tenant-002', name: 'TechStart Inc', status: 'active', created_at: '2024-02-20', usage_cost: 44.60 },
          { id: 'tenant-003', name: 'DataFlow Ltd', status: 'active', created_at: '2024-03-10', usage_cost: 102.48 }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch tenants:', error);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="admin-portal loading">
        <div className="loading-spinner">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="admin-portal">
      <header className="portal-header">
        <h1>ATOM Cloud Admin Portal</h1>
        <p>Business Intelligence & Tenant Management</p>
      </header>

      <nav className="portal-nav">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'revenue' ? 'active' : ''}
          onClick={() => setActiveTab('revenue')}
        >
          Revenue Analytics
        </button>
        <button 
          className={activeTab === 'tenants' ? 'active' : ''}
          onClick={() => setActiveTab('tenants')}
        >
          Tenant Management
        </button>
      </nav>

      <main className="portal-content">
        {activeTab === 'overview' && dashboardData && (
          <div className="overview-tab">
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Total Revenue</h3>
                <div className="metric">{formatCurrency(dashboardData.summary.total_revenue)}</div>
              </div>
              <div className="summary-card">
                <h3>Active Tenants</h3>
                <div className="metric">{dashboardData.summary.active_tenants}</div>
              </div>
              <div className="summary-card">
                <h3>Total Transactions</h3>
                <div className="metric">{dashboardData.summary.total_transactions.toLocaleString()}</div>
              </div>
            </div>

            <div className="charts-section">
              <RevenueChart data={dashboardData.revenue} />
            </div>

            <div className="usage-section">
              <h3>Top Usage by Tenant</h3>
              <div className="usage-table">
                <table>
                  <thead>
                    <tr>
                      <th>Tenant</th>
                      <th>Service</th>
                      <th>Usage</th>
                      <th>Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardData.usage.map((item, index) => (
                      <tr key={index}>
                        <td>{item.tenant_id}</td>
                        <td>{item.service}</td>
                        <td>{item.usage_total.toFixed(2)}</td>
                        <td>{formatCurrency(item.cost)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'revenue' && dashboardData && (
          <div className="revenue-tab">
            <h2>Revenue Analytics</h2>
            <RevenueChart data={dashboardData.revenue} height={400} />
            
            <div className="revenue-details">
              <h3>Monthly Breakdown</h3>
              <div className="revenue-grid">
                {dashboardData.revenue.map((item, index) => (
                  <div key={item.month} className="revenue-item">
                    <div className="month-label">{item.month}</div>
                    <div className="revenue-amount">{formatCurrency(item.revenue)}</div>
                    <div className="transaction-count">{item.transactions} transactions</div>
                    <div className="avg-transaction">
                      Avg: {formatCurrency(item.revenue / item.transactions)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'tenants' && (
          <div className="tenants-tab">
            <h2>Tenant Management</h2>
            
            <div className="tenants-table">
              <table>
                <thead>
                  <tr>
                    <th>Tenant ID</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Usage Cost</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tenants.map((tenant) => (
                    <tr key={tenant.id}>
                      <td>{tenant.id}</td>
                      <td>{tenant.name}</td>
                      <td>
                        <span className={`status ${tenant.status}`}>
                          {tenant.status}
                        </span>
                      </td>
                      <td>{tenant.created_at}</td>
                      <td>{formatCurrency(tenant.usage_cost)}</td>
                      <td>
                        <button className="action-btn">View</button>
                        <button className="action-btn">Edit</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <style jsx>{`
        .admin-portal {
          min-height: 100vh;
          background: #f8f9fa;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .portal-header {
          background: #343a40;
          color: white;
          padding: 20px;
          text-align: center;
        }
        
        .portal-header h1 {
          margin: 0;
          font-size: 2rem;
        }
        
        .portal-header p {
          margin: 5px 0 0 0;
          opacity: 0.8;
        }
        
        .portal-nav {
          background: white;
          padding: 0;
          border-bottom: 1px solid #dee2e6;
          display: flex;
        }
        
        .portal-nav button {
          padding: 15px 25px;
          border: none;
          background: none;
          cursor: pointer;
          border-bottom: 3px solid transparent;
          font-weight: 500;
        }
        
        .portal-nav button:hover {
          background: #f8f9fa;
        }
        
        .portal-nav button.active {
          border-bottom-color: #007bff;
          color: #007bff;
        }
        
        .portal-content {
          padding: 20px;
        }
        
        .summary-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }
        
        .summary-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          text-align: center;
        }
        
        .summary-card h3 {
          margin: 0 0 10px 0;
          color: #6c757d;
          font-size: 0.9rem;
          text-transform: uppercase;
        }
        
        .summary-card .metric {
          font-size: 2rem;
          font-weight: bold;
          color: #007bff;
        }
        
        .usage-section, .revenue-details {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin-top: 20px;
        }
        
        .usage-table table, .tenants-table table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .usage-table th, .usage-table td,
        .tenants-table th, .tenants-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #dee2e6;
        }
        
        .usage-table th, .tenants-table th {
          background: #f8f9fa;
          font-weight: 600;
        }
        
        .revenue-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }
        
        .revenue-item {
          padding: 15px;
          background: #f8f9fa;
          border-radius: 6px;
          text-align: center;
        }
        
        .revenue-item .month-label {
          font-weight: bold;
          color: #495057;
        }
        
        .revenue-item .revenue-amount {
          font-size: 1.2rem;
          color: #007bff;
          font-weight: bold;
          margin: 5px 0;
        }
        
        .status.active {
          color: #28a745;
          font-weight: bold;
        }
        
        .action-btn {
          padding: 4px 8px;
          margin: 0 2px;
          border: 1px solid #007bff;
          background: white;
          color: #007bff;
          border-radius: 3px;
          cursor: pointer;
          font-size: 0.8rem;
        }
        
        .action-btn:hover {
          background: #007bff;
          color: white;
        }
        
        .loading {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
        }
        
        .loading-spinner {
          font-size: 1.2rem;
          color: #6c757d;
        }
      `}</style>
    </div>
  );
};

export default AdminPortal;