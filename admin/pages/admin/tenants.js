import { useState, useEffect } from 'react';
import axios from 'axios';

export default function AdminTenants() {
  const [tenants, setTenants] = useState([]);

  useEffect(() => {
    // Fetch tenants from Hasura or custom endpoint
    // Mock data for now
    setTenants([
      { workspace_id: '123e4567-e89b-12d3-a456-426614174000', name: 'Demo Workspace', owner_email: 'demo@naksha.test', db_size: '10MB', created_at: '2023-01-01' }
    ]);
  }, []);

  const handleSuspend = (id) => {
    // Call suspend script
    alert(`Suspend workspace ${id}`);
  };

  const handleBackup = (id) => {
    // Call backup script
    alert(`Backup workspace ${id}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Admin - Tenants</h1>
        <table className="w-full bg-white rounded shadow">
          <thead>
            <tr className="bg-gray-200">
              <th className="p-4 text-left">Workspace ID</th>
              <th className="p-4 text-left">Name</th>
              <th className="p-4 text-left">Owner Email</th>
              <th className="p-4 text-left">DB Size</th>
              <th className="p-4 text-left">Created At</th>
              <th className="p-4 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((tenant) => (
              <tr key={tenant.workspace_id} className="border-t">
                <td className="p-4">{tenant.workspace_id}</td>
                <td className="p-4">{tenant.name}</td>
                <td className="p-4">{tenant.owner_email}</td>
                <td className="p-4">{tenant.db_size}</td>
                <td className="p-4">{tenant.created_at}</td>
                <td className="p-4 space-x-2">
                  <button
                    onClick={() => handleSuspend(tenant.workspace_id)}
                    className="bg-red-500 text-white px-2 py-1 rounded text-sm"
                  >
                    Suspend
                  </button>
                  <button
                    onClick={() => handleBackup(tenant.workspace_id)}
                    className="bg-blue-500 text-white px-2 py-1 rounded text-sm"
                  >
                    Backup
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
