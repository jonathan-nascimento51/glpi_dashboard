/**
 * Componente para exibir alertas de monitoramento em tempo real
 * Mostra alertas críticos e permite reconhecimento
 */

import React, { useState } from 'react';
import { MonitoringAlert } from '../utils/dataMonitor';

interface MonitoringAlertsProps {
  alerts: MonitoringAlert[];
  onAcknowledge?: (alertId: string) => void;
  maxVisible?: number;
  onClose?: () => void;
}

const MonitoringAlerts: React.FC<MonitoringAlertsProps> = ({
  alerts,
  onAcknowledge,
  maxVisible = 5,
  onClose
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Filtrar alertas não reconhecidos e ordenar por severidade
  const unacknowledgedAlerts = alerts
    .filter(alert => !alert.acknowledged)
    .sort((a, b) => {
      const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
      return severityOrder[b.severity] - severityOrder[a.severity];
    });
  
  const visibleAlerts = isExpanded 
    ? unacknowledgedAlerts 
    : unacknowledgedAlerts.slice(0, maxVisible);
  
  const hiddenCount = unacknowledgedAlerts.length - maxVisible;
  
  if (unacknowledgedAlerts.length === 0) {
    return null;
  }

  // Se minimizado, mostrar apenas um indicador pequeno
  if (isMinimized) {
    return (
      <div className="fixed top-4 right-4 z-50">
        <button
          onClick={() => setIsMinimized(false)}
          className="bg-red-500 hover:bg-red-600 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg transition-all duration-200 animate-pulse"
          title={`${unacknowledgedAlerts.length} alertas pendentes`}
        >
          <span className="text-lg">🚨</span>
          <span className="absolute -top-1 -right-1 bg-white text-red-500 text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
            {unacknowledgedAlerts.length}
          </span>
        </button>
      </div>
    );
  }
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 border-red-500 text-red-800';
      case 'high': return 'bg-orange-100 border-orange-500 text-orange-800';
      case 'medium': return 'bg-yellow-100 border-yellow-500 text-yellow-800';
      case 'low': return 'bg-blue-100 border-blue-500 text-blue-800';
      default: return 'bg-gray-100 border-gray-500 text-gray-800';
    }
  };
  
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return 'ℹ️';
      default: return '📋';
    }
  };
  
  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'agora';
    if (minutes < 60) return `${minutes}m atrás`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h atrás`;
    
    const days = Math.floor(hours / 24);
    return `${days}d atrás`;
  };
  
  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <div className="bg-white rounded-lg shadow-lg border border-gray-200">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg">🔍</span>
            <h3 className="font-semibold text-gray-900">
              Alertas de Monitoramento
            </h3>
            <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
              {unacknowledgedAlerts.length}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {hiddenCount > 0 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                {isExpanded ? 'Menos' : `+${hiddenCount} mais`}
              </button>
            )}
            
            {/* Botão Minimizar */}
            <button
              onClick={() => setIsMinimized(true)}
              className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
              title="Minimizar"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            
            {/* Botão Fechar */}
            {onClose && (
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
                title="Fechar"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
        
        {/* Alerts List */}
        <div className="max-h-96 overflow-y-auto">
          {visibleAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 border-l-4 ${getSeverityColor(alert.severity)} border-b border-gray-100 last:border-b-0`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-lg">{getSeverityIcon(alert.severity)}</span>
                    <h4 className="font-medium text-sm">
                      {alert.ruleName}
                    </h4>
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(alert.timestamp)}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-2">
                    {alert.message}
                  </p>
                  
                  {alert.details && (
                    <details className="text-xs text-gray-600">
                      <summary className="cursor-pointer hover:text-gray-800">
                        Detalhes técnicos
                      </summary>
                      <pre className="mt-1 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                        {JSON.stringify(alert.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
                
                {onAcknowledge && (
                  <button
                    onClick={() => onAcknowledge(alert.id)}
                    className="ml-2 text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100"
                    title="Reconhecer alerta"
                  >
                    ✓
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {/* Footer */}
        <div className="px-4 py-2 bg-gray-50 rounded-b-lg">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>
              Sistema de monitoramento ativo
            </span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Online</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonitoringAlerts;