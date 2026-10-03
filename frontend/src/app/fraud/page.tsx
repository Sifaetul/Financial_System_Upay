'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { ShieldBan, AlertOctagon, ArrowRightCircle } from 'lucide-react';
import Link from 'next/link';

export default function Fraud() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSignals() {
      try {
        const res: any = await apiClient<any>('/investigation/alerts').catch(() => ({ items: [] }));
        const allAlerts = Array.isArray(res) ? res : (res.items || []);
        setSignals(allAlerts.filter((a: any) => a.type === 'FRAUD_RISK' || a.severity === 'CRITICAL'));
      } catch (err) {} finally { setLoading(false); }
    }
    fetchSignals();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-red-50 border border-red-200 p-6 rounded-xl flex items-start gap-4">
        <ShieldBan className="text-red-500 w-12 h-12 flex-shrink-0" />
        <div>
          <h1 className="text-2xl font-bold text-red-900">Fraud Detection Engine</h1>
          <p className="text-red-700 mt-1">Real-time monitoring of transaction streams. The AI engine automatically flags anomalous patterns, velocity spikes, and known bad actors.</p>
        </div>
      </div>

      {loading ? <div className="text-center p-8 text-slate-500 animate-pulse">Scanning live streams...</div> : (
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <AlertOctagon className="text-slate-400" size={20} /> Active Fraud Signals ({signals.length})
          </h2>
          
          <div className="grid grid-cols-1 gap-3">
            {signals.map((sig: any) => (
              <div key={sig.id} className="bg-white border-l-4 border-l-red-500 border-t border-r border-b border-slate-200 p-4 rounded-r-xl shadow-sm flex flex-col md:flex-row md:items-center justify-between hover:bg-slate-50 transition-colors">
                
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-0.5 rounded">{sig.severity}</span>
                    <span className="font-semibold text-slate-900">{sig.type.replace('_', ' ')}</span>
                  </div>
                  <div className="text-sm text-slate-500 font-mono">Entity: {sig.entity_id}</div>
                  <div className="text-xs text-slate-400">Detected: {new Date(sig.created_at).toLocaleString()}</div>
                </div>

                <div className="mt-4 md:mt-0 flex items-center gap-3">
                  <span className="text-sm font-medium text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
                    Status: {sig.status}
                  </span>
                  <Link href="/investigations" className="flex items-center gap-1 text-sm font-bold text-white bg-red-600 hover:bg-red-700 px-4 py-2 rounded shadow-sm transition-colors">
                    Investigate <ArrowRightCircle size={16} />
                  </Link>
                </div>

              </div>
            ))}
            
            {signals.length === 0 && (
              <div className="bg-white border border-slate-200 p-8 rounded-xl text-center text-slate-500">
                No active fraud signals detected in the current window.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
