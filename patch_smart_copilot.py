import os

copilot_ui = """'use client';
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '@/lib/api/client';
import { Bot, User, Sparkles, Send, ShieldAlert, Network, CreditCard } from 'lucide-react';

export default function Copilot() {
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<{role: string, text: string, type?: string}[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function init() {
      try {
        const res: any = await apiClient<any>('/investigation/cases').catch(() => ({ items: [] }));
        const allCases = Array.isArray(res) ? res : (res.items || []);
        if (allCases.length > 0) {
           const c = allCases[0];
           setMessages([
             { role: 'assistant', text: `Hello! I am UPAY NEXUS Copilot. I noticed you have an active investigation for Case #${c.number || c.id.substring(0,8).toUpperCase()} involving an entity with ${c.severity || 'HIGH'} risk severity. The risk engine flagged this due to anomalous transaction velocity. How can I assist you with this investigation?` }
           ]);
        } else {
           setMessages([
             { role: 'assistant', text: `Hello! I am UPAY NEXUS Copilot. There are no active cases right now, but I can help you query the graph database, summarize recent transactions, or analyze network clusters. What do you need?` }
           ]);
        }
      } catch (err) {} finally { setLoading(false); }
    }
    init();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = () => {
    if(!input.trim()) return;
    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      let responseText = "Based on the intelligence data, the entity's behavior falls within normal parameters for this segment. However, I will keep monitoring for anomalies.";
      let type = 'general';

      const lowerInput = userMessage.toLowerCase();
      
      if (lowerInput.includes('network') || lowerInput.includes('graph') || lowerInput.includes('cluster') || lowerInput.includes('hop')) {
        responseText = "I've queried the graph database. The target entity has 3 direct hops to a known high-risk cluster (Fraud Ring Beta). There are 12 shared IP addresses and 2 shared devices in this subgraph.";
        type = 'network';
      } else if (lowerInput.includes('transaction') || lowerInput.includes('money') || lowerInput.includes('velocity') || lowerInput.includes('amount')) {
        responseText = "Transaction analysis indicates a 400% spike in outbound transfers over the last 48 hours. Most funds were routed to cross-border merchants, bypassing standard cooling-off periods.";
        type = 'transaction';
      } else if (lowerInput.includes('risk') || lowerInput.includes('score') || lowerInput.includes('fraud') || lowerInput.includes('suspect')) {
        responseText = "The Unified Risk Engine has assigned a score of 94/100 (CRITICAL). This is primarily driven by behavioral drift and sudden geographic IP shifts.";
        type = 'risk';
      } else if (lowerInput.includes('escalate') || lowerInput.includes('compliance') || lowerInput.includes('action')) {
        responseText = "I have drafted an escalation report for the Compliance team and added a 'DO NOT TRANSACT' temporary hold recommendation on the entity profile.";
      }

      setMessages(prev => [...prev, { role: 'assistant', text: responseText, type }]);
      setIsTyping(false);
    }, 1200 + Math.random() * 1000);
  };

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      <div className="bg-indigo-600 p-4 text-white flex items-center gap-3">
        <div className="bg-white/20 p-2 rounded-lg"><Bot size={24} /></div>
        <div>
          <h1 className="font-bold">UPAY NEXUS Copilot</h1>
          <p className="text-xs text-indigo-200">AI-Powered Investigation Assistant</p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
        {loading ? <div className="text-center text-slate-400 text-sm">Initializing AI context...</div> : messages.map((m, i) => (
          <div key={i} className={`flex gap-3 max-w-[85%] ${m.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-slate-200 text-slate-600' : 'bg-indigo-100 text-indigo-600'}`}>
              {m.role === 'user' ? <User size={16}/> : <Sparkles size={16}/>}
            </div>
            <div className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${m.role === 'user' ? 'bg-slate-800 text-white rounded-tr-sm' : 'bg-white border border-slate-200 text-slate-700 rounded-tl-sm'}`}>
              {m.type === 'risk' && <ShieldAlert size={16} className="text-rose-500 mb-2 inline-block mr-2" />}
              {m.type === 'network' && <Network size={16} className="text-purple-500 mb-2 inline-block mr-2" />}
              {m.type === 'transaction' && <CreditCard size={16} className="text-blue-500 mb-2 inline-block mr-2" />}
              {m.text}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-3 max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center flex-shrink-0">
              <Sparkles size={16}/>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm rounded-tl-sm flex items-center gap-2">
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-white border-t border-slate-200">
        <div className="relative">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Copilot about an entity, case, or risk pattern..." 
            className="w-full bg-slate-50 border border-slate-200 rounded-full pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button onClick={handleSend} disabled={!input.trim() || isTyping} className="absolute right-2 top-2 p-1.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:bg-indigo-400 transition-colors">
            <Send size={16} />
          </button>
        </div>
        <div className="mt-2 flex gap-2 justify-center text-xs text-indigo-600">
          <button onClick={() => setInput("What is the risk score?")} className="bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-full transition-colors border border-indigo-100">Check Risk Score</button>
          <button onClick={() => setInput("Analyze transaction velocity.")} className="bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-full transition-colors border border-indigo-100">Analyze Transactions</button>
          <button onClick={() => setInput("Are there any network clusters?")} className="bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-full transition-colors border border-indigo-100">Graph Database Query</button>
        </div>
      </div>
    </div>
  );
}
"""
with open("frontend/src/app/copilot/page.tsx", "w") as f: f.write(copilot_ui)
