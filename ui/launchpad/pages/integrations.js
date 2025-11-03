import { useState } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const menuItems = {
  'External Connections': {
    items: [
      { name: 'Foreign Data Wrappers', action: 'wrappers' },
      { name: 'API Connections', action: 'api-connections' },
      { name: 'Database Links', action: 'db-links' }
    ]
  },
  'Event Streaming': {
    items: [
      { name: 'Webhooks', action: 'webhooks' },
      { name: 'Event Triggers', action: 'triggers' },
      { name: 'Message Queues', action: 'queues' }
    ]
  },
  'Third Party': {
    items: [
      { name: 'Cloud Services', action: 'cloud' },
      { name: 'Analytics Tools', action: 'analytics' },
      { name: 'Monitoring', action: 'monitoring' }
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
    'wrappers': { title: 'Foreign Data Wrappers', desc: 'Connect to external databases and data sources' },
    'api-connections': { title: 'API Connections', desc: 'REST and GraphQL API integrations' },
    'db-links': { title: 'Database Links', desc: 'Cross-database connections and federation' },
    'webhooks': { title: 'Webhooks', desc: 'HTTP callbacks for database events' },
    'triggers': { title: 'Event Triggers', desc: 'Database event-driven automation' },
    'queues': { title: 'Message Queues', desc: 'Asynchronous message processing' },
    'cloud': { title: 'Cloud Services', desc: 'AWS, GCP, Azure service integrations' },
    'analytics': { title: 'Analytics Tools', desc: 'Business intelligence and analytics platforms' },
    'monitoring': { title: 'Monitoring Tools', desc: 'External monitoring and alerting systems' }
  };

  const config = sectionConfig[activeSection] || { title: 'Integrations', desc: 'External integrations' };

  return (
    <div className="flex-1 p-6">
      <div className="quantum-card p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground mb-4">{config.desc}</p>
        <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors">
          Configure Integration
        </button>
      </div>
    </div>
  );
};

export default function Integrations() {
  const [activeSection, setActiveSection] = useState('wrappers');

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