import React, { useState } from 'react';
import SchemaVisualizer from '../launchpad/components/SchemaVisualizer';
import TableGrid from '../launchpad/components/TableGrid';

const DataStudio = () => {
  const [activeTab, setActiveTab] = useState('schema');
  const [selectedTable, setSelectedTable] = useState('users');

  const tabs = [
    { id: 'schema', label: 'Schema', icon: '🗂️' },
    { id: 'data', label: 'Data', icon: '📊' },
    { id: 'sql', label: 'SQL Editor', icon: '💻' },
    { id: 'backup', label: 'Backup', icon: '💾' },
    { id: 'migrations', label: 'Migrations', icon: '🔄' }
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="border-b border-gray-800">
        <div className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {activeTab === 'schema' && <SchemaVisualizer />}
        
        {activeTab === 'data' && (
          <div>
            <div className="mb-4">
              <select
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                className="bg-gray-800 text-white px-3 py-2 rounded border border-gray-700"
              >
                <option value="users">users</option>
                <option value="projects">projects</option>
                <option value="tasks">tasks</option>
              </select>
            </div>
            <TableGrid tableName={selectedTable} />
          </div>
        )}

        {activeTab === 'sql' && (
          <div className="bg-gray-900 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">SQL Editor</h3>
            <textarea
              className="w-full h-64 bg-gray-800 text-white p-4 rounded border border-gray-700 font-mono"
              placeholder="SELECT * FROM users;"
            />
            <button className="mt-4 px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700">
              Execute Query
            </button>
          </div>
        )}

        {activeTab === 'backup' && (
          <div className="bg-gray-900 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Database Backups</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded">
                <div>
                  <div className="font-medium">backup_1703123456</div>
                  <div className="text-sm text-gray-400">25.6 MB • Jan 1, 2024</div>
                </div>
                <button className="px-3 py-1 bg-violet-600 text-white rounded text-sm">
                  Restore
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'migrations' && (
          <div className="bg-gray-900 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Database Migrations</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded">
                <div>
                  <div className="font-medium">001_initial_schema</div>
                  <div className="text-sm text-gray-400">Applied • Jan 1, 2024</div>
                </div>
                <span className="px-2 py-1 bg-green-600 text-white rounded text-xs">
                  Applied
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataStudio;