'use client';
import { useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function Agents() {
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
      const res = await apiClient<any>(`/agents/${queryId}/intelligence`);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Agent Intelligence</h1>
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
