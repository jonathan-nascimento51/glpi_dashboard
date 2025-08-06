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
    <div className={cn("grid grid-cols-1 lg:grid-cols-2 gap-6", className)}>
      {Object.entries(metrics.niveis || {}).map(([level, levelData]) => {
        const config = levelConfig[level as keyof typeof levelConfig]
        if (!config || !levelData) return null
        const total = levelData.novos + levelData.progresso + levelData.pendentes + levelData.resolvidos
        
        return (
          <motion.div
            key={level}
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            <Card className="figma-level-card">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="figma-heading-large flex items-center gap-2">
                    <div className={`p-2 rounded-xl bg-gradient-to-br shadow-lg ${config.color}`}>
                      <TrendingUp className="h-5 w-5 text-white" />
                    </div>
                    {config.title}
                  </CardTitle>
                  <Badge variant="outline" className={`${config.bgColor} ${config.textColor} border-0`}>
                    Total: {total}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(statusConfig).map(([status, statusConf]) => {
                    const Icon = statusConf.icon
                    const value = levelData[status as keyof typeof levelData]
                    
                    return (
                      <div
                        key={status}
                        className="flex items-center justify-between p-3 rounded-lg figma-glass-card transition-colors duration-200"
                      >
                        <div className="flex items-center gap-2">
                          <div className={`p-1.5 rounded-md ${statusConf.bgColor}`}>
                            <Icon className={`h-4 w-4 ${statusConf.color}`} />
                          </div>
                          <span className="figma-body">
                            {statusConf.label}
                          </span>
                        </div>
                        <span className="figma-numeric">
                          {value}
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
  )
}