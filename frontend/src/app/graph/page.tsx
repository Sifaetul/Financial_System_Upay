"use client"
import { useState } from 'react'
import dynamic from 'next/dynamic'

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false })

export default function GraphExplorer() {
  const [nodeType, setNodeType] = useState('ACCOUNT')
  const [nodeId, setNodeId] = useState('')
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [signals, setSignals] = useState([])

  const fetchGraph = async () => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`http://localhost:8000/api/v1/graph/neighborhood/${nodeType}/${nodeId}?depth=2`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to fetch graph data')
      const data = await res.json()
      
      const gData = {
        nodes: data.nodes.map((n: any) => ({ id: n.id, name: n.entity_id, val: 1, type: n.type })),
        links: data.edges.map((e: any) => ({ source: e.source, target: e.target, name: e.type }))
      }
      setGraphData(gData as any)

      if (nodeType === 'ACCOUNT') {
        const sigRes = await fetch(`http://localhost:8000/api/v1/graph/signals/${nodeType}/${nodeId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (sigRes.ok) {
          const sigData = await sigRes.json()
          setSignals(sigData.signals)
        }
      }
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col h-screen">
      <h1 className="text-3xl font-bold mb-8">Graph Intelligence Explorer</h1>
      
      <div className="flex gap-4 mb-8">
        <select value={nodeType} onChange={e => setNodeType(e.target.value)} className="border p-2 rounded">
          <option value="ACCOUNT">Account</option>
          <option value="DEVICE">Device</option>
          <option value="TRANSACTION">Transaction</option>
        </select>
        <input 
          type="text" 
          placeholder="Entity ID" 
          value={nodeId} 
          onChange={e => setNodeId(e.target.value)}
          className="border p-2 rounded flex-1"
        />
        <button onClick={fetchGraph} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded">
          {loading ? 'Loading...' : 'Explore Graph'}
        </button>
      </div>

      {error && <div className="text-red-500 mb-4">{error}</div>}

      <div className="flex flex-1 gap-8">
        <div className="flex-1 border rounded bg-white relative">
            {graphData.nodes.length > 0 ? (
                <ForceGraph2D
                graphData={graphData}
                nodeLabel="name"
                nodeColor={(node: any) => node.type === 'ACCOUNT' ? '#3b82f6' : node.type === 'DEVICE' ? '#eab308' : '#ef4444'}
                linkColor={() => '#cbd5e1'}
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}
                width={800}
                height={600}
                />
            ) : (
                <div className="absolute inset-0 flex items-center justify-center text-gray-400">No graph data</div>
            )}
        </div>
        
        <div className="w-1/3 bg-gray-50 p-4 border rounded overflow-y-auto">
          <h2 className="text-xl font-bold mb-4">Network Evidence</h2>
          {signals.length === 0 ? (
            <p className="text-gray-500">No active network signals detected.</p>
          ) : (
            <div className="space-y-4">
              {signals.map((sig: any, idx) => (
                <div key={idx} className="bg-white p-4 border rounded shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-red-600">{sig.signal_type}</span>
                    <span className="text-sm bg-gray-200 px-2 py-1 rounded">Val: {sig.normalized_value}</span>
                  </div>
                  <p className="text-sm text-gray-700">{sig.explanation}</p>
                  <p className="text-xs text-gray-500 mt-2 font-mono">{sig.evidence}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
