import os

monitoring_ui = """'use client';
import { Activity, Cpu, Server, Database, CheckCircle2 } from 'lucide-react';

export default function Monitoring() {
  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2"><Activity className="text-emerald-600" /> AI Model & System Monitoring</h1>
        <p className="text-sm text-slate-500 mt-1">Real-time inference telemetry and risk engine health metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-sm font-medium flex items-center gap-2 mb-3"><Cpu size={16}/> Inference Latency</div>
          <div className="text-3xl font-bold text-slate-800">14<span className="text-lg text-slate-500 font-normal">ms</span></div>
          <div className="text-xs text-emerald-600 mt-2 font-medium">99th percentile: 28ms</div>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-sm font-medium flex items-center gap-2 mb-3"><Server size={16}/> Model Drift (30d)</div>
          <div className="text-3xl font-bold text-slate-800">1.2<span className="text-lg text-slate-500 font-normal">%</span></div>
          <div className="text-xs text-emerald-600 mt-2 font-medium">Within acceptable bounds</div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-sm font-medium flex items-center gap-2 mb-3"><Database size={16}/> Graph Database</div>
          <div className="text-3xl font-bold text-emerald-600 flex items-center gap-2"><CheckCircle2 size={24}/> HEALTHY</div>
          <div className="text-xs text-slate-500 mt-2 font-medium">Query latency: 8ms</div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-sm font-medium flex items-center gap-2 mb-3"><Activity size={16}/> Engine Uptime</div>
          <div className="text-3xl font-bold text-slate-800">99.99<span className="text-lg text-slate-500 font-normal">%</span></div>
          <div className="text-xs text-slate-500 mt-2 font-medium">Zero downtime detected</div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="font-bold text-slate-800 mb-4">Active AI Models</h3>
        <div className="space-y-4">
           {['XGBoost Transaction Scorer v2.1', 'GNN Network Analyzer (Live)', 'NLP Behavior Profiler'].map((model, i) => (
             <div key={i} className="flex justify-between items-center p-3 border border-slate-100 bg-slate-50 rounded-lg text-sm">
               <span className="font-medium text-slate-700">{model}</span>
               <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold">ONLINE</span>
             </div>
           ))}
        </div>
      </div>
    </div>
  );
}
"""

with open("frontend/src/app/monitoring/page.tsx", "w") as f: f.write(monitoring_ui)
