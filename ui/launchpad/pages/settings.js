import { useState } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const menuItems = {
  'Configuration': {
    items: [
      { name: 'Database Config', action: 'db-config' },
      { name: 'Connection Settings', action: 'connections' },
      { name: 'Environment Variables', action: 'env-vars' }
    ]
  },
  'Access Control': {
    items: [
      { name: 'Roles', action: 'roles' },
      { name: 'Policies', action: 'policies' },
      { name: 'Permissions', action: 'permissions' }
    ]
  },
  'Extensions': {
    items: [
      { name: 'Database Extensions', action: 'extensions' },
      { name: 'Publications', action: 'publications' },
      { name: 'Subscriptions', action: 'subscriptions' }
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
    'db-config': { title: 'Database Configuration', desc: 'Database connection and performance settings' },
    'connections': { title: 'Connection Settings', desc: 'Manage database connections and pools' },
    'env-vars': { title: 'Environment Variables', desc: 'Application configuration variables' },
    'roles': { title: 'User Roles', desc: 'Manage user roles and permissions' },
    'policies': { title: 'Security Policies', desc: 'Row Level Security and access policies' },
    'permissions': { title: 'Permissions', desc: 'Fine-grained access control' },
    'extensions': { title: 'Database Extensions', desc: 'Installed database extensions and plugins' },
    'publications': { title: 'Publications', desc: 'Logical replication publications' },
    'subscriptions': { title: 'Subscriptions', desc: 'Replication subscriptions' }
  };

  const config = sectionConfig[activeSection] || { title: 'Settings', desc: 'Platform configuration' };

  return (
    <div className="flex-1 p-6">
      <div className="quantum-card p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground mb-4">{config.desc}</p>
        <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors">
          Configure
        </button>
      </div>
    </div>
  );
};

export default function Settings() {
  const [activeSection, setActiveSection] = useState('db-config');

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