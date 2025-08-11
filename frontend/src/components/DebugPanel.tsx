import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const DebugPanel: React.FC = () => {
  const [kpis, setKpis] = useState<any>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [technicians, setTechnicians] = useState<any>(null);
  const [tickets, setTickets] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isVisible, setIsVisible] = useState(false);

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

  return (
    <>
      {/* Botão Toggle */}
      <button
        onClick={() => setIsVisible(!isVisible)}
        style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          background: isVisible ? '#ff6b6b' : '#4ecdc4',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          fontSize: '12px',
          fontWeight: 'bold',
          cursor: 'pointer',
          zIndex: 10000,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
          transition: 'all 0.3s ease'
        }}
        title={isVisible ? 'Ocultar Debug Panel' : 'Mostrar Debug Panel'}
      >
        {isVisible ? '✕' : '🐛'}
      </button>

      {/* Debug Panel */}
      {isVisible && (
        <div style={{ 
          position: 'fixed', 
          top: '60px', 
          right: '10px', 
          background: 'rgba(173, 216, 230, 0.95)', 
          padding: '10px', 
          fontSize: '12px',
          zIndex: 9999,
          maxWidth: '400px',
          maxHeight: '70vh',
          overflow: 'auto',
          border: '1px solid #ccc',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          animation: 'fadeIn 0.3s ease-in-out'
        }}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '14px' }}> DEBUG PANEL</h3>
          
          {loading && (
            <div style={{ background: 'yellow', padding: '5px', borderRadius: '4px', marginBottom: '10px' }}>
               Carregando dados de debug...
            </div>
          )}
          
          {error && (
            <div style={{ background: 'red', color: 'white', padding: '5px', borderRadius: '4px', marginBottom: '10px' }}>
               Erro: {error}
            </div>
          )}
          
          {!loading && !error && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
              <div>
                <strong> KPIs:</strong>
                <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '80px', margin: '2px 0', borderRadius: '4px' }}>
                  {JSON.stringify(kpis, null, 2)}
                </pre>
              </div>
              <div>
                <strong> System Status:</strong>
                <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '80px', margin: '2px 0', borderRadius: '4px' }}>
                  {JSON.stringify(systemStatus, null, 2)}
                </pre>
              </div>
              <div>
                <strong> Technicians:</strong>
                <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '80px', margin: '2px 0', borderRadius: '4px' }}>
                  {JSON.stringify(technicians, null, 2)}
                </pre>
              </div>
              <div>
                <strong> Tickets:</strong>
                <pre style={{ background: 'white', padding: '5px', fontSize: '10px', overflow: 'auto', maxHeight: '80px', margin: '2px 0', borderRadius: '4px' }}>
                  {JSON.stringify(tickets, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
      
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  );
};

export default DebugPanel;
