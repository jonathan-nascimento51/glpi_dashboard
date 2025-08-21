/**
 * Componente para monitoramento em tempo real do sistema de cache
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  Activity, 
  Database, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Trash2
} from 'lucide-react';
import { cacheManager, CacheAnalytics } from '../utils/cacheStrategies';
import { 
  metricsCache, 
  systemStatusCache, 
  technicianRankingCache, 
  newTicketsCache 
} from '../services/cache';

interface CacheStats {
  size: number;
  hits: number;
  misses: number;
  hitRate: number;
  averageResponseTime: number;
  isActivated: boolean;
  requestCount: number;
  dynamicTtlEnabled?: boolean;
  priorityDistribution?: { high: number; medium: number; low: number };
  averageTtl?: number;
}

interface CacheMonitorProps {
  refreshInterval?: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const CacheMonitor: React.FC<CacheMonitorProps> = ({ refreshInterval = 5000 }) => {
  const [allStats, setAllStats] = useState<Record<string, CacheStats>>({});
  const [performanceReport, setPerformanceReport] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const refreshStats = async () => {
    setIsRefreshing(true);
    try {
      // Obter estatísticas de todos os caches
      const stats = {
        metrics: metricsCache.getStats(),
        systemStatus: systemStatusCache.getStats(),
        technicianRanking: technicianRankingCache.getStats(),
        newTickets: newTicketsCache.getStats(),
        ...cacheManager.getAllStats()
      };
      
      setAllStats(stats);
      
      // Gerar relatório de performance
      const report = CacheAnalytics.generatePerformanceReport(stats);
      setPerformanceReport(report);
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Erro ao atualizar estatísticas do cache:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshStats();
    const interval = setInterval(refreshStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const clearAllCaches = () => {
    metricsCache.clear();
    systemStatusCache.clear();
    technicianRankingCache.clear();
    newTicketsCache.clear();
    cacheManager.clearAll();
    refreshStats();
  };

  const getEfficiencyColor = (efficiency: string) => {
    switch (efficiency) {
      case 'excellent': return 'bg-green-500';
      case 'good': return 'bg-blue-500';
      case 'fair': return 'bg-yellow-500';
      case 'poor': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getEfficiencyIcon = (efficiency: string) => {
    switch (efficiency) {
      case 'excellent': return <CheckCircle className="h-4 w-4" />;
      case 'good': return <TrendingUp className="h-4 w-4" />;
      case 'fair': return <Clock className="h-4 w-4" />;
      case 'poor': return <AlertTriangle className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  // Preparar dados para gráficos
  const hitRateData = Object.entries(allStats).map(([name, stats]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    hitRate: (stats.hitRate * 100).toFixed(1),
    hits: stats.hits,
    misses: stats.misses
  }));

  const priorityData = Object.entries(allStats)
    .filter(([, stats]) => stats.priorityDistribution)
    .flatMap(([name, stats]) => [
      { name: `${name} - High`, value: stats.priorityDistribution!.high, color: '#0088FE' },
      { name: `${name} - Medium`, value: stats.priorityDistribution!.medium, color: '#00C49F' },
      { name: `${name} - Low`, value: stats.priorityDistribution!.low, color: '#FFBB28' }
    ])
    .filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Monitor de Cache</h2>
          <p className="text-muted-foreground">
            Última atualização: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={refreshStats}
            disabled={isRefreshing}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button
            onClick={clearAllCaches}
            variant="destructive"
            size="sm"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Limpar Todos
          </Button>
        </div>
      </div>

      {/* Resumo Geral */}
      {performanceReport && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Resumo do Sistema
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-lg font-medium">{performanceReport.summary}</div>
              {performanceReport.overallRecommendations.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-sm">Recomendações Gerais:</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                    {performanceReport.overallRecommendations.map((rec: string, index: number) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="details">Detalhes</TabsTrigger>
          <TabsTrigger value="analytics">Análises</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Cards de Estatísticas */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(allStats).map(([name, stats]) => {
              const analysis = performanceReport?.details[name]?.analysis;
              return (
                <Card key={name}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium capitalize">
                      {name.replace(/([A-Z])/g, ' $1').trim()}
                    </CardTitle>
                    <Database className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-bold">{stats.size}</span>
                        <Badge 
                          variant={stats.isActivated ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {stats.isActivated ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </div>
                      
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span>Hit Rate</span>
                          <span>{(stats.hitRate * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={stats.hitRate * 100} className="h-1" />
                      </div>
                      
                      <div className="text-xs text-muted-foreground space-y-1">
                        <div>Hits: {stats.hits} | Misses: {stats.misses}</div>
                        <div>Tempo médio: {stats.averageResponseTime.toFixed(0)}ms</div>
                        {stats.dynamicTtlEnabled && (
                          <div>TTL médio: {formatDuration(stats.averageTtl || 0)}</div>
                        )}
                      </div>
                      
                      {analysis && (
                        <div className="flex items-center gap-1 mt-2">
                          {getEfficiencyIcon(analysis.efficiency)}
                          <Badge 
                            className={`text-xs ${getEfficiencyColor(analysis.efficiency)} text-white`}
                          >
                            {analysis.efficiency}
                          </Badge>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          {/* Detalhes por Cache */}
          <div className="grid gap-4">
            {Object.entries(allStats).map(([name, stats]) => {
              const analysis = performanceReport?.details[name]?.analysis;
              return (
                <Card key={name}>
                  <CardHeader>
                    <CardTitle className="capitalize flex items-center gap-2">
                      <Database className="h-5 w-5" />
                      {name.replace(/([A-Z])/g, ' $1').trim()}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2">
                        <h4 className="font-medium">Estatísticas Básicas</h4>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span>Tamanho:</span>
                            <span>{stats.size} entradas</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Hits:</span>
                            <span>{stats.hits}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Misses:</span>
                            <span>{stats.misses}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Hit Rate:</span>
                            <span>{(stats.hitRate * 100).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Tempo Médio:</span>
                            <span>{stats.averageResponseTime.toFixed(0)}ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Requisições:</span>
                            <span>{stats.requestCount}</span>
                          </div>
                        </div>
                      </div>
                      
                      {stats.dynamicTtlEnabled && stats.priorityDistribution && (
                        <div className="space-y-2">
                          <h4 className="font-medium">TTL Dinâmico</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>TTL Médio:</span>
                              <span>{formatDuration(stats.averageTtl || 0)}</span>
                            </div>
                            <div className="space-y-1">
                              <div className="flex justify-between">
                                <span>Alta Prioridade:</span>
                                <span>{stats.priorityDistribution.high}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Média Prioridade:</span>
                                <span>{stats.priorityDistribution.medium}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Baixa Prioridade:</span>
                                <span>{stats.priorityDistribution.low}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {analysis && analysis.recommendations.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <h4 className="font-medium text-sm">Recomendações:</h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                          {analysis.recommendations.map((rec: string, index: number) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {/* Gráficos de Análise */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Taxa de Hit por Cache</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={hitRateData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value, name) => [
                        name === 'hitRate' ? `${value}%` : value,
                        name === 'hitRate' ? 'Hit Rate' : name
                      ]}
                    />
                    <Bar dataKey="hitRate" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {priorityData.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Distribuição de Prioridades</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={priorityData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {priorityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CacheMonitor;