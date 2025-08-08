import React from 'react';
import { MetricCard } from './MetricCard';
import { TicketStatus } from '../types';
import { MaintenanceMetrics } from '../hooks/useMaintenanceDashboard';



interface MaintenanceMetricsGridProps {
  metrics: MaintenanceMetrics;
  onFilterByStatus: (status: TicketStatus) => void;
}

export const MaintenanceMetricsGrid: React.FC<MaintenanceMetricsGridProps> = ({
  metrics,
  onFilterByStatus
}) => {
  console.log('🔧 MaintenanceMetricsGrid - DADOS RECEBIDOS:', {
    metrics,
    'metrics.total': metrics.total
  });

  // Verificação de segurança para evitar erros
  if (!metrics) {
    console.log('⚠️ MaintenanceMetricsGrid - Métricas não disponíveis');
    return <div>Carregando métricas de manutenção...</div>;
  }

  // Usa o total calculado pelo backend
  const { novos, progresso, pendentes, resolvidos, total, maintenance_context } = metrics;

  const metricCards: Array<{
    type: TicketStatus;
    value: number;
    change: string;
  }> = [
    {
      type: 'new',
      value: novos || 0,
      change: '0',
    },
    {
      type: 'progress',
      value: progresso || 0,
      change: '0',
    },
    {
      type: 'pending',
      value: pendentes || 0,
      change: '0',
    },
    {
      type: 'resolved',
      value: resolvidos || 0,
      change: '0',
    },
  ];



  return (
    <div className="space-y-6">
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
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

      {/* Maintenance Context Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          🔧 Contexto de Manutenção
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {maintenance_context.total_categories}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Categorias Totais</div>
          </div>
          
          <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <div className="text-3xl font-bold text-red-600 dark:text-red-400">
              {maintenance_context.critical_categories}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Categorias Críticas</div>
          </div>
          
          <div className="text-center p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
            <div className="text-3xl font-bold text-amber-600 dark:text-amber-400">
              {maintenance_context.avg_resolution_time}h
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Tempo Médio de Resolução</div>
          </div>
        </div>
      </div>

      {/* Total Summary Card with Maintenance Focus */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 truncate">
              🏢 Dashboard de Manutenção - Casa Civil
            </h3>
            <div className="flex items-baseline space-x-2 min-w-0">
              <span className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white truncate flex-shrink-0">
                {total?.toLocaleString('pt-BR') || '0'}
              </span>
              <span className="text-xs lg:text-sm text-gray-500 dark:text-gray-400 truncate flex-shrink">
                chamados de manutenção
              </span>
            </div>
          </div>
          
          {/* Maintenance KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 lg:gap-4 text-center lg:min-w-0 lg:flex-shrink-0">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 min-w-0">
              <div className="text-xl lg:text-2xl font-bold text-blue-600 dark:text-blue-400 truncate">
                {total > 0 ? (((resolvidos || 0) / total) * 100).toFixed(1) : '0.0'}%
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300 truncate">
                Taxa de Resolução
              </div>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 min-w-0">
              <div className="text-xl lg:text-2xl font-bold text-green-600 dark:text-green-400 truncate">
                {total > 0 ? ((((progresso || 0)) / total) * 100).toFixed(1) : '0.0'}%
              </div>
              <div className="text-xs text-green-700 dark:text-green-300 truncate">
                Em Execução
              </div>
            </div>
            <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 min-w-0">
              <div className="text-xl lg:text-2xl font-bold text-orange-600 dark:text-orange-400 truncate">
                {total > 0 ? (((pendentes || 0) / total) * 100).toFixed(1) : '0.0'}%
              </div>
              <div className="text-xs text-orange-700 dark:text-orange-300 truncate">
                Aguardando
              </div>
            </div>
          </div>
        </div>
        
        {/* Progress Bar with Maintenance Context */}
        <div className="mt-6">
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
            <span>Status dos Serviços de Manutenção</span>
            <span>100%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div className="h-full flex">
              <div 
                className="bg-blue-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((novos || 0) / total) * 100}%` : '0%' }}
                title={`Novos Chamados: ${novos || 0} (${total > 0 ? (((novos || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
              <div 
                className="bg-yellow-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((progresso || 0) / total) * 100}%` : '0%' }}
                title={`Em Execução: ${progresso || 0} (${total > 0 ? (((progresso || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
              <div 
                className="bg-orange-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((pendentes || 0) / total) * 100}%` : '0%' }}
                title={`Aguardando Material/Aprovação: ${pendentes || 0} (${total > 0 ? (((pendentes || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
              />
              <div 
                className="bg-green-500 transition-all duration-500"
                style={{ width: total > 0 ? `${((resolvidos || 0) / total) * 100}%` : '0%' }}
                title={`Serviços Concluídos: ${resolvidos || 0} (${total > 0 ? (((resolvidos || 0) / total) * 100).toFixed(1) : '0.0'}%)`}
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
              Em Execução
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-1" />
              Aguardando
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1" />
              Concluídos
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};