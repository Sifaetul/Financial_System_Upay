"use client"
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

export default function Agent360() {
  const params = useParams()
  const agentId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchAgent = async () => {
      try {
        const token = localStorage.getItem('token')
        const res = await fetch(`http://localhost:8000/api/v1/agents/${agentId}/intelligence`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Failed to fetch agent data')
        setData(await res.json())
      } catch (err: any) {
        setError(err.message)
      }
      setLoading(false)
    }
    if (agentId) fetchAgent()
  }, [agentId])

  if (loading) return <div className="p-8">Loading Agent Intelligence...</div>
  if (error) return <div className="p-8 text-red-500">{error}</div>
  if (!data) return <div className="p-8">Agent not found</div>

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <h1 className="text-3xl font-bold">Agent Intelligence</h1>
      
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Agent Overview</h2>
          <div className="text-2xl font-bold">{data.identifier}</div>
          <div className="text-sm mt-4 text-gray-500">ID: {data.agent_id}</div>
        </div>

        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Transaction Volume</h2>
          <div className="text-2xl font-bold text-blue-600">${data.transaction_volume.toFixed(2)}</div>
          <div className="text-sm mt-4 text-gray-500">Count: {data.transaction_count}</div>
        </div>

        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Customer Reach</h2>
          <div className="text-2xl font-bold text-purple-600">{data.unique_customer_count}</div>
          <div className="text-sm mt-4 text-gray-500">Unique customers interacted</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-xl font-bold mb-4">Performance Metrics</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">Average Transaction</div>
              <div className="text-xl font-semibold">${data.average_transaction_amount.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Reversals</div>
              <div className="text-xl font-semibold text-orange-500">{data.reversal_count}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Successful Txs</div>
              <div className="text-xl font-semibold text-green-600">{data.successful_transaction_count}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Failed Txs</div>
              <div className="text-xl font-semibold text-red-600">{data.failed_transaction_count}</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 border rounded p-6 shadow-sm overflow-y-auto max-h-96">
          <h2 className="text-xl font-bold mb-4">Agent Signals</h2>
          {data.signals.length === 0 ? (
            <div className="text-gray-500">No active intelligence signals.</div>
          ) : (
            <div className="space-y-4">
              {data.signals.map((sig: any, idx: number) => (
                <div key={idx} className="bg-white p-4 border rounded shadow-sm border-red-200">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-red-600">{sig.signal_type}</span>
                    <span className="text-sm bg-gray-200 px-2 py-1 rounded font-mono">Val: {sig.raw_value.toFixed(2)}</span>
                  </div>
                  <p className="text-sm text-gray-700">{sig.explanation}</p>
                  <p className="text-xs text-gray-500 mt-2">{sig.evidence}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
