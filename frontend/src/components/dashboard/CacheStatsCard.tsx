import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  Database,
  Zap,
  MemoryStick,
  TrendingUp,
  RefreshCw,
  Trash2,
  Target,
  Activity,
} from 'lucide-react';
import { useCacheStats, useCacheHealth } from '../../hooks/useCacheStats';
import { cn } from '../../lib/utils';

/**
 * Componente para exibir estatísticas detalhadas do cache
 */
export const CacheStatsCard: React.FC = () => {
  const {
    stats,
    isLoading,
    refreshStats,
    clearAllCaches,
    invalidateTicketCache,
    invalidateMetricsCache,
    optimizeCaches,
  } = useCacheStats();

  const health = useCacheHealth();

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getHealthColor = (status: string): string => {
    switch (status) {
      case 'excellent':
        return 'text-green-600';
      case 'good':
        return 'text-blue-600';
      case 'fair':
        return 'text-yellow-600';
      case 'poor':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getHealthBadgeVariant = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'default';
      case 'good':
        return 'secondary';
      case 'fair':
        return 'outline';
      case 'poor':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  return (
    <Card className='w-full'>
      <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
        <CardTitle className='text-sm font-medium flex items-center gap-2'>
          <Database className='h-4 w-4' />
          Cache Inteligente
        </CardTitle>
        <Badge
          variant={getHealthBadgeVariant(health.status)}
          className={cn('capitalize', getHealthColor(health.status))}
        >
          {health.status}
        </Badge>
      </CardHeader>

      <CardContent className='space-y-4'>
        {/* Estatísticas Gerais */}
        <div className='grid grid-cols-2 gap-4'>
          <div className='space-y-1'>
            <div className='flex items-center gap-2 text-sm text-muted-foreground'>
              <Target className='h-3 w-3' />
              Hit Rate
            </div>
            <div className={cn('text-lg font-semibold', getHealthColor(health.status))}>
              {formatPercentage(stats.total.hitRate)}
            </div>
          </div>

          <div className='space-y-1'>
            <div className='flex items-center gap-2 text-sm text-muted-foreground'>
              <MemoryStick className='h-3 w-3' />
              Memória
            </div>
            <div className='text-lg font-semibold'>{formatBytes(stats.total.memoryUsage)}</div>
          </div>
        </div>

        {/* Estatísticas por Cache */}
        <div className='space-y-3'>
          <h4 className='text-sm font-medium flex items-center gap-2'>
            <Activity className='h-3 w-3' />
            Detalhes por Cache
          </h4>

          <div className='space-y-2'>
            {/* Cache de Métricas */}
            <div className='flex justify-between items-center p-2 bg-muted/50 rounded'>
              <div className='flex items-center gap-2'>
                <TrendingUp className='h-3 w-3 text-blue-500' />
                <span className='text-sm font-medium'>Métricas</span>
              </div>
              <div className='flex items-center gap-3 text-xs text-muted-foreground'>
                <span>{stats.metrics.size} entradas</span>
                <span>{formatPercentage(stats.metrics.hitRate)} hit</span>
                <span>{formatBytes(stats.metrics.memoryUsage)}</span>
              </div>
            </div>

            {/* Cache de Tickets */}
            <div className='flex justify-between items-center p-2 bg-muted/50 rounded'>
              <div className='flex items-center gap-2'>
                <Zap className='h-3 w-3 text-green-500' />
                <span className='text-sm font-medium'>Tickets</span>
              </div>
              <div className='flex items-center gap-3 text-xs text-muted-foreground'>
                <span>{stats.tickets.size} entradas</span>
                <span>{formatPercentage(stats.tickets.hitRate)} hit</span>
                <span>{formatBytes(stats.tickets.memoryUsage)}</span>
              </div>
            </div>

            {/* Cache de Status */}
            <div className='flex justify-between items-center p-2 bg-muted/50 rounded'>
              <div className='flex items-center gap-2'>
                <Database className='h-3 w-3 text-purple-500' />
                <span className='text-sm font-medium'>Sistema</span>
              </div>
              <div className='flex items-center gap-3 text-xs text-muted-foreground'>
                <span>{stats.systemStatus.size} entradas</span>
                <span>{formatPercentage(stats.systemStatus.hitRate)} hit</span>
                <span>{formatBytes(stats.systemStatus.memoryUsage)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Ações */}
        <div className='flex flex-wrap gap-2 pt-2 border-t'>
          <Button
            variant='outline'
            size='sm'
            onClick={refreshStats}
            disabled={isLoading}
            className='flex items-center gap-1'
          >
            <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
            Atualizar
          </Button>

          <Button
            variant='outline'
            size='sm'
            onClick={optimizeCaches}
            className='flex items-center gap-1'
          >
            <Zap className='h-3 w-3' />
            Otimizar
          </Button>

          <Button
            variant='outline'
            size='sm'
            onClick={clearAllCaches}
            className='flex items-center gap-1 text-destructive hover:text-destructive'
          >
            <Trash2 className='h-3 w-3' />
            Limpar
          </Button>
        </div>

        {/* Ações Específicas */}
        <div className='flex flex-wrap gap-2'>
          <Button variant='ghost' size='sm' onClick={invalidateMetricsCache} className='text-xs'>
            Invalidar Métricas
          </Button>

          <Button variant='ghost' size='sm' onClick={invalidateTicketCache} className='text-xs'>
            Invalidar Tickets
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Componente compacto para exibir apenas o status do cache
 */
export const CacheHealthIndicator: React.FC = () => {
  const health = useCacheHealth();

  return (
    <div className='flex items-center gap-2'>
      <Database className={cn('h-4 w-4', getHealthColor(health.status))} />
      <span className='text-sm font-medium'>Cache: {formatPercentage(health.hitRate)}</span>
      <Badge variant={getHealthBadgeVariant(health.status)} className='text-xs'>
        {health.status}
      </Badge>
    </div>
  );
};

// Funções auxiliares exportadas para reutilização
function getHealthColor(status: string): string {
  switch (status) {
    case 'excellent':
      return 'text-green-600';
    case 'good':
      return 'text-blue-600';
    case 'fair':
      return 'text-yellow-600';
    case 'poor':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

function getHealthBadgeVariant(status: string) {
  switch (status) {
    case 'excellent':
      return 'default';
    case 'good':
      return 'secondary';
    case 'fair':
      return 'outline';
    case 'poor':
      return 'destructive';
    default:
      return 'outline';
  }
}

function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}
