'use client';
import { MetricCard } from '@/components/MetricCard';
export default function Showcase() {
  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-extrabold text-slate-900">UPAY NEXUS Pipeline Showcase</h1>
        <p className="text-lg text-gray-500">A visual representation of the intelligence pipeline.</p>
      </div>
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-8 bg-slate-50 rounded-xl border border-slate-200">
        <MetricCard title="1. Ingestion" value="Transactions" />
        <span className="text-3xl text-slate-400">&rarr;</span>
        <MetricCard title="2. Fraud Engine" value="Scoring" />
        <span className="text-3xl text-slate-400">&rarr;</span>
        <MetricCard title="3. Network Graph" value="Entity Links" />
        <span className="text-3xl text-slate-400">&rarr;</span>
        <MetricCard title="4. Copilot" value="Investigation" />
      </div>
    </div>
  );
}
