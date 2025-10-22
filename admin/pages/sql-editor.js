import { useState } from 'react';
import Layout from '../components/Layout';

export default function SQLEditor() {
  return (
    <Layout title="SQL Editor">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded mb-4">
              New query
            </button>
          </div>
          
          {/* Query History */}
          <div className="flex-1 p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Recent queries</h3>
            <div className="text-center py-8">
              <p className="text-sm text-gray-500">No queries yet</p>
              <p className="text-xs text-gray-400 mt-1">Your query history will appear here</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Query Editor */}
          <div className="flex-1 flex flex-col">
            <div className="border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">SQL Editor</h2>
                <div className="flex space-x-2">
                  <button className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">
                    Save
                  </button>
                  <button className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                    Run
                  </button>
                </div>
              </div>
            </div>
            
            {/* Code Editor */}
            <div className="flex-1 bg-gray-900 text-white font-mono text-sm">
              <div className="p-4">
                <div className="text-green-400">-- Welcome to Supabase SQL Editor</div>
                <div className="text-green-400">-- You can query your database directly from here</div>
                <div className="mt-4">
                  <span className="text-blue-400">SELECT</span> * <span className="text-blue-400">FROM</span> users;
                </div>
              </div>
            </div>
          </div>
          
          {/* Results Panel */}
          <div className="h-64 border-t border-gray-200 bg-white">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-900">Results</h3>
            </div>
            <div className="p-4 text-center text-gray-500">
              <p className="text-sm">Run a query to see results here</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}