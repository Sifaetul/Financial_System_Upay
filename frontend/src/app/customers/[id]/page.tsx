"use client"
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

export default function Customer360() {
  const params = useParams()
  const customerId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchCustomer = async () => {
      try {
        const token = localStorage.getItem('token')
        const res = await fetch(`http://localhost:8000/api/v1/customers/${customerId}/360`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Failed to fetch customer data')
        setData(await res.json())
      } catch (err: any) {
        setError(err.message)
      }
      setLoading(false)
    }
    if (customerId) fetchCustomer()
  }, [customerId])

  if (loading) return <div className="p-8">Loading Customer 360...</div>
  if (error) return <div className="p-8 text-red-500">{error}</div>
  if (!data) return <div className="p-8">Customer not found</div>

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <h1 className="text-3xl font-bold">Customer 360 Intelligence</h1>
      
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Customer Status</h2>
          <div className="text-2xl font-bold uppercase">{data.status}</div>
          <div className="text-sm mt-4 text-gray-500 truncate" title={data.customer_id}>ID: {data.customer_id}</div>
        </div>

        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Lifecycle State</h2>
          <div className="text-2xl font-bold text-blue-600">{data.profile.lifecycle_state}</div>
          <div className="text-sm mt-4 text-gray-500">Active Days: {data.profile.active_days}</div>
        </div>

        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Current Segment</h2>
          <div className="text-2xl font-bold text-purple-600">{data.segment.segment_name}</div>
          <div className="text-sm mt-4 text-gray-500 truncate" title={data.segment.evidence}>
            Evidence: {data.segment.evidence}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-xl font-bold mb-4">Activity Summary</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">Transaction Count</div>
              <div className="text-xl font-semibold">{data.profile.transaction_count}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Total Volume</div>
              <div className="text-xl font-semibold">${data.profile.transaction_volume.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Average Amount</div>
              <div className="text-xl font-semibold">${data.profile.average_transaction_amount.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Behavioral Stability</div>
              <div className={`text-xl font-semibold ${data.profile.behavioral_stability === 'HIGHLY_CHANGING' ? 'text-red-500' : 'text-green-500'}`}>
                {data.profile.behavioral_stability}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 border rounded p-6 shadow-sm overflow-y-auto max-h-96">
          <h2 className="text-xl font-bold mb-4">Customer Intelligence Signals</h2>
          {data.signals.length === 0 ? (
            <div className="text-gray-500">No active intelligence signals.</div>
          ) : (
            <div className="space-y-4">
              {data.signals.map((sig: any, idx: number) => (
                <div key={idx} className="bg-white p-4 border rounded shadow-sm border-red-200">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-red-600">{sig.signal_type}</span>
                    <span className="text-sm bg-gray-200 px-2 py-1 rounded font-mono">Val: {sig.normalized_value}</span>
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
