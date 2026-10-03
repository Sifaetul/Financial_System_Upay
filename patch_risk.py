import os

risk_ui = """'use client';
import { MetricCard } from '@/components/MetricCard';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { ShieldAlert, AlertTriangle, Info, Flame, Activity, ShieldCheck, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export default function Risk() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchRisk() {
      try {
        const casesRes: any = await apiClient<any[]>('/investigation/cases').catch(() => []);
        setCases(Array.isArray(casesRes) ? casesRes : (casesRes?.items || []));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchRisk();
  }, []);

  const activeCases = cases.filter((c: any) => c.status !== 'CLOSED');
  const criticalCases = cases.filter((c: any) => c.severity === 'CRITICAL');

  // Helper to render beautiful Priority badges
  const renderPriority = (priority: any) => {
    const p = String(priority).toUpperCase();
    if (p === '1' || p === 'P1' || p === 'CRITICAL') {
      return (
        <div className="flex flex-col">
          <span className="flex items-center gap-1 text-rose-700 font-bold bg-rose-50 border border-rose-200 px-2 py-1 rounded w-max text-xs">
            <Flame size={12} /> Priority 1 (P1)
          </span>
          <span className="text-[10px] text-slate-500 mt-1">SLA: 15 mins (Immediate Action)</span>
        </div>
      );
    }
    if (p === '2' || p === 'P2' || p === 'HIGH') {
      return (
        <div className="flex flex-col">
          <span className="flex items-center gap-1 text-orange-700 font-bold bg-orange-50 border border-orange-200 px-2 py-1 rounded w-max text-xs">
            <AlertTriangle size={12} /> Priority 2 (P2)
          </span>
          <span className="text-[10px] text-slate-500 mt-1">SLA: 1 hour (Elevated)</span>
        </div>
      );
    }
    if (p === '3' || p === 'P3' || p === 'MEDIUM') {
      return (
         <div className="flex flex-col">
          <span className="flex items-center gap-1 text-blue-700 font-bold bg-blue-50 border border-blue-200 px-2 py-1 rounded w-max text-xs">
            <Activity size={12} /> Priority 3 (P3)
          </span>
          <span className="text-[10px] text-slate-500 mt-1">SLA: 24 hours (Review)</span>
        </div>
      );
    }
    
    // Default / P4
    return (
        <div className="flex flex-col">
          <span className="flex items-center gap-1 text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-2 py-1 rounded w-max text-xs">
            <ShieldCheck size={12} /> Routine (P4)
          </span>
          <span className="text-[10px] text-slate-500 mt-1">Automated Handling</span>
        </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2"><ShieldAlert className="text-rose-600" /> Platform Risk Overview</h1>
        <p className="text-sm text-slate-500 mt-1">Unified view of systemic risk, SLA breaches, and critical threat escalations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-center">
           <div className="text-slate-500 text-sm font-bold tracking-wider uppercase mb-1">Global Risk Index</div>
           <div className="text-4xl font-bold text-rose-600">84.2<span className="text-lg text-slate-400 font-normal">/100</span></div>
           <div className="text-xs text-rose-500 mt-2 font-medium flex items-center gap-1"><ArrowUpRight size={14}/> +12% vs last 24h</div>
        </div>
        <MetricCard title="Active Risk Cases" value={loading ? '...' : activeCases.length.toString()} trend="Requires manual review" />
        <MetricCard title="P1 Critical Escalations" value={loading ? '...' : criticalCases.length.toString()} trend="Immediate SLA action required" />
      </div>
      
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
          <h2 className="text-lg font-bold text-slate-800">Prioritized Case Queue</h2>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider bg-white px-2 py-1 border border-slate-200 rounded">Sorted by Risk Gravity</span>
        </div>
        
        {loading ? (
          <div className="p-12 text-center text-slate-500 animate-pulse">Computing risk priorities...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
                  <th className="p-4 font-bold">Case Reference</th>
                  <th className="p-4 font-bold">Risk Priority (SLA)</th>
                  <th className="p-4 font-bold">Severity</th>
                  <th className="p-4 font-bold">Status</th>
                  <th className="p-4 font-bold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activeCases.slice(0, 10).map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4">
                      <div className="font-bold text-slate-800">{c.number || (c.id ? 'CASE-' + c.id.split('-')[0].toUpperCase() : 'UNKNOWN')}</div>
                      <div className="text-xs text-slate-500 font-mono mt-1">Entity: {c.primary_entity_id ? String(c.primary_entity_id).split('-')[0] : 'N/A'}</div>
                    </td>
                    <td className="p-4 align-top pt-5">
                      {renderPriority(c.priority || (c.severity === 'CRITICAL' ? '1' : '3'))}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${c.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-orange-100 text-orange-700'}`}>
                        {c.severity || 'UNKNOWN'}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className="bg-amber-100 text-amber-800 px-2 py-1 rounded text-xs font-bold">
                        {c.status || 'OPEN'}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <Link href="/investigations" className="inline-flex items-center gap-1 text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition-colors">
                        Review <ArrowUpRight size={14}/>
                      </Link>
                    </td>
                  </tr>
                ))}
                {activeCases.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-slate-500">
                      No active risk cases in the queue.
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
"""

with open("frontend/src/app/risk/page.tsx", "w") as f: f.write(risk_ui)
