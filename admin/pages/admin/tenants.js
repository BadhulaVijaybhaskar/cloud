import { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import Card from '../../components/Card';
import Button from '../../components/Button';
import Modal from '../../components/Modal';

export default function AdminTenants() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTenant, setNewTenant] = useState({ name: '', email: '' });

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setTenants([
        { 
          workspace_id: '123e4567-e89b-12d3-a456-426614174000', 
          name: 'Demo Workspace', 
          owner_email: 'demo@naksha.test', 
          db_size: '10MB', 
          created_at: '2024-01-15',
          status: 'active',
          users: 25,
          projects: 5
        },
        { 
          workspace_id: '456e7890-e12b-34d5-a678-901234567890', 
          name: 'Production App', 
          owner_email: 'admin@company.com', 
          db_size: '2.5GB', 
          created_at: '2024-01-10',
          status: 'active',
          users: 150,
          projects: 12
        },
        { 
          workspace_id: '789e0123-e45b-67d8-a901-234567890123', 
          name: 'Test Environment', 
          owner_email: 'test@example.com', 
          db_size: '500MB', 
          created_at: '2024-01-08',
          status: 'suspended',
          users: 5,
          projects: 2
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredTenants = tenants.filter(tenant =>
    tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tenant.owner_email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'suspended': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleSuspend = async (id) => {
    if (confirm('Are you sure you want to suspend this workspace?')) {
      try {
        // API call to suspend
        setTenants(prev => prev.map(t => 
          t.workspace_id === id ? { ...t, status: 'suspended' } : t
        ));
      } catch (err) {
        alert('Failed to suspend workspace');
      }
    }
  };

  const handleActivate = async (id) => {
    try {
      // API call to activate
      setTenants(prev => prev.map(t => 
        t.workspace_id === id ? { ...t, status: 'active' } : t
      ));
    } catch (err) {
      alert('Failed to activate workspace');
    }
  };

  const handleBackup = (id) => {
    alert(`Starting backup for workspace ${id}`);
  };

  const handleCreateTenant = async () => {
    try {
      const tenant = {
        workspace_id: Date.now().toString(),
        ...newTenant,
        owner_email: newTenant.email,
        db_size: '0MB',
        created_at: new Date().toISOString().split('T')[0],
        status: 'active',
        users: 0,
        projects: 0
      };
      setTenants([tenant, ...tenants]);
      setShowCreateModal(false);
      setNewTenant({ name: '', email: '' });
    } catch (err) {
      alert('Failed to create workspace');
    }
  };

  return (
    <Layout title="Admin - Tenants">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Tenant Management</h1>
            <p className="mt-1 text-sm text-gray-500">Manage workspaces and tenant accounts</p>
          </div>
          <Button onClick={() => setShowCreateModal(true)} className="mt-4 sm:mt-0">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Workspace
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Total Workspaces</p>
              <p className="text-2xl font-bold">{tenants.length}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Active</p>
              <p className="text-2xl font-bold">{tenants.filter(t => t.status === 'active').length}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-red-500 to-red-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Suspended</p>
              <p className="text-2xl font-bold">{tenants.filter(t => t.status === 'suspended').length}</p>
            </div>
          </Card>
          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <div className="text-center">
              <p className="text-sm opacity-90">Total Users</p>
              <p className="text-2xl font-bold">{tenants.reduce((sum, t) => sum + t.users, 0)}</p>
            </div>
          </Card>
        </div>

        {/* Search */}
        <Card>
          <div className="relative max-w-md">
            <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search workspaces..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </Card>

        {/* Tenants Table */}
        <Card>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse flex items-center space-x-4 p-4">
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/6"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Workspace</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Owner</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Users</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DB Size</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTenants.map((tenant) => (
                    <tr key={tenant.workspace_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{tenant.name}</div>
                          <div className="text-sm text-gray-500">{tenant.workspace_id}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {tenant.owner_email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(tenant.status)}`}>
                          {tenant.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {tenant.users}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {tenant.db_size}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {tenant.created_at}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex space-x-2">
                          {tenant.status === 'active' ? (
                            <Button
                              size="sm"
                              variant="danger"
                              onClick={() => handleSuspend(tenant.workspace_id)}
                            >
                              Suspend
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              variant="success"
                              onClick={() => handleActivate(tenant.workspace_id)}
                            >
                              Activate
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleBackup(tenant.workspace_id)}
                          >
                            Backup
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!loading && filteredTenants.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No workspaces found</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating a new workspace</p>
            </div>
          )}
        </Card>
      </div>

      {/* Create Workspace Modal */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Workspace">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Workspace Name
            </label>
            <input
              type="text"
              value={newTenant.name}
              onChange={(e) => setNewTenant({ ...newTenant, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter workspace name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Owner Email
            </label>
            <input
              type="email"
              value={newTenant.email}
              onChange={(e) => setNewTenant({ ...newTenant, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter owner email"
            />
          </div>
          <div className="flex space-x-3 pt-4">
            <Button 
              onClick={handleCreateTenant} 
              disabled={!newTenant.name.trim() || !newTenant.email.trim()} 
              className="flex-1"
            >
              Create Workspace
            </Button>
            <Button 
              variant="secondary" 
              onClick={() => setShowCreateModal(false)} 
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
}
