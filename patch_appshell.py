import os

with open("frontend/src/components/AppShell.tsx", "r") as f: content = f.read()

new_appshell = """'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X } from 'lucide-react';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const NavLink = ({ href, label, indent = false }: { href: string, label: string, indent?: boolean }) => {
    const isActive = pathname === href || pathname?.startsWith(`${href}/`);
    return (
      <Link 
        href={href} 
        className={`block px-3 py-2 rounded text-sm ${isActive ? 'bg-blue-600 text-white font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'} ${indent ? 'ml-4 border-l border-slate-700 pl-4' : ''}`}
      >
        {label}
      </Link>
    );
  };

  const NavGroup = ({ title, children }: { title: string, children: React.ReactNode }) => {
    const [open, setOpen] = useState(true);
    return (
      <div className="space-y-1 mt-2">
        <button 
          onClick={() => setOpen(!open)} 
          className="w-full flex items-center justify-between text-left px-3 py-2 text-sm font-semibold text-slate-100 hover:bg-slate-800 rounded transition-colors"
        >
          {title}
          <span className="text-slate-500 text-xs">{open ? '▼' : '▶'}</span>
        </button>
        {open && <div className="space-y-1">{children}</div>}
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      
      {/* Sidebar */}
      <aside className={`${isSidebarOpen ? 'w-64' : 'w-0 opacity-0 overflow-hidden'} transition-all duration-300 ease-in-out bg-slate-950 text-white flex flex-col shadow-xl z-20 border-r border-slate-800 shrink-0`}>
        <div className="p-5 flex justify-between items-center border-b border-slate-800">
          <div className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-white whitespace-nowrap">UPAY NEXUS AI</span>
            <span className="text-[10px] uppercase tracking-wider text-emerald-400 font-semibold mt-1">Intelligence Operations</span>
          </div>
          {/* Optional close button inside sidebar for mobile view if needed */}
        </div>
        
        <nav className="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar">
          <div className="px-3 pt-2 pb-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider">Main</div>
          <NavLink href="/dashboard" label="Overview" />
          <NavLink href="/transactions" label="Live Activity" />

          <NavGroup title="Risk & Fraud">
            <NavLink href="/risk" label="Risk Overview" indent />
            <NavLink href="/fraud" label="Fraud Detection" indent />
          </NavGroup>

          <NavGroup title="Intelligence">
            <NavLink href="/customers" label="Customer Intel" indent />
            <NavLink href="/merchants" label="Merchant Intel" indent />
            <NavLink href="/network" label="Network Intel" indent />
            <NavLink href="/financial" label="Financial Intel" indent />
          </NavGroup>

          <NavGroup title="Investigations">
            <NavLink href="/investigations" label="Active Cases" indent />
          </NavGroup>

          <NavLink href="/copilot" label="AI Copilot" />
          <NavLink href="/reports" label="Reports" />

          <div className="px-3 pt-6 pb-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider">System</div>
          <NavLink href="/alerts" label="Alerts" />
          <NavLink href="/monitoring" label="Model Monitoring" />
          <NavLink href="/governance/audit" label="Audit Log" />
          <NavLink href="/settings" label="Settings" />
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-50/50">
        
        {/* Top Header */}
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 sticky top-0 z-10 shadow-sm shrink-0">
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-slate-100 rounded-md text-slate-500 transition-colors"
            title="Toggle Sidebar"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <div className="ml-4 text-sm font-medium text-slate-600 capitalize">
            {pathname === '/' ? 'Dashboard' : pathname.split('/').filter(Boolean).join(' / ')}
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </div>
        
      </main>
    </div>
  );
}
"""

with open("frontend/src/components/AppShell.tsx", "w") as f: f.write(new_appshell)
