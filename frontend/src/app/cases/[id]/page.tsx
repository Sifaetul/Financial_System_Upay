"use client"
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import CopilotPanel from '@/components/CopilotPanel'

export default function CaseDetail() {
  const params = useParams()
  const caseId = params.id as string
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    const fetchCase = async () => {
      const token = localStorage.getItem('token')
      const res = await fetch(`http://localhost:8000/api/v1/investigation/cases/${caseId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) setData(await res.json())
    }
    if (caseId) fetchCase()
  }, [caseId])

  if (!data) return <div className="p-8">Loading Case...</div>

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">{data.number}: {data.title}</h1>
          <p className="text-gray-500 mt-2">{data.description}</p>
        </div>
        <div className="text-right">
          <span className="px-3 py-1 bg-gray-200 rounded font-semibold mr-2">{data.status}</span>
          <span className="px-3 py-1 bg-red-200 text-red-800 rounded font-semibold">{data.severity}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border rounded p-6">
          <h2 className="text-xl font-bold mb-4">Aggregated Evidence</h2>
          {data.evidence.length === 0 ? <p className="text-gray-500">No evidence attached.</p> : (
            <ul className="space-y-3">
              {data.evidence.map((e: any) => (
                <li key={e.id} className="p-3 bg-gray-50 border rounded text-sm">
                  <span className="font-semibold">{e.type}</span> - {e.relevance}
                  <p className="text-gray-600 mt-1">{e.explanation}</p>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white border rounded p-6">
          <h2 className="text-xl font-bold mb-4">Investigation Timeline</h2>
          {data.timeline.length === 0 ? <p className="text-gray-500">No actions recorded.</p> : (
            <ul className="space-y-3">
              {data.timeline.map((t: any) => (
                <li key={t.id} className="p-3 bg-blue-50 border border-blue-100 rounded text-sm">
                  <div className="flex justify-between">
                    <span className="font-semibold text-blue-800">{t.action}</span>
                    <span className="text-gray-500 text-xs">{new Date(t.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-gray-700 mt-1">{t.details}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="bg-white border rounded p-6">
        <h2 className="text-xl font-bold mb-4">Investigator Notes</h2>
        {data.notes.length === 0 ? <p className="text-gray-500">No notes yet.</p> : (
          <ul className="space-y-4">
            {data.notes.map((n: any) => (
              <li key={n.id} className="p-4 bg-yellow-50 border border-yellow-200 rounded">
                <p>{n.content}</p>
                <div className="text-xs text-gray-500 mt-2 text-right">Added {new Date(n.created_at).toLocaleString()}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
      <CopilotPanel caseId={caseId} />
    </div>
  )
}
