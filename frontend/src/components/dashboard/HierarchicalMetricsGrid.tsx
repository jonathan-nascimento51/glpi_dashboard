import React, { useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { KPICard } from './KPICard';
import { MetricsData, TicketStatus } from '@/types';
import { Ticket, Clock, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';
import { usePerformanceMonitoring, useRenderTracker } from '../../hooks/usePerformanceMonitoring';
import { performanceMonitor } from '../../utils/performanceMonitor';
import { useThrottledCallback } from '../../hooks/useDebounce';

interface HierarchicalMetricsGridProps {
  metrics: MetricsData;
  onFilterByStatus?: (status: TicketStatus) => void;
  className?: string;
}

// Funções auxiliares
function getTrendDirection(trend?: string): 'up' | 'down' | 'stable' {
  if (!trend) return 'stable';
  const value = parseFloat(trend.replace('%', '').replace('+', ''));
  if (value > 0) return 'up';
  if (value < 0) return 'down';
  return 'stable';
}

function parseTrendValue(trend?: string): number {
  if (!trend) return 0;
  return Math.abs(parseFloat(trend.replace('%', '').replace('+', '')));
}

// Função para determinar prioridade baseada no valor e tendência
function getKPIPriority(value: number, trend?: { direction: 'up' | 'down' | 'stable'; value: number }): 'critical' | 'high' | 'normal' | 'low' {
  // Tickets pendentes com tendência de alta são críticos
  if (value > 50 && trend?.direction === 'up' && trend.value > 20) {
    return 'critical';
  }
  
  // Valores altos são de alta prioridade
  if (value > 100) {
    return 'high';
  }
  
  // Tendências negativas em tickets resolvidos são preocupantes
  if (trend?.direction === 'down' && trend.value > 15) {
    return 'high';
  }
  
  return 'normal';
}

// Função para determinar tamanho baseado na importância do KPI
function getKPISize(status: TicketStatus, value: number): 'small' | 'medium' | 'large' | 'hero' {
  // Tickets pendentes são o KPI mais crítico
  if (status === 'pending' && value > 0) {
    return 'hero';
  }
  
  // Tickets novos e em progresso são importantes
  if ((status === 'new' || status === 'progress') && value > 20) {
    return 'large';
  }
  
  // Tickets resolvidos são importantes mas menos críticos
  if (status === 'resolved') {
    return 'medium';
  }
  
  return 'medium';
}

// Variantes de animação
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut' as const,
    },
  },
} as const;

export const HierarchicalMetricsGrid = React.memo<HierarchicalMetricsGridProps>(function HierarchicalMetricsGrid({
  metrics,
  onFilterByStatus,
  className,
}) {
  const { measureRender } = usePerformanceMonitoring('HierarchicalMetricsGrid');
  const { trackRender } = useRenderTracker('HierarchicalMetricsGrid');

  useEffect(() => {
    trackRender();
    measureRender(() => {
      performanceMonitor.markComponentRender('HierarchicalMetricsGrid', {
        hasMetrics: !!metrics,
        metricsKeys: metrics ? Object.keys(metrics).length : 0,
      });
    });
  }, [metrics, trackRender, measureRender]);

  // Verificação de segurança
  if (!metrics) {
    return (
      <div className='grid grid-cols-4 grid-rows-2 gap-4 h-96'>
        {[...Array(6)].map((_, i) => (
          <div key={i} className='figma-glass-card animate-pulse rounded-lg' />
        ))}
      </div>
    );
  }

  // Callbacks throttled para os cliques
  const handleNewClick = useThrottledCallback(
    useCallback(() => {
      performanceMonitor.startMeasure('filter-click-new');
      onFilterByStatus?.('new');
      performanceMonitor.endMeasure('filter-click-new');
    }, [onFilterByStatus]),
    500
  );

  const handleProgressClick = useThrottledCallback(
    useCallback(() => {
      performanceMonitor.startMeasure('filter-click-progress');
      onFilterByStatus?.('progress');
      performanceMonitor.endMeasure('filter-click-progress');
    }, [onFilterByStatus]),
    500
  );

  const handlePendingClick = useThrottledCallback(
    useCallback(() => {
      performanceMonitor.startMeasure('filter-click-pending');
      onFilterByStatus?.('pending');
      performanceMonitor.endMeasure('filter-click-pending');
    }, [onFilterByStatus]),
    500
  );

  const handleResolvedClick = useThrottledCallback(
    useCallback(() => {
      performanceMonitor.startMeasure('filter-click-resolved');
      onFilterByStatus?.('resolved');
      performanceMonitor.endMeasure('filter-click-resolved');
    }, [onFilterByStatus]),
    500
  );

  // Configuração dos KPIs com hierarquia
  const kpiCards = useMemo(() => {
    const cards = [
      {
        title: 'Pendentes',
        value: metrics.pendentes || 0,
        status: 'pending' as const,
        icon: AlertTriangle,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.pendentes),
          value: parseTrendValue(metrics.tendencias?.pendentes),
          label: 'vs. período anterior',
        },
        onClick: handlePendingClick,
        size: getKPISize('pending', metrics.pendentes || 0),
        priority: getKPIPriority(metrics.pendentes || 0, {
          direction: getTrendDirection(metrics.tendencias?.pendentes),
          value: parseTrendValue(metrics.tendencias?.pendentes),
        }),
      },
      {
        title: 'Novos',
        value: metrics.novos || 0,
        status: 'new' as const,
        icon: Ticket,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.novos),
          value: parseTrendValue(metrics.tendencias?.novos),
          label: 'vs. período anterior',
        },
        onClick: handleNewClick,
        size: getKPISize('new', metrics.novos || 0),
        priority: getKPIPriority(metrics.novos || 0, {
          direction: getTrendDirection(metrics.tendencias?.novos),
          value: parseTrendValue(metrics.tendencias?.novos),
        }),
      },
      {
        title: 'Em Progresso',
        value: metrics.progresso || 0,
        status: 'progress' as const,
        icon: Clock,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.progresso),
          value: parseTrendValue(metrics.tendencias?.progresso),
          label: 'vs. período anterior',
        },
        onClick: handleProgressClick,
        size: getKPISize('progress', metrics.progresso || 0),
        priority: getKPIPriority(metrics.progresso || 0, {
          direction: getTrendDirection(metrics.tendencias?.progresso),
          value: parseTrendValue(metrics.tendencias?.progresso),
        }),
      },
      {
        title: 'Resolvidos',
        value: metrics.resolvidos || 0,
        status: 'resolved' as const,
        icon: CheckCircle,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.resolvidos),
          value: parseTrendValue(metrics.tendencias?.resolvidos),
          label: 'vs. período anterior',
        },
        onClick: handleResolvedClick,
        size: getKPISize('resolved', metrics.resolvidos || 0),
        priority: getKPIPriority(metrics.resolvidos || 0, {
          direction: getTrendDirection(metrics.tendencias?.resolvidos),
          value: parseTrendValue(metrics.tendencias?.resolvidos),
        }),
      },
    ];

    // Ordenar por prioridade (crítico primeiro)
    return cards.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, normal: 2, low: 3 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }, [metrics, handleNewClick, handleProgressClick, handlePendingClick, handleResolvedClick]);

  // KPI de total como card adicional
  const totalCard = useMemo(() => {
    const total = (metrics.novos || 0) + (metrics.progresso || 0) + (metrics.pendentes || 0) + (metrics.resolvidos || 0);
    return {
      title: 'Total de Tickets',
      value: total,
      status: 'total' as const,
      icon: TrendingUp,
      trend: {
        direction: 'stable' as const,
        value: 0,
        label: 'total geral',
      },
      onClick: () => {},
      size: 'medium' as const,
      priority: 'normal' as const,
    };
  }, [metrics]);

  return (
    <motion.div
      variants={containerVariants}
      initial='hidden'
      animate='visible'
      className={`grid grid-cols-4 grid-rows-3 gap-4 h-auto ${className || ''}`}
    >
      {/* Renderizar KPIs principais com hierarquia */}
      {kpiCards.map((card, index) => (
        <motion.div key={`kpi-${card.status}`} variants={itemVariants}>
          <KPICard
            title={card.title}
            value={card.value}
            status={card.status}
            icon={card.icon}
            trend={card.trend}
            size={card.size}
            priority={card.priority}
            onClick={card.onClick}
            className='h-full'
          />
        </motion.div>
      ))}
      
      {/* Card de total */}
      <motion.div variants={itemVariants}>
        <KPICard
          title={totalCard.title}
          value={totalCard.value}
          status={totalCard.status}
          icon={totalCard.icon}
          trend={totalCard.trend}
          size={totalCard.size}
          priority={totalCard.priority}
          onClick={totalCard.onClick}
          className='h-full'
        />
      </motion.div>
    </motion.div>
  );
});