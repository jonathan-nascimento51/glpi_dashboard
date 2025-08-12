import React, { useEffect, useMemo } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking } from "@/types"
import { cn } from "@/lib/utils"
import { usePerformanceMonitoring } from '@/hooks/usePerformanceMonitoring'
import { performanceMonitor } from "../../utils/performanceMonitor"
import { useSelectiveMemo, useStableCallback, useOptimizedList } from '@/hooks/useOptimization'

interface ModernDashboardProps {
  metrics: MetricsData
  levelMetrics?: any
  systemStatus?: SystemStatus | null
  technicianRanking?: TechnicianRanking[]
  onFilterByStatus?: (status: TicketStatus) => void
  isLoading?: boolean
  className?: string
}

// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.01,
      delayChildren: 0
    }
  }
} as const

const itemVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.05,
      ease: "easeOut" as const
    }
  }
} as const

// Componente de card memoizado
const MetricCard = React.memo<{
  title: string
  value: number | string
  icon?: React.ReactNode
  trend?: number
  onClick?: () => void
  className?: string
}>(({ title, value, icon, trend, onClick, className }) => {
  return (
    <motion.div variants={itemVariants}>
      <Card 
        className={cn(
          "cursor-pointer hover:shadow-lg transition-all duration-200",
          className
        )}
        onClick={onClick}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 className="text-sm font-medium">{title}</h3>
          {icon}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {trend !== undefined && (
            <p className={cn(
              "text-xs",
              trend > 0 ? "text-green-600" : trend < 0 ? "text-red-600" : "text-gray-600"
            )}>
              {trend > 0 ? "+" : ""}{trend}% from last month
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
})

// Componente de ranking memoizado
const TechnicianRankingCard = React.memo<{
  ranking: TechnicianRanking[]
}>(({ ranking }) => {
  const optimizedRanking = useOptimizedList(
    ranking,
    undefined,
    (a, b) => (b.resolved_tickets || 0) - (a.resolved_tickets || 0)
  )

  return (
    <motion.div variants={itemVariants}>
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Top Technicians</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {optimizedRanking.slice(0, 5).map((tech, index) => (
              <div key={tech.id || index} className="flex items-center justify-between">
                <span className="text-sm">{tech.name}</span>
                <span className="text-sm font-medium">{tech.resolved_tickets || 0}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
})

export const ModernDashboard = React.memo<ModernDashboardProps>(function ModernDashboard({
  metrics,
  levelMetrics,
  technicianRanking = [],
  onFilterByStatus,
  isLoading = false,
  className
}) {
  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('ModernDashboard')

  // Memoização seletiva dos dados principais
  const memoizedMetrics = useSelectiveMemo(
    metrics,
    (data) => ({
      total: data?.total || 0,
      open: data?.open || 0,
      inProgress: data?.in_progress || 0,
      resolved: data?.resolved || 0,
      closed: data?.closed || 0
    }),
    [metrics?.total, metrics?.open, metrics?.in_progress, metrics?.resolved, metrics?.closed]
  )

  // Callback estável para filtros
  const stableFilterCallback = useStableCallback((status: TicketStatus) => {
    onFilterByStatus?.(status)
  })

  // Memoização dos cards de métricas
  const metricCards = useMemo(() => [
    {
      title: "Total Tickets",
      value: memoizedMetrics.total,
      onClick: () => stableFilterCallback('all' as TicketStatus)
    },
    {
      title: "Open Tickets",
      value: memoizedMetrics.open,
      onClick: () => stableFilterCallback('open')
    },
    {
      title: "In Progress",
      value: memoizedMetrics.inProgress,
      onClick: () => stableFilterCallback('in_progress')
    },
    {
      title: "Resolved",
      value: memoizedMetrics.resolved,
      onClick: () => stableFilterCallback('resolved')
    },
    {
      title: "Closed",
      value: memoizedMetrics.closed,
      onClick: () => stableFilterCallback('closed')
    }
  ], [memoizedMetrics, stableFilterCallback])

  // Track component renders
  useEffect(() => {
    measureRender(() => {
      performanceMonitor.markComponentRender('ModernDashboard', {
        metricsCount: Object.keys(metrics || {}).length,
        technicianCount: technicianRanking.length,
        isLoading
      })
    })
  }, [metrics, technicianRanking, isLoading, measureRender])

  if (isLoading) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="space-y-0 pb-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      className={cn("space-y-6", className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {metricCards.map((card, index) => (
          <MetricCard
            key={`metric-${index}`}
            title={card.title}
            value={card.value}
            onClick={card.onClick}
          />
        ))}
      </div>

      {/* Technician Ranking */}
      {technicianRanking.length > 0 && (
        <TechnicianRankingCard ranking={technicianRanking} />
      )}

      {/* Level Metrics */}
      {levelMetrics && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Level Metrics</h3>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {Object.entries(levelMetrics).map(([level, data]: [string, any]) => (
                  <div key={level} className="text-center">
                    <h4 className="text-sm font-medium text-gray-600">{level}</h4>
                    <p className="text-2xl font-bold">{data?.total || 0}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  )
})

ModernDashboard.displayName = 'ModernDashboard'
