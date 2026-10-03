import React from 'react';
export function DataTable({ headers, rows }: { headers: string[], rows: any[][] }) {
  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((h, i) => <th key={i} className="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">{h}</th>)}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {row.map((cell, j) => <td key={j} className="px-6 py-4 whitespace-nowrap text-gray-900">{cell}</td>)}
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={headers.length} className="px-6 py-4 text-center text-gray-500">No data available</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
