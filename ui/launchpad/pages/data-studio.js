import { useState, useEffect } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const menuItems = {
  'Database Management': {
    items: [
      { name: 'Schema Visualizer', action: 'schema-viz' },
      { name: 'Tables', action: 'tables' },
      { name: 'Functions', action: 'functions' },
      { name: 'Triggers', action: 'triggers' },
      { name: 'Enumerated Types', action: 'enums' },
      { name: 'Extensions', action: 'extensions' },
      { name: 'Indexes', action: 'indexes' },
      { name: 'Publications', action: 'publications' },
      { name: 'Replication', action: 'replication' }
    ]
  },
  'Configuration': {
    items: [
      { name: 'Roles', action: 'roles' },
      { name: 'Policies', action: 'policies' },
      { name: 'Settings', action: 'settings' }
    ]
  },
  'Platform': {
    items: [
      { name: 'Backups', action: 'backups' },
      { name: 'Migrations', action: 'migrations' },
      { name: 'Wrappers', action: 'wrappers' },
      { name: 'Webhooks', action: 'webhooks' }
    ]
  },
  'Tools': {
    items: [
      { name: 'Security Advisor', action: 'security-advisor' },
      { name: 'Performance Advisor', action: 'performance-advisor' },
      { name: 'Query Performance', action: 'query-performance' }
    ]
  }
};

const Sidebar = ({ activeSection, onSectionChange, isAIMode, onModeToggle }) => {
  return (
    <div className="w-64 bg-card/50 border-r border-border/50 h-full overflow-y-auto">

      
      {Object.entries(menuItems).map(([category, { items }]) => (
        <div key={category} className="p-4">
          <h3 className="text-sm font-semibold text-muted-foreground mb-2">
            {category}
          </h3>
          <div className="space-y-1">
            {items.map((item) => (
              <button
                key={item.action}
                onClick={() => onSectionChange(item.action)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeSection === item.action
                    ? 'bg-primary/20 text-primary'
                    : 'hover:bg-accent/50'
                }`}
              >
                {item.name}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

const ContentArea = ({ activeSection, isAIMode, tables, selectedTable, tableData, onTableSelect }) => {
  const handleAction = (action) => {
    const mode = isAIMode ? 'AI' : 'Manual';
    alert(`${mode} ${action} activated! This would provide ${isAIMode ? 'AI-powered' : 'traditional'} functionality.`);
  };

  if (activeSection === 'tables') {
    return (
      <div className="flex-1 p-6">

        
        <div className="space-y-6">
          <div className="flex justify-between items-center border-b border-border/50 pb-4">
            <div className="flex gap-4">
              {tables.map((table) => (
                <button
                  key={table.name}
                  onClick={() => onTableSelect(table.name)}
                  className={`px-6 py-3 rounded-lg text-base font-medium transition-colors ${
                    selectedTable === table.name
                      ? 'bg-primary/20 text-primary border border-primary/50'
                      : 'hover:bg-accent/50'
                  }`}
                >
                  {table.name}
                </button>
              ))}
            </div>
            <button 
              onClick={() => handleAction('Create Table')}
              className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
            >
              {isAIMode ? 'AI Create Table' : 'Create Table'}
            </button>
          </div>
          
          <div>
            {selectedTable ? (
              <div className="quantum-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold">{selectedTable}</h3>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => document.querySelector('.floating-atom-chat button').click()}
                      className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded text-sm hover:bg-emerald-500/30"
                    >
                      Ask AI
                    </button>
                  </div>
                </div>
                {tableData.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          {tables.find(t => t.name === selectedTable)?.columns.map((col) => (
                            <th key={col} className="text-left p-2 font-medium">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {tableData.map((row, idx) => (
                          <tr key={idx} className="border-b border-border/50 hover:bg-accent/20">
                            {row.map((cell, cellIdx) => (
                              <td key={cellIdx} className="p-2">{cell}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : (
              <div className="quantum-card p-12 text-center">
                <h3 className="text-xl font-semibold mb-2">Select a Table</h3>
                <p className="text-muted-foreground">Choose a table to view and manage</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  const sectionConfig = {
    'schema-viz': { title: 'Schema Visualizer', desc: 'Visual database schema designer' },
    'functions': { title: 'Functions', desc: 'Database functions and procedures' },
    'triggers': { title: 'Triggers', desc: 'Database triggers and events' },
    'enums': { title: 'Enumerated Types', desc: 'Custom enumerated data types' },
    'extensions': { title: 'Extensions', desc: 'Database extensions and plugins' },
    'indexes': { title: 'Indexes', desc: 'Database indexes and performance' },
    'publications': { title: 'Publications', desc: 'Logical replication publications' },
    'replication': { title: 'Replication', desc: 'Database replication settings' },
    'roles': { title: 'Roles', desc: 'User roles and permissions' },
    'policies': { title: 'Policies', desc: 'Row Level Security policies' },
    'settings': { title: 'Settings', desc: 'Database configuration' },
    'backups': { title: 'Backups', desc: 'Database backups and restore' },
    'migrations': { title: 'Migrations', desc: 'Schema migrations' },
    'wrappers': { title: 'Wrappers', desc: 'Foreign data wrappers' },
    'webhooks': { title: 'Webhooks', desc: 'Database webhooks' },
    'security-advisor': { title: 'Security Advisor', desc: 'Security recommendations' },
    'performance-advisor': { title: 'Performance Advisor', desc: 'Performance optimization' },
    'query-performance': { title: 'Query Performance', desc: 'Query analysis and optimization' }
  };

  const config = sectionConfig[activeSection] || { title: 'Data Studio', desc: 'Database management' };

  return (
    <div className="flex-1 p-6">
      <div className="quantum-card p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground mb-4">{config.desc}</p>
        <button 
          onClick={() => handleAction(config.title)}
          className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
        >
          {isAIMode ? 'AI Configure' : 'Configure'}
        </button>
      </div>
    </div>
  );
};

export default function DataStudio() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState([]);

  const [isAIMode, setIsAIMode] = useState(true);
  const [activeSection, setActiveSection] = useState('tables');

  useEffect(() => {
    loadTables();
  }, []);

  const loadTables = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/data/tables');
      if (response.ok) {
        const data = await response.json();
        setTables(data.tables || []);
      } else {
        throw new Error('Backend not available');
      }
    } catch (error) {
      setTables([
        { name: 'Users', rows: 1247, columns: ['id', 'email', 'created_at', 'last_login'] },
        { name: 'Projects', rows: 89, columns: ['id', 'name', 'status', 'owner_id'] },
        { name: 'Analytics', rows: 15420, columns: ['id', 'event', 'user_id', 'timestamp'] },
        { name: 'Deployments', rows: 342, columns: ['id', 'project_id', 'status', 'deployed_at'] }
      ]);
    }

  };

  const loadTableData = async (tableName) => {
    setSelectedTable(tableName);
    try {
      const response = await fetch('http://localhost:8001/api/data/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql: `SELECT * FROM ${tableName} LIMIT 50` })
      });
      if (response.ok) {
        const data = await response.json();
        setTableData(data.rows || []);
      }
    } catch (error) {
      const mockData = {
        Users: [
          ['1', 'admin@atom.cloud', '2024-01-15', '2024-01-20'],
          ['2', 'user@example.com', '2024-01-16', '2024-01-19']
        ],
        Projects: [
          ['1', 'E-commerce Platform', 'active', '1'],
          ['2', 'Analytics Dashboard', 'learning', '1']
        ]
      };
      setTableData(mockData[tableName] || []);
    }
  };



  return (
    <LaunchpadLayout>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20 flex">
        <Sidebar 
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          isAIMode={isAIMode}
          onModeToggle={() => setIsAIMode(!isAIMode)}
        />
        <ContentArea 
          activeSection={activeSection}
          isAIMode={isAIMode}
          tables={tables}
          selectedTable={selectedTable}
          tableData={tableData}
          onTableSelect={loadTableData}
        />
      </div>
    </LaunchpadLayout>
  );
}