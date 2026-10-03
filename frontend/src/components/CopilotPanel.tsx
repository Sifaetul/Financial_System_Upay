"use client"
import { useState, useRef, useEffect } from 'react'

export default function CopilotPanel({ caseId }: { caseId: string }) {
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  
  const endRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendQuery = async () => {
    if (!input.trim()) return
    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`http://localhost:8000/api/v1/copilot/cases/${caseId}/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ question: userMsg.content })
      })
      
      if (res.ok) {
        const data = await res.json()
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer,
          evidence: data.evidence,
          confidence: data.confidence,
          keyFindings: data.key_findings,
          uncertainties: data.uncertainties
        }])
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Could not retrieve response.' }])
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Network Error.' }])
    }
    setLoading(false)
  }

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 z-50 flex items-center gap-2"
      >
        <span>💬 AI Copilot</span>
      </button>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-white border border-gray-300 rounded-lg shadow-2xl flex flex-col z-50" style={{ height: '600px' }}>
      <div className="bg-blue-600 text-white p-3 rounded-t-lg flex justify-between items-center">
        <h3 className="font-bold flex items-center gap-2">
          ⚡ AI Investigation Copilot
        </h3>
        <button onClick={() => setIsOpen(false)} className="hover:text-gray-200 font-bold">✕</button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="text-gray-500 text-center mt-10 text-sm">
            Ask the AI Copilot about this case. It uses RAG to fetch context and evidence securely.
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-3 rounded-lg max-w-[85%] ${m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {m.content}
            </div>
            
            {m.evidence && m.evidence.length > 0 && (
              <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded w-full border">
                <strong>Citations:</strong>
                <ul className="list-disc list-inside mt-1">
                  {m.evidence.map((e: any, idx: number) => (
                    <li key={idx}>[{e.source_type}] {e.source_id} - {Math.round(e.relevance * 100)}%</li>
                  ))}
                </ul>
              </div>
            )}
            
            {m.role === 'assistant' && m.confidence && (
              <div className={`text-[10px] mt-1 font-semibold ${m.confidence === 'HIGH' ? 'text-green-600' : 'text-yellow-600'}`}>
                Confidence: {m.confidence}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="text-gray-500 text-sm italic">AI Copilot is thinking...</div>
        )}
        <div ref={endRef} />
      </div>
      
      <div className="p-3 border-t bg-gray-50 rounded-b-lg">
        <div className="flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendQuery()}
            placeholder="Ask about evidence, transactions..." 
            className="flex-1 p-2 border rounded focus:outline-blue-500 text-sm"
          />
          <button 
            onClick={sendQuery}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 hover:bg-blue-700"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
