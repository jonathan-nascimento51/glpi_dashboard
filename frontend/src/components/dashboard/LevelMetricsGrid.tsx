import React, { useMemo } from "react"
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
    title: "nível N1",
    color: "from-slate-600 to-slate-700",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  n2: {
    title: "nível N2",
    color: "from-slate-700 to-slate-800",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  n3: {
    title: "nível N3",
    color: "from-slate-500 to-slate-600",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  n4: {
    title: "nível N4",
    color: "from-slate-800 to-slate-900",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  }
}

const statusConfig = {
  novos: {
    icon: AlertCircle,
    color: "text-gray-900 dark:text-gray-100",
    bgColor: "bg-blue-100 dark:bg-blue-900/30 border-0",
    iconColor: "text-blue-600 dark:text-blue-400",
    label: "Novos"
  },
  progresso: {
    icon: Clock,
    color: "text-gray-900 dark:text-gray-100",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30 border-0",
    iconColor: "text-yellow-600 dark:text-yellow-400",
    label: "Em Progresso"
  },
  pendentes: {
    icon: Users,
    color: "text-gray-900 dark:text-gray-100",
    bgColor: "bg-red-100 dark:bg-red-900/30 border-0",
    iconColor: "text-red-600 dark:text-red-400",
    label: "Pendentes"
  },
  resolvidos: {
    icon: CheckCircle,
    color: "text-gray-900 dark:text-gray-100",
    bgColor: "bg-green-100 dark:bg-green-900/30 border-0",
    iconColor: "text-green-600 dark:text-green-400",
    label: "Resolvidos"
  }
}

// Variantes de animação movidas para fora do componente
const itemVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut" as const
    }
  },
  hover: {
    y: -8,
    scale: 1.03,
    transition: {
      duration: 0.3,
      ease: "easeInOut" as const
    }
  }
} as const

const iconVariants = {
  hover: {
    scale: 1.2,
    rotate: 10,
    transition: {
      duration: 0.3,
      ease: "easeInOut" as const
    }
  }
} as const

const statusVariants = {
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: "easeInOut" as const
    }
  }
} as const

// Componente StatusItem memoizado
const StatusItem = React.memo<{
  status: string
  statusConf: typeof statusConfig[keyof typeof statusConfig]
  value: number | undefined
}>(function StatusItem({ status, statusConf, value }) {
  const Icon = statusConf.icon
  
  return (
    <motion.div
key={`status-item-${status}`}
      variants={statusVariants}
      whileHover="hover"
      className="flex items-center justify-between p-4 rounded-lg figma-glass-card min-h-[60px] border border-gray-100/50 dark:border-gray-800/50 cursor-pointer"
    >
      <div className="flex items-center gap-3">
        <motion.div 
          className={`p-2 rounded-lg ${statusConf.bgColor} shadow-sm`}
          whileHover={{ scale: 1.1 }}
          transition={{ duration: 0.2 }}
        >
          <Icon className={`h-4 w-4 ${statusConf.iconColor}`} />
        </motion.div>
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {statusConf.label}
        </span>
      </div>
      <motion.span 
        className={`text-lg font-bold ${statusConf.color} tabular-nums`}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
      >
        {value || 0}
      </motion.span>
    </motion.div>
  )
})

// Componente LevelCard memoizado
const LevelCard = React.memo<{
  level: string
  levelData: any
  config: typeof levelConfig[keyof typeof levelConfig]
}>(function LevelCard({ level, levelData, config }) {
  const total = useMemo(() => {
    return Object.values(levelData).reduce((sum: number, value) => sum + (Number(value) || 0), 0)
  }, [levelData])
  
  return (
    <motion.div
      key={`level-motion-${level}`}
      variants={itemVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className="h-full flex cursor-pointer"
    >
      <Card className="figma-glass-card border-0 shadow-none h-full w-full flex flex-col relative overflow-hidden">
        <CardHeader className="pb-3 px-4 pt-4 flex-shrink-0">
          <div className="flex items-center justify-between relative z-10">
            <CardTitle className="text-lg font-semibold flex items-center gap-3">
              <motion.div 
                variants={iconVariants}
                className={`p-2 rounded-lg bg-gradient-to-br shadow-sm ${config.color}`}
              >
                <TrendingUp className="h-5 w-5 text-white" />
              </motion.div>
              <span className="whitespace-nowrap">{config.title}</span>
            </CardTitle>
            <motion.div
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.2 }}
            >
              <Badge variant="outline" className={`${config.bgColor} ${config.textColor} border-0 text-sm px-3 py-1.5 font-bold`}>
                {total}
              </Badge>
            </motion.div>
          </div>
        </CardHeader>
        
        <CardContent className="px-4 pb-4 flex-1 relative z-10">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full h-full">
            {Object.entries(statusConfig).map(([status, statusConf]) => {
              const value = levelData[status as keyof typeof levelData]
              
              return (
                <StatusItem
                  key={`level-${level}-${status}`}
                  status={status}
                  statusConf={statusConf}
                  value={value}
                />
              )
            })}
          </div>
        </CardContent>
        
        {/* Gradient Background */}
        <div className={cn(
          "absolute inset-0 bg-gradient-to-br opacity-5 rounded-2xl",
          config.color
        )} />
        
        {/* Shine Effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 opacity-0"
          whileHover={{
            opacity: [0, 1, 0],
            x: [-100, 300]
          }}
          transition={{ duration: 0.6 }}
        />
      </Card>
    </motion.div>
  )
})

export const LevelMetricsGrid = React.memo<LevelMetricsGridProps>(function LevelMetricsGrid({
  metrics,
  className
}) {
  // Verificação de segurança para evitar erros
  if (!metrics || !metrics.niveis) {
    return (
      <Card className={cn("glass-card h-full premium-shadow", className)}>
        <CardContent className="flex items-center justify-center h-48">
          <div className="text-center">
            <div className="figma-body mb-2">ðŸ“Š</div>
        <div className="figma-body">Carregando mÃ©tricas por nível...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Memoizar as entradas dos nÃ­veis
  const levelEntries = useMemo(() => {
    return Object.entries(metrics.niveis || {})
  }, [metrics.niveis])

  return (
    <div className={cn("h-full flex flex-col overflow-hidden", className)}>
      <div className="grid grid-cols-1 sm:grid-cols-2 grid-rows-1 sm:grid-rows-2 gap-2 sm:gap-3 h-full overflow-hidden p-1">
        {levelEntries.map(([level, levelData]) => {
          const config = levelConfig[level as keyof typeof levelConfig]
          if (!config || !levelData) return null
          
          return (
            <LevelCard
              key={`level-card-${level}`}
              level={level}
              levelData={levelData}
              config={config}
            />
          )
        })}
      </div>
    </div>
  )
})

