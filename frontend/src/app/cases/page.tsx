"use client"
import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function CasesQueue() {
  const [cases, setCases] = useState([])

  useEffect(() => {
    const fetchCases = async () => {
      const token = localStorage.getItem('token')
      const res = await fetch('http://localhost:8000/api/v1/investigation/cases', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) setCases(await res.json())
    }
    fetchCases()
  }, [])

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Investigation Cases</h1>
      <table className="w-full text-left bg-white shadow-sm border rounded">
        <thead>
          <tr className="bg-gray-100 border-b">
            <th className="p-3">Number</th>
            <th className="p-3">Status</th>
            <th className="p-3">Severity</th>
            <th className="p-3">Assignee</th>
            <th className="p-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((c: any) => (
            <tr key={c.id} className="border-b">
              <td className="p-3 font-mono">{c.number}</td>
              <td className="p-3 font-semibold">{c.status}</td>
              <td className="p-3">
                <span className={`px-2 py-1 rounded text-xs ${c.severity === 'CRITICAL' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'}`}>
                  {c.severity}
                </span>
              </td>
              <td className="p-3 text-sm text-gray-500">{c.assigned_investigator_id || 'Unassigned'}</td>
              <td className="p-3">
                <Link href={`/cases/${c.id}`} className="text-blue-500 hover:underline">View Case</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
