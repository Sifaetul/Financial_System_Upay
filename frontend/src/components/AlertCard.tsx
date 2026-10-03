import React from 'react';
export function AlertCard({ title, message, severity = 'info' }: { title: string, message: string, severity?: 'info' | 'warning' | 'critical' }) {
  const colors = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    critical: 'bg-red-50 border-red-200 text-red-800'
  };
  return (
    <div className={`p-4 rounded-lg border ${colors[severity]} mb-4`}>
      <h4 className="font-semibold">{title}</h4>
      <p className="text-sm mt-1">{message}</p>
    </div>
  );
}
