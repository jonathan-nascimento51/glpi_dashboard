import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { InteractiveChart } from './InteractiveChart';
import { LazyInteractiveChart } from '../LazyComponents';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart3, PieChart, TrendingUp, MousePointer } from 'lucide-react';
import { cn } from '@/lib/utils';

// Dados de exemplo para demonstração
const sampleData = [
  {
    name: 'Jan',
    novos: 45,
    progresso: 32,
    pendentes: 18,
    resolvidos: 89,
  },
  {
    name: 'Fev',
    novos: 52,
    progresso: 28,
    pendentes: 22,
    resolvidos: 95,
  },
  {
    name: 'Mar',
    novos: 38,
    progresso: 35,
    pendentes: 15,
    resolvidos: 102,
  },
  {
    name: 'Abr',
    novos: 61,
    progresso: 42,
    pendentes: 28,
    resolvidos: 87,
  },
  {
    name: 'Mai',
    novos: 49,
    progresso: 31,
    pendentes: 19,
    resolvidos: 98,
  },
];

interface ChartDashboardExampleProps {
  className?: string;
}

/**
 * Componente de exemplo demonstrando o uso do sistema de drill-down em gráficos
 * Mostra diferentes tipos de gráficos com funcionalidades interativas
 */
export const ChartDashboardExample: React.FC<ChartDashboardExampleProps> = ({ className }) => {
  const [selectedChartType, setSelectedChartType] = useState<'area' | 'bar' | 'pie'>('area');
  const [drillDownType, setDrillDownType] = useState<'status' | 'category' | 'technician' | 'priority'>('status');
  const [enableDrillDown, setEnableDrillDown] = useState(true);

  const chartVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const totalTickets = useMemo(() => {
    return sampleData.reduce((acc, item) => {
      return acc + item.novos + item.progresso + item.pendentes + item.resolvidos;
    }, 0);
  }, []);

  const averageResolution = useMemo(() => {
    const totalResolved = sampleData.reduce((acc, item) => acc + item.resolvidos, 0);
    return ((totalResolved / totalTickets) * 100).toFixed(1);
  }, [totalTickets]);

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header com controles */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Sistema de Drill-Down em Gráficos
          </CardTitle>
          <div className="flex flex-wrap gap-4 mt-4">
            {/* Controle de tipo de gráfico */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Tipo:</span>
              <Tabs value={selectedChartType} onValueChange={(value) => setSelectedChartType(value as any)}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="area" className="text-xs">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    Área
                  </TabsTrigger>
                  <TabsTrigger value="bar" className="text-xs">
                    <BarChart3 className="h-3 w-3 mr-1" />
                    Barras
                  </TabsTrigger>
                  <TabsTrigger value="pie" className="text-xs">
                    <PieChart className="h-3 w-3 mr-1" />
                    Pizza
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            {/* Controle de drill-down */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Drill-down:</span>
              <Tabs value={drillDownType} onValueChange={(value) => setDrillDownType(value as any)}>
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="status" className="text-xs">Status</TabsTrigger>
                  <TabsTrigger value="category" className="text-xs">Categoria</TabsTrigger>
                  <TabsTrigger value="technician" className="text-xs">Técnico</TabsTrigger>
                  <TabsTrigger value="priority" className="text-xs">Prioridade</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            {/* Toggle de interatividade */}
            <Button
              variant={enableDrillDown ? "default" : "outline"}
              size="sm"
              onClick={() => setEnableDrillDown(!enableDrillDown)}
              className="flex items-center gap-2"
            >
              <MousePointer className="h-3 w-3" />
              {enableDrillDown ? 'Interativo' : 'Estático'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{totalTickets}</div>
              <div className="text-sm text-blue-700">Total de Tickets</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{averageResolution}%</div>
              <div className="text-sm text-green-700">Taxa de Resolução</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{sampleData.length}</div>
              <div className="text-sm text-purple-700">Períodos</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Gráfico principal com drill-down */}
      <motion.div
        variants={chartVariants}
        initial="hidden"
        animate="visible"
        transition={{ duration: 0.5 }}
      >
        <InteractiveChart
          data={sampleData}
          type={selectedChartType}
          title={`Evolução dos Tickets - ${selectedChartType === 'area' ? 'Área' : selectedChartType === 'bar' ? 'Barras' : 'Pizza'}`}
          enableDrillDown={enableDrillDown}
          drillDownType={drillDownType}
          showInteractiveIndicator={enableDrillDown}
          className="h-96"
        />
      </motion.div>

      {/* Grid com múltiplos gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          variants={chartVariants}
          initial="hidden"
          animate="visible"
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <InteractiveChart
            data={sampleData}
            type="bar"
            title="Tickets por Status (Barras)"
            enableDrillDown={enableDrillDown}
            drillDownType="status"
            showInteractiveIndicator={enableDrillDown}
          />
        </motion.div>

        <motion.div
          variants={chartVariants}
          initial="hidden"
          animate="visible"
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <InteractiveChart
            data={sampleData}
            type="pie"
            title="Distribuição Atual (Pizza)"
            enableDrillDown={enableDrillDown}
            drillDownType="category"
            showInteractiveIndicator={enableDrillDown}
          />
        </motion.div>
      </div>

      {/* Informações sobre drill-down */}
      {enableDrillDown && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Como usar o Drill-Down</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Badge variant="outline" className="mt-1">1</Badge>
                <div>
                  <p className="font-medium">Clique nos elementos do gráfico</p>
                  <p className="text-sm text-gray-600">Barras, fatias ou áreas são clicáveis quando o drill-down está ativo</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Badge variant="outline" className="mt-1">2</Badge>
                <div>
                  <p className="font-medium">Navegação automática</p>
                  <p className="text-sm text-gray-600">O sistema navega para páginas de detalhe com filtros aplicados</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Badge variant="outline" className="mt-1">3</Badge>
                <div>
                  <p className="font-medium">Indicadores visuais</p>
                  <p className="text-sm text-gray-600">Badges e ícones aparecem ao passar o mouse sobre gráficos interativos</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ChartDashboardExample;