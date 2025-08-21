import React, { useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { TrendingUp, BarChart3, PieChart as PieChartIcon, MousePointer } from 'lucide-react';
import { useChartNavigation, createDrillDownData } from '@/hooks/useChartNavigation';

interface ChartData {
  name: string;
  novos: number;
  progresso: number;
  pendentes: number;
  resolvidos: number;
  total?: number;
}

interface TicketChartProps {
  data: ChartData[];
  type?: 'area' | 'bar' | 'pie';
  title?: string;
  className?: string;
  enableDrillDown?: boolean;
}

const COLORS = {
  novos: '#3B82F6',
  progresso: '#F59E0B',
  pendentes: '#EF4444',
  resolvidos: '#10B981',
};

const PIE_COLORS = ['#3B82F6', '#F59E0B', '#EF4444', '#10B981'];

// Variantes de animação movidas para fora do componente para evitar recriação
const chartVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut' as const,
    },
  },
} as const;

// Configurações de margem memoizadas
const chartMargins = {
  top: 20,
  right: 30,
  left: 20,
  bottom: 5,
};

export const TicketChart = React.memo<TicketChartProps>(function TicketChart({
  data,
  type = 'area',
  title = 'Evolução dos Tickets',
  className,
  enableDrillDown = true,
}) {
  const { createClickHandler, isClickable } = useChartNavigation();
  // Tooltip customizado memoizado
  const CustomTooltip = useCallback(({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className='figma-glass-card rounded-lg p-3 shadow-none'>
          <p className='figma-body font-medium'>{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={`tooltip-entry-${index}`} className='text-sm' style={{ color: entry.color }}>
              {entry.name}: <span className='font-semibold'>{typeof entry.value === 'object' ? JSON.stringify(entry.value) : entry.value}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  }, []);

  // Dados do gráfico de pizza memoizados
  const pieData = useMemo(() => {
    if (data.length === 0) return [];
    const lastDataPoint = data[data.length - 1];
    return [
      { name: 'Novos', value: lastDataPoint.novos, color: COLORS.novos },
      { name: 'Em Progresso', value: lastDataPoint.progresso, color: COLORS.progresso },
      { name: 'Pendentes', value: lastDataPoint.pendentes, color: COLORS.pendentes },
      { name: 'Resolvidos', value: lastDataPoint.resolvidos, color: COLORS.resolvidos },
    ];
  }, [data]);

  // Ícone do gráfico memoizado
  const chartIcon = useMemo(() => {
    switch (type) {
      case 'bar':
        return <BarChart3 className='h-5 w-5' />;
      case 'pie':
        return <PieChartIcon className='h-5 w-5' />;
      default:
        return <TrendingUp className='h-5 w-5' />;
    }
  }, [type]);

  // Label do tipo de gráfico memoizado
  const typeLabel = useMemo(() => {
    switch (type) {
      case 'area':
        return 'Área';
      case 'bar':
        return 'Barras';
      case 'pie':
        return 'Pizza';
      default:
        return 'Área';
    }
  }, [type]);

  // Handlers de clique para drill-down
  const handleBarClick = useCallback(
    (data: any, index: number) => {
      if (!enableDrillDown) return;
      
      const clickHandler = createClickHandler('status', {
        filters: { period: data.name },
        metadata: { chartType: 'bar', dataIndex: index },
      });
      clickHandler(data);
    },
    [enableDrillDown, createClickHandler]
  );

  const handlePieClick = useCallback(
    (data: any, index: number) => {
      if (!enableDrillDown) return;
      
      const statusMap: Record<string, string> = {
        'Novos': 'new',
        'Em Progresso': 'progress', 
        'Pendentes': 'pending',
        'Resolvidos': 'resolved',
      };
      
      const clickHandler = createClickHandler('status', {
        name: statusMap[data.name] || data.name,
        filters: { status: statusMap[data.name] || data.name },
        metadata: { chartType: 'pie', dataIndex: index },
      });
      clickHandler(data);
    },
    [enableDrillDown, createClickHandler]
  );

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width='100%' height={300}>
            <BarChart 
              data={data} 
              margin={chartMargins}
              onClick={enableDrillDown ? handleBarClick : undefined}
            >
              <CartesianGrid strokeDasharray='3 3' stroke='#f0f0f0' />
              <XAxis
                dataKey='name'
                stroke='#6b7280'
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis stroke='#6b7280' fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar 
                dataKey='novos' 
                fill={COLORS.novos} 
                name='Novos' 
                radius={[2, 2, 0, 0]}
                className={enableDrillDown ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
              />
              <Bar
                dataKey='progresso'
                fill={COLORS.progresso}
                name='Em Progresso'
                radius={[2, 2, 0, 0]}
                className={enableDrillDown ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
              />
              <Bar
                dataKey='pendentes'
                fill={COLORS.pendentes}
                name='Pendentes'
                radius={[2, 2, 0, 0]}
                className={enableDrillDown ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
              />
              <Bar
                dataKey='resolvidos'
                fill={COLORS.resolvidos}
                name='Resolvidos'
                radius={[2, 2, 0, 0]}
                className={enableDrillDown ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width='100%' height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx='50%'
                cy='50%'
                innerRadius={60}
                outerRadius={120}
                paddingAngle={2}
                dataKey='value'
                onClick={enableDrillDown ? handlePieClick : undefined}
                className={enableDrillDown ? 'cursor-pointer' : ''}
              >
                {pieData.map((_, index) => (
                  <Cell 
                    key={`pie-cell-${index}`} 
                    fill={PIE_COLORS[index % PIE_COLORS.length]}
                    className={enableDrillDown ? 'hover:opacity-80 transition-opacity' : ''}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      default: // area
        return (
          <ResponsiveContainer width='100%' height={300}>
            <AreaChart 
              data={data} 
              margin={chartMargins}
              onClick={enableDrillDown ? handleBarClick : undefined}
              className={enableDrillDown ? 'cursor-pointer' : ''}
            >
              <defs>
                <linearGradient id='colorNovos' x1='0' y1='0' x2='0' y2='1'>
                  <stop offset='5%' stopColor={COLORS.novos} stopOpacity={0.3} />
                  <stop offset='95%' stopColor={COLORS.novos} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id='colorProgresso' x1='0' y1='0' x2='0' y2='1'>
                  <stop offset='5%' stopColor={COLORS.progresso} stopOpacity={0.3} />
                  <stop offset='95%' stopColor={COLORS.progresso} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id='colorPendentes' x1='0' y1='0' x2='0' y2='1'>
                  <stop offset='5%' stopColor={COLORS.pendentes} stopOpacity={0.3} />
                  <stop offset='95%' stopColor={COLORS.pendentes} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id='colorResolvidos' x1='0' y1='0' x2='0' y2='1'>
                  <stop offset='5%' stopColor={COLORS.resolvidos} stopOpacity={0.3} />
                  <stop offset='95%' stopColor={COLORS.resolvidos} stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray='3 3' stroke='#f0f0f0' />
              <XAxis
                dataKey='name'
                stroke='#6b7280'
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis stroke='#6b7280' fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type='monotone'
                dataKey='novos'
                stackId='1'
                stroke={COLORS.novos}
                fill='url(#colorNovos)'
                name='Novos'
                className={enableDrillDown ? 'hover:opacity-80 transition-opacity' : ''}
              />
              <Area
                type='monotone'
                dataKey='progresso'
                stackId='1'
                stroke={COLORS.progresso}
                fill='url(#colorProgresso)'
                name='Em Progresso'
                className={enableDrillDown ? 'hover:opacity-80 transition-opacity' : ''}
              />
              <Area
                type='monotone'
                dataKey='pendentes'
                stackId='1'
                stroke={COLORS.pendentes}
                fill='url(#colorPendentes)'
                name='Pendentes'
                className={enableDrillDown ? 'hover:opacity-80 transition-opacity' : ''}
              />
              <Area
                type='monotone'
                dataKey='resolvidos'
                stackId='1'
                stroke={COLORS.resolvidos}
                fill='url(#colorResolvidos)'
                name='Resolvidos'
                className={enableDrillDown ? 'hover:opacity-80 transition-opacity' : ''}
              />
            </AreaChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <motion.div variants={chartVariants} initial='hidden' animate='visible' className={className}>
      <Card className={cn('figma-glass-card border-0 shadow-none', enableDrillDown && 'hover:shadow-md transition-shadow')}>
        <CardHeader>
          <div className='flex items-center justify-between'>
            <CardTitle className='figma-heading-large flex items-center gap-2'>
              {chartIcon}
              {title}
              {enableDrillDown && (
                <MousePointer className='h-4 w-4 text-muted-foreground' title='Clique para navegar' />
              )}
            </CardTitle>
            <div className='flex gap-2'>
              <Badge variant='outline' className='text-xs'>
                {typeLabel}
              </Badge>
              {enableDrillDown && (
                <Badge variant='outline' className='text-xs'>
                  Interativo
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent>{renderChart()}</CardContent>
      </Card>
    </motion.div>
  );
});
