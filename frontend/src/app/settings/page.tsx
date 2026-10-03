'use client';
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
