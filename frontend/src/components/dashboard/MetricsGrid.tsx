import React, { useEffect, useCallback, useMemo } from "react"
import { motion } from "framer-motion"
import { StatusCard } from "./StatusCard"
import { MetricsData, TicketStatus } from "@/types"
import { Ticket, Clock, AlertTriangle, CheckCircle } from "lucide-react"
import { usePerformanceMonitoring, useRenderTracker } from "../../hooks/usePerformanceMonitoring"
import { performanceMonitor } from "../../utils/performanceMonitor"
import { useThrottledCallback } from "../../hooks/useDebounce"
import { generateMetricsKey, generateSkeletonKey } from "../../utils/keyUtils"

interface MetricsGridProps {
  metrics: MetricsData | null
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
      ease: "easeOut" as const
    }
  }
} as const

export const MetricsGrid = React.memo<MetricsGridProps>(function MetricsGrid({
  metrics,
  onFilterByStatus,
  className
}) {
  // Performance monitoring hooks (apenas em desenvolvimento)
  const { measureRender } = usePerformanceMonitoring('MetricsGrid')
  const { trackRender } = useRenderTracker('MetricsGrid')
  
  // Track component renders apenas em desenvolvimento e com debounce
  useEffect(() => {
    if (process.env.NODE_ENV !== 'development') return;
    
    const timeoutId = setTimeout(() => {
      trackRender();
      
      measureRender(() => {
        performanceMonitor.markComponentRender('MetricsGrid', {
          hasMetrics: !!metrics,
          metricsKeys: metrics ? Object.keys(metrics).length : 0
        })
      })
    }, 100); // Debounce de 100ms
    
    return () => clearTimeout(timeoutId);
  }, [metrics?.novos, metrics?.progresso, metrics?.pendentes, metrics?.resolvidos]) // Apenas dependências essenciais
  
  // Componente renderizado com métricas válidas

  // Verificação de segurança
  if (!metrics) {
    // console.log('⚠️ MetricsGrid - Metrics é null/undefined, mostrando skeleton')
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={generateSkeletonKey(i, 'metrics-grid')} className="h-32 figma-glass-card animate-pulse rounded-lg" />
        ))}
      </div>
    )
  }

  // Callbacks memoizados para os cliques com throttle
  const handleNewClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-new')
    onFilterByStatus?.("new")
    performanceMonitor.endMeasure('filter-click-new')
  }, [onFilterByStatus])

  const handleProgressClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-progress')
    onFilterByStatus?.("progress")
    performanceMonitor.endMeasure('filter-click-progress')
  }, [onFilterByStatus])

  const handlePendingClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-pending')
    onFilterByStatus?.("pending")
    performanceMonitor.endMeasure('filter-click-pending')
  }, [onFilterByStatus])

  const handleResolvedClickImmediate = useCallback(() => {
    performanceMonitor.startMeasure('filter-click-resolved')
    onFilterByStatus?.("resolved")
    performanceMonitor.endMeasure('filter-click-resolved')
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
      {metricCards.map((card) => (
        <motion.div
          key={generateMetricsKey(card.status, 'main-grid')}
          variants={itemVariants}
        >
          <StatusCard
            title={card.title}
            value={card.value}
            status={card.status}
            icon={card.icon}
            trend={card.trend}
            className="h-full cursor-pointer"
            onClick={card.onClick}
          />
        </motion.div>
      ))}
    </motion.div>
  )
})