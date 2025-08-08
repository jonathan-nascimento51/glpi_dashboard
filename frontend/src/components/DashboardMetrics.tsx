import React, { useState, useEffect } from 'react';
import { useDashboard } from '../hooks/useDashboard';
import type {
  DashboardMetrics,
  FilterParams,
  LoadingState,
  PerformanceMetrics
} from '../types/api';
import { isValidLevelMetrics, isValidNiveisMetrics } from '../types/api';

interface DashboardMetricsProps {
  initialFilters?: FilterParams;
  showPerformanceMetrics?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const DashboardMetrics: React.FC<DashboardMetricsProps> = ({
  initialFilters = {},
  showPerformanceMetrics = false,
  autoRefresh = false,
  refreshInterval = 30000
}) => {
  const {
    metrics: data,
    isLoading: loading,
    error,
    refreshData,
    lastUpdated,
    performance,
    updateFilters
  } = useDashboard(initialFilters);

  const [filters, setFilters] = useState<FilterParams>(initialFilters);
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: loading,
    error: null,
    lastUpdated: null
  });

  // Auto refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refreshData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refreshData]);

  // Update loading state
  useEffect(() => {
    setLoadingState({
      isLoading: loading,
      error: error,
      lastUpdated: lastUpdated
    });
  }, [loading, error, lastUpdated]);

  const handleFilterChange = (newFilters: Partial<FilterParams>) => {
    const updatedFilters = { ...filters, ...newFilters };
    console.log('🔍 DashboardMetrics - Filtros atuais:', filters);
    console.log('🔍 DashboardMetrics - Novos filtros:', newFilters);
    console.log('🔍 DashboardMetrics - Filtros combinados:', updatedFilters);
    setFilters(updatedFilters);
    // Aplicar os filtros imediatamente
    updateFilters(updatedFilters);
  };

  const renderMetricsCard = (title: string, value: number, trend?: number) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">{title}</h3>
      <div className="flex items-center justify-between">
        <span className="text-3xl font-bold text-blue-600">{value}</span>
        {trend !== undefined && (
          <span className={`text-sm font-medium ${
            trend > 0 ? 'text-green-500' : trend < 0 ? 'text-red-500' : 'text-gray-500'
          }`}>
            {trend > 0 ? '↗' : trend < 0 ? '↘' : '→'} {Math.abs(trend)}%
          </span>
        )}
      </div>
    </div>
  );

  const renderLevelMetrics = (levelMetrics: any) => {
    if (!isValidLevelMetrics(levelMetrics)) {
      return <div className="text-red-500">Dados de nível inválidos</div>;
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {renderMetricsCard('Novos', levelMetrics.novos)}
        {renderMetricsCard('Em Progresso', levelMetrics.progresso)}
        {renderMetricsCard('Pendentes', levelMetrics.pendentes)}
        {renderMetricsCard('Resolvidos', levelMetrics.resolvidos)}
      </div>
    );
  };

  const renderNiveisMetrics = (niveisMetrics: any) => {
    if (!isValidNiveisMetrics(niveisMetrics)) {
      return <div className="text-red-500">Dados de níveis inválidos</div>;
    }

    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Métricas por Nível</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(niveisMetrics).map(([nivel, metrics]) => {
            if (typeof metrics === 'object' && metrics !== null) {
              return (
                <div key={nivel} className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-700 mb-2">{nivel}</h3>
                  {renderLevelMetrics(metrics)}
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>
    );
  };

  const renderPerformanceMetrics = (perfMetrics: PerformanceMetrics) => (
    <div className="bg-gray-50 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">Métricas de Performance</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-600">Tempo de Resposta:</span>
          <span className="ml-2 font-medium">{perfMetrics.responseTime.toFixed(2)}ms</span>
        </div>
        <div>
          <span className="text-gray-600">Cache Hit:</span>
          <span className="ml-2 font-medium">{perfMetrics.cacheHit ? 'Sim' : 'Não'}</span>
        </div>
        <div>
          <span className="text-gray-600">Endpoint:</span>
          <span className="ml-2 font-medium">{perfMetrics.endpoint}</span>
        </div>
      </div>
    </div>
  );

  const renderFilters = () => (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">Filtros</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Data Início</label>
          <input
            type="date"
            value={filters.dateRange?.startDate || ''}
            onChange={(e) => handleFilterChange({ 
              dateRange: { 
                startDate: e.target.value,
                endDate: filters.dateRange?.endDate || ''
              } 
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Data Fim</label>
          <input
            type="date"
            value={filters.dateRange?.endDate || ''}
            onChange={(e) => handleFilterChange({ 
              dateRange: { 
                startDate: filters.dateRange?.startDate || '',
                endDate: e.target.value
              } 
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            value={filters.status?.[0] || ''}
            onChange={(e) => handleFilterChange({ status: e.target.value ? [e.target.value] : [] })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="aberto">Aberto</option>
            <option value="fechado">Fechado</option>
            <option value="pendente">Pendente</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Prioridade</label>
          <select
            value={filters.priority?.[0] || ''}
            onChange={(e) => handleFilterChange({ priority: e.target.value ? [e.target.value] : [] })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas</option>
            <option value="baixa">Baixa</option>
            <option value="media">Média</option>
            <option value="alta">Alta</option>
            <option value="critica">Crítica</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Níveis</label>
          <select
            value={filters.levels?.[0] || ''}
            onChange={(e) => handleFilterChange({ levels: e.target.value ? [e.target.value] : [] })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="Manutenção Geral">Manutenção Geral</option>
            <option value="Patrimônio">Patrimônio</option>
            <option value="Atendimento">Atendimento</option>
            <option value="Mecanografia">Mecanografia</option>
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={() => refreshData()}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Carregando...' : 'Atualizar'}
          </button>
        </div>
      </div>
    </div>
  );

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Erro ao carregar dados</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
            <div className="mt-4">
              <button
                onClick={() => refreshData()}
                className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Tentar novamente
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando métricas do dashboard...</p>
          {loadingState.error && (
            <div className="mt-2 text-sm text-red-500">
              Erro: {loadingState.error}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Nenhum dado disponível</p>
        <button
          onClick={() => refreshData()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Carregar dados
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard GLPI</h1>
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <span className="text-sm text-gray-500">
              Última atualização: {lastUpdated.toLocaleString()}
            </span>
          )}
          <button
            onClick={() => refreshData()}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Atualizar
          </button>
        </div>
      </div>

      {/* Filters */}
      {renderFilters()}

      {/* Performance Metrics */}
      {showPerformanceMetrics && performance && renderPerformanceMetrics(performance)}

      {/* Main Metrics */}
      {data.niveis && renderNiveisMetrics(data.niveis)}

      {/* Trends */}
      {data.tendencias && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Tendências</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {renderMetricsCard('Novos', parseInt(data.tendencias.novos || '0'))}
            {renderMetricsCard('Pendentes', parseInt(data.tendencias.pendentes || '0'))}
            {renderMetricsCard('Em Progresso', parseInt(data.tendencias.progresso || '0'))}
            {renderMetricsCard('Resolvidos', parseInt(data.tendencias.resolvidos || '0'))}
          </div>
        </div>
      )}


    </div>
  );
};

export default DashboardMetrics;