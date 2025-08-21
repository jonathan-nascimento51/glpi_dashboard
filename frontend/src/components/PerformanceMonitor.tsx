import React, { useState } from 'react';
import { Activity, Clock, Zap, TrendingUp, TrendingDown, BarChart3, X } from 'lucide-react';
import { useFilterPerformance } from '../hooks/useFilterPerformance';

interface PerformanceMonitorProps {
  className?: string;
  compact?: boolean;
  showHistory?: boolean;
}

/**
 * Componente para monitorar performance de filtros em tempo real
 */
export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  className = '',
  compact = false,
  showHistory = true,
}) => {
  const { metrics, clearMetrics, isFilterInProgress } = useFilterPerformance();
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  
  // Calcular estatísticas adicionais
  const cacheHitRate = metrics.filterHistory.length > 0 
    ? (metrics.filterHistory.filter(entry => entry.cached).length / metrics.filterHistory.length) * 100
    : 0;
  
  const recentFilters = metrics.filterHistory.slice(-10);
  const averageRecentTime = recentFilters.length > 0
    ? recentFilters.reduce((sum, entry) => sum + entry.responseTime, 0) / recentFilters.length
    : 0;
  
  // Determinar status de performance
  const getPerformanceStatus = () => {
    if (metrics.averageResponseTime < 100) return { status: 'excellent', color: 'text-green-600', bg: 'bg-green-50' };
    if (metrics.averageResponseTime < 300) return { status: 'good', color: 'text-blue-600', bg: 'bg-blue-50' };
    if (metrics.averageResponseTime < 500) return { status: 'fair', color: 'text-yellow-600', bg: 'bg-yellow-50' };
    return { status: 'poor', color: 'text-red-600', bg: 'bg-red-50' };
  };
  
  const performanceStatus = getPerformanceStatus();
  
  if (compact) {
    return (
      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg ${performanceStatus.bg} ${className}`}>
        <Activity 
          className={`w-4 h-4 ${performanceStatus.color} ${isFilterInProgress ? 'animate-pulse' : ''}`} 
        />
        <span className={`text-sm font-medium ${performanceStatus.color}`}>
          {metrics.averageResponseTime.toFixed(0)}ms
        </span>
        {isFilterInProgress && (
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
        )}
      </div>
    );
  }
  
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Activity className={`w-5 h-5 text-blue-600 ${isFilterInProgress ? 'animate-pulse' : ''}`} />
          <h3 className="font-semibold text-gray-900">Performance Monitor</h3>
          {isFilterInProgress && (
            <div className="flex items-center gap-1 text-sm text-blue-600">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
              <span>Filtering...</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="Toggle details"
          >
            <BarChart3 className="w-4 h-4" />
          </button>
          <button
            onClick={clearMetrics}
            className="p-1 text-gray-400 hover:text-red-600 transition-colors"
            title="Clear metrics"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Métricas principais */}
      <div className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {/* Tempo médio */}
          <div className={`p-3 rounded-lg ${performanceStatus.bg}`}>
            <div className="flex items-center gap-2 mb-1">
              <Clock className={`w-4 h-4 ${performanceStatus.color}`} />
              <span className="text-sm font-medium text-gray-600">Avg Time</span>
            </div>
            <div className={`text-lg font-bold ${performanceStatus.color}`}>
              {metrics.averageResponseTime.toFixed(0)}ms
            </div>
          </div>
          
          {/* Total de filtros */}
          <div className="p-3 rounded-lg bg-gray-50">
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Total</span>
            </div>
            <div className="text-lg font-bold text-gray-900">
              {metrics.totalFilters}
            </div>
          </div>
          
          {/* Cache hit rate */}
          <div className="p-3 rounded-lg bg-green-50">
            <div className="flex items-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-gray-600">Cache Hit</span>
            </div>
            <div className="text-lg font-bold text-green-600">
              {cacheHitRate.toFixed(0)}%
            </div>
          </div>
          
          {/* Último filtro */}
          <div className="p-3 rounded-lg bg-blue-50">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-600">Last</span>
            </div>
            <div className="text-lg font-bold text-blue-600">
              {metrics.lastFilterTime.toFixed(0)}ms
            </div>
          </div>
        </div>
        
        {/* Detalhes expandidos */}
        {showDetails && (
          <div className="space-y-4">
            {/* Estatísticas detalhadas */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-red-50">
                <div className="flex items-center gap-2 mb-1">
                  <TrendingUp className="w-4 h-4 text-red-600" />
                  <span className="text-sm font-medium text-gray-600">Slowest</span>
                </div>
                <div className="text-lg font-bold text-red-600">
                  {metrics.slowestFilter.toFixed(0)}ms
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-green-50">
                <div className="flex items-center gap-2 mb-1">
                  <TrendingDown className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-gray-600">Fastest</span>
                </div>
                <div className="text-lg font-bold text-green-600">
                  {metrics.fastestFilter.toFixed(0)}ms
                </div>
              </div>
            </div>
            
            {/* Histórico recente */}
            {showHistory && recentFilters.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Recent Filters</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {recentFilters.reverse().map((entry, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-700">
                          {entry.filterType}
                        </span>
                        {entry.cached && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                            Cached
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`font-medium ${
                          entry.responseTime < 100 ? 'text-green-600' :
                          entry.responseTime < 300 ? 'text-blue-600' :
                          entry.responseTime < 500 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {entry.responseTime.toFixed(0)}ms
                        </span>
                        <span className="text-gray-500 text-xs">
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Recomendações */}
            <div className="p-3 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Performance Tips</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                {metrics.averageResponseTime > 500 && (
                  <li>• Consider increasing debounce delay for better performance</li>
                )}
                {cacheHitRate < 30 && metrics.totalFilters > 10 && (
                  <li>• Low cache hit rate - consider optimizing filter caching</li>
                )}
                {metrics.slowestFilter > 1000 && (
                  <li>• Some filters are very slow - investigate backend performance</li>
                )}
                {metrics.totalFilters > 100 && (
                  <li>• High filter usage - monitor for potential performance issues</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceMonitor;