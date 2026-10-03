# Patch Fraud Page
with open("frontend/src/app/fraud/page.tsx", "r") as f:
    fraud_content = f.read()

fraud_content = fraud_content.replace("'/fraud/signals'", "'/investigation/alerts'")
# Make sure it parses the array
fraud_content = fraud_content.replace(
    "setSignals(Array.isArray(res) ? res : (res.items || []));",
    "const allAlerts = Array.isArray(res) ? res : (res.items || []);\n        setSignals(allAlerts.filter(a => a.type === 'FRAUD_RISK' || a.severity === 'CRITICAL'));"
)
fraud_content = fraud_content.replace("sig.severity === 'High'", "sig.severity === 'CRITICAL'")

with open("frontend/src/app/fraud/page.tsx", "w") as f:
    f.write(fraud_content)


# Patch Risk Page
risk_page_content = """'use client';
import { MetricCard } from '@/components/MetricCard';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { DataTable } from '@/components/DataTable';

export default function Risk() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchRisk() {
      try {
        const casesRes = await apiClient<any[]>('/investigation/cases').catch(() => []);
        setCases(Array.isArray(casesRes) ? casesRes : (casesRes?.items || []));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchRisk();
  }, []);

  const activeCases = cases.filter(c => c.status !== 'CLOSED');
  const criticalCases = cases.filter(c => c.severity === 'CRITICAL');

  const rows = activeCases.slice(0, 10).map((c: any) => [
    c.number || c.id.substring(0,8),
    c.status,
    c.severity,
    c.priority
  ]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Risk Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricCard title="Active Risk Cases" value={loading ? '...' : activeCases.length.toString()} trend="Requires review" />
        <MetricCard title="Critical Risk Cases" value={loading ? '...' : criticalCases.length.toString()} trend="Urgent action required" />
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Latest Risk Cases</h2>
        {loading ? <p>Loading...</p> : <DataTable headers={['Case Number', 'Status', 'Severity', 'Priority']} rows={rows} />}
      </div>
    </div>
  );
}
"""

with open("frontend/src/app/risk/page.tsx", "w") as f:
    f.write(risk_page_content)
