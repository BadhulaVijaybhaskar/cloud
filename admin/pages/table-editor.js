import React from 'react';
import Layout from '../components/Layout';

export default function TableEditor() {
  return React.createElement(Layout, { title: 'Table Editor' },
    React.createElement('div', { style: { display: 'flex', height: '100vh' } },
      // Sidebar
      React.createElement('div', { 
        style: { 
          width: '320px', 
          background: 'white', 
          borderRight: '1px solid #e5e7eb', 
          display: 'flex', 
          flexDirection: 'column' 
        } 
      },
        React.createElement('div', { style: { padding: '16px', borderBottom: '1px solid #e5e7eb' } },
          React.createElement('div', { style: { marginBottom: '16px' } },
            React.createElement('select', { 
              style: { 
                width: '100%', 
                border: '1px solid #d1d5db', 
                borderRadius: '4px', 
                padding: '8px 12px', 
                fontSize: '0.875rem', 
                background: 'white' 
              } 
            },
              React.createElement('option', null, 'schema public'),
              React.createElement('option', null, 'schema auth')
            )
          ),
          React.createElement('button', { 
            style: { 
              width: '100%', 
              textAlign: 'left', 
              padding: '8px 12px', 
              fontSize: '0.875rem', 
              color: '#374151', 
              background: 'transparent', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer' 
            } 
          }, 'New table')
        ),
        
        // Search
        React.createElement('div', { style: { padding: '0 16px', marginBottom: '16px' } },
          React.createElement('div', { style: { position: 'relative' } },
            React.createElement('input', {
              type: 'text',
              placeholder: 'Search tables...',
              style: {
                width: '100%',
                padding: '8px 12px 8px 32px',
                fontSize: '0.875rem',
                border: '1px solid #d1d5db',
                borderRadius: '4px'
              }
            }),
            React.createElement('span', { 
              style: { 
                position: 'absolute', 
                left: '8px', 
                top: '8px', 
                color: '#9ca3af' 
              } 
            }, '🔍')
          )
        ),
        
        // No Tables Message
        React.createElement('div', { 
          style: { 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            padding: '32px', 
            textAlign: 'center' 
          } 
        },
          React.createElement('div', { style: { color: '#9ca3af', marginBottom: '16px', fontSize: '3rem' } }, '📋'),
          React.createElement('h3', { style: { fontSize: '0.875rem', fontWeight: '500', color: '#111827', marginBottom: '4px' } }, 'No tables or views'),
          React.createElement('p', { style: { fontSize: '0.75rem', color: '#6b7280', marginBottom: '16px' } }, 'Any tables or views you create will be listed here.'),
          
          React.createElement('div', { style: { fontSize: '0.75rem', color: '#9ca3af' } },
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' } },
              React.createElement('div', { style: { width: '16px', height: '16px', background: '#e5e7eb', borderRadius: '4px' } }),
              React.createElement('span', null, 'postgres_lsn')
            ),
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' } },
              React.createElement('div', { style: { width: '16px', height: '16px', background: '#e5e7eb', borderRadius: '4px' } }),
              React.createElement('span', null, 'postgres_fdw')
            )
          )
        )
      ),

      // Main Content
      React.createElement('div', { style: { flex: 1, display: 'flex', flexDirection: 'column' } },
        // Main Area
        React.createElement('div', { style: { flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' } },
          React.createElement('div', { style: { textAlign: 'center', maxWidth: '400px' } },
            React.createElement('div', { 
              style: { 
                width: '64px', 
                height: '64px', 
                background: '#f3f4f6', 
                borderRadius: '8px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                margin: '0 auto 16px auto',
                fontSize: '2rem'
              } 
            }, '➕'),
            React.createElement('h2', { style: { fontSize: '1.125rem', fontWeight: '500', color: '#111827', marginBottom: '8px' } }, 'Create a table'),
            React.createElement('p', { style: { fontSize: '0.875rem', color: '#6b7280', marginBottom: '24px' } }, 'Design and create a new database table'),
            React.createElement('button', { 
              style: { 
                padding: '8px 16px', 
                background: '#111827', 
                color: 'white', 
                borderRadius: '4px', 
                fontSize: '0.875rem', 
                border: 'none', 
                cursor: 'pointer' 
              } 
            }, 'Create a new table')
          )
        ),
        
        // Recent Items
        React.createElement('div', { style: { borderTop: '1px solid #e5e7eb', padding: '24px' } },
          React.createElement('h3', { style: { fontSize: '0.875rem', fontWeight: '500', color: '#111827', marginBottom: '16px' } }, 'Recent items'),
          React.createElement('div', { style: { textAlign: 'center', padding: '32px 0' } },
            React.createElement('p', { style: { fontSize: '0.875rem', color: '#6b7280' } }, 'No recent items yet'),
            React.createElement('p', { style: { fontSize: '0.75rem', color: '#9ca3af', marginTop: '4px' } }, 'Items will appear here as you browse through your project')
          )
        )
      )
    )
  );
}