import os

# Define the base structure
components_dir = "frontend/src/components"
app_dir = "frontend/src/app"

os.makedirs(components_dir, exist_ok=True)
os.makedirs(app_dir, exist_ok=True)

# Components to generate
components = {
    "AppShell.tsx": """
import React from 'react';
import Link from 'next/link';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-4 text-xl font-bold border-b border-slate-700">UPAY NEXUS AI</div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-2 text-sm">
          <Link href="/dashboard" className="block hover:bg-slate-800 p-2 rounded">Dashboard</Link>
          <Link href="/transactions" className="block hover:bg-slate-800 p-2 rounded">Transactions</Link>
          <Link href="/risk" className="block hover:bg-slate-800 p-2 rounded">Risk</Link>
          <Link href="/fraud" className="block hover:bg-slate-800 p-2 rounded">Fraud</Link>
          <Link href="/network" className="block hover:bg-slate-800 p-2 rounded">Network</Link>
          <Link href="/customers" className="block hover:bg-slate-800 p-2 rounded">Customers</Link>
          <Link href="/merchants" className="block hover:bg-slate-800 p-2 rounded">Merchants</Link>
          <Link href="/agents" className="block hover:bg-slate-800 p-2 rounded">Agents</Link>
          <Link href="/financial" className="block hover:bg-slate-800 p-2 rounded">Financial</Link>
          <Link href="/alerts" className="block hover:bg-slate-800 p-2 rounded">Alerts</Link>
          <Link href="/investigations" className="block hover:bg-slate-800 p-2 rounded">Investigations</Link>
          <Link href="/copilot" className="block hover:bg-slate-800 p-2 rounded">Copilot</Link>
          <Link href="/competition" className="block hover:bg-slate-800 p-2 rounded">Competition</Link>
          <Link href="/monitoring" className="block hover:bg-slate-800 p-2 rounded">Monitoring</Link>
          <div className="pt-4 pb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Governance</div>
          <Link href="/governance/models" className="block hover:bg-slate-800 p-2 rounded">Models</Link>
          <Link href="/governance/audit" className="block hover:bg-slate-800 p-2 rounded">Audit</Link>
          <div className="pt-4 pb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Misc</div>
          <Link href="/showcase" className="block hover:bg-slate-800 p-2 rounded text-emerald-400">Showcase</Link>
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}
""",
    "MetricCard.tsx": """
import React from 'react';
export function MetricCard({ title, value, trend }: { title: string, value: string | number, trend?: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
      <span className="text-gray-500 text-sm font-medium mb-1">{title}</span>
      <span className="text-3xl font-bold text-gray-900">{value}</span>
      {trend && <span className="text-sm mt-2 text-emerald-600 font-medium">{trend}</span>}
    </div>
  );
}
""",
    "AlertCard.tsx": """
import React from 'react';
export function AlertCard({ title, message, severity = 'info' }: { title: string, message: string, severity?: 'info' | 'warning' | 'critical' }) {
  const colors = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    critical: 'bg-red-50 border-red-200 text-red-800'
  };
  return (
    <div className={`p-4 rounded-lg border ${colors[severity]} mb-4`}>
      <h4 className="font-semibold">{title}</h4>
      <p className="text-sm mt-1">{message}</p>
    </div>
  );
}
""",
    "Badge.tsx": """
import React from 'react';
export function Badge({ children, color = 'blue' }: { children: React.ReactNode, color?: 'blue' | 'green' | 'red' | 'yellow' | 'gray' }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    red: 'bg-red-100 text-red-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    gray: 'bg-gray-100 text-gray-800',
  };
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[color]}`}>
      {children}
    </span>
  );
}
""",
    "DataTable.tsx": """
import React from 'react';
export function DataTable({ headers, rows }: { headers: string[], rows: any[][] }) {
  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((h, i) => <th key={i} className="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">{h}</th>)}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {row.map((cell, j) => <td key={j} className="px-6 py-4 whitespace-nowrap text-gray-900">{cell}</td>)}
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={headers.length} className="px-6 py-4 text-center text-gray-500">No data available</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
"""
}

for name, content in components.items():
    with open(os.path.join(components_dir, name), "w") as f:
        f.write(content.strip() + "\n")

# Pages to generate
pages = {
    "dashboard/page.tsx": """
'use client';
import { MetricCard } from '@/components/MetricCard';
import { AlertCard } from '@/components/AlertCard';
import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  
  useEffect(() => {
    // Simulate fetch
    setData({ health: '99.9%', riskTrend: '+2.4%', alerts: 3 });
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Platform Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Platform Health" value={data?.health || '...'} trend="Operational" />
        <MetricCard title="Risk Trend" value={data?.riskTrend || '...'} trend="Needs Attention" />
        <MetricCard title="Active Alerts" value={data?.alerts || '...'} trend="Resolved 12 today" />
      </div>
      <div>
        <h2 className="text-lg font-semibold mb-4">Critical Alerts</h2>
        <AlertCard title="Unusual Volume Spike" message="High transaction volume detected in Node B." severity="critical" />
        <AlertCard title="Model Drift Warning" message="Fraud detection model accuracy dropped by 0.5%." severity="warning" />
      </div>
    </div>
  );
}
""",
    "transactions/page.tsx": """
'use client';
import { DataTable } from '@/components/DataTable';
import Link from 'next/link';

export default function Transactions() {
  const rows = [
    [<Link href="/transactions/TX-1001" className="text-blue-600 hover:underline">TX-1001</Link>, '2026-10-01', '$150.00', 'Completed'],
    [<Link href="/transactions/TX-1002" className="text-blue-600 hover:underline">TX-1002</Link>, '2026-10-01', '$2,450.00', 'Flagged']
  ];
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Transactions</h1>
      <DataTable headers={['ID', 'Date', 'Amount', 'Status']} rows={rows} />
    </div>
  );
}
""",
    "transactions/[id]/page.tsx": """
'use client';
export default function TransactionDetail({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Transaction {params.id}</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-600">Details for {params.id} would load here.</p>
      </div>
    </div>
  );
}
""",
    "risk/page.tsx": """
'use client';
import { MetricCard } from '@/components/MetricCard';
export default function Risk() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Risk Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricCard title="Current Risk Score" value="42 / 100" trend="Moderate" />
        <MetricCard title="High Severity Signals" value="14" trend="-2 from yesterday" />
      </div>
    </div>
  );
}
""",
    "fraud/page.tsx": """
'use client';
import { DataTable } from '@/components/DataTable';
import { Badge } from '@/components/Badge';
export default function Fraud() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Fraud Overview</h1>
      <DataTable headers={['Signal ID', 'Type', 'Severity', 'Status']} rows={[
        ['SIG-991', 'Account Takeover', <Badge color="red">High</Badge>, 'Open'],
        ['SIG-992', 'Synthetic Identity', <Badge color="yellow">Medium</Badge>, 'Investigating']
      ]} />
    </div>
  );
}
""",
    "network/page.tsx": """
'use client';
import { useEffect, useState } from 'react';

export default function Network() {
  const [ForceGraph2D, setForceGraph2D] = useState<any>(null);
  useEffect(() => {
    import('react-force-graph-2d').then(mod => setForceGraph2D(() => mod.default));
  }, []);

  const graphData = {
    nodes: [{ id: '1', name: 'Alice' }, { id: '2', name: 'Bob' }, { id: '3', name: 'Charlie' }],
    links: [{ source: '1', target: '2' }, { source: '2', target: '3' }]
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <h1 className="text-2xl font-bold">Network Graph</h1>
      <div className="flex-1 bg-white border border-gray-200 rounded-lg overflow-hidden">
        {ForceGraph2D ? (
          <ForceGraph2D
            graphData={graphData}
            width={800}
            height={500}
            nodeAutoColorBy="group"
            nodeCanvasObject={(node: any, ctx: any, globalScale: any) => {
              const label = node.name || node.id;
              const fontSize = 12/globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;
              ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.beginPath(); ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false); ctx.fill();
              ctx.fillStyle = 'black';
              ctx.fillText(label, node.x, node.y + 8);
            }}
          />
        ) : <div className="p-8">Loading graph...</div>}
      </div>
    </div>
  );
}
""",
    "customers/page.tsx": """
'use client';
export default function Customers() { return <div className="p-6"><h1 className="text-2xl font-bold">Customers Profiles</h1></div>; }
""",
    "financial/page.tsx": """
'use client';
export default function Financial() { return <div className="p-6"><h1 className="text-2xl font-bold">Financial Overview</h1></div>; }
""",
    "merchants/page.tsx": """
'use client';
export default function Merchants() { return <div className="p-6"><h1 className="text-2xl font-bold">Merchants Profiles</h1></div>; }
""",
    "agents/page.tsx": """
'use client';
export default function Agents() { return <div className="p-6"><h1 className="text-2xl font-bold">Agents Profiles</h1></div>; }
""",
    "alerts/page.tsx": """
'use client';
export default function Alerts() { return <div className="p-6"><h1 className="text-2xl font-bold">Ops Alerts</h1></div>; }
""",
    "investigations/page.tsx": """
'use client';
export default function Investigations() { return <div className="p-6"><h1 className="text-2xl font-bold">Case Management</h1></div>; }
""",
    "copilot/page.tsx": """
'use client';
export default function Copilot() {
  return (
    <div className="space-y-6 flex flex-col h-[80vh]">
      <h1 className="text-2xl font-bold">AI Assistant</h1>
      <div className="flex-1 bg-white border border-gray-200 rounded-lg p-6 flex flex-col justify-end">
        <div className="bg-gray-100 p-4 rounded-lg self-start max-w-lg mb-4">Hello! I am your UPAY NEXUS Copilot. How can I help you investigate today?</div>
        <input type="text" placeholder="Type a message..." className="w-full border border-gray-300 rounded p-3" />
      </div>
    </div>
  );
}
""",
    "competition/page.tsx": """
'use client';
export default function Competition() { return <div className="p-6"><h1 className="text-2xl font-bold">Competition & What-If Simulations</h1></div>; }
""",
    "monitoring/page.tsx": """
'use client';
export default function Monitoring() { return <div className="p-6"><h1 className="text-2xl font-bold">System Monitoring</h1></div>; }
""",
    "governance/models/page.tsx": """
'use client';
export default function ModelsGov() { return <div className="p-6"><h1 className="text-2xl font-bold">Model Governance</h1></div>; }
""",
    "governance/audit/page.tsx": """
'use client';
export default function AuditGov() { return <div className="p-6"><h1 className="text-2xl font-bold">Audit Logs</h1></div>; }
""",
    "showcase/page.tsx": """
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
""",
    "layout.tsx": """
import './globals.css';
import { AppShell } from '@/components/AppShell';

export const metadata = {
  title: 'UPAY NEXUS AI',
  description: 'Fintech intelligence platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  );
}
"""
}

for path_name, content in pages.items():
    full_path = os.path.join(app_dir, path_name)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content.strip() + "\n")

# Re-write the page.tsx at the root of app to redirect to dashboard or show welcome
with open(os.path.join(app_dir, "page.tsx"), "w") as f:
    f.write("""
import { redirect } from 'next/navigation';
export default function Home() {
  redirect('/dashboard');
}
""".strip() + "\n")

print("Frontend structure generated.")
