import { useState } from 'react';
import Layout from '../components/Layout';

export default function TableEditor() {
  return (
    <Layout title="Table Editor">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="mb-4">
              <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm bg-white">
                <option>schema public</option>
                <option>schema auth</option>
              </select>
            </div>
            
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded mb-4">
              New table
            </button>
          </div>
          
          {/* Search */}
          <div className="px-4 mb-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Search tables..."
                className="w-full px-3 py-2 pl-8 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-gray-400"
              />
              <svg className="absolute left-2 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          {/* No Tables Message */}
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              </svg>
            </div>
            <h3 className="text-sm font-medium text-gray-900 mb-1">No tables or views</h3>
            <p className="text-xs text-gray-500 mb-4">Any tables or views you create will be listed here.</p>
            
            <div className="space-y-2 text-xs text-gray-400">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gray-200 rounded"></div>
                <span>postgres_lsn</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gray-200 rounded"></div>
                <span>postgres_fdw</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gray-200 rounded"></div>
                <span>postgres_fdw</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Main Area */}
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <h2 className="text-lg font-medium text-gray-900 mb-2">Create a table</h2>
              <p className="text-sm text-gray-500 mb-6">Design and create a new database table</p>
              <button className="px-4 py-2 bg-gray-900 text-white rounded text-sm hover:bg-gray-800">
                Create a new table
              </button>
            </div>
          </div>
          
          {/* Recent Items */}
          <div className="border-t border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-900 mb-4">Recent items</h3>
            <div className="text-center py-8">
              <p className="text-sm text-gray-500">No recent items yet</p>
              <p className="text-xs text-gray-400 mt-1">Items will appear here as you browse through your project</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}