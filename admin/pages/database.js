import React, { useState } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';

export default function Database() {
  const [activeTab, setActiveTab] = useState('tables');
  const [tables] = useState([
    { name: 'users', rows: 1247, size: '2.4 MB', type: 'table' },
    { name: 'posts', rows: 3421, size: '5.1 MB', type: 'table' },
    { name: 'embeddings', rows: 8932, size: '45.2 MB', type: 'vector' },
    { name: 'user_stats', rows: 1247, size: '890 KB', type: 'view' }
  ]);

  const tabs = [
    { id: 'tables', name: 'Tables', count: tables.filter(t => t.type === 'table').length },
    { id: 'views', name: 'Views', count: tables.filter(t => t.type === 'view').length },
    { id: 'vectors', name: 'Vector Indexes', count: tables.filter(t => t.type === 'vector').length },
    { id: 'functions', name: 'Functions', count: 12 },
    { id: 'triggers', name: 'Triggers', count: 5 }
  ];

  return React.createElement(Layout, { title: 'Database' },
    React.createElement('div', { style: { display: 'flex', height: '100vh' } },
      React.createElement('div', { style: { width: '320px', backgroundColor: 'white', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column' } },
        React.createElement('div', { style: { padding: '16px', borderBottom: '1px solid #e5e7eb' } },
          React.createElement('div', { style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' } },
            React.createElement('h2', { style: { fontSize: '18px', fontWeight: '600', color: '#111827' } }, 'Schema Designer'),
            React.createElement(Button, { size: 'sm' }, '🧠 AI Assistant')
          ),
          React.createElement('div', { style: { marginBottom: '16px' } },
            React.createElement('label', { style: { display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' } }, 'Database Engine'),
            React.createElement('select', { style: { width: '100%', border: '1px solid #d1d5db', borderRadius: '4px', padding: '8px 12px', fontSize: '14px' } },
              React.createElement('option', null, 'PostgreSQL (Primary)'),
              React.createElement('option', null, 'SQLite (Local)'),
              React.createElement('option', null, 'DuckDB (Analytics)'),
              React.createElement('option', null, 'VectorDB (Embeddings)')
            )
          ),
          React.createElement('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '4px' } },
            tabs.map((tab) =>
              React.createElement('button', {
                key: tab.id,
                onClick: () => setActiveTab(tab.id),
                style: {
                  padding: '4px 12px',
                  fontSize: '12px',
                  fontWeight: '500',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: activeTab === tab.id ? '#dcfce7' : 'transparent',
                  color: activeTab === tab.id ? '#15803d' : '#6b7280',
                  cursor: 'pointer'
                }
              }, `${tab.name} (${tab.count})`)
            )
          )
        ),
        React.createElement('div', { style: { flex: 1, overflowY: 'auto', padding: '16px' } },
          React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: '8px' } },
            tables.filter(t => activeTab === 'tables' ? t.type === 'table' : activeTab === 'vectors' ? t.type === 'vector' : activeTab === 'views' ? t.type === 'view' : true).map((table) =>
              React.createElement('div', {
                key: table.name,
                style: {
                  padding: '12px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: 'white'
                }
              },
                React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
                  React.createElement('div', {
                    style: {
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: table.type === 'vector' ? '#8b5cf6' : table.type === 'view' ? '#3b82f6' : '#10b981'
                    }
                  }),
                  React.createElement('span', { style: { fontWeight: '500', fontSize: '14px' } }, table.name)
                ),
                React.createElement('div', { style: { fontSize: '12px', color: '#6b7280', marginTop: '4px', marginLeft: '16px' } },
                  `${table.rows.toLocaleString()} rows • ${table.size}`
                )
              )
            )
          ),
          React.createElement(Button, { style: { width: '100%', marginTop: '16px' }, size: 'sm' },
            `+ Create ${activeTab === 'tables' ? 'Table' : activeTab === 'vectors' ? 'Vector Index' : 'View'}`
          )
        )
      ),
      React.createElement('div', { style: { flex: 1, display: 'flex', flexDirection: 'column' } },
        React.createElement('div', { style: { backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '24px' } },
          React.createElement('div', { style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between' } },
            React.createElement('div', null,
              React.createElement('h1', { style: { fontSize: '20px', fontWeight: '600', color: '#111827' } }, 'users'),
              React.createElement('p', { style: { fontSize: '14px', color: '#6b7280' } }, 'PostgreSQL table • 1,247 rows • 2.4 MB')
            ),
            React.createElement('div', { style: { display: 'flex', gap: '12px' } },
              React.createElement(Button, { variant: 'secondary', size: 'sm' }, '🔍 Query'),
              React.createElement(Button, { variant: 'secondary', size: 'sm' }, '📊 Analytics'),
              React.createElement(Button, { size: 'sm' }, '✏️ Edit Schema')
            )
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', borderBottom: '1px solid #e5e7eb' } },
          React.createElement('div', { style: { display: 'flex' } },
            React.createElement('button', { style: { padding: '8px 16px', fontSize: '14px', fontWeight: '500', color: '#059669', borderBottom: '2px solid #059669', border: 'none', backgroundColor: 'transparent' } }, 'Data'),
            React.createElement('button', { style: { padding: '8px 16px', fontSize: '14px', fontWeight: '500', color: '#6b7280', border: 'none', backgroundColor: 'transparent' } }, 'Schema'),
            React.createElement('button', { style: { padding: '8px 16px', fontSize: '14px', fontWeight: '500', color: '#6b7280', border: 'none', backgroundColor: 'transparent' } }, 'Indexes'),
            React.createElement('button', { style: { padding: '8px 16px', fontSize: '14px', fontWeight: '500', color: '#6b7280', border: 'none', backgroundColor: 'transparent' } }, 'Policies (RLS)'),
            React.createElement('button', { style: { padding: '8px 16px', fontSize: '14px', fontWeight: '500', color: '#6b7280', border: 'none', backgroundColor: 'transparent' } }, 'Relationships')
          )
        ),
        React.createElement('div', { style: { backgroundColor: '#eff6ff', borderBottom: '1px solid #bfdbfe', padding: '16px' } },
          React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '12px' } },
            React.createElement('div', { style: { width: '32px', height: '32px', backgroundColor: '#dbeafe', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' } },
              React.createElement('span', { style: { color: '#2563eb' } }, '🧠')
            ),
            React.createElement('div', { style: { flex: 1 } },
              React.createElement('p', { style: { fontSize: '14px', fontWeight: '500', color: '#1e3a8a' } }, 'AI Suggestions'),
              React.createElement('p', { style: { fontSize: '12px', color: '#1d4ed8' } }, 'Add UUID primary key • Create email unique index • Generate RLS policy for user isolation')
            ),
            React.createElement(Button, { size: 'sm', variant: 'secondary' }, 'Apply All')
          )
        ),
        React.createElement('div', { style: { flex: 1, backgroundColor: '#f9fafb', padding: '24px' } },
          React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' } },
            React.createElement('div', { style: { overflowX: 'auto' } },
              React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
                React.createElement('thead', { style: { backgroundColor: '#f9fafb' } },
                  React.createElement('tr', null,
                    React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } },
                      'id ', React.createElement('span', { style: { color: '#3b82f6' } }, '(int8)')
                    ),
                    React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } },
                      'email ', React.createElement('span', { style: { color: '#10b981' } }, '(text)')
                    ),
                    React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } },
                      'name ', React.createElement('span', { style: { color: '#10b981' } }, '(text)')
                    ),
                    React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } },
                      'created_at ', React.createElement('span', { style: { color: '#8b5cf6' } }, '(timestamptz)')
                    ),
                    React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Actions')
                  )
                ),
                React.createElement('tbody', { style: { backgroundColor: 'white' } },
                  [
                    { id: 1, email: 'john@example.com', name: 'John Doe', created_at: '2024-01-15T10:30:00Z' },
                    { id: 2, email: 'jane@example.com', name: 'Jane Smith', created_at: '2024-01-14T15:45:00Z' },
                    { id: 3, email: 'bob@example.com', name: 'Bob Johnson', created_at: '2024-01-13T09:20:00Z' }
                  ].map((row) =>
                    React.createElement('tr', { key: row.id, style: { borderTop: '1px solid #e5e7eb' } },
                      React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, row.id),
                      React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, row.email),
                      React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, row.name),
                      React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#6b7280' } }, new Date(row.created_at).toLocaleString()),
                      React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#6b7280' } },
                        React.createElement('div', { style: { display: 'flex', gap: '8px' } },
                          React.createElement('button', { style: { color: '#2563eb', backgroundColor: 'transparent', border: 'none', cursor: 'pointer' } }, 'Edit'),
                          React.createElement('button', { style: { color: '#dc2626', backgroundColor: 'transparent', border: 'none', cursor: 'pointer' } }, 'Delete')
                        )
                      )
                    )
                  )
                )
              )
            )
          )
        )
      )
    )
  );
}