import { motion } from "framer-motion"
import { StatusCard } from "./StatusCard"
import { MetricsData, TicketStatus } from "@/types"
import { Ticket, Clock, AlertTriangle, CheckCircle } from "lucide-react"

interface MetricsGridProps {
  metrics: MetricsData
  onFilterByStatus?: (status: TicketStatus) => void
  className?: string
}

export function MetricsGrid({
  metrics,
  onFilterByStatus,
  className
}: MetricsGridProps) {
  // Verificação de segurança
  if (!metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 figma-glass-card animate-pulse rounded-lg" />
        ))}
      </div>
    )
  }

  // Configuração dos cards de métricas
  const metricCards = [
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
      onClick: () => onFilterByStatus?.("new")
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
      onClick: () => onFilterByStatus?.("progress")
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
      onClick: () => onFilterByStatus?.("pending")
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
      onClick: () => onFilterByStatus?.("resolved")
    }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.02, // Muito rápido
        delayChildren: 0
      }
    }
  }

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
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                duration: 0.1, // Ultra-rápido
                ease: "easeOut"
              }
            }
          }}
          onClick={card.onClick}
          // Remover whileTap completamente
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
}

// Funções auxiliares para processar tendências
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