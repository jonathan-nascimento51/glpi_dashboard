import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { performHealthCheck, apiMonitor, HealthCheckResult, ValidationResult } from '../utils/apiValidator';
import { debugLog, errorLog } from '../config/apiConfig';

interface ApiHealthMonitorProps {
  showDetails?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const ApiHealthMonitor: React.FC<ApiHealthMonitorProps> = ({
  showDetails = false,
  autoRefresh = true,
  refreshInterval = 30000
}) => {
  const [healthStatus, setHealthStatus] = useState<HealthCheckResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const checkHealth = async () => {
    setIsLoading(true);
    try {
      debugLog('ApiHealthMonitor - Executando health check...');
      const result = await performHealthCheck();
      setHealthStatus(result);
      setLastUpdate(new Date());
    } catch (error) {
      errorLog('ApiHealthMonitor - Erro durante health check:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Health check inicial
    checkHealth();

    // Configurar auto-refresh
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(checkHealth, refreshInterval);
    }

    // Listener para falhas de health check
    const handleHealthCheckFailed = (event: CustomEvent<HealthCheckResult>) => {
      setHealthStatus(event.detail);
      setLastUpdate(new Date());
    };

    window.addEventListener('api-health-check-failed', handleHealthCheckFailed as EventListener);

    return () => {
      if (interval) clearInterval(interval);
      window.removeEventListener('api-health-check-failed', handleHealthCheckFailed as EventListener);
    };
  }, [autoRefresh, refreshInterval]);

  const getStatusIcon = () => {
    if (isLoading) {
      return <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />;
    }
    
    if (!healthStatus) {
      return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
    
    return healthStatus.overall 
      ? <CheckCircle className="w-4 h-4 text-green-500" />
      : <XCircle className="w-4 h-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (isLoading) return 'Verificando...';
    if (!healthStatus) return 'Status desconhecido';
    return healthStatus.overall ? 'API Saudável' : 'Problemas na API';
  };

  const getStatusColor = () => {
    if (isLoading) return 'text-blue-600';
    if (!healthStatus) return 'text-yellow-600';
    return healthStatus.overall ? 'text-green-600' : 'text-red-600';
  };

  const formatResponseTime = (time?: number) => {
    if (!time) return 'N/A';
    return `${Math.round(time)}ms`;
  };

  if (!showDetails) {
    // Versão compacta - apenas ícone e status
    return (
      <div 
        className="flex items-center space-x-2 cursor-pointer hover:opacity-80 transition-opacity"
        onClick={checkHealth}
        title={`${getStatusText()} - Clique para atualizar`}
      >
        {getStatusIcon()}
        <span className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
        {lastUpdate && (
          <span className="text-xs text-gray-500">
            {lastUpdate.toLocaleTimeString()}
          </span>
        )}
      </div>
    );
  }

  // Versão detalhada
  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <h3 className={`font-semibold ${getStatusColor()}`}>
            {getStatusText()}
          </h3>
        </div>
        <button
          onClick={checkHealth}
          disabled={isLoading}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Verificando...' : 'Atualizar'}
        </button>
      </div>

      {lastUpdate && (
        <p className="text-sm text-gray-600 mb-4">
          Última verificação: {lastUpdate.toLocaleString()}
        </p>
      )}

      {healthStatus && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-700 mb-2">Status dos Endpoints:</h4>
          {healthStatus.results.map((result: ValidationResult, index: number) => (
            <div 
              key={index} 
              className={`flex items-center justify-between p-2 rounded ${
                result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
              }`}
            >
              <div className="flex items-center space-x-2">
                {result.success 
                  ? <CheckCircle className="w-4 h-4 text-green-500" />
                  : <XCircle className="w-4 h-4 text-red-500" />
                }
                <span className="text-sm font-medium">
                  {result.endpoint}
                </span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <span className={result.success ? 'text-green-600' : 'text-red-600'}>
                  {result.success ? 'OK' : 'ERRO'}
                </span>
                <span className="text-gray-500">
                  {formatResponseTime(result.responseTime)}
                </span>
              </div>
            </div>
          ))}
          
          {healthStatus.results.some(r => !r.success) && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <h5 className="font-medium text-yellow-800 mb-2">Problemas Detectados:</h5>
              <ul className="text-sm text-yellow-700 space-y-1">
                {healthStatus.results
                  .filter((r: ValidationResult) => !r.success)
                  .map((result: ValidationResult, index: number) => (
                    <li key={index}>
                      <strong>{result.endpoint}:</strong> {result.error}
                    </li>
                  ))
                }
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Indicador de auto-refresh */}
      {autoRefresh && (
        <div className="mt-4 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500 flex items-center space-x-1">
            <RefreshCw className="w-3 h-3" />
            <span>Atualização automática a cada {refreshInterval / 1000}s</span>
          </p>
        </div>
      )}
    </div>
  );
};

export default ApiHealthMonitor;
