import { useState } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const menuItems = {
  'Performance': {
    items: [
      { name: 'Performance Advisor', action: 'performance-advisor' },
      { name: 'Query Performance', action: 'query-performance' },
      { name: 'Resource Usage', action: 'resources' }
    ]
  },
  'System Health': {
    items: [
      { name: 'System Metrics', action: 'metrics' },
      { name: 'Health Checks', action: 'health' },
      { name: 'Uptime Monitoring', action: 'uptime' }
    ]
  },
  'Alerts & Notifications': {
    items: [
      { name: 'Alert Rules', action: 'alerts' },
      { name: 'Notification Channels', action: 'notifications' },
      { name: 'Incident Management', action: 'incidents' }
    ]
  }
};

const Sidebar = ({ activeSection, onSectionChange }) => {
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

const ContentArea = ({ activeSection }) => {
  const sectionConfig = {
    'performance-advisor': { title: 'Performance Advisor', desc: 'AI-powered performance optimization recommendations' },
    'query-performance': { title: 'Query Performance', desc: 'Query analysis and optimization tools' },
    'resources': { title: 'Resource Usage', desc: 'CPU, memory, and storage monitoring' },
    'metrics': { title: 'System Metrics', desc: 'Real-time system performance metrics' },
    'health': { title: 'Health Checks', desc: 'Automated system health monitoring' },
    'uptime': { title: 'Uptime Monitoring', desc: 'Service availability and uptime tracking' },
    'alerts': { title: 'Alert Rules', desc: 'Configure performance and error alerts' },
    'notifications': { title: 'Notification Channels', desc: 'Email, Slack, and webhook notifications' },
    'incidents': { title: 'Incident Management', desc: 'Track and manage system incidents' }
  };

  const config = sectionConfig[activeSection] || { title: 'Monitoring', desc: 'System monitoring' };

  return (
    <div className="flex-1 p-6">
      <div className="quantum-card p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground mb-4">{config.desc}</p>
        <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors">
          Configure Monitoring
        </button>
      </div>
    </div>
  );
};

export default function Monitoring() {
  const [activeSection, setActiveSection] = useState('performance-advisor');

  return (
    <LaunchpadLayout>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20 flex">
        <Sidebar 
          activeSection={activeSection}
          onSectionChange={setActiveSection}
        />
        <ContentArea activeSection={activeSection} />
      </div>
    </LaunchpadLayout>
  );
}