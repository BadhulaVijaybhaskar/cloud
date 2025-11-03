import { useState } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const menuItems = {
  'Security Analysis': {
    items: [
      { name: 'Security Advisor', action: 'security-advisor' },
      { name: 'Vulnerability Scan', action: 'vuln-scan' },
      { name: 'Compliance Check', action: 'compliance' }
    ]
  },
  'Access Control': {
    items: [
      { name: 'Authentication', action: 'auth' },
      { name: 'Authorization', action: 'authz' },
      { name: 'API Keys', action: 'api-keys' }
    ]
  },
  'Monitoring': {
    items: [
      { name: 'Security Events', action: 'events' },
      { name: 'Audit Logs', action: 'audit' },
      { name: 'Threat Detection', action: 'threats' }
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
    'security-advisor': { title: 'Security Advisor', desc: 'AI-powered security recommendations and analysis' },
    'vuln-scan': { title: 'Vulnerability Scanner', desc: 'Automated security vulnerability detection' },
    'compliance': { title: 'Compliance Check', desc: 'SOC2, GDPR, and industry compliance monitoring' },
    'auth': { title: 'Authentication', desc: 'User authentication and identity management' },
    'authz': { title: 'Authorization', desc: 'Role-based access control and permissions' },
    'api-keys': { title: 'API Keys', desc: 'API key management and rotation' },
    'events': { title: 'Security Events', desc: 'Real-time security event monitoring' },
    'audit': { title: 'Audit Logs', desc: 'Comprehensive audit trail and logging' },
    'threats': { title: 'Threat Detection', desc: 'AI-powered threat detection and response' }
  };

  const config = sectionConfig[activeSection] || { title: 'Security', desc: 'Security management' };

  return (
    <div className="flex-1 p-6">
      <div className="quantum-card p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground mb-4">{config.desc}</p>
        <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors">
          Configure Security
        </button>
      </div>
    </div>
  );
};

export default function Security() {
  const [activeSection, setActiveSection] = useState('security-advisor');

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