import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const DebugPanel: React.FC = () => {
  const [kpis, setKpis] = useState<any>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [technicians, setTechnicians] = useState<any>(null);
  const [tickets, setTickets] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDebugData = async () => {
      try {
        setLoading(true);
        console.log(' DebugPanel - Carregando dados...');

        const [kpisResult, statusResult, techniciansResult, ticketsResult] = await Promise.all([
          apiService.getMetrics(),
          apiService.getSystemStatus(),
          apiService.getTechnicianRanking(),
          apiService.getNewTickets(6)
        ]);

        console.log(' KPIs:', kpisResult);
        console.log(' System Status:', statusResult);
        console.log(' Technicians:', techniciansResult);
        console.log(' Tickets:', ticketsResult);

        setKpis(kpisResult);
        setSystemStatus(statusResult);
        setTechnicians(techniciansResult);
        setTickets(ticketsResult);
      } catch (err) {
        console.error(' Erro no DebugPanel:', err);
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    loadDebugData();
  }, []);

  if (loading) {
    return (
      <div style={{ background: 'yellow', padding: '10px', margin: '10px' }}>
         Carregando dados de debug...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: 'red', color: 'white', padding: '10px', margin: '10px' }}>
         Erro: {error}
      </div>
    );
  }

  return (
    <div style={{ background: 'lightblue', padding: '10px', margin: '10px', fontSize: '12px' }}>
      <h3> DEBUG PANEL</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div>
          <strong> KPIs:</strong>
          <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '100px' }}>
            {JSON.stringify(kpis, null, 2)}
          </pre>
        </div>
        <div>
          <strong> System Status:</strong>
          <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '100px' }}>
            {JSON.stringify(systemStatus, null, 2)}
          </pre>
        </div>
        <div>
          <strong> Technicians:</strong>
          <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '100px' }}>
            {JSON.stringify(technicians, null, 2)}
          </pre>
        </div>
        <div>
          <strong> Tickets:</strong>
          <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '100px' }}>
            {JSON.stringify(tickets, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default DebugPanel;
