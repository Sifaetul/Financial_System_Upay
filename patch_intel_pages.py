import os

customers_code = """'use client';
import { DataTable } from '@/components/DataTable';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Customers() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch recent txs to get a valid customer ID
        const txs = await apiClient<any[]>('/transactions').catch(() => []);
        const txList = Array.isArray(txs) ? txs : (txs?.items || []);
        
        if (txList.length > 0) {
           const targetId = txList[0].sender_account_id;
           const intel = await apiClient<any>(`/customers/${targetId}/360`).catch(() => null);
           setData(intel);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Customer Intelligence (360)</h1>
      {loading ? <p>Loading live customer profile...</p> : data ? (
        <div className="bg-white p-6 rounded border shadow-sm space-y-4">
           <h2 className="text-lg font-semibold border-b pb-2">Profile Overview: {data.customer_id}</h2>
           <div className="grid grid-cols-2 gap-4">
             <div><span className="text-slate-500 text-sm block">Risk Score</span><span className="font-bold text-lg text-amber-600">{data.risk_score}</span></div>
             <div><span className="text-slate-500 text-sm block">Segment</span><span className="font-bold">{data.segment}</span></div>
             <div><span className="text-slate-500 text-sm block">Average Txn Value</span><span className="font-bold">৳{data.average_transaction_value}</span></div>
             <div><span className="text-slate-500 text-sm block">Frequent Location</span><span className="font-bold">{data.frequent_locations?.[0] || 'Unknown'}</span></div>
           </div>
        </div>
      ) : <p className="text-slate-500">No active customer profiles found in recent transactions.</p>}
    </div>
  );
}
"""

merchants_code = """'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Merchants() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const txs = await apiClient<any[]>('/transactions').catch(() => []);
        const txList = Array.isArray(txs) ? txs : (txs?.items || []);
        
        if (txList.length > 0) {
           // Assume receiver is merchant for demo
           const targetId = txList[0].receiver_account_id;
           const intel = await apiClient<any>(`/merchants/${targetId}/intelligence`).catch(() => null);
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
      <h1 className="text-2xl font-bold">Merchant Intelligence</h1>
      {loading ? <p>Loading merchant profile...</p> : data ? (
        <div className="bg-white p-6 rounded border shadow-sm space-y-4">
           <h2 className="text-lg font-semibold border-b pb-2">Merchant: {data.merchant_id}</h2>
           <div className="grid grid-cols-2 gap-4">
             <div><span className="text-slate-500 text-sm block">Risk Level</span><span className="font-bold text-lg text-green-600">{data.risk_level}</span></div>
             <div><span className="text-slate-500 text-sm block">Daily Volume</span><span className="font-bold">{data.daily_volume}</span></div>
             <div><span className="text-slate-500 text-sm block">Anomalies Detected</span><span className="font-bold text-red-600">{data.anomalies_detected}</span></div>
             <div><span className="text-slate-500 text-sm block">Agent Liquidity</span><span className="font-bold">{data.agent_liquidity_status}</span></div>
           </div>
        </div>
      ) : <p className="text-slate-500">No active merchant profiles found.</p>}
    </div>
  );
}
"""

network_code = """'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Network() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const txs = await apiClient<any[]>('/transactions').catch(() => []);
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
      <h1 className="text-2xl font-bold">Network Intelligence</h1>
      <p className="text-sm text-slate-500">Visualizing 1-hop and 2-hop connected financial entities.</p>
      {loading ? <p>Loading graph topology...</p> : data ? (
        <div className="bg-slate-900 text-white p-6 rounded border border-slate-800 shadow-sm space-y-4 font-mono text-sm">
           <div className="text-emerald-400 mb-4">&gt; GRAPH_TOPOLOGY_LOADED</div>
           <div>TARGET NODE: ACCOUNT::{data.node_id}</div>
           <div>NEIGHBORHOOD SIZE: {data.neighbors?.length || 0} Connected Entities</div>
           <div className="mt-4 border-t border-slate-800 pt-4">
             <div className="text-slate-400 mb-2">DETECTED EDGES:</div>
             {data.neighbors?.map((n: any, idx: number) => (
                <div key={idx} className="ml-4">
                   ├── [{n.relationship_type}] &rarr; {n.connected_node_type}::{n.connected_node_id} (Weight: {n.weight})
                </div>
             ))}
           </div>
        </div>
      ) : <p className="text-slate-500">No network data available.</p>}
    </div>
  );
}
"""

financial_code = """'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Financial() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const txs = await apiClient<any[]>('/transactions').catch(() => []);
        const txList = Array.isArray(txs) ? txs : (txs?.items || []);
        
        if (txList.length > 0) {
           const targetId = txList[0].sender_account_id;
           const intel = await apiClient<any>(`/customers/${targetId}/financial`).catch(() => null);
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
      <h1 className="text-2xl font-bold">Financial Intelligence</h1>
      {loading ? <p>Loading financial goals...</p> : data ? (
        <div className="bg-white p-6 rounded border shadow-sm space-y-4">
           <h2 className="text-lg font-semibold border-b pb-2">Financial Health: {data.customer_id}</h2>
           <div className="grid grid-cols-2 gap-4">
             <div><span className="text-slate-500 text-sm block">Financial Health Score</span><span className="font-bold text-lg text-blue-600">{data.financial_health_score}/100</span></div>
             <div><span className="text-slate-500 text-sm block">Primary Goal</span><span className="font-bold">{data.savings_goals?.[0]?.goal_name || 'N/A'}</span></div>
             <div><span className="text-slate-500 text-sm block">Goal Progress</span><span className="font-bold text-emerald-600">{data.savings_goals?.[0]?.progress_percentage || 0}%</span></div>
             <div><span className="text-slate-500 text-sm block">Category Insights</span><span className="font-bold">{data.spending_insights?.top_category || 'N/A'}</span></div>
           </div>
        </div>
      ) : <p className="text-slate-500">No financial data available.</p>}
    </div>
  );
}
"""

with open("frontend/src/app/customers/page.tsx", "w") as f: f.write(customers_code)
with open("frontend/src/app/merchants/page.tsx", "w") as f: f.write(merchants_code)
with open("frontend/src/app/network/page.tsx", "w") as f: f.write(network_code)
with open("frontend/src/app/financial/page.tsx", "w") as f: f.write(financial_code)
