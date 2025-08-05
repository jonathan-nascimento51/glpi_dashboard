import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { MetricsGrid } from "./MetricsGrid"
import { StatusCard } from "./StatusCard"
import { RankingTable } from "./RankingTable"
import { TicketChart } from "./TicketChart"
import DateRangeFilter, { type DateRange } from "../DateRangeFilter"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Activity, 
  Users, 
  Clock, 
  TrendingUp,
  BarChart3,
  PieChart,
  RefreshCw
} from "lucide-react"
import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking } from "@/types"
import { cn, formatRelativeTime } from "@/lib/utils"

interface ModernDashboardProps {
  metrics: MetricsData
  systemStatus?: SystemStatus | null
  technicianRanking?: TechnicianRanking[]
  onFilterByStatus?: (status: TicketStatus) => void
  onRefresh?: () => void
  onDateRangeChange?: (dateRange: DateRange) => void
  lastUpdate?: Date | null
  dateRange?: DateRange
  isLoading?: boolean
  className?: string
}

export function ModernDashboard({
  metrics,
  systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  onRefresh,
  onDateRangeChange,
  lastUpdate,
  dateRange,
  isLoading = false,
  className
}: ModernDashboardProps) {
  // Corrigir o estado inicial para incluir a propriedade 'label' obrigatória
  const [currentDateRange, setCurrentDateRange] = useState<DateRange>(
    dateRange || {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      end: new Date(),
      label: 'Últimos 7 dias'
    }
  )
  const [chartType, setChartType] = useState<'area' | 'bar' | 'pie'>('area')
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    if (dateRange) {
      setCurrentDateRange(dateRange)
    }
  }, [dateRange])

  const handleDateRangeChange = (newDateRange: DateRange) => {
    setCurrentDateRange(newDateRange)
    onDateRangeChange?.(newDateRange)
  }

  const handleRefresh = async () => {
    if (onRefresh) {
      setIsRefreshing(true)
      try {
        await onRefresh()
      } finally {
        setIsRefreshing(false)
      }
    }
  }

  // Gerar dados para o gráfico
  const chartData = [
    { name: 'Novos', value: metrics.novos, color: '#3b82f6' },
    { name: 'Em Progresso', value: metrics.em_progresso, color: '#f59e0b' },
    { name: 'Pendentes', value: metrics.pendentes, color: '#ef4444' },
    { name: 'Resolvidos', value: metrics.resolvidos, color: '#10b981' }
  ]

  // Calcular métricas derivadas
  const totalTickets = metrics.novos + metrics.em_progresso + metrics.pendentes + metrics.resolvidos
  const activeUsers = technicianRanking.length
  const averageResolutionTime = technicianRanking.length > 0 
    ? technicianRanking.reduce((acc, tech) => acc + (tech.total || 0), 0) / technicianRanking.length
    : 0

  // Formatar dados do ranking
  const rankingData = technicianRanking.map((tech, index) => ({
    position: index + 1,
    name: tech.nome || tech.name || 'Técnico',
    resolved: tech.total || 0,
    avatar: tech.avatar || null
  }))

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
      className={cn("space-y-6 p-6 min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50", className)}
    >
      {/* Header com filtro de data */}
      <motion.div variants={itemVariants} className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard GLPI</h1>
          <p className="text-sm text-gray-600">
            {lastUpdate && `Última atualização: ${formatRelativeTime(lastUpdate)}`}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <DateRangeFilter
            variant="modern"
            value={currentDateRange}
            onChange={handleDateRangeChange}
          />
          
          <Button
            onClick={handleRefresh}
            disabled={isRefreshing}
            size="sm"
            className="flex items-center gap-2"
          >
            <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
            Atualizar
          </Button>
        </div>
      </motion.div>

      {/* Cards de métricas principais */}
      <motion.div variants={itemVariants}>
        <MetricsGrid 
          metrics={metrics}
          onFilterByStatus={onFilterByStatus}
          className="mb-6"
        />
      </motion.div>
      
      {/* Gráficos e tabelas */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Gráfico principal */}
        <motion.div variants={itemVariants} className="xl:col-span-2">
          <Card className="border-0 shadow-lg bg-white/95">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  Evolução dos Tickets
                </CardTitle>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant={chartType === 'area' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType('area')}
                  >
                    <TrendingUp className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={chartType === 'bar' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType('bar')}
                  >
                    <BarChart3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={chartType === 'pie' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType('pie')}
                  >
                    <PieChart className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent>
              <TicketChart 
                data={chartData}
                type={chartType}
                title=""
              />
            </CardContent>
          </Card>
        </motion.div>

        {/* Cards de status lateral */}
        <motion.div variants={itemVariants} className="space-y-4">
          <StatusCard
            title="Sistema"
            value={systemStatus?.sistema_ativo ? 1 : 0}
            status={systemStatus?.sistema_ativo ? "online" : "offline"}
            icon={Activity}
            trend={{
              direction: 'stable',
              value: 0,
              label: systemStatus?.sistema_ativo ? "Online" : "Offline"
            }}
          />
          
          <StatusCard
            title="Técnicos Ativos"
            value={activeUsers}
            status="active"
            icon={Users}
            trend={{
              direction: activeUsers > 0 ? 'up' : 'stable',
              value: activeUsers,
              label: "online agora"
            }}
          />
          
          <StatusCard
            title="Resolução Média"
            value={Math.round(averageResolutionTime * 100) / 100}
            status="progress"
            icon={Clock}
            trend={{
              direction: 'stable',
              value: Math.round(averageResolutionTime * 100) / 100,
              label: "horas/ticket"
            }}
          />
        </motion.div>
      </div>

      {/* Tabela de ranking */}
      <motion.div variants={itemVariants}>
        <RankingTable 
          data={rankingData}
          title="Ranking de Técnicos"
        />
      </motion.div>
    </motion.div>
  )
}