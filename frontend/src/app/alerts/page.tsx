'use client';
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '@/lib/api/client';
import { AlertCard } from '@/components/AlertCard';

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsStatus, setWsStatus] = useState('CONNECTING');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initial fetch
    async function fetchAlerts() {
      try {
        const res = await apiClient<any[]>('/investigation/alerts');
        setAlerts(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchAlerts();

    // WebSocket connection
    const token = localStorage.getItem('auth_token');
    let reconnectTimeout: NodeJS.Timeout;
    
    function connectWs() {
      if (!token) {
        setWsStatus('OFFLINE');
        return;
      }
      setWsStatus('CONNECTING');
      const ws = new WebSocket(`ws://${window.location.host}/api/v1/ws/alerts?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => setWsStatus('LIVE');
      ws.onclose = () => {
        setWsStatus('RECONNECTING');
        reconnectTimeout = setTimeout(connectWs, 5000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (event) => {
        try {
          const newAlert = JSON.parse(event.data);
          setAlerts(prev => [newAlert, ...prev]);
        } catch (e) {}
      };
    }

    connectWs();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Ops Alerts</h1>
        <div className={`px-3 py-1 rounded text-sm font-bold ${wsStatus === 'LIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          WebSocket: {wsStatus}
        </div>
      </div>
      
      {loading && <div>Loading alerts...</div>}
      
      <div className="space-y-4">
        {alerts.map((a, i) => (
          <AlertCard 
            key={a.id || i} 
            title={a.type || 'Alert'} 
            message={`Entity: ${a.entity_id} | Status: ${a.status}`} 
            severity={a.severity?.toLowerCase() || 'warning'} 
          />
        ))}
        {!loading && alerts.length === 0 && <div className="text-gray-500">No alerts found</div>}
      </div>
    </div>
  );
}
