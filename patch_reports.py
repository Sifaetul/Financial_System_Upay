import os

reports_ui = """'use client';
import { useState } from 'react';
import { FileText, Download, FileSpreadsheet, Plus, Filter, Calendar } from 'lucide-react';

export default function Reports() {
  const [generating, setGenerating] = useState(false);
  
  const mockReports = [
    { id: 'REP-1029', title: 'Q3 Automated Fraud Ring Analysis', type: 'PDF', date: '2026-10-01', size: '2.4 MB', status: 'Ready' },
    { id: 'REP-1028', title: 'High-Risk Merchant Exposure List', type: 'CSV', date: '2026-09-28', size: '156 KB', status: 'Ready' },
    { id: 'REP-1027', title: 'Monthly Compliance Audit Log', type: 'PDF', date: '2026-09-01', size: '5.1 MB', status: 'Ready' },
    { id: 'REP-1026', title: 'Cross-Border Transaction Anomalies', type: 'CSV', date: '2026-08-15', size: '890 KB', status: 'Ready' }
  ];

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => setGenerating(false), 2000);
  };

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><FileText className="text-blue-600" /> Automated Reports</h1>
          <p className="text-sm text-slate-500 mt-1">Generate, export, and securely share financial intelligence reports.</p>
        </div>
        <button 
          onClick={handleGenerate}
          disabled={generating}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded font-medium text-sm transition-colors flex items-center gap-2 shadow-sm"
        >
          {generating ? <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <Plus size={16} />}
          {generating ? 'Compiling Data...' : 'Generate New Report'}
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center gap-4 text-sm text-slate-600">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded border border-slate-200">
            <Filter size={14} /> All Types
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded border border-slate-200">
            <Calendar size={14} /> Last 90 Days
          </div>
        </div>
        
        <div className="divide-y divide-slate-100">
          {mockReports.map(report => (
            <div key={report.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between hover:bg-slate-50 transition-colors group">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${report.type === 'PDF' ? 'bg-rose-100 text-rose-600' : 'bg-emerald-100 text-emerald-600'}`}>
                  {report.type === 'PDF' ? <FileText size={20} /> : <FileSpreadsheet size={20} />}
                </div>
                <div>
                  <h3 className="font-bold text-slate-800">{report.title}</h3>
                  <div className="text-xs text-slate-500 flex items-center gap-3 mt-1">
                    <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">{report.id}</span>
                    <span>Generated: {report.date}</span>
                    <span>{report.size}</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 md:mt-0 flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="text-slate-500 hover:text-blue-600 flex items-center gap-1 text-sm font-medium transition-colors">
                  <Download size={16} /> Download {report.type}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      
    </div>
  );
}
"""

with open("frontend/src/app/reports/page.tsx", "w") as f: f.write(reports_ui)

