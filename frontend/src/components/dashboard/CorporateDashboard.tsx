import React, { useMemo, useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MetricsData, TicketStatus, SystemStatus, TechnicianRanking } from "@/types"
import { cn } from "@/lib/utils"

import { CategoryRankingCard } from "./CategoryRankingCard"

import { NewTicketsList } from "./NewTicketsList"
import { 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  HardHat, 
  Settings, 
  TrendingUp, 
  Users, 
  Wrench,
  FileText,
  Target,
  ChevronLeft,
  ChevronRight
} from "lucide-react"

interface CorporateDashboardProps {
  metrics: MetricsData
  levelMetrics?: any
  systemStatus?: SystemStatus | null
  technicianRanking?: TechnicianRanking[]
  onFilterByStatus?: (status: TicketStatus) => void
  isLoading?: boolean
  className?: string
}

// Componente de Métrica Corporativa
interface CorporateMetricCardProps {
  title: string
  value: number | string
  subtitle?: string
  icon: React.ComponentType<any>
  trend?: {
    value: number
    isPositive: boolean
  }
  onClick?: () => void
  className?: string
  statusClass?: string
}

const CorporateMetricCard: React.FC<CorporateMetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  onClick,
  className,
  statusClass
}) => {
  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.02 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
      className={cn(
        "cursor-pointer group",
        className
      )}
    >
      <Card className={cn("figma-glass-card h-full border-0 shadow-lg hover:shadow-xl transition-all duration-300", statusClass)}>
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 rounded-xl flex items-center justify-center shadow-sm">
                  <Icon className="h-6 w-6 text-slate-700 dark:text-slate-300" />
                </div>
                <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 uppercase tracking-wide">{title}</h3>
              </div>
              
              <div className="space-y-3">
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100">{value}</div>
                {subtitle && (
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{subtitle}</p>
                )}
                {trend && (
                  <div className={cn(
                    "flex items-center gap-2 text-sm font-medium px-2 py-1 rounded-full w-fit",
                    trend.isPositive 
                      ? "text-emerald-700 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/20" 
                      : "text-red-700 bg-red-50 dark:text-red-400 dark:bg-red-900/20"
                  )}>
                    <TrendingUp className={cn(
                      "h-4 w-4",
                      !trend.isPositive && "rotate-180"
                    )} />
                    <span>{Math.abs(trend.value)}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

// Componente de Carrossel para Seções
interface CarouselSectionProps {
  mainMetrics: any[]
  statusMetrics: any[]
}

const CarouselSection: React.FC<CarouselSectionProps> = ({ mainMetrics, statusMetrics: _ }) => {
  const [currentSlide, setCurrentSlide] = useState(0)
  
  const slides = [
    {
      id: 'status',
      title: 'Status dos Chamados',
      icon: Activity,
      iconBg: 'from-green-500 to-teal-600',
      content: (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {mainMetrics.map((metric, index) => (
            <CorporateMetricCard key={index} {...metric} />
          ))}
        </div>
      )
    },
    {
      id: 'categories',
      title: 'Top Chamados por Categoria',
      icon: Target,
      iconBg: 'from-yellow-500 to-orange-600',
      content: <CategoryRankingCard />
    }
  ]
  
  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length)
  }
  
  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length)
  }
  
  const currentSlideData = slides[currentSlide]
  const IconComponent = currentSlideData.icon
  
  return (
    <section className="space-y-6">
      {/* Header com navegação */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl lg:text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-3">
          <div className={`w-8 h-8 bg-gradient-to-br ${currentSlideData.iconBg} rounded-lg flex items-center justify-center`}>
            <IconComponent className="h-4 w-4 text-white" />
          </div>
          {currentSlideData.title}
        </h2>
        
        <div className="flex items-center gap-2">
          {/* Indicadores */}
          <div className="flex gap-1 mr-3">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-2 h-2 rounded-full transition-all duration-200 ${
                  index === currentSlide 
                    ? 'bg-slate-600 dark:bg-slate-300' 
                    : 'bg-slate-300 dark:bg-slate-600'
                }`}
              />
            ))}
          </div>
          
          {/* Botões de navegação */}
          <Button
            variant="outline"
            size="sm"
            onClick={prevSlide}
            className="h-8 w-8 p-0"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={nextSlide}
            className="h-8 w-8 p-0"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Conteúdo do slide */}
      <motion.div
        key={currentSlide}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        {currentSlideData.content}
      </motion.div>
    </section>
  )
}

export const CorporateDashboard: React.FC<CorporateDashboardProps> = ({
  metrics,
  levelMetrics: _levelMetrics,
  systemStatus: _systemStatus,
  technicianRanking = [],
  onFilterByStatus,
  isLoading = false,
  className
}) => {
  // Calcular métricas derivadas
  const derivedMetrics = useMemo(() => {
    const total = (metrics.novos || 0) + (metrics.progresso || 0) + (metrics.pendentes || 0) + (metrics.resolvidos || 0)
    const efficiency = total > 0 ? ((metrics.resolvidos || 0) / total * 100) : 0
    const activeTickets = (metrics.novos || 0) + (metrics.progresso || 0)
    const avgResolutionTime = "2.3h" // Placeholder - seria calculado do backend
    
    return {
      total,
      efficiency: efficiency.toFixed(1),
      activeTickets,
      avgResolutionTime
    }
  }, [metrics])

  // Métricas principais do dashboard
  const mainMetrics = useMemo(() => [
    {
      title: "Total de Chamados",
      value: derivedMetrics.total.toLocaleString(),
      subtitle: "Todos os status",
      icon: FileText,
      trend: { value: 12, isPositive: true }
    },
    {
      title: "Chamados Ativos",
      value: derivedMetrics.activeTickets.toLocaleString(),
      subtitle: "Novos + Em progresso",
      icon: Activity,
      trend: { value: 8, isPositive: false },
      onClick: () => onFilterByStatus?.("progress")
    },
    {
      title: "Taxa de Resolução",
      value: `${derivedMetrics.efficiency}%`,
      subtitle: "Eficiência operacional",
      icon: Target,
      trend: { value: 5, isPositive: true }
    },
    {
      title: "Tempo Médio",
      value: derivedMetrics.avgResolutionTime,
      subtitle: "Resolução de chamados",
      icon: Clock,
      trend: { value: 15, isPositive: true }
    }
  ], [derivedMetrics, onFilterByStatus])

  // Métricas detalhadas por status
  const statusMetrics = useMemo(() => [
    {
      title: "Novos Chamados",
      value: (metrics.novos || 0).toLocaleString(),
      subtitle: "Aguardando atendimento",
      icon: AlertCircle,
      onClick: () => onFilterByStatus?.("new"),
      statusClass: "status-new"
    },
    {
      title: "Em Progresso",
      value: (metrics.progresso || 0).toLocaleString(),
      subtitle: "Sendo processados",
      icon: Settings,
      onClick: () => onFilterByStatus?.("progress"),
      statusClass: "status-progress"
    },
    {
      title: "Pendentes",
      value: (metrics.pendentes || 0).toLocaleString(),
      subtitle: "Aguardando informações",
      icon: Clock,
      onClick: () => onFilterByStatus?.("pending"),
      statusClass: "status-pending"
    },
    {
      title: "Resolvidos",
      value: (metrics.resolvidos || 0).toLocaleString(),
      subtitle: "Concluídos com sucesso",
      icon: CheckCircle2,
      onClick: () => onFilterByStatus?.("resolved"),
      statusClass: "status-resolved"
    }
  ], [metrics, onFilterByStatus])

  if (isLoading) {
    return (
      <div className="space-y-8 p-6">
        {/* Loading skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="corporate-card animate-pulse">
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-slate-200 rounded-lg" />
                  <div className="h-4 bg-slate-200 rounded w-24" />
                </div>
                <div className="space-y-2">
                  <div className="h-8 bg-slate-200 rounded w-16" />
                  <div className="h-3 bg-slate-200 rounded w-32" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={cn("space-y-6 lg:space-y-10 p-4 lg:p-6 max-w-full overflow-hidden", className)}
    >
      {/* Métricas Principais */}
      <section>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <TrendingUp className="h-4 w-4 text-white" />
          </div>
          Métricas Principais
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statusMetrics.map((metric, index) => (
            <CorporateMetricCard key={index} {...metric} />
          ))}
        </div>
      </section>

      {/* Layout Responsivo: Status dos Chamados e Tickets Novos */}
      <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
        {/* Métricas Consolidadas - Responsivo */}
        <div className="lg:col-span-3 flex flex-col">
          <CarouselSection 
            mainMetrics={mainMetrics}
            statusMetrics={statusMetrics}
          />
        </div>

        {/* Tickets Novos - Responsivo */}
        <div className="lg:col-span-4 flex flex-col">
          {/* Título alinhado com os outros cards */}
          <div className="mb-4 lg:mb-6">
            <h2 className="text-xl lg:text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-slate-600 to-slate-700 rounded-lg flex items-center justify-center">
                <AlertCircle className="h-4 w-4 text-white" />
              </div>
              Tickets Novos
            </h2>
          </div>
          <div className="flex-1">
            <NewTicketsList limit={8} hideHeader={true} />
          </div>
        </div>
      </div>

      {/* Informações da Equipe */}
      {technicianRanking.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-6 flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Users className="h-4 w-4 text-white" />
            </div>
            Equipe Técnica
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <CorporateMetricCard
              title="Total de Técnicos"
              value={technicianRanking.length.toString()}
              subtitle="Equipe ativa"
              icon={Users}
            />
            <CorporateMetricCard
              title="Técnicos N1"
              value={technicianRanking.filter(t => t.level === 'N1').length.toString()}
              subtitle="Suporte básico"
              icon={HardHat}
            />
            <CorporateMetricCard
              title="Técnicos Especialistas"
              value={technicianRanking.filter(t => ['N2', 'N3', 'N4'].includes(t.level || '')).length.toString()}
              subtitle="Suporte avançado"
              icon={Wrench}
            />
          </div>
        </section>
      )}




    </motion.div>
  )
}