import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { MetricsGrid } from "./MetricsGrid"
import { LevelMetricsGrid } from "./LevelMetricsGrid"
import { NewTicketsList } from "./NewTicketsList"
import { RankingTable } from "./RankingTable"
import { TicketChart } from "./TicketChart"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  TrendingUp,
  BarChart3,
  PieChart
} from "lucide-react"
import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking } from "@/types"
import { cn, formatRelativeTime } from "@/lib/utils"
import { usePerformanceMonitoring, useRenderTracker } from "../../hooks/usePerformanceMonitoring"
import { performanceMonitor } from "../../utils/performanceMonitor"

interface ModernDashboardProps {
  metrics: MetricsData
  systemStatus?: SystemStatus | null
  technicianRanking?: TechnicianRanking[]
  onFilterByStatus?: (status: TicketStatus) => void
  isLoading?: boolean
  className?: string
}

export function ModernDashboard({
  metrics,
  systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  isLoading = false,
  className
}: ModernDashboardProps) {
  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('ModernDashboard')
  const { trackRender } = useRenderTracker('ModernDashboard')
  
  // Corrigir o estado inicial para incluir a propriedade 'label' obrigatória
  const [chartType, setChartType] = useState<'area' | 'bar' | 'pie'>('area')
  
  // Track component renders
  useEffect(() => {
    trackRender()
    measureRender(() => {
      performanceMonitor.markComponentRender('ModernDashboard', {
        metricsCount: Object.keys(metrics || {}).length,
        technicianCount: technicianRanking.length,
        isLoading
      })
    })
  }, [metrics, technicianRanking, isLoading, trackRender, measureRender])

  // Gerar dados para o gráfico
  const chartData = [
    { name: 'Novos', value: metrics.novos, color: '#3b82f6' },
    { name: 'Em Progresso', value: metrics.em_progresso, color: '#f59e0b' },
    { name: 'Pendentes', value: metrics.pendentes, color: '#ef4444' },
    { name: 'Resolvidos', value: metrics.resolvidos, color: '#10b981' }
  ]

  // Calcular métricas derivadas
  const totalTickets = metrics.novos + metrics.em_progresso + metrics.pendentes + metrics.resolvidos

  // Componente de Skeleton melhorado
  const SkeletonCard = () => (
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.01,
        delayChildren: 0
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.05,
        ease: "easeOut"
      }
    }
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
            metrics={metrics}
            className="h-full"
          />
        </motion.div>

        {/* Lista de tickets novos - ocupando 1 coluna */}
        <motion.div variants={itemVariants} className="dashboard-tickets-section">
          <NewTicketsList 
            className="h-full"
            limit={6}
          />
        </motion.div>
      </div>

      {/* Ranking de técnicos - ocupando toda a largura na parte inferior */}
      <motion.div variants={itemVariants} className="dashboard-ranking-section">
        <RankingTable 
          data={(() => {
            console.log('📊 ModernDashboard - Processando ranking de', technicianRanking?.length || 0, 'técnicos');
            
            // Usar os dados diretamente da API sem transformação desnecessária
            const result = technicianRanking.map((tech) => ({
              id: tech.id || String(tech.name),
              name: tech.name || tech.nome || 'Técnico',
              level: tech.level || 'N1',
              total: tech.total || 0,
              rank: tech.rank || 0
            }))
            
            console.log('✅ ModernDashboard - Ranking processado:', result.length, 'técnicos');
            return result;
          })()
          }
          title="Ranking de Técnicos"
          className="w-full h-full"
        />
      </motion.div>
    </motion.div>
  )
}