import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

export default function Layout({ children, title = "Developer Console" }: LayoutProps) {
  return (
    <div className="min-h-screen neural-background">
      <header className="quantum-card border-b border-border/50 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold neural-text">{title}</h1>
            <nav className="flex space-x-6">
              <a href="#" className="text-foreground/80 hover:text-primary transition-colors font-medium">Projects</a>
              <a href="#" className="text-foreground/80 hover:text-primary transition-colors font-medium">APIs</a>
              <a href="#" className="text-foreground/80 hover:text-primary transition-colors font-medium">Analytics</a>
              <a href="#" className="text-foreground/80 hover:text-primary transition-colors font-medium">Settings</a>
            </nav>
          </div>
        </div>
      </header>
      <main>
        {children}
      </main>
    </div>
  );
}