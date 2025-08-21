import React, { useEffect, useMemo, Suspense, useState } from 'react';
import { motion } from 'framer-motion';
import { HierarchicalMetricsGrid } from './HierarchicalMetricsGrid';
import { LevelMetricsGrid } from './LevelMetricsGrid';

// Componentes lazy centralizados
import {
  LazyNewTicketsList,
  LazyRankingTable,
  ListSkeleton,
  TableSkeleton,
} from '../LazyComponents';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import RequestMonitorDashboard from '../RequestMonitorDashboard';

import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking } from '@/types';
import { cn } from '@/lib/utils';
import { usePerformanceMonitoring } from '@/hooks/usePerformanceMonitoring';
import { performanceMonitor } from '../../utils/performanceMonitor';

interface ModernDashboardProps {
  metrics: MetricsData;
  levelMetrics?: any;
  systemStatus?: SystemStatus | null;
  technicianRanking?: TechnicianRanking[];
  onFilterByStatus?: (status: TicketStatus) => void;
  isLoading?: boolean;
  className?: string;
  filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
  };
}

// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.01,
      delayChildren: 0,
    },
  },
} as const;

const itemVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.05,
      ease: 'easeOut' as const,
    },
  },
} as const;

// Componente SkeletonCard memoizado
const SkeletonCard = React.memo(function SkeletonCard() {
  return (
    <Card className='figma-glass-card shadow-none'>
      <CardHeader className='pb-2'>
        <div className='flex items-center justify-between'>
          <div className='h-4 figma-glass-card rounded animate-pulse w-20' />
          <div className='h-8 w-8 figma-glass-card rounded-full animate-pulse' />
        </div>
      </CardHeader>
      <CardContent>
        <div className='space-y-3'>
          <div className='h-8 figma-glass-card rounded animate-pulse w-16' />
          <div className='h-3 figma-glass-card rounded animate-pulse w-24' />
        </div>
      </CardContent>
    </Card>
  );
});

export const ModernDashboard = React.memo<ModernDashboardProps>(function ModernDashboard({
  metrics,
  levelMetrics,
  systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  isLoading = false,
  className,
  filters,
}) {
  // Estado para monitorar se o monitor está minimizado
  const [isMonitorMinimized, setIsMonitorMinimized] = useState(() => {
    const saved = localStorage.getItem('requestMonitorMinimized');
    return saved ? JSON.parse(saved) : false;
  });

  // Escutar mudanças no localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('requestMonitorMinimized');
      setIsMonitorMinimized(saved ? JSON.parse(saved) : false);
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Também escutar mudanças diretas no localStorage
    const interval = setInterval(() => {
      const saved = localStorage.getItem('requestMonitorMinimized');
      const currentState = saved ? JSON.parse(saved) : false;
      if (currentState !== isMonitorMinimized) {
        setIsMonitorMinimized(currentState);
      }
    }, 100);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [isMonitorMinimized]);

  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('ModernDashboard');

  // Track component renders
  useEffect(() => {
    measureRender(() => {
      performanceMonitor.markComponentRender('ModernDashboard', {
        metricsCount: Object.keys(metrics || {}).length,
        technicianCount: technicianRanking.length,
        isLoading,
      });
    });
  }, [metrics, technicianRanking, isLoading, measureRender]);

  // Memoizar dados do ranking processados
  const processedRankingData = useMemo(() => {
    const result = technicianRanking.map(tech => ({
      id: tech.id || String(tech.name),
      name: tech.name || tech.nome || 'Técnico',
      level: tech.level || 'N1',
      total: tech.total || tech.total_tickets || 0,
      rank: tech.rank || 0,
    }));

    return result;
  }, [technicianRanking]);

  // Loading state
  if (isLoading) {
    return (
      <div className='space-y-6 p-6 min-h-screen'>
        {/* Header skeleton */}
        <div className='flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4'>
          <div className='space-y-2'>
            <div className='h-8 figma-glass-card rounded animate-pulse w-64' />
            <div className='h-4 figma-glass-card rounded animate-pulse w-48' />
          </div>
          <div className='flex items-center gap-3'>
            <div className='h-10 figma-glass-card rounded animate-pulse w-32' />
            <div className='h-10 figma-glass-card rounded animate-pulse w-24' />
          </div>
        </div>

        {/* Metrics skeleton */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
          {[...Array(4)].map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>

        {/* Charts skeleton */}
        <div className='grid grid-cols-1 xl:grid-cols-3 gap-6'>
          <div className='xl:col-span-2'>
            <Card className='figma-glass-card shadow-none'>
              <CardHeader>
                <div className='h-6 figma-glass-card rounded animate-pulse w-40' />
              </CardHeader>
              <CardContent>
                <div className='h-64 figma-glass-card rounded animate-pulse' />
              </CardContent>
            </Card>
          </div>
          <div className='space-y-4'>
            {[...Array(3)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial='hidden'
      animate='visible'
      className={cn(
        isMonitorMinimized 
          ? 'dashboard-fullscreen-container-minimized' 
          : 'dashboard-fullscreen-container', 
        className
      )}
    >
      {/* Cards de métricas principais */}
      <motion.div variants={itemVariants} className='dashboard-metrics-section'>
        <HierarchicalMetricsGrid metrics={metrics} onFilterByStatus={onFilterByStatus} />
      </motion.div>

      {/* Layout principal com métricas por nível e tickets novos */}
      <div className='dashboard-main-grid'>
        {/* Métricas por nível de atendimento - ocupando 2 colunas */}
        <motion.div variants={itemVariants} className='dashboard-levels-section'>
          <LevelMetricsGrid metrics={{ niveis: levelMetrics }} className='h-full' />
        </motion.div>

        {/* Lista de tickets novos - ocupando 1 coluna */}
        <motion.div variants={itemVariants} className='dashboard-tickets-section'>
          <Suspense fallback={<ListSkeleton />}>
            <LazyNewTicketsList className='h-full' limit={6} />
          </Suspense>
        </motion.div>
      </div>

      {/* Layout inferior com ranking e monitor de requisições */}
      <div className={isMonitorMinimized ? 'dashboard-bottom-grid-minimized' : 'dashboard-bottom-grid'}>
        {/* Ranking de técnicos */}
        <motion.div variants={itemVariants} className='dashboard-ranking-section'>
          <Suspense fallback={<TableSkeleton />}>
            <LazyRankingTable
              data={processedRankingData}
              title='Ranking de Técnicos'
              className='w-full h-full'
              filters={filters}
            />
          </Suspense>
        </motion.div>

        {/* Monitor de requisições - só renderizar se não estiver minimizado */}
        {!isMonitorMinimized && (
          <motion.div variants={itemVariants} className='dashboard-monitor-section'>
            <RequestMonitorDashboard className='h-full' />
          </motion.div>
        )}
      </div>
      
      {/* Renderizar o monitor minimizado se necessário */}
      {isMonitorMinimized && <RequestMonitorDashboard />}
    </motion.div>
  );
});
