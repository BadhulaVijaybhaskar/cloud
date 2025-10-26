import React, { useState } from 'react';
import Layout from '../components/Layout';

export default function Storage() {
  const [buckets] = useState([
    { name: 'avatars', size: '2.4 MB', files: 156, public: true, created: '2024-01-15' },
    { name: 'documents', size: '45.2 MB', files: 89, public: false, created: '2024-01-10' }
  ]);

  return React.createElement(Layout, { title: 'Storage' },
    React.createElement('div', { style: { padding: '32px', maxWidth: '1152px' } },
      React.createElement('div', { style: { marginBottom: '32px' } },
        React.createElement('h1', { style: { fontSize: '24px', fontWeight: '400', color: '#111827', marginBottom: '8px' } }, 'Storage'),
        React.createElement('p', { style: { color: '#4b5563' } }, 'Store and serve any type of digital content')
      ),
      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '32px' } },
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Total Storage'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '47.6 MB')
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Total Files'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '245')
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Buckets'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, buckets.length)
          )
        ),
        React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '24px' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', color: '#6b7280', marginBottom: '4px' } }, 'Bandwidth (24h)'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '1.2 GB')
          )
        )
      ),
      React.createElement('div', { style: { backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' } },
        React.createElement('div', { style: { padding: '16px 24px', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'space-between' } },
          React.createElement('h3', { style: { fontSize: '18px', fontWeight: '500', color: '#111827' } }, 'Buckets'),
          React.createElement('button', { style: { padding: '8px 16px', backgroundColor: '#111827', color: 'white', borderRadius: '4px', fontSize: '14px', border: 'none', cursor: 'pointer' } }, 'New bucket')
        ),
        React.createElement('div', { style: { overflowX: 'auto' } },
          React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
            React.createElement('thead', { style: { backgroundColor: '#f9fafb' } },
              React.createElement('tr', null,
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Name'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Visibility'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Files'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Size'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Created'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Actions')
              )
            ),
            React.createElement('tbody', { style: { backgroundColor: 'white' } },
              buckets.map((bucket) =>
                React.createElement('tr', { key: bucket.name, style: { borderTop: '1px solid #e5e7eb' } },
                  React.createElement('td', { style: { padding: '16px 24px' } },
                    React.createElement('div', { style: { display: 'flex', alignItems: 'center' } },
                      React.createElement('div', { style: { width: '32px', height: '32px', backgroundColor: '#dbeafe', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' } },
                        React.createElement('svg', { style: { width: '16px', height: '16px', color: '#2563eb' }, fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
                          React.createElement('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: 2, d: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z' })
                        )
                      ),
                      React.createElement('div', { style: { marginLeft: '12px' } },
                        React.createElement('div', { style: { fontSize: '14px', fontWeight: '500', color: '#111827' } }, bucket.name)
                      )
                    )
                  ),
                  React.createElement('td', { style: { padding: '16px 24px' } },
                    React.createElement('span', {
                      style: {
                        padding: '4px 8px',
                        fontSize: '12px',
                        fontWeight: '500',
                        borderRadius: '9999px',
                        backgroundColor: bucket.public ? '#dcfce7' : '#f3f4f6',
                        color: bucket.public ? '#166534' : '#374151'
                      }
                    }, bucket.public ? 'Public' : 'Private')
                  ),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, bucket.files),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, bucket.size),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#6b7280' } }, bucket.created),
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