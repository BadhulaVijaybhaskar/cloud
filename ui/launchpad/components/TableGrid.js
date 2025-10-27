import React, { useState, useEffect } from 'react';

const TableGrid = ({ tableName }) => {
  const [rows, setRows] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [editingRow, setEditingRow] = useState(null);

  useEffect(() => {
    if (tableName) {
      fetchTableData();
    }
  }, [tableName, page]);

  const fetchTableData = async () => {
    try {
      const response = await fetch(`/api/data/crud/tables/${tableName}/rows?page=${page}&limit=50`);
      const data = await response.json();
      
      setRows(data.rows || []);
      setTotal(data.total || 0);
      
      if (data.rows && data.rows.length > 0) {
        setColumns(Object.keys(data.rows[0]));
      }
    } catch (error) {
      console.error('Table data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (row) => {
    setEditingRow({ ...row });
  };

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/data/crud/tables/${tableName}/rows/${editingRow.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: editingRow })
      });
      
      if (response.ok) {
        setEditingRow(null);
        fetchTableData();
      }
    } catch (error) {
      console.error('Update error:', error);
    }
  };

  const handleDelete = async (rowId) => {
    if (!confirm('Delete this row?')) return;
    
    try {
      const response = await fetch(`/api/data/crud/tables/${tableName}/rows/${rowId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchTableData();
      }
    } catch (error) {
      console.error('Delete error:', error);
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
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{tableName}</h3>
        <div className="text-sm text-gray-400">
          {total} rows • Page {page}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              {columns.map((col) => (
                <th key={col} className="text-left py-2 px-3 text-gray-300 font-medium">
                  {col}
                </th>
              ))}
              <th className="text-right py-2 px-3 text-gray-300 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx} className="border-b border-gray-800 hover:bg-gray-800">
                {columns.map((col) => (
                  <td key={col} className="py-2 px-3 text-gray-200">
                    {editingRow && editingRow.id === row.id ? (
                      <input
                        type="text"
                        value={editingRow[col] || ''}
                        onChange={(e) => setEditingRow({...editingRow, [col]: e.target.value})}
                        className="bg-gray-700 text-white px-2 py-1 rounded text-sm w-full"
                      />
                    ) : (
                      String(row[col] || '')
                    )}
                  </td>
                ))}
                <td className="py-2 px-3 text-right">
                  {editingRow && editingRow.id === row.id ? (
                    <div className="space-x-2">
                      <button
                        onClick={handleSave}
                        className="text-teal-400 hover:text-teal-300 text-xs"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingRow(null)}
                        className="text-gray-400 hover:text-gray-300 text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="space-x-2">
                      <button
                        onClick={() => handleEdit(row)}
                        className="text-violet-400 hover:text-violet-300 text-xs"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(row.id)}
                        className="text-red-400 hover:text-red-300 text-xs"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4">
        <button
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
          className="px-3 py-1 bg-gray-800 text-gray-300 rounded text-sm disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-gray-400 text-sm">
          Page {page} of {Math.ceil(total / 50)}
        </span>
        <button
          onClick={() => setPage(page + 1)}
          disabled={page >= Math.ceil(total / 50)}
          className="px-3 py-1 bg-gray-800 text-gray-300 rounded text-sm disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default TableGrid;