import React from 'react';
export function MetricCard({ title, value, trend }: { title: string, value: string | number, trend?: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
      <span className="text-gray-500 text-sm font-medium mb-1">{title}</span>
      <span className="text-3xl font-bold text-gray-900">{value}</span>
      {trend && <span className="text-sm mt-2 text-emerald-600 font-medium">{trend}</span>}
    </div>
  );
}
