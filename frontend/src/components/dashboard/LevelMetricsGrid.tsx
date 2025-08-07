import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Users, 
  Clock, 
  AlertCircle, 
  CheckCircle,
  TrendingUp
} from "lucide-react"
import { MetricsData } from "@/types"
import { cn } from "@/lib/utils"

interface LevelMetricsGridProps {
  metrics?: MetricsData
  className?: string
}

const levelConfig = {
  n1: {
    title: "Nível N1",
    color: "from-slate-600 to-slate-700",
    bgColor: "bg-slate-50",
    textColor: "text-slate-700"
  },
  n2: {
    title: "Nível N2",
    color: "from-slate-700 to-slate-800",
    bgColor: "bg-slate-50",
    textColor: "text-slate-700"
  },
  n3: {
    title: "Nível N3",
    color: "from-slate-500 to-slate-600",
    bgColor: "bg-slate-50",
    textColor: "text-slate-700"
  },
  n4: {
    title: "Nível N4",
    color: "from-slate-800 to-slate-900",
    bgColor: "bg-slate-50",
    textColor: "text-slate-700"
  }
}

const statusConfig = {
  novos: {
    icon: AlertCircle,
    color: "text-blue-600",
    bgColor: "bg-blue-100",
    label: "Novos"
  },
  progresso: {
    icon: Clock,
    color: "text-yellow-600",
    bgColor: "bg-yellow-100",
    label: "Em Progresso"
  },
  pendentes: {
    icon: Users,
    color: "text-red-600",
    bgColor: "bg-red-100",
    label: "Pendentes"
  },
  resolvidos: {
    icon: CheckCircle,
    color: "text-green-600",
    bgColor: "bg-green-100",
    label: "Resolvidos"
  }
}

export function LevelMetricsGrid({ metrics, className }: LevelMetricsGridProps) {
  // Verificação de segurança para evitar erros
  if (!metrics || !metrics.niveis) {
    return (
      <Card className={cn("figma-glass-card h-full", className)}>
        <CardContent className="flex items-center justify-center h-48">
          <div className="text-center">
            <div className="figma-body mb-2">📊</div>
        <div className="figma-body">Carregando métricas por nível...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  }

  return (
    <div className={cn("h-full flex flex-col overflow-hidden", className)}>
      <div className="grid grid-cols-1 sm:grid-cols-2 grid-rows-1 sm:grid-rows-2 gap-2 sm:gap-3 h-full overflow-hidden p-1">
        {Object.entries(metrics.niveis || {}).map(([level, levelData]) => {
          const config = levelConfig[level as keyof typeof levelConfig]
          if (!config || !levelData) return null
          const total = Object.values(levelData).reduce((sum, value) => sum + (value || 0), 0)
          
          return (
            <motion.div
              key={level}
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              className="h-full flex"
            >
              <Card className="figma-glass-card border-0 shadow-sm hover:shadow-md transition-all duration-300 h-full w-full flex flex-col">
                <CardHeader className="pb-2 px-4 pt-4 flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-semibold flex items-center gap-2">
                      <div className={`p-1.5 rounded-lg bg-gradient-to-br shadow-sm ${config.color}`}>
                        <TrendingUp className="h-4 w-4 text-white" />
                      </div>
                      <span className="whitespace-nowrap">{config.title}</span>
                    </CardTitle>
                    <Badge variant="outline" className={`${config.bgColor} ${config.textColor} border-0 text-xs px-2 py-1`}>
                      {total}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="px-4 pb-4 flex-1">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full">
                    {Object.entries(statusConfig).map(([status, statusConf]) => {
                      const Icon = statusConf.icon
                      const value = levelData[status as keyof typeof levelData]
                      
                      return (
                        <div
                          key={status}
                          className="flex items-center justify-between p-3 rounded-lg figma-glass-card transition-all duration-200 hover:scale-[1.02] hover:shadow-md min-h-[50px] border border-gray-100/50 dark:border-gray-800/50"
                        >
                          <div className="flex items-center gap-2">
                            <div className={`p-1.5 rounded-lg ${statusConf.bgColor} shadow-sm`}>
                              <Icon className={`h-3.5 w-3.5 ${statusConf.color}`} />
                            </div>
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                              {statusConf.label}
                            </span>
                          </div>
                          <span className={`text-sm font-bold ${statusConf.color} tabular-nums`}>
                            {value || 0}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}