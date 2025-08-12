import React from 'react';
import { motion } from 'framer-motion';
import { LevelCard } from './DashboardCard';
import { StateWrapper } from '../../../shared/components/StateComponents';
import type { MetricsGridProps, LevelMetrics } from '../types/dashboardTypes';
import { ComponentState } from '../../../shared/types/states';

interface ExtendedMetricsGridProps extends MetricsGridProps {
  state?: ComponentState<LevelMetrics>;
  onRetry?: () => void;
  className?: string;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  }
};

export const MetricsGrid: React.FC<ExtendedMetricsGridProps> = ({
  metrics,
  state,
  onRetry,
  onLevelClick,
  className = '',
  isLoading = false,
  error
}) => {
  // Determinar estado baseado nas props ou estado explícito
  const gridState = state || {
    type: isLoading ? 'loading' : error ? 'error' : 'success',
    data: metrics,
    error: error ? new Error(error) : undefined
  } as ComponentState<LevelMetrics>;

  // Verificar se está vazio
  const isEmpty = !isLoading && !error && (!metrics || 
    Object.values(metrics).every(level => level.total === 0));

  // Calcular estatísticas gerais
  const totalTickets = React.useMemo(() => {
    if (!metrics) return 0;
    return Object.values(metrics).reduce((sum, level) => sum + level.total, 0);
  }, [metrics]);

  const totalResolved = React.useMemo(() => {
    if (!metrics) return 0;
    return Object.values(metrics).reduce((sum, level) => sum + level.fechados, 0);
  }, [metrics]);

  const resolutionRate = React.useMemo(() => {
    if (totalTickets === 0) return 0;
    return Math.round((totalResolved / totalTickets) * 100);
  }, [totalTickets, totalResolved]);

  const avgResolutionTime = React.useMemo(() => {
    if (!metrics) return 0;
    const levels = Object.values(metrics);
    const totalTime = levels.reduce((sum, level) => sum + level.tempo_medio_resolucao, 0);
    return Math.round(totalTime / levels.length);
  }, [metrics]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Estatísticas gerais */}
      <StateWrapper
        isLoading={gridState.type === 'loading'}
        isError={gridState.type === 'error'}
        isEmpty={isEmpty}
        error={gridState.error}
        onRetry={onRetry}
        loadingProps={{ variant: 'skeleton' }}
        errorProps={{ 
          variant: 'default',
          message: 'Erro ao carregar métricas do dashboard'
        }}
        emptyProps={{ 
          variant: 'default',
          message: 'Nenhuma métrica disponível',
          description: 'Não há dados de tickets para exibir no momento.'
        }}
      >
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="space-y-6"
        >
          {/* Resumo geral */}
          <motion.div 
            variants={itemVariants}
            className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200"
          >
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Resumo Geral</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{totalTickets.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Total de Tickets</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{totalResolved.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Resolvidos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{resolutionRate}%</div>
                <div className="text-sm text-gray-600">Taxa de Resolução</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{avgResolutionTime}h</div>
                <div className="text-sm text-gray-600">Tempo Médio</div>
              </div>
            </div>
          </motion.div>

          {/* Grid de níveis */}
          <motion.div variants={itemVariants}>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Métricas por Nível</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(metrics).map(([level, levelMetrics]) => (
                <motion.div key={level} variants={itemVariants}>
                  <LevelCard
                    level={level}
                    metrics={levelMetrics}
                    onClick={() => onLevelClick?.(level)}
                    state={{
                      type: 'success',
                      data: levelMetrics
                    }}
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Detalhes por status */}
          <motion.div variants={itemVariants}>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Distribuição por Status</h2>
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nível</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Total</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Abertos</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Pendentes</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Fechados</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Tempo Médio</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {Object.entries(metrics).map(([level, levelMetrics]) => {
                      const completionRate = levelMetrics.total > 0 
                        ? Math.round((levelMetrics.fechados / levelMetrics.total) * 100)
                        : 0;
                      
                      return (
                        <tr 
                          key={level} 
                          className="hover:bg-gray-50 cursor-pointer transition-colors"
                          onClick={() => onLevelClick?.(level)}
                        >
                          <td className="px-4 py-3">
                            <div className="flex items-center">
                              <span className="font-medium text-gray-900">{level}</span>
                              <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                                completionRate >= 80 ? 'bg-green-100 text-green-800' :
                                completionRate >= 60 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {completionRate}%
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-center font-medium">
                            {levelMetrics.total.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="text-blue-600 font-medium">
                              {levelMetrics.abertos.toLocaleString()}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="text-orange-600 font-medium">
                              {levelMetrics.pendentes.toLocaleString()}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="text-green-600 font-medium">
                              {levelMetrics.fechados.toLocaleString()}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="text-gray-700">
                              {levelMetrics.tempo_medio_resolucao}h
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </StateWrapper>
    </div>
  );
};