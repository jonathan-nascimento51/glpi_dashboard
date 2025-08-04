import React from 'react';
import { MetricCard } from './MetricCard';
import { MetricsData, TicketStatus } from '../types';

interface MetricsGridProps {
  metrics: MetricsData;
  onFilterByStatus: (status: TicketStatus) => void;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({
  metrics,
  onFilterByStatus,
}) => {
  // Verificação de segurança para evitar erros
  if (!metrics) {
    return <div>Carregando métricas...</div>;
  }

  // Usa o total calculado pelo backend ou calcula se não estiver disponível
  const total = metrics.total || (metrics.novos || 0) + (metrics.pendentes || 0) + (metrics.progresso || 0) + (metrics.resolvidos || 0);

  const metricCards: Array<{
    type: TicketStatus;
    value: number;
    change: string;
  }> = [
    {
      type: 'new',
      value: metrics.novos || 0,
      change: metrics.tendencias?.novos || '0',
    },
    {
      type: 'progress',
      value: metrics.progresso || 0,
      change: metrics.tendencias?.progresso || '0',
    },
    {
      type: 'pending',
      value: metrics.pendentes || 0,
      change: metrics.tendencias?.pendentes || '0',
    },
    {
      type: 'resolved',
      value: metrics.resolvidos || 0,
      change: metrics.tendencias?.resolvidos || '0',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((metric) => (
          <MetricCard
            key={metric.type}
            type={metric.type}
            value={metric.value}
            change={metric.change}
            onClick={() => onFilterByStatus(metric.type)}
          />
        ))}
      </div>

      {/* Total Summary Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Total de Chamados
            </h3>
            <div className="flex items-baseline space-x-2">
              <span className="text-4xl font-bold text-gray-900 dark:text-white">
                {total.toLocaleString('pt-BR')}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                chamados registrados
              </span>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {total > 0 ? (((metrics.resolvidos || 0) / total) * 100).toFixed(1) : '0.0'}%
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300">
                Taxa de Resolução
              </div>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {total > 0 ? (((metrics.progresso || 0) / total) * 100).toFixed(1) : '0.0'}%
              </div>
              <div className="text-xs text-green-700 dark:text-green-300">
                Em Andamento
              </div>
            </div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
            <span>Distribuição de Status</span>
            <span>100%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div className="h-full flex">
              <div 
                className="bg-blue-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((metrics.novos || 0) / total) * 100}%` : '0%' }}
                title={`Novos: ${metrics.novos || 0} (${total > 0 ? (((metrics.novos || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
              <div 
                className="bg-yellow-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((metrics.progresso || 0) / total) * 100}%` : '0%' }}
                title={`Em Progresso: ${metrics.progresso || 0} (${total > 0 ? (((metrics.progresso || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
              <div 
                className="bg-orange-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((metrics.pendentes || 0) / total) * 100}%` : '0%' }}
                title={`Pendentes: ${metrics.pendentes || 0} (${total > 0 ? (((metrics.pendentes || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
              <div 
                className="bg-green-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((metrics.resolvidos || 0) / total) * 100}%` : '0%' }}
                title={`Resolvidos: ${metrics.resolvidos || 0} (${total > 0 ? (((metrics.resolvidos || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
            </div>
          </div>
          <div className="flex justify-between mt-2 text-xs">
            <span className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-1" />
              Novos
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1" />
              Progresso
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-1" />
              Pendentes
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1" />
              Resolvidos
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};