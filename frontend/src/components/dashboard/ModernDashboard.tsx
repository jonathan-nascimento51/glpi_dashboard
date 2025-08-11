import React, { useEffect, useMemo, Suspense } from 'react';
import { motion } from 'framer-motion';
import { MetricsGrid } from './MetricsGrid';
import { LevelMetricsGrid } from './LevelMetricsGrid';

// Componentes lazy centralizados
import { 
  LazyNewTicketsList, 
  LazyRankingTable,
  ListSkeleton,
  TableSkeleton 
} from '../LazyComponents';

import { RankingDebugPanel } from '../debug/RankingDebugPanel'

import { Card, CardContent, CardHeader } from "@/components/ui/card"

import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking } from "@/types"
import { cn } from "@/lib/utils"
import { usePerformanceMonitoring } from '@/hooks/usePerformanceMonitoring'
import { performanceMonitor } from "../../utils/performanceMonitor"

interface ModernDashboardProps {
  metrics: MetricsData
  levelMetrics?: any
  systemStatus?: SystemStatus | null
  technicianRanking?: TechnicianRanking[]
  onFilterByStatus?: (status: TicketStatus) => void
  isLoading?: boolean
  // Novos props para estados específicos do ranking
  rankingLoading?: boolean
  rankingError?: string | null
  rankingLastUpdated?: Date
  rankingIsUpdating?: boolean
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

// Componente SkeletonCard memoizado
const SkeletonCard = React.memo(function SkeletonCard() {
  return (
    <Card className="figma-glass-card shadow-none">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="h-4 figma-glass-card rounded animate-pulse w-20" />
          <div className="h-8 w-8 figma-glass-card rounded-full animate-pulse" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-8 figma-glass-card rounded animate-pulse w-16" />
          <div className="h-3 figma-glass-card rounded animate-pulse w-24" />
        </div>
      </CardContent>
    </Card>
  )
})

export const ModernDashboard = React.memo<ModernDashboardProps>(function ModernDashboard({
  metrics,
  levelMetrics,
  systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  isLoading = false,
  // Novos props para estados específicos do ranking
  rankingLoading = false,
  rankingError = null,
  rankingLastUpdated,
  rankingIsUpdating = false,
  className
}) {
  // Sistema funcionando corretamente
    // console.log('✅ ModernDashboard carregado - correção dos níveis aplicada');


  
  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('ModernDashboard')
  const [showDebugPanel, setShowDebugPanel] = React.useState(false)
  
  // Track component renders (apenas em desenvolvimento e com throttling)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      const timeoutId = setTimeout(() => {
        measureRender(() => {
          performanceMonitor.markComponentRender('ModernDashboard', {
            metricsCount: Object.keys(metrics || {}).length,
            technicianCount: technicianRanking?.length || 0,
            isLoading
          })
        })
      }, 100); // Debounce de 100ms para evitar chamadas excessivas
      
      return () => clearTimeout(timeoutId);
    }
  }, [metrics, technicianRanking, isLoading, measureRender])

  // Memoizar dados do ranking processados
  const processedRankingData = useMemo(() => {
    if (!technicianRanking || !Array.isArray(technicianRanking)) {
      return []
    }
    
    const result = technicianRanking.map((tech, index) => ({
      id: `technician-${index}-${tech.id || 'unknown'}-${String(tech.name || 'unnamed').replace(/\s+/g, '-').toLowerCase()}`,
      name: tech.name || tech.nome || 'Técnico',
      level: tech.level || 'N1', // Manter fallback apenas para casos extremos
      total: tech.total || 0,
      rank: tech.rank || 0
    }))
    
    return result
  }, [technicianRanking])

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6 p-6 min-h-screen">
        {/* Header skeleton */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-2">
            <div className="h-8 figma-glass-card rounded animate-pulse w-64" />
            <div className="h-4 figma-glass-card rounded animate-pulse w-48" />
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 figma-glass-card rounded animate-pulse w-32" />
            <div className="h-10 figma-glass-card rounded animate-pulse w-24" />
          </div>
        </div>
        
        {/* Metrics skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
        
        {/* Charts skeleton */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <Card className="figma-glass-card shadow-none">
              <CardHeader>
                <div className="h-6 figma-glass-card rounded animate-pulse w-40" />
              </CardHeader>
              <CardContent>
                <div className="h-64 figma-glass-card rounded animate-pulse" />
              </CardContent>
            </Card>
          </div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={cn("dashboard-fullscreen-container", className)}
    >

      
      {/* Cards de métricas principais */}
      <motion.div variants={itemVariants} className="dashboard-metrics-section">
        <MetricsGrid 
          metrics={metrics}
          onFilterByStatus={onFilterByStatus}
        />
      </motion.div>
      
      {/* Layout principal com métricas por nível e tickets novos */}
      <div className="dashboard-main-grid">
        {/* Métricas por nível de atendimento - ocupando 2 colunas */}
        <motion.div variants={itemVariants} className="dashboard-levels-section">
          <LevelMetricsGrid 
            metrics={levelMetrics}
            className="h-full"
          />
        </motion.div>

        {/* Lista de tickets novos - ocupando 1 coluna */}
        <motion.div variants={itemVariants} className="dashboard-tickets-section">
          <Suspense fallback={<ListSkeleton />}>
            <LazyNewTicketsList 
              className="h-full"
              limit={6}
            />
          </Suspense>
        </motion.div>
      </div>

      {/* Ranking de técnicos - ocupando toda a largura na parte inferior */}
      <motion.div variants={itemVariants} className="dashboard-ranking-section">
        <Suspense fallback={<TableSkeleton />}>
          {rankingError ? (
            <Card className="w-full h-full figma-glass-card">
              <CardHeader>
                <CardTitle className="text-red-600">Erro no Ranking</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-red-500">{rankingError}</p>
                <button 
                  onClick={() => window.location.reload()} 
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Tentar Novamente
                </button>
              </CardContent>
            </Card>
          ) : (
            <LazyRankingTable 
              data={processedRankingData}
              title="Ranking de Técnicos"
              className="w-full h-full"
              isLoading={rankingLoading}
              isUpdating={rankingIsUpdating}
              lastUpdated={rankingLastUpdated}
            />
          )}
        </Suspense>
      </motion.div>
      
      {/* Debug Panel */}
      <RankingDebugPanel 
        isVisible={showDebugPanel}
        onToggle={() => setShowDebugPanel(!showDebugPanel)}
      />
    </motion.div>
  )
})