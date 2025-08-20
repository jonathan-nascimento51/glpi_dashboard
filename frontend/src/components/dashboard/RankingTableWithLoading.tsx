import React, { useEffect, useState } from 'react';
import { RankingTable } from './RankingTable';
import { LoadingProgress } from '../LoadingProgress';
import { useTechnicianRanking } from '../../hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TechnicianRanking } from '@/types';

interface RankingTableWithLoadingProps {
  title?: string;
  className?: string;
  filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
  };
  onError?: (error: Error) => void;
  onTimeout?: () => void;
}

const RankingTableWithLoading: React.FC<RankingTableWithLoadingProps> = ({
  title = 'Ranking de Técnicos',
  className,
  filters,
  onError,
  onTimeout,
}) => {
  const [retryCount, setRetryCount] = useState(0);
  const [lastError, setLastError] = useState<Error | null>(null);

  // Determinar tempo estimado baseado nos filtros
  const getEstimatedTime = () => {
    if (filters?.start_date || filters?.end_date) {
      return 180; // 3 minutos para consultas com filtros de data
    }
    if (filters?.limit && filters.limit > 50) {
      return 120; // 2 minutos para consultas com muitos resultados
    }
    return 60; // 1 minuto para consultas simples
  };

  const getTimeoutDuration = () => {
    return getEstimatedTime() + 60; // Adiciona 1 minuto ao tempo estimado
  };

  const {
    data: rankingData,
    loading: isLoading,
    error,
    execute: fetchRanking,
  } = useTechnicianRanking(filters, {
    autoExecute: true,
    onError: (err) => {
      setLastError(err);
      onError?.(err);
    },
  });

  // Reset error when filters change
  useEffect(() => {
    setLastError(null);
    setRetryCount(0);
  }, [filters]);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    setLastError(null);
    fetchRanking();
  };

  const handleTimeout = () => {
    console.warn('Ranking request timed out');
    onTimeout?.();
  };

  const getLoadingText = () => {
    if (retryCount > 0) {
      return `Tentativa ${retryCount + 1} - Carregando ranking...`;
    }
    if (filters?.start_date || filters?.end_date) {
      return 'Processando dados históricos...';
    }
    if (filters?.limit && filters.limit > 50) {
      return 'Carregando ranking completo...';
    }
    return 'Carregando ranking de técnicos...';
  };

  // Se está carregando, mostrar o LoadingProgress
  if (isLoading) {
    return (
      <Card className={cn('h-full', className)}>
        <CardHeader>
          <CardTitle className='flex items-center justify-between'>
            {title}
            {retryCount > 0 && (
              <span className='text-sm font-normal text-yellow-600 dark:text-yellow-400'>
                Tentativa {retryCount + 1}
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className='flex items-center justify-center h-64'>
          <LoadingProgress
            isLoading={isLoading}
            text={getLoadingText()}
            estimatedTime={getEstimatedTime()}
            timeoutDuration={getTimeoutDuration()}
            onTimeout={handleTimeout}
            variant='detailed'
            showProgress={true}
            showTimeEstimate={true}
            size='md'
          />
        </CardContent>
      </Card>
    );
  }

  // Se há erro, mostrar estado de erro
  if (error || lastError) {
    const currentError = error || lastError;
    return (
      <Card className={cn('h-full', className)}>
        <CardHeader>
          <CardTitle className='flex items-center space-x-2'>
            <AlertCircle className='w-5 h-5 text-red-500' />
            <span>{title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className='flex flex-col items-center justify-center h-64 space-y-4'>
          <div className='text-center space-y-2'>
            <p className='text-red-600 dark:text-red-400 font-medium'>
              Erro ao carregar ranking
            </p>
            <p className='text-sm text-gray-600 dark:text-gray-400'>
              {currentError?.message || 'Erro desconhecido'}
            </p>
            {retryCount > 0 && (
              <p className='text-xs text-gray-500 dark:text-gray-500'>
                Tentativas realizadas: {retryCount}
              </p>
            )}
          </div>
          <button
            onClick={handleRetry}
            className='flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors'
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
            <span>Tentar novamente</span>
          </button>
        </CardContent>
      </Card>
    );
  }

  // Se não há dados, mostrar estado vazio
  if (!rankingData || rankingData.length === 0) {
    return (
      <Card className={cn('h-full', className)}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className='flex flex-col items-center justify-center h-64 space-y-4'>
          <div className='text-center space-y-2'>
            <p className='text-gray-600 dark:text-gray-400 font-medium'>
              Nenhum dado encontrado
            </p>
            <p className='text-sm text-gray-500 dark:text-gray-500'>
              Não há técnicos para exibir com os filtros aplicados
            </p>
          </div>
          <button
            onClick={handleRetry}
            className='flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors'
          >
            <RefreshCw className='w-4 h-4' />
            <span>Recarregar</span>
          </button>
        </CardContent>
      </Card>
    );
  }

  // Renderizar a tabela com dados
  return (
    <RankingTable
      data={rankingData}
      title={title}
      className={className}
      filters={filters}
    />
  );
};

export default RankingTableWithLoading;