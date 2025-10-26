import React, { useState } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Card from '../components/Card';

export default function AIServices() {
  const [models] = useState([
    { name: 'text-embedding-ada-002', provider: 'OpenAI', tokens: 2456789, cost: '$24.57', status: 'active' },
    { name: 'all-MiniLM-L6-v2', provider: 'HuggingFace', tokens: 1234567, cost: '$0.00', status: 'active' },
    { name: 'gpt-4-turbo', provider: 'OpenAI', tokens: 89012, cost: '$89.01', status: 'active' }
  ]);

  const [pipelines] = useState([
    { name: 'content-embeddings', status: 'running', processed: 12456, errors: 3, lastRun: '2024-01-20T10:30:00Z' },
    { name: 'user-classification', status: 'completed', processed: 8901, errors: 0, lastRun: '2024-01-20T09:15:00Z' },
    { name: 'document-analysis', status: 'failed', processed: 234, errors: 12, lastRun: '2024-01-20T08:45:00Z' }
  ]);

  return React.createElement(Layout, { title: 'AI Services' },
    React.createElement('div', { style: { padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' } },
      React.createElement('div', { style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between' } },
        React.createElement('div', null,
          React.createElement('h1', { style: { fontSize: '24px', fontWeight: '600', color: '#111827' } }, '🧠 AI Services'),
          React.createElement('p', { style: { color: '#4b5563' } }, 'Manage embeddings, orchestration, and AI model integrations')
        ),
        React.createElement('div', { style: { display: 'flex', gap: '12px' } },
          React.createElement(Button, { variant: 'secondary', size: 'sm' }, '📊 Usage Analytics'),
          React.createElement(Button, { size: 'sm' }, '+ New Pipeline')
        )
      ),
      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' } },
        React.createElement(Card, { style: { background: 'linear-gradient(to right, #8b5cf6, #7c3aed)', color: 'white' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', opacity: 0.9 } }, 'Total Embeddings'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: 'bold' } }, '2.4M')
          )
        ),
        React.createElement(Card, { style: { background: 'linear-gradient(to right, #3b82f6, #2563eb)', color: 'white' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', opacity: 0.9 } }, 'Active Models'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: 'bold' } }, models.length)
          )
        ),
        React.createElement(Card, { style: { background: 'linear-gradient(to right, #10b981, #059669)', color: 'white' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', opacity: 0.9 } }, 'Monthly Cost'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: 'bold' } }, '$113.58')
          )
        ),
        React.createElement(Card, { style: { background: 'linear-gradient(to right, #f97316, #ea580c)', color: 'white' } },
          React.createElement('div', { style: { textAlign: 'center' } },
            React.createElement('p', { style: { fontSize: '14px', opacity: 0.9 } }, 'Pipelines'),
            React.createElement('p', { style: { fontSize: '24px', fontWeight: 'bold' } }, pipelines.length)
          )
        )
      ),
      React.createElement('div', { style: { borderBottom: '1px solid #e5e7eb' } },
        React.createElement('nav', { style: { display: 'flex', gap: '32px', marginBottom: '-1px' } },
          React.createElement('button', { style: { padding: '8px 4px', borderBottom: '2px solid #8b5cf6', fontWeight: '500', fontSize: '14px', color: '#7c3aed', backgroundColor: 'transparent', border: 'none' } }, 'Embeddings Dashboard'),
          React.createElement('button', { style: { padding: '8px 4px', borderBottom: '2px solid transparent', fontWeight: '500', fontSize: '14px', color: '#6b7280', backgroundColor: 'transparent', border: 'none' } }, 'Orchestration Monitor'),
          React.createElement('button', { style: { padding: '8px 4px', borderBottom: '2px solid transparent', fontWeight: '500', fontSize: '14px', color: '#6b7280', backgroundColor: 'transparent', border: 'none' } }, 'Vector Inspector'),
          React.createElement('button', { style: { padding: '8px 4px', borderBottom: '2px solid transparent', fontWeight: '500', fontSize: '14px', color: '#6b7280', backgroundColor: 'transparent', border: 'none' } }, 'Prompt Templates')
        )
      ),
      React.createElement(Card, { title: '🤖 Model Usage & Token Consumption' },
        React.createElement('div', { style: { overflowX: 'auto' } },
          React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
            React.createElement('thead', { style: { backgroundColor: '#f9fafb' } },
              React.createElement('tr', null,
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Model'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Provider'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Tokens Used'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Cost (30d)'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Status'),
                React.createElement('th', { style: { padding: '12px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' } }, 'Actions')
              )
            ),
            React.createElement('tbody', { style: { backgroundColor: 'white' } },
              models.map((model) =>
                React.createElement('tr', { key: model.name, style: { borderTop: '1px solid #e5e7eb' } },
                  React.createElement('td', { style: { padding: '16px 24px' } },
                    React.createElement('div', { style: { display: 'flex', alignItems: 'center' } },
                      React.createElement('div', { style: { width: '32px', height: '32px', backgroundColor: '#f3e8ff', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' } },
                        React.createElement('span', { style: { color: '#7c3aed', fontSize: '14px' } }, '🧠')
                      ),
                      React.createElement('div', { style: { marginLeft: '12px' } },
                        React.createElement('div', { style: { fontSize: '14px', fontWeight: '500', color: '#111827' } }, model.name)
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
                        backgroundColor: model.provider === 'OpenAI' ? '#dcfce7' : '#dbeafe',
                        color: model.provider === 'OpenAI' ? '#166534' : '#1e40af'
                      }
                    }, model.provider)
                  ),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, model.tokens.toLocaleString()),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#111827' } }, model.cost),
                  React.createElement('td', { style: { padding: '16px 24px' } },
                    React.createElement('span', { style: { padding: '4px 8px', fontSize: '12px', fontWeight: '500', borderRadius: '9999px', backgroundColor: '#dcfce7', color: '#166534' } }, model.status)
                  ),
                  React.createElement('td', { style: { padding: '16px 24px', fontSize: '14px', color: '#6b7280' } },
                    React.createElement('div', { style: { display: 'flex', gap: '8px' } },
                      React.createElement('button', { style: { color: '#2563eb', backgroundColor: 'transparent', border: 'none', cursor: 'pointer' } }, 'Configure'),
                      React.createElement('button', { style: { color: '#4b5563', backgroundColor: 'transparent', border: 'none', cursor: 'pointer' } }, 'Analytics')
                    )
                  )
                )
              )
            )
          )
        )
      ),
      React.createElement(Card, { title: '🔄 AI Pipeline Status' },
        React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: '16px' } },
          pipelines.map((pipeline) =>
            React.createElement('div', {
              key: pipeline.name,
              style: {
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px',
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }
            },
              React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '16px' } },
                React.createElement('div', {
                  style: {
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: pipeline.status === 'running' ? '#10b981' : pipeline.status === 'completed' ? '#3b82f6' : '#ef4444'
                  }
                }),
                React.createElement('div', null,
                  React.createElement('h3', { style: { fontWeight: '500', color: '#111827' } }, pipeline.name),
                  React.createElement('p', { style: { fontSize: '14px', color: '#6b7280' } },
                    `Processed: ${pipeline.processed.toLocaleString()} • Errors: ${pipeline.errors} • Last run: ${new Date(pipeline.lastRun).toLocaleString()}`
                  )
                )
              ),
              React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '12px' } },
                React.createElement('span', {
                  style: {
                    padding: '4px 8px',
                    fontSize: '12px',
                    fontWeight: '500',
                    borderRadius: '9999px',
                    backgroundColor: pipeline.status === 'running' ? '#dcfce7' : pipeline.status === 'completed' ? '#dbeafe' : '#fee2e2',
                    color: pipeline.status === 'running' ? '#166534' : pipeline.status === 'completed' ? '#1e40af' : '#991b1b'
                  }
                }, pipeline.status),
                React.createElement(Button, { size: 'sm', variant: 'secondary' }, 'View Details')
              )
            )
          )
        )
      )
    )
  );
}