import { useState } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const menuItems = {
  'Backup & Restore': {
    items: [
      { name: 'Backups', action: 'backups' },
      { name: 'Restore Points', action: 'restore' },
      { name: 'Backup Schedules', action: 'schedules' }
    ]
  },
  'Database Operations': {
    items: [
      { name: 'Migrations', action: 'migrations' },
      { name: 'Schema Changes', action: 'schema-changes' },
      { name: 'Replication', action: 'replication' }
    ]
  },
  'Maintenance': {
    items: [
      { name: 'Vacuum & Analyze', action: 'vacuum' },
      { name: 'Index Maintenance', action: 'index-maint' },
      { name: 'Statistics', action: 'statistics' }
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
    'backups': { title: 'Database Backups', desc: 'Automated and manual database backups' },
    'restore': { title: 'Restore Points', desc: 'Point-in-time recovery options' },
    'schedules': { title: 'Backup Schedules', desc: 'Configure automated backup schedules' },
    'migrations': { title: 'Schema Migrations', desc: 'Database schema version control' },
    'schema-changes': { title: 'Schema Changes', desc: 'Track and manage schema modifications' },
    'replication': { title: 'Database Replication', desc: 'Master-slave and logical replication' },
    'vacuum': { title: 'Vacuum & Analyze', desc: 'Database maintenance and optimization' },
    'index-maint': { title: 'Index Maintenance', desc: 'Index rebuilding and optimization' },
    'statistics': { title: 'Database Statistics', desc: 'Query planner statistics and analysis' }
  };

  const config = sectionConfig[activeSection] || { title: 'Operations', desc: 'Database operations' };

  return (
    <div className="flex-1 p-6">
      <div className="quantum-card p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground mb-4">{config.desc}</p>
        <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors">
          Manage
        </button>
      </div>
    </div>
  );
};

export default function Operations() {
  const [activeSection, setActiveSection] = useState('backups');

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