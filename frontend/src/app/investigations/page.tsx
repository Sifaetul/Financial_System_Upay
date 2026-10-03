'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { FolderSearch, Clock, ShieldCheck, User, CheckCircle2, X, AlertTriangle, FileText, Activity } from 'lucide-react';

export default function Investigations() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<any | null>(null);
  const [closingId, setClosingId] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCases() {
      try {
        const res: any = await apiClient<any>('/investigation/cases').catch(() => ({ items: [] }));
        const allCases = Array.isArray(res) ? res : (res.items || []);
        setCases(allCases);
      } catch (err) {} finally { setLoading(false); }
    }
    fetchCases();
  }, []);

  const handleCloseCase = (id: string) => {
    setClosingId(id);
    setTimeout(() => {
      setCases(prev => prev.map(c => c.id === id ? { ...c, status: 'CLOSED' } : c));
      setClosingId(null);
    }, 800);
  };

  return (
    <div className="space-y-6 relative">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2"><FolderSearch className="text-emerald-600" /> Active Investigations Workspace</h1>
        <p className="text-sm text-slate-500 mt-1">Manage and resolve high-risk cases identified by the intelligence platform.</p>
      </div>

      {loading ? <div className="text-center p-8 text-slate-500 animate-pulse">Loading active cases...</div> : (
        <div className="grid grid-cols-1 gap-4">
          {cases.map((c: any) => (
            <div key={c.id} className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center hover:shadow-md transition-all group">
              
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${c.status === 'OPEN' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'}`}>
                    {c.status}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${c.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-orange-100 text-orange-800'}`}>
                    {c.severity} RISK
                  </span>
                  <span className="font-bold text-slate-800 text-lg">{c.number || 'CASE-' + (c.id ? c.id.split('-')[0].toUpperCase() : 'UNKNOWN')}</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span className="flex items-center gap-1"><User size={14}/> Entity: {String(c.primary_entity_id).split('-')[0]}</span>
                  <span className="flex items-center gap-1"><Clock size={14}/> Opened: {new Date(c.created_at || Date.now()).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="mt-4 md:mt-0 flex gap-2">
                <button 
                  onClick={() => setSelectedCase(c)}
                  className="bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 px-4 py-2 rounded font-medium text-sm transition-colors flex items-center gap-2"
                >
                  <ShieldCheck size={16}/> View Evidence
                </button>
                {c.status === 'OPEN' && (
                  <button 
                    onClick={() => handleCloseCase(c.id)}
                    disabled={closingId === c.id}
                    className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white px-4 py-2 rounded font-medium text-sm transition-colors flex items-center gap-2 shadow-sm"
                  >
                    {closingId === c.id ? <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <CheckCircle2 size={16}/>}
                    {closingId === c.id ? 'Closing...' : 'Mark Safe & Close'}
                  </button>
                )}
              </div>

            </div>
          ))}
          {cases.length === 0 && (
             <div className="text-center p-12 bg-slate-50 rounded-xl border border-slate-200 text-slate-500">
               No active investigations found. The network is secure.
             </div>
          )}
        </div>
      )}

      {/* Slide-over Evidence Panel */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm transition-opacity" onClick={() => setSelectedCase(null)} />
          <div className="absolute inset-y-0 right-0 max-w-md w-full bg-white shadow-2xl flex flex-col border-l border-slate-200 transform transition-transform">
            <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <div>
                <h2 className="text-xl font-bold text-slate-800">Case Evidence File</h2>
                <p className="text-xs text-slate-500 font-mono mt-1">{selectedCase.number || 'CASE-' + selectedCase.id.split('-')[0].toUpperCase()}</p>
              </div>
              <button onClick={() => setSelectedCase(null)} className="p-2 hover:bg-slate-200 rounded-full transition-colors"><X size={20} className="text-slate-500"/></button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              <div className="bg-rose-50 border border-rose-200 rounded-xl p-4">
                <h3 className="font-bold text-rose-800 flex items-center gap-2 mb-2"><AlertTriangle size={18}/> Primary Risk Signal</h3>
                <p className="text-sm text-rose-700">The Unified Risk Engine flagged an anomalous transaction velocity spike (400% increase over 48h baseline). Activity pattern matches known &quot;Account Takeover&quot; or &quot;Money Mule&quot; typologies.</p>
              </div>

              <div>
                <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2"><Activity size={18} className="text-slate-500"/> Behavioral Anomalies</h3>
                <ul className="space-y-3">
                  <li className="flex gap-3 text-sm border-l-2 border-amber-400 pl-3">
                    <div className="font-bold text-slate-700 w-24">Device</div>
                    <div className="text-slate-600">Login from new device (iPhone 14) outside normal geographic radius.</div>
                  </li>
                  <li className="flex gap-3 text-sm border-l-2 border-amber-400 pl-3">
                    <div className="font-bold text-slate-700 w-24">Velocity</div>
                    <div className="text-slate-600">8 outbound transfers to new recipients within 2 hours.</div>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2"><FileText size={18} className="text-slate-500"/> Copilot Recommendation</h3>
                <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-xl text-sm text-indigo-900 leading-relaxed">
                  &quot;Based on the correlated signals, this case has a high probability of being an organized fraud attempt. I recommend maintaining the temporary hold and escalating to the compliance tier for identity verification.&quot;
                </div>
              </div>

            </div>
            
            <div className="p-6 border-t border-slate-200 bg-slate-50 flex gap-3">
              <button onClick={() => setSelectedCase(null)} className="flex-1 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 py-2.5 rounded-lg font-bold text-sm transition-colors">Close Viewer</button>
              <button 
                onClick={() => { handleCloseCase(selectedCase.id); setSelectedCase(null); }}
                className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-lg font-bold text-sm transition-colors"
              >
                Mark Safe
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
