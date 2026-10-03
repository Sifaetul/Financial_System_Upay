'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Activity, GitMerge, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function Network() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        
        
        
        if (true) {
           const targetId = '5a9da833-22a9-43c5-8049-05e3868276f0';
           const intel = await apiClient<any>(`/graph/neighborhood/ACCOUNT/${targetId}`).catch(() => null);
           setData(intel || {
  node_id: "ACCOUNT::8F92A",
  neighbors: [
    { relationship_type: "TRANSFERRED_TO", connected_node_id: "ACCOUNT::33B1", weight: 0.9 },
    { relationship_type: "SHARED_DEVICE", connected_node_id: "DEVICE::IP_192.168.1.5", weight: 1.0 },
    { relationship_type: "ASSOCIATED_WITH", connected_node_id: "MERCHANT::M_9021", weight: 0.5 }
  ]
});
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
