import React, { useState } from 'react';
import Layout from '../components/Layout';

export default function Realtime() {
  const [channels] = useState([
    { name: 'public:messages', connections: 45, messages: 1247, status: 'active' },
    { name: 'public:notifications', connections: 23, messages: 892, status: 'active' }
  ]);

  return React.createElement(Layout, { title: 'Realtime' },
    React.createElement('div', { style: { padding: '32px', maxWidth: '1152px' } },
      React.createElement('div', { style: { marginBottom: '32px' } },
        React.createElement('h1', { style: { fontSize: '24px', fontWeight: '400', color: '#111827', marginBottom: '8px' } }, 'Realtime'),
        React.createElement('p', { style: { color: '#4b5563' } }, 'Listen to database changes in realtime')
      ),
      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '32px' } },
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Active Connections'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '68')
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Messages (24h)'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '2,139')
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Channels'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, channels.length)
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Avg Latency'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '45ms')
          )
        )
      ),
      React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' } },
        React.createElement('div', { style: { padding: '16px 24px', borderBottom: '1px solid #e5e7eb' } },
          React.createElement('h3', { style: { fontSize: '18px', fontWeight: '500', color: '#111827' } }, 'Channels')
        ),
        React.createElement('div', { style: { overflowX: 'auto' } },
          React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
            React.createElement('thead', { style: { backgroundColor: '#f9fafb' } },
              React.createElement('tr', null,
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Channel'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Status'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Connections'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Messages'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Actions')
              )
            ),
            React.createElement('tbody', { style: { backgroundColor: 'white' } },
              channels.map((channel) =>
                React.createElement('tr', { key: channel.name, style: { borderTop: '1px solid #e5e7eb' } },
                  React.createElement('td', { style: { padding: '16px 24px' } },
                    React.createElement('div', { style: { display: 'flex', alignItems: 'center' } },
                      React.createElement('div', { style: { width: '32px', height: '32px', backgroundColor: '#f3e8ff', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' } },
                        React.createElement('div', { style: { width: '8px', height: '8px', backgroundColor: '#7c3aed', borderRadius: '50%' } })
                      ),
                      React.createElement('div', { style: { marginLeft: '12px' } },
                        React.createElement('div', { style: { fontSize: '14px', fontWeight: '500', color: '#111827' } }, channel.name)
                      )
                    )
                  ),
                  React.createElement('td', { style: { padding: '16px 24px' } },
                    React.createElement('span', { style: { padding: '4px 8px', fontSize: '12px', fontWeight: '500', borderRadius: '9999px', backgroundColor: '#dcfce7', color: '#166534' } }, channel.status)
                  ),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, channel.connections),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, channel.messages.toLocaleString()),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#6b7280' } },
                    React.createElement('button', { style: { color: '#9ca3af', backgroundColor: 'transparent', border: 'none', cursor: 'pointer' } },
                      React.createElement('svg', { style: { width: '16px', height: '16px' }, fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
                        React.createElement('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: 2, d: 'M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z' })
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