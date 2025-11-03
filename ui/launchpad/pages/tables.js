import { useState, useEffect } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const databaseStructure = {
  'atom_cloud': {
    schemas: {
      'public': {
        tables: [
          { name: 'users', rows: 1247, columns: ['id', 'email', 'created_at', 'last_login'] },
          { name: 'projects', rows: 89, columns: ['id', 'name', 'status', 'owner_id'] },
          { name: 'analytics', rows: 15420, columns: ['id', 'event', 'user_id', 'timestamp'] },
          { name: 'deployments', rows: 342, columns: ['id', 'project_id', 'status', 'deployed_at'] }
        ]
      },
      'auth': {
        tables: [
          { name: 'sessions', rows: 523, columns: ['id', 'user_id', 'token', 'expires_at'] },
          { name: 'permissions', rows: 45, columns: ['id', 'role', 'resource', 'action'] }
        ]
      }
    }
  }
};

const Explorer = ({ selectedTable, onTableSelect }) => {
  const [expandedItems, setExpandedItems] = useState({ 'atom_cloud': true, 'public': true });
  
  const toggleExpand = (key) => {
    setExpandedItems(prev => ({ ...prev, [key]: !prev[key] }));
  };
  
  return (
    <div className="w-80 bg-card/50 border-r border-border/50 h-full overflow-y-auto">
      <div className="p-4">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          📊 Tables Explorer
        </h3>
        
        {Object.entries(databaseStructure).map(([dbName, db]) => (
          <div key={dbName} className="mb-2">
            <button 
              onClick={() => toggleExpand(dbName)}
              className="flex items-center gap-2 text-sm font-medium hover:bg-accent/20 p-1 rounded w-full text-left"
            >
              <span>{expandedItems[dbName] ? '📂' : '📁'}</span>
              {dbName}
            </button>
            
            {expandedItems[dbName] && (
              <div className="ml-4 mt-1">
                {Object.entries(db.schemas).map(([schemaName, schema]) => (
                  <div key={schemaName} className="mb-2">
                    <button 
                      onClick={() => toggleExpand(schemaName)}
                      className="flex items-center gap-2 text-xs hover:bg-accent/20 p-1 rounded w-full text-left"
                    >
                      <span>{expandedItems[schemaName] ? '📂' : '📁'}</span>
                      {schemaName}
                    </button>
                    
                    {expandedItems[schemaName] && (
                      <div className="ml-4 mt-1 space-y-1">
                        {schema.tables?.map((table) => (
                          <button
                            key={table.name}
                            onClick={() => onTableSelect(table)}
                            className={`flex items-center gap-2 text-xs p-1 rounded w-full text-left ${
                              selectedTable?.name === table.name ? 'bg-primary/20 text-primary' : 'hover:bg-accent/20'
                            }`}
                          >
                            <span>📊</span>
                            {table.name}
                            <span className="text-muted-foreground ml-auto">({table.rows})</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const TableViewer = ({ selectedTable, tableData }) => {
  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-border/50 bg-card/30 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors">
            📊 Browse Data
          </button>
          <button className="px-3 py-2 border border-border rounded-lg hover:bg-accent/50 transition-colors text-sm">
            ➕ Add Row
          </button>
          <button className="px-3 py-2 border border-border rounded-lg hover:bg-accent/50 transition-colors text-sm">
            🗑️ Delete
          </button>
        </div>
        <div className="text-xs text-muted-foreground">
          {selectedTable ? `Table: ${selectedTable.name} (${selectedTable.rows} rows)` : 'No table selected'}
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        {selectedTable ? (
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">Table: {selectedTable.name}</h3>
              <p className="text-sm text-muted-foreground mb-4">{selectedTable.rows} rows</p>
            </div>
            
            {tableData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border border-border/50">
                  <thead>
                    <tr className="border-b border-border bg-accent/20">
                      {selectedTable.columns.map((col) => (
                        <th key={col} className="text-left p-3 font-medium">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.map((row, idx) => (
                      <tr key={idx} className="border-b border-border/30 hover:bg-accent/10">
                        {row.map((cell, cellIdx) => (
                          <td key={cellIdx} className="p-3">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <div className="text-4xl mb-4">📊</div>
                <div>Select a table to view data</div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            <div className="text-4xl mb-4">📊</div>
            <div>Select a table from the explorer</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default function Tables() {
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState([]);

  const handleTableSelect = (table) => {
    setSelectedTable(table);
    
    // Mock data
    const mockData = {
      users: [
        ['1', 'admin@atom.cloud', '2024-01-15', '2024-01-20'],
        ['2', 'user@example.com', '2024-01-16', '2024-01-19'],
        ['3', 'dev@atom.cloud', '2024-01-17', '2024-01-18']
      ],
      projects: [
        ['1', 'E-commerce Platform', 'active', '1'],
        ['2', 'Analytics Dashboard', 'learning', '1'],
        ['3', 'Mobile App', 'planning', '2']
      ]
    };
    
    setTableData(mockData[table.name] || []);
  };

  return (
    <LaunchpadLayout>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20 flex">
        <Explorer 
          selectedTable={selectedTable}
          onTableSelect={handleTableSelect}
        />
        <TableViewer 
          selectedTable={selectedTable}
          tableData={tableData}
        />
      </div>
    </LaunchpadLayout>
  );
}