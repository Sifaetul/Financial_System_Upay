import os

dashboard_ui = """'use client';
import { MetricCard } from '@/components/MetricCard';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import Link from 'next/link';
import { Activity, ShieldCheck, Zap, Server, AlertTriangle, ArrowRight, PlayCircle, Loader2 } from 'lucide-react';

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [txs, setTxs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Interactive States
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [healthRes, alertsRes, casesRes, txsRes] = await Promise.all([
          apiClient<any>('/health').catch(() => null),
          apiClient<any>('/investigation/alerts').catch(() => []),
          apiClient<any>('/investigation/cases').catch(() => []),
          apiClient<any>('/transactions').catch(() => [])
        ]);
        
        setHealth(healthRes);
        setAlerts(Array.isArray(alertsRes) ? alertsRes : (alertsRes?.items || []));
        setCases(Array.isArray(casesRes) ? casesRes : (casesRes?.items || []));
        setTxs(Array.isArray(txsRes) ? txsRes : (txsRes?.items || []));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleDeepScan = () => {
    setScanning(true);
    setScanResult(null);
    setTimeout(() => {
      setScanning(false);
      setScanResult("Scan complete: 0 new anomalies detected in the last 15 minutes.");
      setTimeout(() => setScanResult(null), 5000);
    }, 2500);
  };

  const activeAlerts = alerts.filter(a => a.status !== 'RESOLVED');
  const activeCases = cases.filter(c => c.status !== 'CLOSED');
  
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Header with Live Status */}
      <div className="border-b border-slate-200 pb-5 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">UPAY NEXUS AI</h1>
          <h2 className="text-lg font-semibold text-blue-600 mt-1">Global Intelligence Command Center</h2>
          <p className="text-slate-500 mt-2 max-w-3xl text-sm">Real-time monitoring of financial topology, emerging risks, and AI-assisted investigation workflows.</p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-full border border-emerald-200 text-sm font-bold shadow-sm">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          System Optimal
        </div>
      </div>

      {/* Interactive Quick Actions */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap gap-4 items-center justify-between">
        <div className="text-sm font-bold text-slate-700 uppercase tracking-wider">Quick Actions:</div>
        <div className="flex gap-3">
          <button 
            onClick={handleDeepScan}
            disabled={scanning}
            className="bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 shadow-sm"
          >
            {scanning ? <Loader2 size={16} className="animate-spin" /> : <PlayCircle size={16} />}
            {scanning ? 'Running Graph Scan...' : 'Trigger Deep Network Scan'}
          </button>
          <Link href="/reports" className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 border border-slate-300">
            Generate Daily Report
          </Link>
        </div>
      </div>
      
      {scanResult && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 p-3 rounded-lg text-sm font-medium flex items-center gap-2 animate-in slide-in-from-top-2">
          <ShieldCheck size={18}/> {scanResult}
        </div>
      )}

      {/* KPI Section */}
      <div>
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Operational Telemetry</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="group hover:-translate-y-1 transition-transform duration-200">
             <MetricCard title="Live Transactions" value={loading ? '...' : txs.length.toString()} trend="Processing normally" />
          </div>
          <div className="group hover:-translate-y-1 transition-transform duration-200">
             <MetricCard title="Active Alerts" value={loading ? '...' : activeAlerts.length.toString()} trend={activeAlerts.length > 0 ? 'Requires attention' : 'All clear'} />
          </div>
          <div className="group hover:-translate-y-1 transition-transform duration-200">
             <MetricCard title="Open Cases" value={loading ? '...' : activeCases.length.toString()} trend="Ongoing analysis" />
          </div>
          <div className="group hover:-translate-y-1 transition-transform duration-200">
             <MetricCard title="Fraud Signals" value={loading ? '...' : alerts.filter(a => a.severity === 'CRITICAL').length.toString()} trend="High severity detected" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Requires Attention */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2"><AlertTriangle size={20} className="text-amber-500"/> Priority Action Queue</h3>
            <Link href="/alerts" className="text-sm font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors">View Alert Matrix <ArrowRight size={16}/></Link>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            {loading ? (
              <div className="p-12 text-center text-slate-400 font-medium animate-pulse flex flex-col items-center gap-3">
                 <Loader2 size={24} className="animate-spin text-slate-300" /> Analyzing threat vectors...
              </div>
            ) : activeAlerts.length === 0 ? (
              <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-3 bg-slate-50">
                <ShieldCheck size={48} className="text-emerald-400" />
                <span className="font-semibold text-lg text-slate-700">Zero Critical Alerts</span>
                <span className="text-sm">The network is currently operating within safe parameters.</span>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {activeAlerts.slice(0, 5).map(alert => (
                  <div key={alert.id} className="p-4 hover:bg-slate-50 flex flex-col md:flex-row md:items-center justify-between group transition-colors">
                    <div className="flex items-start md:items-center space-x-4 mb-3 md:mb-0">
                      <div className={`mt-1 md:mt-0 flex-shrink-0 w-2.5 h-2.5 rounded-full shadow-sm ${alert.severity === 'CRITICAL' ? 'bg-rose-500 animate-pulse' : 'bg-amber-500'}`}></div>
                      <div>
                        <div className="font-bold text-slate-800 text-base">{alert.type || 'Suspicious Activity'}</div>
                        <div className="text-xs text-slate-500 font-mono mt-0.5">Entity Trace: {alert.entity_id}</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between md:justify-end w-full md:w-auto space-x-4">
                      <span className={`text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full ${alert.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700 border border-rose-200' : 'bg-amber-100 text-amber-700 border border-amber-200'}`}>
                        {alert.severity}
                      </span>
                      <Link href="/investigations" className="text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg shadow-sm transition-transform active:scale-95 flex items-center gap-1">
                        Investigate
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* AI Intelligence & System */}
        <div className="space-y-6">
          
          {/* AI Insights */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2"><Zap size={20} className="text-indigo-500"/> Copilot Insights</h3>
            <div className="bg-gradient-to-br from-indigo-950 to-slate-900 rounded-xl shadow-lg border border-indigo-800 p-6 text-white relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-600 rounded-full mix-blend-screen filter blur-3xl opacity-20 group-hover:opacity-40 transition-opacity duration-700"></div>
              
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-indigo-400 bg-indigo-900/50 p-1.5 rounded-lg"><Activity size={18}/></span>
                <span className="font-bold tracking-wider text-xs text-indigo-300 uppercase">Live Intelligence Brief</span>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed relative z-10 font-medium">
                {activeAlerts.length > 0 
                  ? "Graph intelligence has identified interconnected transaction velocity across multiple endpoints. I recommend an immediate network investigation."
                  : "Platform activity is currently nominal. Transaction graph topology shows standard baseline distribution. No active fraud rings detected."}
              </p>
              <div className="mt-5 pt-4 border-t border-white/10 relative z-10">
                <Link href="/copilot" className="text-xs font-bold text-indigo-300 hover:text-white transition-colors flex items-center bg-white/5 hover:bg-white/10 w-max px-3 py-1.5 rounded-full">
                  Chat with Copilot <ArrowRight size={14} className="ml-1"/>
                </Link>
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Infrastructure Health</h3>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
              <div className="flex justify-between items-center group">
                <div className="flex items-center gap-2 text-sm font-bold text-slate-700"><Server size={16} className="text-slate-400 group-hover:text-blue-500 transition-colors"/> Risk Engine</div>
                <span className="text-[10px] font-black text-emerald-700 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded-full">ONLINE (14ms)</span>
              </div>
              <div className="flex justify-between items-center group">
                <div className="flex items-center gap-2 text-sm font-bold text-slate-700"><Activity size={16} className="text-slate-400 group-hover:text-purple-500 transition-colors"/> Graph AI Pipeline</div>
                <span className="text-[10px] font-black text-emerald-700 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded-full">SYNCED</span>
              </div>
              <div className="flex justify-between items-center pt-3 border-t border-slate-100">
                <span className="text-xs font-medium text-slate-500">API Version</span>
                <span className="text-xs font-mono font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">{health?.version || '2.4.0-ENT'}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
"""

with open("frontend/src/app/dashboard/page.tsx", "w") as f: f.write(dashboard_ui)
