import React, { useState, useEffect } from 'react';

const SchemaVisualizer = () => {
  const [tables, setTables] = useState([]);
  const [relations, setRelations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSchemaData();
  }, []);

  const fetchSchemaData = async () => {
    try {
      const [tablesRes, relationsRes] = await Promise.all([
        fetch('/api/data/schema/tables'),
        fetch('/api/data/schema/relations')
      ]);
      
      setTables(await tablesRes.json());
      const relData = await relationsRes.json();
      setRelations(relData.foreign_keys || []);
    } catch (error) {
      console.error('Schema fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Database Schema</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {tables.map((table) => (
          <div key={table.name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">{table.name}</h4>
              <span className="text-xs text-gray-400">{table.type}</span>
            </div>
            <div className="text-sm text-gray-300">
              <div>{table.columns} columns</div>
              <div>{table.rows} rows</div>
            </div>
          </div>
        ))}
      </div>

      {relations.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h4 className="font-medium text-white mb-3">Relationships</h4>
          <div className="space-y-2">
            {relations.map((rel, idx) => (
              <div key={idx} className="flex items-center text-sm text-gray-300">
                <span className="text-teal-400">{rel.from}</span>
                <svg className="w-4 h-4 mx-2 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                <span className="text-violet-400">{rel.to}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SchemaVisualizer;