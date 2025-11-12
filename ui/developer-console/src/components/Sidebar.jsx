import React from 'react';

export default function Sidebar(){
  return (
    <aside className="w-64 bg-white border-r">
      <div className="p-4 font-bold">Developer Console</div>
      <nav className="p-4">
        <ul>
          <li className="py-2"><a href="#/projects">Projects</a></li>
          <li className="py-2"><a href="#/marketplace">Marketplace</a></li>
          <li className="py-2"><a href="#/auth">Auth</a></li>
          <li className="py-2"><a href="#/sql">SQL Editor</a></li>
          <li className="py-2"><a href="#/storage">Storage</a></li>
          <li className="py-2"><a href="#/realtime">Realtime</a></li>
        </ul>
      </nav>
    </aside>
  );
}