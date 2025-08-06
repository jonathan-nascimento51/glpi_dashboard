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
  // Corrigir o estado inicial para incluir a propriedade 'label' obrigatória
  const [chartType, setChartType] = useState<'area' | 'bar' | 'pie'>('area')

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
    <Card className="bg-white/50 backdrop-blur-sm border-0 shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-gray-200 rounded animate-pulse w-20" />
          <div className="h-8 w-8 bg-gray-200 rounded-full animate-pulse" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-16" />
          <div className="h-3 bg-gray-200 rounded animate-pulse w-24" />
        </div>
      </CardContent>
    </Card>
  )

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6 p-6 min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Header skeleton */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-2">
            <div className="h-8 bg-gray-200 rounded animate-pulse w-64" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-48" />
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 bg-gray-200 rounded animate-pulse w-32" />
            <div className="h-10 bg-gray-200 rounded animate-pulse w-24" />
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
            <Card className="bg-white/50 backdrop-blur-sm border-0 shadow-sm">
              <CardHeader>
                <div className="h-6 bg-gray-200 rounded animate-pulse w-40" />
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-200 rounded animate-pulse" />
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
      className={cn("h-full overflow-hidden flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50", className)}
    >
      <div className="flex-1 overflow-y-auto p-4 space-y-4">


        {/* Cards de métricas principais */}
        <motion.div variants={itemVariants}>
          <MetricsGrid 
            metrics={metrics}
            onFilterByStatus={onFilterByStatus}
            className="mb-4"
          />
        </motion.div>
        
        {/* Métricas por nível e Lista de tickets novos */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Métricas por nível de atendimento */}
          <motion.div variants={itemVariants} className="xl:col-span-2">
            <LevelMetricsGrid 
              metrics={metrics}
              className="h-full"
            />
          </motion.div>

          {/* Lista de tickets novos */}
          <motion.div variants={itemVariants}>
            <NewTicketsList 
              className="h-full"
              limit={8}
            />
          </motion.div>
        </div>

        {/* Ranking de técnicos */}
        <motion.div variants={itemVariants}>
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
            className="max-w-full"
          />
        </motion.div>
      </div>
    </motion.div>
  )
}