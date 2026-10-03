'use client';
import { useState } from 'react';
import { Search, ShieldAlert, FileText, UserCheck, Settings, Download } from 'lucide-react';

export default function AuditLog() {
  const [searchTerm, setSearchTerm] = useState('');
  
  const mockLogs = [
    { id: 'EVT-9092', action: 'Case Marked Safe', user: 'jane.doe@upay.nexus', role: 'Senior Investigator', time: '10 mins ago', icon: <UserCheck size={16} className="text-emerald-600"/>, risk: 'LOW' },
    { id: 'EVT-9091', action: 'Risk Model Weights Updated', user: 'admin@upay.nexus', role: 'System Admin', time: '1 hour ago', icon: <Settings size={16} className="text-blue-600"/>, risk: 'CRITICAL' },
    { id: 'EVT-9090', action: 'Generated Monthly Report', user: 'system.cron', role: 'Automated Process', time: '3 hours ago', icon: <FileText size={16} className="text-slate-600"/>, risk: 'LOW' },
    { id: 'EVT-9089', action: 'Account Force-Suspended', user: 'michael.r@upay.nexus', role: 'Fraud Analyst', time: '5 hours ago', icon: <ShieldAlert size={16} className="text-rose-600"/>, risk: 'HIGH' }
  ];

  const filteredLogs = mockLogs.filter(l => l.action.toLowerCase().includes(searchTerm.toLowerCase()) || l.user.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><FileText className="text-slate-700" /> System Audit Log</h1>
          <p className="text-sm text-slate-500 mt-1">Immutable record of all administrative and investigative actions.</p>
        </div>
        <button className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded font-medium text-sm transition-colors flex items-center gap-2">
          <Download size={16} /> Export to CSV
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search by user, action, or ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {filteredLogs.map(log => (
            <div key={log.id} className="p-4 flex flex-col md:flex-row justify-between items-start md:items-center hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-slate-100 rounded-lg">{log.icon}</div>
                <div>
                  <div className="font-bold text-slate-800">{log.action}</div>
                  <div className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                    <span className="font-mono bg-slate-200 px-1.5 py-0.5 rounded text-slate-700">{log.id}</span>
                    <span>•</span>
                    <span className="text-blue-600 font-medium">{log.user}</span>
                    <span>({log.role})</span>
                  </div>
                </div>
              </div>
              <div className="mt-2 md:mt-0 flex items-center gap-4 text-sm">
                <span className={`px-2 py-1 rounded text-xs font-bold ${log.risk === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : log.risk === 'HIGH' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                  {log.risk} RISK
                </span>
                <span className="text-slate-400">{log.time}</span>
              </div>
            </div>
          ))}
          {filteredLogs.length === 0 && <div className="p-8 text-center text-slate-500">No logs found matching your search.</div>}
        </div>
      </div>
    </div>
  );
}
