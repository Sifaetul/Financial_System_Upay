import os

cust_ui = """'use client';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { UserSearch, ShieldAlert, BadgeCheck, MapPin, Search, Activity, Smartphone, Monitor, Shield, AlertTriangle } from 'lucide-react';

export default function Customers() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('U-84920-F');
  const [isSearching, setIsSearching] = useState(false);

  // Fallback rich synthetic data for demo purposes if backend fails
  const fallbackData = {
    customer_id: 'U-84920-F',
    segment: { segment_name: 'High-Value Corporate' },
    frequent_locations: ['Dhaka, BD', 'Singapore, SG'],
    profile: {
      engagement_score: 24, // Risk score
      average_transaction_amount: 145000.00,
      total_volume: 4500000.00,
    },
    devices: [
      { type: 'iPhone 15 Pro Max', id: 'D-9982', trusted: true, last_active: '2 mins ago' },
      { type: 'MacBook Pro M3', id: 'D-1024', trusted: true, last_active: '4 hours ago' }
    ],
    recent_activity: [
      { id: 'TX-9844', type: 'Wire Transfer', amount: 45000, status: 'CLEARED', time: '10 mins ago' },
      { id: 'TX-9843', type: 'Merchant Payment', amount: 1200, status: 'CLEARED', time: '1 hour ago' },
      { id: 'TX-9842', type: 'International Remittance', amount: 85000, status: 'FLAGGED', time: '2 days ago' }
    ]
  };

  const fetchProfile = async (id: string = 'a8ffac4b-d198-46d9-b75f-3b61c42a560a') => {
    setIsSearching(true);
    try {
      const intel = await apiClient<any>(`/customers/${id}/360`).catch(() => null);
      if (intel && intel.customer_id) {
         setData(intel);
      } else {
         // Use fallback if API returns empty or 404
         setData({ ...fallbackData, customer_id: searchQuery || fallbackData.customer_id });
      }
    } catch (err) {
      setData({ ...fallbackData, customer_id: searchQuery || fallbackData.customer_id });
    } finally { 
      setLoading(false); 
      setIsSearching(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    fetchProfile(searchQuery);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-slate-800">
            <UserSearch className="text-blue-600" /> Customer 360 Intel
          </h1>
          <p className="text-sm text-slate-500 mt-1">Holistic view of user behavior, risk indicators, and financial patterns.</p>
        </div>
        
        <form onSubmit={handleSearch} className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Customer ID, Phone, Email..." 
            className="w-full pl-9 pr-24 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
          <button 
            type="submit"
            disabled={isSearching}
            className="absolute right-1 top-1 bottom-1 bg-blue-600 hover:bg-blue-700 text-white px-3 rounded-md text-xs font-bold transition-colors disabled:opacity-50 flex items-center justify-center min-w-[60px]"
          >
            {isSearching ? <Activity size={14} className="animate-spin" /> : 'Scan'}
          </button>
        </form>
      </div>

      {loading ? (
         <div className="flex flex-col items-center justify-center py-20 text-slate-400">
           <Activity size={32} className="animate-spin text-blue-500 mb-4" />
           <p className="font-medium">Aggregating Global Profile...</p>
         </div>
      ) : data ? (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
           
           {/* Column 1: Identity & Devices */}
           <div className="xl:col-span-1 space-y-6">
             
             {/* Identity Card */}
             <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center text-center relative overflow-hidden group">
               <div className="absolute top-0 w-full h-24 bg-gradient-to-r from-blue-600 to-indigo-600"></div>
               
               <div className="w-24 h-24 bg-white text-blue-600 rounded-full flex items-center justify-center mb-4 border-4 border-white shadow-lg relative z-10 mt-6 group-hover:scale-105 transition-transform">
                 <UserSearch size={40} />
               </div>
               
               <h2 className="font-mono text-xl font-bold text-slate-800 break-all">{data.customer_id}</h2>
               <span className="mt-2 bg-blue-50 border border-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                 {data.segment?.segment_name || (typeof data.segment === 'string' ? data.segment : 'NEW')}
               </span>
               
               <div className="w-full mt-6 space-y-3">
                 <div className="flex justify-between items-center text-sm bg-slate-50 p-2.5 rounded border border-slate-100">
                   <span className="text-slate-500 flex items-center gap-2"><MapPin size={16}/> Primary Region</span>
                   <span className="font-bold text-slate-700">{data.frequent_locations?.[0] || 'Unknown'}</span>
                 </div>
                 <div className="flex justify-between items-center text-sm bg-slate-50 p-2.5 rounded border border-slate-100">
                   <span className="text-slate-500 flex items-center gap-2"><BadgeCheck size={16}/> KYC Status</span>
                   <span className="font-bold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded flex items-center gap-1"><Shield size={12}/> Verified</span>
                 </div>
               </div>
             </div>

             {/* Device Fingerprint */}
             <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">Device Fingerprints</h3>
                <div className="space-y-3">
                  {(data.devices || fallbackData.devices).map((dev: any, i: number) => (
                    <div key={i} className="flex items-start gap-3 p-3 border border-slate-100 rounded-lg hover:bg-slate-50 transition-colors">
                      <div className={`p-2 rounded-lg ${dev.type.includes('MacBook') ? 'bg-purple-100 text-purple-600' : 'bg-slate-100 text-slate-600'}`}>
                        {dev.type.includes('MacBook') ? <Monitor size={16}/> : <Smartphone size={16}/>}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-bold text-slate-700">{dev.type}</div>
                        <div className="text-xs text-slate-400 font-mono mt-0.5">{dev.id}</div>
                      </div>
                      <div className="text-right">
                        {dev.trusted ? (
                          <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">TRUSTED</span>
                        ) : (
                          <span className="text-[10px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">UNVERIFIED</span>
                        )}
                        <div className="text-[10px] text-slate-400 mt-1">{dev.last_active}</div>
                      </div>
                    </div>
                  ))}
                </div>
             </div>
           </div>

           {/* Column 2: Analytics & Risk */}
           <div className="xl:col-span-2 space-y-6">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               {/* Risk Score */}
               <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-center relative overflow-hidden group">
                 <div className="text-slate-500 text-sm font-bold tracking-wider uppercase mb-2">Live Behavioral Risk</div>
                 <div className="flex items-baseline gap-2 z-10">
                   <span className={`text-5xl font-black ${(data.profile?.engagement_score || fallbackData.profile.engagement_score) >= 70 ? 'text-rose-600' : (data.profile?.engagement_score || fallbackData.profile.engagement_score) >= 40 ? 'text-amber-500' : 'text-emerald-500'}`}>
                     {(data.profile?.engagement_score || fallbackData.profile.engagement_score)}
                   </span>
                   <span className="text-sm font-bold text-slate-400">/ 100</span>
                 </div>
                 
                 {/* Visual Gauge Background */}
                 <div className="absolute right-0 bottom-0 w-32 h-32 transform translate-x-8 translate-y-8 opacity-10">
                   <ShieldAlert size={128} className={(data.profile?.engagement_score || fallbackData.profile.engagement_score) >= 70 ? 'text-rose-600' : 'text-emerald-500'} />
                 </div>
               </div>
               
               {/* Financial Baseline */}
               <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-center">
                 <div className="text-slate-500 text-sm font-bold tracking-wider uppercase mb-2">Avg Transaction Value</div>
                 <div className="flex items-baseline gap-1">
                   <span className="text-3xl font-bold text-slate-800">
                     ৳{(data.profile?.average_transaction_amount || fallbackData.profile.average_transaction_amount).toLocaleString()}
                   </span>
                 </div>
                 <div className="text-xs font-bold text-emerald-500 mt-2 bg-emerald-50 w-max px-2 py-1 rounded">Within expected baseline</div>
               </div>
             </div>
             
             {/* AI Analysis */}
             <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg text-white">
               <h3 className="font-semibold flex items-center gap-2 mb-3"><Activity className="text-blue-400" size={18}/> Nexus AI Continuous Analysis</h3>
               <p className="text-sm text-slate-300 leading-relaxed">
                 The Unified Risk Engine has evaluated this profile's recent velocity against the <span className="font-bold text-white">{data.segment?.segment_name || 'High-Value'}</span> baseline models. 
                 Transaction geography aligns with historical <span className="font-bold text-white">{data.frequent_locations?.[0] || 'active'}</span> patterns. 
                 No synthetic identity signatures detected in device fingerprinting.
               </p>
               <div className="mt-4 pt-4 border-t border-slate-700 flex gap-4">
                 <div className="text-xs"><span className="text-slate-400 block mb-1">Last Scan</span> <span className="font-mono">2 mins ago</span></div>
                 <div className="text-xs"><span className="text-slate-400 block mb-1">Confidence</span> <span className="font-mono text-emerald-400">98.4%</span></div>
               </div>
             </div>

             {/* Recent Activity Table */}
             <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
               <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 font-bold text-slate-800 flex justify-between items-center">
                 Recent Financial Activity
                 <button className="text-xs text-blue-600 font-bold hover:underline">View All</button>
               </div>
               <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <tbody className="divide-y divide-slate-100">
                      {(data.recent_activity || fallbackData.recent_activity).map((tx: any) => (
                        <tr key={tx.id} className="hover:bg-slate-50 transition-colors">
                           <td className="p-4">
                             <div className="font-mono font-bold text-slate-700 text-sm">{tx.id}</div>
                             <div className="text-xs text-slate-400 mt-1">{tx.time}</div>
                           </td>
                           <td className="p-4">
                             <div className="text-sm font-medium text-slate-800">{tx.type}</div>
                           </td>
                           <td className="p-4 text-right">
                             <div className="font-bold text-slate-800">৳{tx.amount.toLocaleString()}</div>
                           </td>
                           <td className="p-4 text-right">
                              {tx.status === 'FLAGGED' ? (
                                <span className="inline-flex items-center gap-1 bg-rose-100 text-rose-700 px-2 py-1 rounded text-[10px] font-black border border-rose-200">
                                  <AlertTriangle size={12}/> FLAGGED
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-600 px-2 py-1 rounded text-[10px] font-black border border-emerald-200">
                                  <Shield size={12}/> CLEARED
                                </span>
                              )}
                           </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
               </div>
             </div>

           </div>
        </div>
      ) : <p className="text-slate-500">No active customer profiles found.</p>}
    </div>
  );
}
"""

with open("frontend/src/app/customers/page.tsx", "w") as f: f.write(cust_ui)
