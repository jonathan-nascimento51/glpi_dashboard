import React, { useEffect, useCallback, useMemo } from "react"
import { motion } from "framer-motion"
import { StatusCard } from "./StatusCard"
import { MetricsData, TicketStatus } from "@/types"
import { Ticket, Clock, AlertTriangle, CheckCircle } from "lucide-react"
import { usePerformanceMonitoring, useRenderTracker } from "../../hooks/usePerformanceMonitoring"
import { performanceMonitor } from "../../utils/performanceMonitor"
import { useThrottledCallback } from "../../hooks/useDebounce"

interface MetricsGridProps {
  metrics: MetricsData
  onFilterByStatus?: (status: TicketStatus) => void
  className?: string
}

// Funções auxiliares movidas para fora do componente
function getTrendDirection(trend?: string): 'up' | 'down' | 'stable' {
  if (!trend) return 'stable'
  const value = parseFloat(trend.replace('%', '').replace('+', ''))
  if (value > 0) return 'up'
  if (value < 0) return 'down'
  return 'stable'
}

function parseTrendValue(trend?: string): number {
  if (!trend) return 0
  return Math.abs(parseFloat(trend.replace('%', '').replace('+', '')))
}

// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.02,
      delayChildren: 0
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.1,
      ease: "easeOut"
    }
  }
}

export const MetricsGrid = React.memo<MetricsGridProps>(function MetricsGrid({
  metrics,
  onFilterByStatus,
  className
}) {
  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('MetricsGrid')
  const { trackRender } = useRenderTracker('MetricsGrid')
  
  // Track component renders
  useEffect(() => {
    // Log DETALHADO das props recebidas para depuração - APÓS CORREÇÃO DO CACHE
    // console.log('🔍 MetricsGrid - Props recebidas COMPLETAS (APÓS CORREÇÃO):', {
    //   metrics,
    //   hasMetrics: !!metrics,
    //   metricsType: typeof metrics,
    //   metricsKeys: metrics ? Object.keys(metrics) : [],
    //   metricsValues: metrics ? {
    //     novos: metrics.novos,
    //     pendentes: metrics.pendentes,
    //     progresso: metrics.progresso,
    //     resolvidos: metrics.resolvidos,
    //     total: metrics.total,
    //     niveis: metrics.niveis,
    //     tendencias: metrics.tendencias
    //   } : 'METRICS É NULL/UNDEFINED',
    //   onFilterByStatus: !!onFilterByStatus
    // });
    
    // Log específico dos valores que deveriam aparecer nos cards
    if (metrics) {
      // console.log('📊 MetricsGrid - VALORES DOS CARDS (APÓS CORREÇÃO):', {
      //   'Card Novos': metrics.novos,
      //   'Card Pendentes': metrics.pendentes,
      //   'Card Em Progresso': metrics.progresso,
      //   'Card Resolvidos': metrics.resolvidos,
      //   'Total Calculado': metrics.total
      // });
      
      // Verificar se os valores são válidos
      if (metrics.novos === undefined || metrics.pendentes === undefined || 
          metrics.progresso === undefined || metrics.resolvidos === undefined) {
        // console.error('❌ MetricsGrid - ALGUNS VALORES SÃO UNDEFINED!');
      } else {
        // console.log('✅ MetricsGrid - TODOS OS VALORES SÃO VÁLIDOS!');
      }
    } else {
      // console.error('❌ MetricsGrid - METRICS É NULL/UNDEFINED - Cards ficarão zerados!');
    }
    
    trackRender()
    measureRender(() => {
      performanceMonitor.markComponentRender('MetricsGrid', {
        hasMetrics: !!metrics,
        metricsKeys: metrics ? Object.keys(metrics).length : 0
      })
    })
  }, [metrics, trackRender, measureRender, onFilterByStatus])
  
  // Componente renderizado com métricas válidas

  // Verificação de segurança
  if (!metrics) {
    // console.log('⚠️ MetricsGrid - Metrics é null/undefined, mostrando skeleton')
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 figma-glass-card animate-pulse rounded-lg" />
        ))}
      </div>
    )
  }

  // Callbacks memoizados para os cliques com throttle
  const handleNewClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-new')
    onFilterByStatus?.("new")
    performanceMonitor.endMeasure('filter-click-new', 'Filter by New Status')
  }, [onFilterByStatus])

  const handleProgressClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-progress')
    onFilterByStatus?.("progress")
    performanceMonitor.endMeasure('filter-click-progress', 'Filter by Progress Status')
  }, [onFilterByStatus])

  const handlePendingClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-pending')
    onFilterByStatus?.("pending")
    performanceMonitor.endMeasure('filter-click-pending', 'Filter by Pending Status')
  }, [onFilterByStatus])

  const handleResolvedClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-resolved')
    onFilterByStatus?.("resolved")
    performanceMonitor.endMeasure('filter-click-resolved', 'Filter by Resolved Status')
  }, [onFilterByStatus])

  // Throttled versions to prevent rapid clicks
  const handleNewClick = useThrottledCallback(handleNewClickImmediate, 500)
  const handleProgressClick = useThrottledCallback(handleProgressClickImmediate, 500)
  const handlePendingClick = useThrottledCallback(handlePendingClickImmediate, 500)
  const handleResolvedClick = useThrottledCallback(handleResolvedClickImmediate, 500)

  // Configuração dos cards de métricas memoizada
  const metricCards = useMemo(() => {
    const cards = [
      {
        title: "Novos",
        value: metrics.novos || 0,
        status: "new" as const,
        icon: Ticket,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.novos),
          value: parseTrendValue(metrics.tendencias?.novos),
          label: "vs. período anterior"
        },
        onClick: handleNewClick
      },
      {
        title: "Em Progresso",
        value: metrics.progresso || 0,
        status: "progress" as const,
        icon: Clock,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.progresso),
          value: parseTrendValue(metrics.tendencias?.progresso),
          label: "vs. período anterior"
        },
        onClick: handleProgressClick
      },
      {
        title: "Pendentes",
        value: metrics.pendentes || 0,
        status: "pending" as const,
        icon: AlertTriangle,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.pendentes),
          value: parseTrendValue(metrics.tendencias?.pendentes),
          label: "vs. período anterior"
        },
        onClick: handlePendingClick
      },
      {
        title: "Resolvidos",
        value: metrics.resolvidos || 0,
        status: "resolved" as const,
        icon: CheckCircle,
        trend: {
          direction: getTrendDirection(metrics.tendencias?.resolvidos),
          value: parseTrendValue(metrics.tendencias?.resolvidos),
          label: "vs. período anterior"
        },
        onClick: handleResolvedClick
      }
    ]
    
    return cards
  }, [metrics, handleNewClick, handleProgressClick, handlePendingClick, handleResolvedClick])

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className || ''}`}
    >
      {metricCards.map((card, index) => (
        <motion.div
          key={card.status}
          variants={itemVariants}
          onClick={card.onClick}
        >
          <StatusCard
            title={card.title}
            value={card.value}
            status={card.status}
            icon={card.icon}
            trend={card.trend}
            className="h-full"
          />
        </motion.div>
      ))}
    </motion.div>
  )
})