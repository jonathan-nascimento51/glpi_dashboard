/**
 * Componente para exibir estatísticas de monitoramento de requisições
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Progress,
  Alert,
  AlertDescription,
} from '../ui';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  Database,
  RefreshCw,
  Download,
  Trash2,
  BarChart3,
  Zap,
} from 'lucide-react';
import { useRequestMonitor, useRequestPerformance } from '../../hooks/useRequestMonitor';

interface RequestMonitorCardProps {
  className?: string;
  showDetailedView?: boolean;
}

export const RequestMonitorCard: React.FC<RequestMonitorCardProps> = ({
  className = '',
  showDetailedView = false,
}) => {
  const {
    stats,
    isLoading,
    error,
    slowestRequests,
    topEndpoints,
    detailedStats,
    refreshStats,
    clearHistory,
    exportData,
    getDetailedStats,
  } = useRequestMonitor({
    autoRefresh: true,
    refreshInterval: 30000,
    enableRealTimeUpdates: true,
  });

  const { performanceScore, isPerformanceGood, isPerformanceFair } = useRequestPerformance();

  const [activeTab, setActiveTab] = useState('overview');
  const [detailPeriod, setDetailPeriod] = useState(60);

  const handleExport = () => {
    const data = exportData();
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `request-monitor-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleGetDetailedStats = (period: number) => {
    setDetailPeriod(period);
    getDetailedStats(period);
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getPerformanceColor = () => {
    if (isPerformanceGood) return 'text-green-600';
    if (isPerformanceFair) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceBadgeVariant = () => {
    if (isPerformanceGood) return 'default';
    if (isPerformanceFair) return 'secondary';
    return 'destructive';
  };

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Activity className='h-5 w-5' />
            Monitor de Requisições
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant='destructive'>
            <XCircle className='h-4 w-4' />
            <AlertDescription>{typeof error === 'string' ? error : error?.message || 'Erro desconhecido'}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className='flex items-center justify-between'>
          <CardTitle className='flex items-center gap-2'>
            <Activity className='h-5 w-5' />
            Monitor de Requisições
            <Badge variant={getPerformanceBadgeVariant()}>{performanceScore}% Performance</Badge>
          </CardTitle>
          <div className='flex items-center gap-2'>
            <Button variant='outline' size='sm' onClick={refreshStats} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button variant='outline' size='sm' onClick={handleExport}>
              <Download className='h-4 w-4' />
            </Button>
            <Button variant='outline' size='sm' onClick={clearHistory}>
              <Trash2 className='h-4 w-4' />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className='grid w-full grid-cols-4'>
            <TabsTrigger value='overview'>Visão Geral</TabsTrigger>
            <TabsTrigger value='performance'>Performance</TabsTrigger>
            <TabsTrigger value='endpoints'>Endpoints</TabsTrigger>
            <TabsTrigger value='detailed'>Detalhado</TabsTrigger>
          </TabsList>

          <TabsContent value='overview' className='space-y-4'>
            <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
              <div className='text-center'>
                <div className='text-2xl font-bold text-blue-600'>{stats.totalRequests}</div>
                <div className='text-sm text-gray-500'>Total</div>
              </div>
              <div className='text-center'>
                <div className='text-2xl font-bold text-green-600'>{stats.successfulRequests}</div>
                <div className='text-sm text-gray-500'>Sucesso</div>
              </div>
              <div className='text-center'>
                <div className='text-2xl font-bold text-red-600'>{stats.failedRequests}</div>
                <div className='text-sm text-gray-500'>Erro</div>
              </div>
              <div className='text-center'>
                <div className='text-2xl font-bold text-purple-600'>{stats.cachedRequests}</div>
                <div className='text-sm text-gray-500'>Cache</div>
              </div>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              <div className='flex items-center gap-3 p-3 bg-gray-50 rounded-lg'>
                <Clock className='h-5 w-5 text-blue-500' />
                <div>
                  <div className='font-semibold'>{formatDuration(stats.averageResponseTime)}</div>
                  <div className='text-sm text-gray-500'>Tempo Médio</div>
                </div>
              </div>
              <div className='flex items-center gap-3 p-3 bg-gray-50 rounded-lg'>
                <TrendingUp className='h-5 w-5 text-green-500' />
                <div>
                  <div className='font-semibold'>{stats.requestsPerMinute.toFixed(1)}/min</div>
                  <div className='text-sm text-gray-500'>Req/Minuto</div>
                </div>
              </div>
              <div className='flex items-center gap-3 p-3 bg-gray-50 rounded-lg'>
                <Database className='h-5 w-5 text-purple-500' />
                <div>
                  <div className='font-semibold'>{(stats.cacheHitRate * 100).toFixed(1)}%</div>
                  <div className='text-sm text-gray-500'>Cache Hit</div>
                </div>
              </div>
            </div>

            <div className='space-y-2'>
              <div className='flex justify-between text-sm'>
                <span>Taxa de Erro</span>
                <span className={stats.errorRate > 0.1 ? 'text-red-600' : 'text-green-600'}>
                  {(stats.errorRate * 100).toFixed(1)}%
                </span>
              </div>
              <Progress value={stats.errorRate * 100} className='h-2' />
            </div>
          </TabsContent>

          <TabsContent value='performance' className='space-y-4'>
            <div className='text-center p-6 bg-gray-50 rounded-lg'>
              <div className={`text-4xl font-bold ${getPerformanceColor()}`}>
                {performanceScore}%
              </div>
              <div className='text-lg font-semibold mt-2'>Score de Performance</div>
              <div className='text-sm text-gray-500 mt-1'>
                {isPerformanceGood ? 'Excelente' : isPerformanceFair ? 'Bom' : 'Precisa Melhorar'}
              </div>
            </div>

            <div className='space-y-4'>
              <h4 className='font-semibold flex items-center gap-2'>
                <Zap className='h-4 w-4' />
                Requisições Mais Lentas
              </h4>
              <div className='space-y-2'>
                {slowestRequests.slice(0, 5).map((request, index) => (
                  <div
                    key={request.id}
                    className='flex items-center justify-between p-2 bg-gray-50 rounded'
                  >
                    <div className='flex items-center gap-2'>
                      <Badge variant='outline'>#{index + 1}</Badge>
                      <span className='font-mono text-sm'>{request.endpoint}</span>
                    </div>
                    <div className='flex items-center gap-2'>
                      <span className='text-sm text-gray-500'>
                        {formatDuration(request.duration || 0)}
                      </span>
                      {request.status === 'error' && <XCircle className='h-4 w-4 text-red-500' />}
                      {request.status === 'success' && (
                        <CheckCircle className='h-4 w-4 text-green-500' />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value='endpoints' className='space-y-4'>
            <h4 className='font-semibold flex items-center gap-2'>
              <BarChart3 className='h-4 w-4' />
              Endpoints Mais Utilizados
            </h4>
            <div className='space-y-2'>
              {topEndpoints.slice(0, 10).map((endpoint, index) => (
                <div
                  key={endpoint.endpoint}
                  className='flex items-center justify-between p-3 bg-gray-50 rounded-lg'
                >
                  <div className='flex items-center gap-3'>
                    <Badge variant='outline'>#{index + 1}</Badge>
                    <span className='font-mono text-sm'>{endpoint.endpoint}</span>
                  </div>
                  <div className='flex items-center gap-4 text-sm'>
                    <div className='text-center'>
                      <div className='font-semibold'>{endpoint.count}</div>
                      <div className='text-gray-500'>Chamadas</div>
                    </div>
                    <div className='text-center'>
                      <div className='font-semibold'>{formatDuration(endpoint.avgDuration)}</div>
                      <div className='text-gray-500'>Média</div>
                    </div>
                    <div className='text-center'>
                      <div
                        className={`font-semibold ${
                          endpoint.errorRate > 0.1 ? 'text-red-600' : 'text-green-600'
                        }`}
                      >
                        {(endpoint.errorRate * 100).toFixed(1)}%
                      </div>
                      <div className='text-gray-500'>Erro</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value='detailed' className='space-y-4'>
            <div className='flex items-center gap-2 mb-4'>
              <span className='text-sm font-medium'>Período:</span>
              {[15, 30, 60, 120].map(period => (
                <Button
                  key={period}
                  variant={detailPeriod === period ? 'default' : 'outline'}
                  size='sm'
                  onClick={() => handleGetDetailedStats(period)}
                >
                  {period}min
                </Button>
              ))}
            </div>

            {detailedStats && (
              <div className='space-y-4'>
                <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
                  <div className='text-center p-3 bg-blue-50 rounded-lg'>
                    <div className='text-xl font-bold text-blue-600'>
                      {detailedStats.stats.totalRequests}
                    </div>
                    <div className='text-sm text-gray-500'>Total no Período</div>
                  </div>
                  <div className='text-center p-3 bg-green-50 rounded-lg'>
                    <div className='text-xl font-bold text-green-600'>
                      {formatDuration(detailedStats.stats.averageResponseTime)}
                    </div>
                    <div className='text-sm text-gray-500'>Tempo Médio</div>
                  </div>
                  <div className='text-center p-3 bg-purple-50 rounded-lg'>
                    <div className='text-xl font-bold text-purple-600'>
                      {(detailedStats.stats.cacheHitRate * 100).toFixed(1)}%
                    </div>
                    <div className='text-sm text-gray-500'>Cache Hit</div>
                  </div>
                  <div className='text-center p-3 bg-red-50 rounded-lg'>
                    <div className='text-xl font-bold text-red-600'>
                      {(detailedStats.stats.errorRate * 100).toFixed(1)}%
                    </div>
                    <div className='text-sm text-gray-500'>Taxa de Erro</div>
                  </div>
                </div>

                {detailedStats.errors.length > 0 && (
                  <div>
                    <h5 className='font-semibold mb-2'>Erros no Período</h5>
                    <div className='space-y-1'>
                      {detailedStats.errors.slice(0, 5).map((error, index) => (
                        <div
                          key={index}
                          className='flex items-center justify-between p-2 bg-red-50 rounded text-sm'
                        >
                          <span className='font-mono'>{error.endpoint}</span>
                          <div className='flex items-center gap-2'>
                            <span className='text-red-600'>
                              {typeof error.error === 'string' 
                                ? error.error 
                                : error.error?.message || error.error?.toString() || JSON.stringify(error.error)
                              }
                            </span>
                            <Badge variant='destructive'>{error.count}</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default RequestMonitorCard;
