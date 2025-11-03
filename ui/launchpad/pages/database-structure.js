import { useState } from 'react';
import LaunchpadLayout from '../components/LaunchpadLayout';

const TopNav = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'functions', name: 'Functions', icon: '⚙️' },
    { id: 'triggers', name: 'Triggers', icon: '⚡' },
    { id: 'enums', name: 'Enums', icon: '📝' },
    { id: 'indexes', name: 'Indexes', icon: '🔍' }
  ];
  
  return (
    <div className="border-b border-border/50 bg-card/30 px-6 py-3">
      <div className="flex gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
              activeTab === tab.id ? 'bg-primary/20 text-primary' : 'hover:bg-accent/50'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

const ContentArea = ({ activeTab }) => {
  const tabConfig = {
    'functions': { 
      title: 'Database Functions', 
      desc: 'Manage stored procedures and functions',
      items: ['get_user_stats()', 'calculate_metrics()', 'update_timestamps()', 'validate_email()']
    },
    'triggers': { 
      title: 'Database Triggers', 
      desc: 'Configure database triggers and events',
      items: ['user_audit_trigger', 'project_update_trigger', 'session_cleanup_trigger']
    },
    'enums': { 
      title: 'Enumerated Types', 
      desc: 'Define custom enumerated data types',
      items: ['user_status', 'project_status', 'permission_level', 'notification_type']
    },
    'indexes': { 
      title: 'Database Indexes', 
      desc: 'Advanced index configuration and optimization',
      items: ['idx_users_email', 'idx_projects_status', 'idx_analytics_timestamp', 'idx_sessions_user_id']
    }
  };
  
  const config = tabConfig[activeTab] || tabConfig['functions'];
  
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">{config.title}</h2>
        <p className="text-muted-foreground">{config.desc}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {config.items.map((item, idx) => (
          <div key={item} className="quantum-card p-4 hover:bg-accent/10 transition-colors cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium">{item}</h3>
              <button className="text-xs text-muted-foreground hover:text-foreground">
                ⚙️ Edit
              </button>
            </div>
            <p className="text-sm text-muted-foreground">
              {activeTab === 'functions' ? 'Database function' :
               activeTab === 'triggers' ? 'Trigger event' :
               activeTab === 'enums' ? 'Enumerated type' :
               'Database index'} #{idx + 1}
            </p>
          </div>
        ))}
        
        <div className="border-2 border-dashed border-border/50 hover:border-primary/50 transition-colors p-4 rounded-lg flex flex-col items-center justify-center text-center space-y-2 cursor-pointer group">
          <div className="w-12 h-12 bg-gradient-to-r from-teal-500/10 to-violet-500/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="text-2xl">➕</span>
          </div>
          <div>
            <h3 className="font-semibold">Create New</h3>
            <p className="text-sm text-muted-foreground">Add new {activeTab.slice(0, -1)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function DatabaseStructure() {
  const [activeTab, setActiveTab] = useState('functions');

  return (
    <LaunchpadLayout>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-secondary/20">
        <TopNav 
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        <ContentArea activeTab={activeTab} />
      </div>
    </LaunchpadLayout>
  );
}