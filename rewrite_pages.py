import os

TEMPLATE = """'use client';
import { useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function __COMPONENT_NAME__() {
  const [queryId, setQueryId] = useState('');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!queryId) return;
    setLoading(true);
    setError('');
    setData(null);
    try {
      const res = await apiClient<any>(`__API_PATH_TEMPLATE__`);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">__TITLE__</h1>
      <div className="flex space-x-4">
        <input 
          type="text" 
          value={queryId} 
          onChange={e => setQueryId(e.target.value)} 
          placeholder="Enter ID..." 
          className="border p-2 rounded"
        />
        <button onClick={handleSearch} className="bg-blue-600 text-white px-4 py-2 rounded">Search</button>
      </div>
      
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      
      {data && (
        <div className="bg-gray-50 p-4 rounded overflow-auto border">
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
      {!loading && !error && !data && <div className="text-gray-500">No data loaded. Search for an ID.</div>}
    </div>
  );
}
"""

pages = [
    ("financial", "Financial Overview", "/customers/${queryId}/financial"),
    ("merchants", "Merchant Intelligence", "/merchants/${queryId}/intelligence"),
    ("agents", "Agent Intelligence", "/agents/${queryId}/intelligence"),
    ("competition", "Competition Hub", "/evolution/${queryId}"),
]

for folder, title, path in pages:
    code = TEMPLATE.replace("__COMPONENT_NAME__", folder.capitalize())
    code = code.replace("__TITLE__", title)
    code = code.replace("__API_PATH_TEMPLATE__", path)
    os.makedirs(f"frontend/src/app/{folder}", exist_ok=True)
    with open(f"frontend/src/app/{folder}/page.tsx", "w") as f:
        f.write(code)

