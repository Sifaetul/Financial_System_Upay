import os

files_to_update = {
    'frontend/src/app/dashboard/page.tsx': ''''use client';
import { MetricCard } from '@/components/MetricCard';
import { AlertCard } from '@/components/AlertCard';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await apiClient<any>('/system/health');
        setData(res);
      } catch (err) {
        // Fallback or empty state
        setData(null);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Platform Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Platform Health" value={loading ? '...' : (data?.status || 'Unknown')} trend="Operational" />
        <MetricCard title="Version" value={loading ? '...' : (data?.version || 'Unknown')} trend="Needs Attention" />
        <MetricCard title="Active Alerts" value={loading ? '...' : '0'} trend="Resolved 12 today" />
      </div>
      <div>
        <h2 className="text-lg font-semibold mb-4">Critical Alerts</h2>
        <AlertCard title="System Status" message={loading ? 'Loading...' : `Status: ${data?.status || 'Unknown'}`} severity="warning" />
      </div>
    </div>
  );
}
''',
    'frontend/src/app/transactions/page.tsx': ''''use client';
import { DataTable } from '@/components/DataTable';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTransactions() {
      try {
        const res = await apiClient<any>('/transactions');
        setTransactions(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchTransactions();
  }, []);

  const rows = transactions.map((tx: any) => [
    <Link key={tx.id} href={`/transactions/${tx.id}`} className="text-blue-600 hover:underline">{tx.id}</Link>,
    tx.created_at || tx.date || 'Unknown',
    tx.amount || '$0.00',
    tx.status || 'Pending'
  ]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Transactions</h1>
      {loading ? <p>Loading...</p> : <DataTable headers={['ID', 'Date', 'Amount', 'Status']} rows={rows} />}
    </div>
  );
}
''',
    'frontend/src/app/risk/page.tsx': ''''use client';
import { MetricCard } from '@/components/MetricCard';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Risk() {
  const [riskData, setRiskData] = useState<any>(null);
  
  useEffect(() => {
    async function fetchRisk() {
      try {
        const res = await apiClient<any>('/risk/summary').catch(() => apiClient<any>('/system/health'));
        setRiskData(res);
      } catch (e) {
        console.error(e);
      }
    }
    fetchRisk();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Risk Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricCard title="Current Risk Score" value={riskData?.score || 'N/A'} trend="Moderate" />
        <MetricCard title="High Severity Signals" value={riskData?.high_severity || '0'} trend="Stable" />
      </div>
    </div>
  );
}
''',
    'frontend/src/app/fraud/page.tsx': ''''use client';
import { DataTable } from '@/components/DataTable';
import { Badge } from '@/components/Badge';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Fraud() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSignals() {
      try {
        const res = await apiClient<any>('/fraud/signals').catch(() => ({ items: [] }));
        setSignals(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchSignals();
  }, []);

  const rows = signals.map((sig: any) => [
    sig.id,
    sig.type || 'Unknown',
    <Badge key={sig.id} color={sig.severity === 'High' ? 'red' : 'yellow'}>{sig.severity || 'Low'}</Badge>,
    sig.status || 'Open'
  ]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Fraud Overview</h1>
      {loading ? <p>Loading...</p> : <DataTable headers={['Signal ID', 'Type', 'Severity', 'Status']} rows={rows} />}
    </div>
  );
}
''',
    'frontend/src/app/alerts/page.tsx': ''''use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Alerts() { 
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const res = await apiClient<any>('/alerts').catch(() => ({ items: [] }));
        setAlerts(res.items || []);
      } catch (e) {
        console.error(e);
      }
    }
    fetchAlerts();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Ops Alerts</h1>
      <ul>
        {alerts.map((a: any, i) => <li key={i}>{a.message || 'Alert'}</li>)}
        {alerts.length === 0 && <li>No alerts</li>}
      </ul>
    </div>
  ); 
}
''',
    'frontend/src/app/customers/page.tsx': ''''use client';
import { DataTable } from '@/components/DataTable';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Customers() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCustomers() {
      try {
        const res = await apiClient<any>('/customers').catch(() => ({ items: [] }));
        setCustomers(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchCustomers();
  }, []);

  const rows = customers.map((c: any) => [
    <Link key={c.id} href={`/customers/${c.id}`} className="text-blue-600 hover:underline">{c.id}</Link>,
    c.name || 'Unknown',
    c.status || 'Active'
  ]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Customers</h1>
      {loading ? <p>Loading...</p> : <DataTable headers={['ID', 'Name', 'Status']} rows={rows} />}
    </div>
  );
}
'''
}

for filepath, content in files_to_update.items():
    with open(filepath, 'w') as f:
        f.write(content)
