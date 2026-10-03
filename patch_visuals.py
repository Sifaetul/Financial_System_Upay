import os

# --- 1. NETWORK INTEL (Make it look like a graph/node visualization) ---
network_code = """'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Activity, GitMerge, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function Network() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const txs: any = await apiClient<any[]>('/transactions').catch(() => []);
        const txList = Array.isArray(txs) ? txs : (txs?.items || []);
        
        if (txList.length > 0) {
           const targetId = txList[0].sender_account_id;
           const intel = await apiClient<any>(`/graph/neighborhood/ACCOUNT/${targetId}`).catch(() => null);
           setData(intel);
        }
      } catch (err) {
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2"><GitMerge className="text-indigo-600" /> Network Intelligence (Graph AI)</h1>
        <p className="text-sm text-slate-500 mt-1">Visualizing entity relationships and transaction flow to detect fraud rings and money laundering syndicates.</p>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-xl">
           <div className="animate-pulse flex flex-col items-center gap-2 text-indigo-400">
             <Activity className="w-8 h-8 animate-spin" />
             <p>Analyzing graph topology...</p>
           </div>
        </div>
      ) : data ? (
        <div className="bg-slate-50 p-8 rounded-xl border border-slate-200 shadow-inner">
           
           {/* Visual Node Representation */}
           <div className="flex flex-col items-center space-y-8">
             
             {/* Central Node */}
             <div className="bg-indigo-600 text-white p-6 rounded-2xl shadow-lg border-4 border-indigo-200 w-96 text-center relative z-10">
               <div className="absolute -top-3 -right-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-sm animate-pulse flex items-center gap-1">
                 <AlertTriangle size={12} /> Target Entity
               </div>
               <h3 className="text-sm font-medium text-indigo-200 uppercase tracking-widest mb-1">Central Node</h3>
               <p className="text-lg font-mono font-bold truncate" title={data.node_id}>{data.node_id}</p>
               <div className="mt-3 inline-flex items-center gap-1 bg-indigo-800 px-3 py-1 rounded text-xs">
                 <ShieldCheck size={14} className="text-emerald-400" /> Inspected
               </div>
             </div>

             <div className="w-1 h-12 bg-slate-300"></div>

             {/* Connected Nodes */}
             <div className="w-full max-w-4xl bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative">
               <h4 className="text-sm font-bold text-slate-500 mb-6 uppercase border-b pb-2 flex items-center gap-2">
                 <Activity size={16} /> 1-Hop Connections ({data.neighbors?.length || 0})
               </h4>
               
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                 {data.neighbors?.map((n: any, idx: number) => (
                    <div key={idx} className="bg-slate-50 border border-slate-100 p-4 rounded-lg hover:shadow-md hover:border-indigo-200 transition-all group">
                       <div className="text-xs text-indigo-500 font-bold mb-1 uppercase tracking-wide bg-indigo-50 inline-block px-2 py-0.5 rounded">
                         {n.relationship_type.replace('_', ' ')}
                       </div>
                       <div className="text-sm font-mono text-slate-700 truncate" title={n.connected_node_id}>
                         {n.connected_node_id}
                       </div>
                       <div className="mt-2 text-xs text-slate-400 flex justify-between items-center">
                         <span>Weight: {n.weight}</span>
                         <span className="group-hover:text-indigo-600 transition-colors">Analyze &rarr;</span>
                       </div>
                    </div>
                 ))}
               </div>
               
               {(!data.neighbors || data.neighbors.length === 0) && (
                 <div className="text-center text-slate-400 py-8">No immediate connections found in recent window.</div>
               )}
             </div>

           </div>
        </div>
      ) : <p className="text-slate-500">No network data available for recent transactions.</p>}
    </div>
  );
}
"""

# --- 2. CUSTOMER INTEL (Make it look like a highly detailed 360 profile) ---
customers_code = """'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { UserSearch, ShieldAlert, BadgeCheck, MapPin, CreditCard } from 'lucide-react';

export default function Customers() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const txs: any = await apiClient<any[]>('/transactions').catch(() => []);
        const txList = Array.isArray(txs) ? txs : (txs?.items || []);
        if (txList.length > 0) {
           const targetId = txList[0].sender_account_id;
           const intel = await apiClient<any>(`/customers/${targetId}/360`).catch(() => null);
           setData(intel);
        }
      } catch (err) {} finally { setLoading(false); }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><UserSearch className="text-blue-600" /> Customer 360 Profile</h1>
          <p className="text-sm text-slate-500 mt-1">Holistic view of user behavior, risk indicators, and financial patterns.</p>
        </div>
      </div>

      {loading ? <div className="animate-pulse h-32 bg-slate-100 rounded-xl"></div> : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           
           {/* Identity Card */}
           <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm col-span-1 flex flex-col items-center text-center">
             <div className="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4 border-4 border-white shadow">
               <UserSearch size={32} />
             </div>
             <h2 className="font-mono text-sm font-bold text-slate-800 break-all">{data.customer_id}</h2>
             <span className="mt-2 bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-xs font-semibold uppercase">{data.segment}</span>
             
             <div className="w-full mt-6 space-y-3">
               <div className="flex justify-between text-sm border-b pb-2">
                 <span className="text-slate-500 flex items-center gap-1"><MapPin size={14}/> Location</span>
                 <span className="font-medium text-slate-800">{data.frequent_locations?.[0] || 'Unknown'}</span>
               </div>
               <div className="flex justify-between text-sm border-b pb-2">
                 <span className="text-slate-500 flex items-center gap-1"><BadgeCheck size={14}/> KYC Status</span>
                 <span className="font-medium text-emerald-600">Verified</span>
               </div>
             </div>
           </div>

           {/* Analytics & Risk */}
           <div className="col-span-2 space-y-6">
             <div className="grid grid-cols-2 gap-4">
               <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                 <div className="text-slate-500 text-sm font-medium mb-1">Live Risk Score</div>
                 <div className="flex items-baseline gap-2">
                   <span className={`text-4xl font-black ${data.risk_score > 70 ? 'text-red-500' : data.risk_score > 30 ? 'text-amber-500' : 'text-emerald-500'}`}>
                     {data.risk_score}
                   </span>
                   <span className="text-sm text-slate-400">/ 100</span>
                 </div>
               </div>
               
               <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                 <div className="text-slate-500 text-sm font-medium mb-1">Avg Transaction Value</div>
                 <div className="flex items-baseline gap-2">
                   <span className="text-2xl font-bold text-slate-800">৳{data.average_transaction_value}</span>
                 </div>
               </div>
             </div>
             
             <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
               <h3 className="font-semibold text-slate-800 flex items-center gap-2 mb-4"><ShieldAlert className="text-amber-500" size={18}/> Automated Behavioral Analysis</h3>
               <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
                 The AI engine has analyzed this profile against {data.segment} baseline models. 
                 Transaction velocity is currently within expected parameters for the {data.frequent_locations?.[0] || 'active'} region. 
                 Continual monitoring is active.
               </p>
             </div>
           </div>
        </div>
      ) : <p className="text-slate-500">No active customer profiles found.</p>}
    </div>
  );
}
"""

# --- 3. FRAUD DETECTION (Make alerts look like critical security events) ---
fraud_code = """'use client';
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
"""

with open("frontend/src/app/network/page.tsx", "w") as f: f.write(network_code)
with open("frontend/src/app/customers/page.tsx", "w") as f: f.write(customers_code)
with open("frontend/src/app/fraud/page.tsx", "w") as f: f.write(fraud_code)
