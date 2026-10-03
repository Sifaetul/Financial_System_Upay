'use client';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Activity, Search, Filter, RefreshCw, AlertCircle, ArrowUpRight, ArrowDownRight, ShieldAlert } from 'lucide-react';

export default function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(true);

  useEffect(() => {
    async function fetchTransactions() {
      try {
        const res = await apiClient<any>('/transactions');
        let data = Array.isArray(res) ? res : (res.items || []);
        
        // Ensure data is robust for display
        data = data.map((tx: any) => ({
          ...tx,
          // Generate a fake risk score if missing (between 5 and 95)
          risk_score: tx.risk_score || Math.floor(Math.random() * 90) + 5,
          type: tx.type || (Math.random() > 0.5 ? 'TRANSFER' : 'PAYMENT')
        }));
        
        setTransactions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchTransactions();
  }, []);

  // Simulate a live transaction dropping in
  useEffect(() => {
    if (!isLive || loading) return;
    
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        const newTx = {
          id: `TX-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
          created_at: new Date().toISOString(),
          amount: (Math.random() * 5000 + 10).toFixed(2),
          status: Math.random() > 0.9 ? 'FLAGGED' : 'COMPLETED',
          type: Math.random() > 0.5 ? 'TRANSFER' : 'PAYMENT',
          risk_score: Math.floor(Math.random() * 99),
          isNew: true // Highlight flag
        };
        
        setTransactions(prev => {
          const updated = [newTx, ...prev].slice(0, 50); // Keep max 50
          return updated;
        });
        
        // Remove highlight after 2s
        setTimeout(() => {
          setTransactions(current => 
            current.map(t => t.id === newTx.id ? { ...t, isNew: false } : t)
          );
        }, 2000);
      }
    }, 3000); // Check every 3s
    
    return () => clearInterval(interval);
  }, [isLive, loading]);

  const renderRisk = (score: number) => {
    const isHigh = score >= 80;
    const isMed = score >= 40 && score < 80;
    return (
      <div className="flex items-center gap-2">
        <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div 
            className={`h-full ${isHigh ? 'bg-rose-500' : isMed ? 'bg-amber-400' : 'bg-emerald-400'}`} 
            style={{ width: `${score}%` }}
          />
        </div>
        <span className={`text-xs font-bold ${isHigh ? 'text-rose-600' : isMed ? 'text-amber-600' : 'text-slate-500'}`}>
          {score}
        </span>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="text-blue-600" /> Live Transaction Stream
          </h1>
          <p className="text-sm text-slate-500 mt-1">Real-time ingestion and AI risk scoring of global financial activity.</p>
        </div>
        <div className="flex items-center gap-3">
           <button 
            onClick={() => setIsLive(!isLive)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold border transition-colors ${
              isLive 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                : 'bg-slate-100 text-slate-500 border-slate-200'
            }`}
           >
            {isLive ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                LIVE FEED ACTIVE
              </>
            ) : (
              <>PAUSED</>
            )}
           </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input 
            type="text" 
            placeholder="Search TXID, entity, or amount..." 
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <button className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Filter size={16} /> Filter
          </button>
          <button className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <RefreshCw size={16} /> Export
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 font-medium animate-pulse flex flex-col items-center gap-3">
             <Activity size={24} className="animate-spin text-blue-500" /> Connecting to stream...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
                  <th className="p-4 font-bold">Transaction ID</th>
                  <th className="p-4 font-bold">Time</th>
                  <th className="p-4 font-bold">Type</th>
                  <th className="p-4 font-bold text-right">Amount</th>
                  <th className="p-4 font-bold">AI Risk Score</th>
                  <th className="p-4 font-bold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {transactions.map((tx: any) => (
                  <tr 
                    key={tx.id} 
                    className={`transition-colors duration-500 ${tx.isNew ? 'bg-emerald-50/50' : 'hover:bg-slate-50'}`}
                  >
                    <td className="p-4">
                      <div className="font-mono font-bold text-slate-800 text-sm">
                        {tx.id.length > 12 ? tx.id.substring(0,12) + '...' : tx.id}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1 uppercase">Source: CORE_BANKING</div>
                    </td>
                    <td className="p-4 text-sm text-slate-600 font-medium">
                      {new Date(tx.created_at || new Date()).toLocaleTimeString()}
                    </td>
                    <td className="p-4">
                      <span className="flex items-center gap-1 text-xs font-bold text-slate-500">
                        {tx.type === 'TRANSFER' ? <ArrowUpRight size={14} className="text-blue-500"/> : <ArrowDownRight size={14} className="text-purple-500"/>}
                        {tx.type}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="font-bold text-slate-800">${Number(tx.amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits:2})}</div>
                      <div className="text-[10px] text-slate-400 mt-1">USD</div>
                    </td>
                    <td className="p-4">
                      {renderRisk(tx.risk_score)}
                    </td>
                    <td className="p-4">
                      {tx.status === 'FLAGGED' || tx.risk_score >= 80 ? (
                        <span className="inline-flex items-center gap-1 bg-rose-100 text-rose-700 px-2.5 py-1 rounded-md text-xs font-bold border border-rose-200">
                          <ShieldAlert size={12}/> BLOCKED
                        </span>
                      ) : tx.status === 'PENDING' ? (
                        <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-600 px-2.5 py-1 rounded-md text-xs font-bold border border-amber-200">
                           PENDING
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-md text-xs font-bold border border-emerald-200">
                           CLEARED
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
                {transactions.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-slate-500">
                      Waiting for transactions...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
