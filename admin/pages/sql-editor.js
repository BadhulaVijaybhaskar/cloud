import React from 'react';
import Layout from '../components/Layout';

export default function SQLEditor() {
  const [query, setQuery] = React.useState('-- Welcome to the SQL Editor\n-- Write your queries here\n\nSELECT * FROM users LIMIT 10;');

  return React.createElement(Layout, { title: 'SQL Editor' },
    React.createElement('div', { style: { display: 'flex', height: '100vh', flexDirection: 'column' } },
      // Toolbar
      React.createElement('div', { 
        style: { 
          background: 'white', 
          borderBottom: '1px solid #e5e7eb', 
          padding: '12px 16px', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px' 
        } 
      },
        React.createElement('button', { 
          style: { 
            padding: '8px 16px', 
            background: '#10b981', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            fontSize: '0.875rem', 
            cursor: 'pointer' 
          } 
        }, '▶ Run'),
        React.createElement('button', { 
          style: { 
            padding: '8px 16px', 
            background: 'white', 
            color: '#374151', 
            border: '1px solid #d1d5db', 
            borderRadius: '4px', 
            fontSize: '0.875rem', 
            cursor: 'pointer' 
          } 
        }, 'Save'),
        React.createElement('select', { 
          style: { 
            padding: '8px 12px', 
            border: '1px solid #d1d5db', 
            borderRadius: '4px', 
            fontSize: '0.875rem', 
            background: 'white' 
          } 
        },
          React.createElement('option', null, 'public')
        )
      ),

      React.createElement('div', { style: { display: 'flex', flex: 1 } },
        // Query Editor
        React.createElement('div', { style: { flex: 1, display: 'flex', flexDirection: 'column' } },
          React.createElement('div', { 
            style: { 
              background: '#f8f9fa', 
              padding: '8px 16px', 
              borderBottom: '1px solid #e5e7eb', 
              fontSize: '0.875rem', 
              color: '#6b7280' 
            } 
          }, 'Query'),
          React.createElement('textarea', {
            value: query,
            onChange: (e) => setQuery(e.target.value),
            style: {
              flex: 1,
              padding: '16px',
              border: 'none',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              background: '#1e293b',
              color: '#e2e8f0',
              resize: 'none',
              outline: 'none'
            },
            placeholder: 'Write your SQL query here...'
          })
        ),

        // Results Panel
        React.createElement('div', { 
          style: { 
            width: '50%', 
            borderLeft: '1px solid #e5e7eb', 
            display: 'flex', 
            flexDirection: 'column' 
          } 
        },
          React.createElement('div', { 
            style: { 
              background: '#f8f9fa', 
              padding: '8px 16px', 
              borderBottom: '1px solid #e5e7eb', 
              fontSize: '0.875rem', 
              color: '#6b7280' 
            } 
          }, 'Results'),
          React.createElement('div', { 
            style: { 
              flex: 1, 
              padding: '32px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              textAlign: 'center' 
            } 
          },
            React.createElement('div', null,
              React.createElement('div', { style: { fontSize: '3rem', marginBottom: '16px' } }, '📊'),
              React.createElement('h3', { style: { fontSize: '1rem', fontWeight: '500', color: '#111827', marginBottom: '8px' } }, 'Run a query to see results'),
              React.createElement('p', { style: { fontSize: '0.875rem', color: '#6b7280' } }, 'Click the Run button to execute your SQL query')
            )
          )
        )
      ),

      // Status Bar
      React.createElement('div', { 
        style: { 
          background: '#f8f9fa', 
          borderTop: '1px solid #e5e7eb', 
          padding: '8px 16px', 
          fontSize: '0.75rem', 
          color: '#6b7280', 
          display: 'flex', 
          justifyContent: 'space-between' 
        } 
      },
        React.createElement('span', null, 'Ready'),
        React.createElement('span', null, 'Line 1, Column 1')
      )
    )
  );
}