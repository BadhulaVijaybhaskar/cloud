import React from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import ProjectsPage from './pages/ProjectsPage';

export default function App() {
  return (
    <div className="min-h-screen flex bg-slate-50">
      <Sidebar />
      <div className="flex-1">
        <Topbar />
        <main className="p-6">
          <ProjectsPage />
        </main>
      </div>
    </div>
  );
}