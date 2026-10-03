import os

# Ensure governance directory exists
os.makedirs("frontend/src/app/governance/audit", exist_ok=True)

# 1. Audit Log UI
audit_ui = """'use client';
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
"""

with open("frontend/src/app/governance/audit/page.tsx", "w") as f: f.write(audit_ui)

# 2. Settings UI
settings_ui = """'use client';
import { useState } from 'react';
import { Settings as SettingsIcon, Shield, Bell, Database, Bot, Save } from 'lucide-react';

export default function Settings() {
  const [saving, setSaving] = useState(false);
  
  const handleSave = () => {
    setSaving(true);
    setTimeout(() => setSaving(false), 1000);
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><SettingsIcon className="text-slate-700" /> Platform Settings</h1>
          <p className="text-sm text-slate-500 mt-1">Configure global risk engine parameters and system preferences.</p>
        </div>
        <button 
          onClick={handleSave}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium text-sm transition-colors flex items-center gap-2 shadow-sm"
        >
          {saving ? <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <Save size={16} />}
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Risk Engine Settings */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-bold flex items-center gap-2 mb-4 border-b border-slate-100 pb-2"><Shield className="text-blue-600"/> Risk Engine Configuration</h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-800">Auto-Suspend High Risk Entities</div>
                  <div className="text-xs text-slate-500">Automatically block transactions if risk score exceeds 90.</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-800">Graph Database Real-time Sync</div>
                  <div className="text-xs text-slate-500">Enable Neo4j/Memgraph streaming for network intelligence.</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100">
                <label className="block text-sm font-bold text-slate-700 mb-2">Global Transaction Limit (Anomaly Threshold)</label>
                <input type="number" defaultValue="500000" className="w-full max-w-xs px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
              </div>
            </div>
          </div>
          
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-bold flex items-center gap-2 mb-4 border-b border-slate-100 pb-2"><Bot className="text-indigo-600"/> AI Copilot Preferences</h2>
            <div className="flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-800">Enable Predictive Summaries</div>
                <div className="text-xs text-slate-500">Copilot will pre-generate investigation summaries when a case opens.</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* System Info Sidebar */}
        <div className="space-y-6">
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
            <h2 className="text-sm font-bold text-slate-700 mb-4 uppercase tracking-wider">System Information</h2>
            <ul className="space-y-3 text-sm text-slate-600">
              <li className="flex justify-between"><span className="font-medium">Version</span> <span>v2.4.0 (Enterprise)</span></li>
              <li className="flex justify-between"><span className="font-medium">Environment</span> <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-bold">PRODUCTION</span></li>
              <li className="flex justify-between"><span className="font-medium">Database</span> <span>PostgreSQL 15</span></li>
              <li className="flex justify-between"><span className="font-medium">Redis Cache</span> <span className="text-emerald-600 font-bold">Connected</span></li>
            </ul>
          </div>
          
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-6">
            <h2 className="text-sm font-bold text-rose-800 mb-2 flex items-center gap-2"><Shield className="text-rose-600"/> Danger Zone</h2>
            <p className="text-xs text-rose-600 mb-4">Clearing the Redis cache will force all active risk models to cold-start. This may cause temporary latency spikes.</p>
            <button className="w-full bg-white border border-rose-300 text-rose-700 hover:bg-rose-100 px-4 py-2 rounded font-medium text-sm transition-colors">
              Purge Redis Cache
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
"""
with open("frontend/src/app/settings/page.tsx", "w") as f: f.write(settings_ui)
