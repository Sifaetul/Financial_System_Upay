"use client"
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

export default function Financial360() {
  const params = useParams()
  const customerId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchFinancial = async () => {
      try {
        const token = localStorage.getItem('token')
        const res = await fetch(`http://localhost:8000/api/v1/customers/${customerId}/financial`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Failed to fetch financial data')
        setData(await res.json())
      } catch (err: any) {
        setError(err.message)
      }
      setLoading(false)
    }
    if (customerId) fetchFinancial()
  }, [customerId])

  if (loading) return <div className="p-8">Loading Financial Intelligence...</div>
  if (error) return <div className="p-8 text-red-500">{error}</div>
  if (!data) return <div className="p-8">Customer not found</div>

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <h1 className="text-3xl font-bold">Financial Intelligence & Cash-Flow</h1>
      
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Financial Health</h2>
          <div className={`text-2xl font-bold uppercase ${data.financial_health_score === 'PRESSURED' ? 'text-red-600' : 'text-green-600'}`}>
            {data.financial_health_score}
          </div>
          <div className="text-sm mt-4 text-gray-500">Sufficiency: {data.data_sufficiency}</div>
        </div>

        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Net Cash Flow</h2>
          <div className={`text-2xl font-bold ${data.net_cash_flow < 0 ? 'text-red-600' : 'text-green-600'}`}>
            ${data.net_cash_flow.toFixed(2)}
          </div>
          <div className="text-sm mt-4 text-gray-500">Historical Net Margin</div>
        </div>

        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-500 mb-2">Forecast (30-day)</h2>
          {data.forecast_data && data.forecast_data.status === 'SUFFICIENT_DATA' ? (
            <>
              <div className="text-2xl font-bold text-blue-600">
                ${data.forecast_data.predicted_net_cash_flow.toFixed(2)}
              </div>
              <div className="text-sm mt-4 text-gray-500">
                Confidence: {(data.forecast_data.confidence * 100).toFixed(0)}% (MAE: {data.forecast_data.validation_mae.toFixed(1)})
              </div>
            </>
          ) : (
             <div className="text-lg font-bold text-gray-400">INSUFFICIENT DATA</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border rounded p-6 shadow-sm">
          <h2 className="text-xl font-bold mb-4">Cash-Flow Aggregates</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">Total Inflow</div>
              <div className="text-xl font-semibold text-green-600">${data.total_inflow.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Total Outflow</div>
              <div className="text-xl font-semibold text-red-600">${data.total_outflow.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Average Daily Inflow</div>
              <div className="text-xl font-semibold text-gray-800">${data.average_daily_inflow.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Average Daily Outflow</div>
              <div className="text-xl font-semibold text-gray-800">${data.average_daily_outflow.toFixed(2)}</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 border rounded p-6 shadow-sm overflow-y-auto max-h-96">
          <h2 className="text-xl font-bold mb-4">Financial Intelligence Signals</h2>
          {data.signals.length === 0 ? (
            <div className="text-gray-500">No active financial risk signals.</div>
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
