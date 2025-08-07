import React from 'react';
import { motion } from 'framer-motion';
import { 
  Trash2, 
  RefreshCw, 
  Database, 
  TrendingUp, 
  Clock, 
  BarChart3,
  Info
} from 'lucide-react';
import { useCache } from '../hooks/useCache';

interface CacheManagerProps {
  className?: string;
}

const CacheManager: React.FC<CacheManagerProps> = ({ className = '' }) => {
  const { 
    stats, 
    isLoading, 
    updateStats, 
    clearAll, 
    clearSpecificCache, 
    refreshCache, 
    getCacheInfo 
  } = useCache();

  const formatHitRate = (hitRate: number) => {
    return `${(hitRate * 100).toFixed(1)}%`;
  };

  const formatSize = (size: number) => {
    return `${size} ${size === 1 ? 'item' : 'itens'}`;
  };

  const getCacheTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      metrics: 'Métricas',
      systemStatus: 'Status do Sistema',
      technicianRanking: 'Ranking de Técnicos',
      newTickets: 'Novos Tickets'
    };
    return labels[type] || type;
  };

  const getCacheTypeIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      metrics: <BarChart3 className="w-4 h-4" />,
      systemStatus: <Database className="w-4 h-4" />,
      technicianRanking: <TrendingUp className="w-4 h-4" />,
      newTickets: <Clock className="w-4 h-4" />
    };
    return icons[type] || <Info className="w-4 h-4" />;
  };

  if (!stats) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <div className="flex items-center justify-center h-32">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
          <span className="ml-2 text-gray-600">Carregando estatísticas do cache...</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className={`bg-white rounded-lg shadow-sm border ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">Gerenciador de Cache</h3>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={updateStats}
              disabled={isLoading}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Atualizar</span>
            </button>
            <button
              onClick={clearAll}
              disabled={isLoading}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition-colors disabled:opacity-50"
            >
              <Trash2 className="w-4 h-4" />
              <span>Limpar Tudo</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(stats).map(([cacheType, cacheStats]) => (
            <motion.div
              key={cacheType}
              className="bg-gray-50 rounded-lg p-4 border"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getCacheTypeIcon(cacheType)}
                  <h4 className="font-medium text-gray-900 text-sm">
                    {getCacheTypeLabel(cacheType)}
                  </h4>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Itens:</span>
                  <span className="font-medium">{formatSize(cacheStats.size)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Taxa de Acerto:</span>
                  <span className={`font-medium ${
                    cacheStats.hitRate > 0.7 ? 'text-green-600' : 
                    cacheStats.hitRate > 0.4 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {formatHitRate(cacheStats.hitRate)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Requisições:</span>
                  <span className="font-medium">{cacheStats.totalRequests}</span>
                </div>
              </div>

              <div className="flex space-x-1 mt-3">
                <button
                  onClick={() => refreshCache(cacheType as any)}
                  className="flex-1 flex items-center justify-center space-x-1 px-2 py-1 text-xs bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Refresh</span>
                </button>
                <button
                  onClick={() => clearSpecificCache(cacheType as any)}
                  className="flex-1 flex items-center justify-center space-x-1 px-2 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Limpar</span>
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start space-x-2">
            <Info className="w-4 h-4 text-blue-500 mt-0.5" />
            <div className="text-sm text-blue-700">
              <p className="font-medium mb-1">Sobre o Cache</p>
              <p className="text-xs leading-relaxed">
                O sistema de cache armazena resultados da API por 5 minutos para melhorar a performance. 
                A taxa de acerto indica quantas requisições foram atendidas pelo cache sem precisar consultar a API.
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CacheManager;