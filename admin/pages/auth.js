import React from 'react';
import Layout from '../components/Layout';

export default function Authentication() {
  const [activeTab, setActiveTab] = React.useState('users');

  const tabStyle = {
    padding: '12px 24px',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    borderBottom: '2px solid transparent',
    fontSize: '0.875rem'
  };

  const activeTabStyle = {
    ...tabStyle,
    borderBottomColor: '#3b82f6',
    color: '#3b82f6'
  };

  return React.createElement(Layout, { title: 'Authentication' },
    React.createElement('div', { style: { padding: '24px' } },
      // Header
      React.createElement('div', { style: { marginBottom: '32px' } },
        React.createElement('h1', { style: { fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '8px' } }, 'Authentication'),
        React.createElement('p', { style: { color: '#6b7280' } }, 'Manage your project\'s users and authentication settings')
      ),

      // Tabs
      React.createElement('div', { style: { borderBottom: '1px solid #e5e7eb', marginBottom: '24px' } },
        React.createElement('div', { style: { display: 'flex' } },
          React.createElement('button', {
            style: activeTab === 'users' ? activeTabStyle : tabStyle,
            onClick: () => setActiveTab('users')
          }, 'Users'),
          React.createElement('button', {
            style: activeTab === 'policies' ? activeTabStyle : tabStyle,
            onClick: () => setActiveTab('policies')
          }, 'Policies'),
          React.createElement('button', {
            style: activeTab === 'settings' ? activeTabStyle : tabStyle,
            onClick: () => setActiveTab('settings')
          }, 'Settings')
        )
      ),

      // Content
      activeTab === 'users' && React.createElement('div', null,
        React.createElement('div', { 
          style: { 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '24px' 
          } 
        },
          React.createElement('h2', { style: { fontSize: '1.125rem', fontWeight: '500' } }, 'Users'),
          React.createElement('button', { 
            style: { 
              padding: '8px 16px', 
              background: '#3b82f6', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              fontSize: '0.875rem', 
              cursor: 'pointer' 
            } 
          }, 'Add user')
        ),

        React.createElement('div', { 
          style: { 
            background: 'white', 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            overflow: 'hidden' 
          } 
        },
          React.createElement('table', { style: { width: '100%', fontSize: '0.875rem' } },
            React.createElement('thead', { style: { background: '#f9fafb' } },
              React.createElement('tr', null,
                React.createElement('th', { style: { padding: '12px 16px', textAlign: 'left', fontWeight: '500' } }, 'Email'),
                React.createElement('th', { style: { padding: '12px 16px', textAlign: 'left', fontWeight: '500' } }, 'Created'),
                React.createElement('th', { style: { padding: '12px 16px', textAlign: 'left', fontWeight: '500' } }, 'Last Sign In'),
                React.createElement('th', { style: { padding: '12px 16px', textAlign: 'left', fontWeight: '500' } }, 'Actions')
              )
            ),
            React.createElement('tbody', null,
              React.createElement('tr', null,
                React.createElement('td', { 
                  style: { 
                    padding: '32px', 
                    textAlign: 'center', 
                    color: '#6b7280' 
                  }, 
                  colSpan: 4 
                },
                  React.createElement('div', { style: { fontSize: '3rem', marginBottom: '16px' } }, '👥'),
                  React.createElement('p', null, 'No users yet'),
                  React.createElement('p', { style: { fontSize: '0.75rem', marginTop: '4px' } }, 'Users will appear here when they sign up')
                )
              )
            )
          )
        )
      ),

      activeTab === 'policies' && React.createElement('div', null,
        React.createElement('h2', { style: { fontSize: '1.125rem', fontWeight: '500', marginBottom: '16px' } }, 'Row Level Security Policies'),
        React.createElement('div', { 
          style: { 
            background: '#fef3c7', 
            border: '1px solid #f59e0b', 
            borderRadius: '8px', 
            padding: '16px', 
            marginBottom: '24px' 
          } 
        },
          React.createElement('p', { style: { fontSize: '0.875rem', color: '#92400e' } }, 'RLS is not enabled. Enable Row Level Security to create policies.')
        ),
        React.createElement('button', { 
          style: { 
            padding: '8px 16px', 
            background: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            fontSize: '0.875rem', 
            cursor: 'pointer' 
          } 
        }, 'Enable RLS')
      ),

      activeTab === 'settings' && React.createElement('div', null,
        React.createElement('h2', { style: { fontSize: '1.125rem', fontWeight: '500', marginBottom: '24px' } }, 'Authentication Settings'),
        
        React.createElement('div', { style: { background: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('h3', { style: { fontSize: '1rem', fontWeight: '500', marginBottom: '16px' } }, 'General Settings'),
          
          React.createElement('div', { style: { marginBottom: '20px' } },
            React.createElement('label', { style: { display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '8px' } }, 'Site URL'),
            React.createElement('input', { 
              type: 'text', 
              defaultValue: 'http://localhost:3000',
              style: { 
                width: '100%', 
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '4px', 
                fontSize: '0.875rem' 
              } 
            })
          ),

          React.createElement('div', { style: { marginBottom: '20px' } },
            React.createElement('label', { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
              React.createElement('input', { type: 'checkbox', defaultChecked: true }),
              React.createElement('span', { style: { fontSize: '0.875rem' } }, 'Enable email confirmations')
            )
          ),

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
          }, 'Save')
        )
      )
    )
  );
}