import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { RefreshCw, AlertTriangle, TrendingUp, Users, Wrench, Calendar } from 'lucide-react';
import { useMaintenanceDashboard } from '../hooks/useMaintenanceDashboard';
import { MaintenanceMetricsGrid } from '../components/MaintenanceMetricsGrid';
import { TechnicalGroupsAnalysis } from '../components/TechnicalGroupsAnalysis';
import { MaintenanceCategoriesChart } from '../components/MaintenanceCategoriesChart';
import { DateRangeFilter } from '../components/DateRangeFilter';
import { TicketStatus } from '../types';

const MaintenanceDashboard: React.FC = () => {
  const {
    metrics,
    categories,
    groups,
    summary,
    loading,
    error,
    refreshData,
    fetchMaintenanceMetrics
  } = useMaintenanceDashboard();

  // Fetch initial data
  useEffect(() => {
    handleRefresh();
  }, []);

  const handleRefresh = async () => {
    try {
      refreshData();
    } catch (error) {
      console.error('Error refreshing dashboard:', error);
    }
  };



  const handleFilterByStatus = (status: TicketStatus) => {
    console.log('Filtering by status:', status);
    // Implementar filtro por status se necessário
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-lg">Carregando dashboard de manutenção...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Erro ao carregar dados: {error}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRefresh}
              className="ml-2"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Tentar novamente
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Wrench className="h-8 w-8 text-blue-600" />
            Dashboard de Manutenção
          </h1>
          <p className="text-gray-600 mt-1">
            Monitoramento e análise dos serviços de manutenção da Casa Civil
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <DateRangeFilter 
            onChange={() => {
              fetchMaintenanceMetrics();
            }}
            variant="modern"
          />
          <Button 
            onClick={handleRefresh} 
            variant="outline" 
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Resumo Executivo */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Tickets</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.overview.total_tickets}</div>
              <p className="text-xs text-muted-foreground">
                {summary.overview.active_tickets} ativos, {summary.overview.resolved_tickets} resolvidos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tempo Médio de Resolução</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.performance_indicators.avg_resolution_time}h</div>
              <p className="text-xs text-muted-foreground">
                Baseado em {summary.overview.categories_count} categorias
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Eficiência dos Grupos</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.performance_indicators.avg_group_efficiency}%</div>
              <p className="text-xs text-muted-foreground">
                {summary.overview.groups_count} grupos técnicos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Categorias Críticas</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {summary.performance_indicators.critical_categories}
              </div>
              <p className="text-xs text-muted-foreground">
                {summary.performance_indicators.high_priority_categories} alta prioridade
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alertas e Recomendações */}
      {summary && summary.alerts.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                Alertas do Sistema
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {summary.alerts.map((alert, index) => (
                <Alert key={index} variant={alert.type === 'warning' ? 'default' : 'destructive'}>
                  <AlertDescription className="flex items-center justify-between">
                    <span>{alert.message}</span>
                    <Badge variant={alert.priority === 'Alta' ? 'destructive' : 'secondary'}>
                      {alert.priority}
                    </Badge>
                  </AlertDescription>
                </Alert>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                Recomendações
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {summary.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Conteúdo Principal em Abas */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="categories">Categorias</TabsTrigger>
          <TabsTrigger value="groups">Grupos Técnicos</TabsTrigger>
          <TabsTrigger value="analytics">Análises</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {metrics && <MaintenanceMetricsGrid metrics={metrics} onFilterByStatus={handleFilterByStatus} />}
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          {categories && <MaintenanceCategoriesChart data={categories} />}
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          {groups && <TechnicalGroupsAnalysis data={groups} />}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Análise de Tendências */}
            <Card>
              <CardHeader>
                <CardTitle>Análise de Tendências</CardTitle>
              </CardHeader>
              <CardContent>
                {metrics && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {metrics.tendencias.resolvidos}
                        </div>
                        <div className="text-sm text-gray-600">Tickets Resolvidos</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {metrics.tendencias.novos}
                        </div>
                        <div className="text-sm text-gray-600">Novos Tickets</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-amber-600">
                          {metrics.tendencias.progresso}
                        </div>
                        <div className="text-sm text-gray-600">Em Progresso</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">
                          {metrics.tendencias.pendentes}
                        </div>
                        <div className="text-sm text-gray-600">Pendentes</div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Contexto de Manutenção */}
            <Card>
              <CardHeader>
                <CardTitle>Contexto de Manutenção</CardTitle>
              </CardHeader>
              <CardContent>
                {metrics && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total de Categorias:</span>
                      <span className="font-semibold">{metrics.maintenance_context.total_categories}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Categorias Críticas:</span>
                      <span className="font-semibold text-red-600">
                        {metrics.maintenance_context.critical_categories}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Tempo Médio de Resolução:</span>
                      <span className="font-semibold">
                        {metrics.maintenance_context.avg_resolution_time}h
                      </span>
                    </div>
                    {metrics.technical_groups_summary && (
                      <>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Total de Grupos:</span>
                          <span className="font-semibold">
                            {metrics.technical_groups_summary.total_groups}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Meta de Eficiência Média:</span>
                          <span className="font-semibold">
                            {metrics.technical_groups_summary.avg_efficiency_target}%
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Footer com informações de atualização */}
      <div className="text-center text-sm text-gray-500 pt-4 border-t">
        Última atualização: {summary ? new Date(summary.timestamp).toLocaleString('pt-BR') : 'N/A'}
      </div>
    </div>
  );
};

export default MaintenanceDashboard;