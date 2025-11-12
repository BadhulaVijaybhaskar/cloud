import React from 'react';

export default function Topbar(){
  return (
    <header className="bg-white border-b px-6 py-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-semibold">ATOM Cloud Console</h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">Simulation Mode</span>
          <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
        </div>
      </div>
    </header>
  );
}