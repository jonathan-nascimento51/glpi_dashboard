import { memo, useMemo } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn, formatNumber, getStatusIcon, getTrendIcon, getTrendColor } from "@/lib/utils"
import { type LucideIcon } from "lucide-react"

interface StatusCardProps {
  title: string
  value: number
  status?: string
  trend?: {
    direction: 'up' | 'down' | 'stable'
    value: number
    label?: string
  }
  icon?: LucideIcon
  className?: string
  variant?: 'default' | 'compact' | 'detailed' | 'gradient'
  showProgress?: boolean
  maxValue?: number
}

// Função auxiliar definida fora do componente para evitar recriação
const getStatusGradient = (status?: string) => {
  switch (status) {
    case 'online': return 'from-green-500 to-emerald-600'
    case 'offline': return 'from-red-500 to-rose-600'
    case 'active': return 'from-blue-500 to-cyan-600'
    case 'progress': return 'from-yellow-500 to-orange-600'
    case 'pending': return 'from-orange-500 to-red-600'
    case 'resolved': return 'from-green-500 to-emerald-600'
    default: return 'from-gray-500 to-slate-600'
  }
}

// Variantes de animação definidas fora do componente
const cardVariants = {
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

const numberVariants = {
  hidden: { scale: 0 },
  visible: {
    scale: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut" as const,
      delay: 0.2
    }
  }
} as const

export const StatusCard = memo<StatusCardProps>(function StatusCard({
  title,
  value,
  status,
  trend,
  icon,
  className,
  variant: _ = 'default'
}) {
  // Memoizar ícones para evitar recálculos
  const StatusIcon = useMemo(() => 
    icon || (status ? getStatusIcon(status) : null), 
    [icon, status]
  )
  
  const TrendIcon = useMemo(() => 
    trend ? getTrendIcon(trend.direction) : null, 
    [trend?.direction]
  )
  
  // Memoizar gradiente do status
  const statusGradient = useMemo(() => getStatusGradient(status), [status])
  
  // Memoizar valor formatado
  const formattedValue = useMemo(() => {
    return formatNumber(value);
  }, [value])


  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className={cn("cursor-pointer", className)}
    >
      <Card className="figma-glass-card relative overflow-hidden rounded-2xl shadow-none">
        {/* Gradient Background */}
        <div className={cn(
          "absolute inset-0 bg-gradient-to-br opacity-5",
          statusGradient
        )} />
        
        {/* Animated Border */}
        <div className="absolute inset-0 rounded-2xl">
          <div className={cn(
            "absolute inset-0 rounded-2xl bg-gradient-to-r opacity-20 blur-sm",
            statusGradient
          )} />
        </div>
        
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 relative z-10">
          <CardTitle className="figma-subheading uppercase tracking-wide">
            {title}
          </CardTitle>
          {StatusIcon && (
            <motion.div
              variants={iconVariants}
              className={cn(
                "p-2 rounded-xl bg-gradient-to-br shadow-lg",
                statusGradient
              )}
            >
              <StatusIcon className="h-5 w-5 text-white" />
            </motion.div>
          )}
        </CardHeader>
        
        <CardContent className="relative z-10">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <motion.div 
                variants={numberVariants}
                className="figma-numeric"
              >
                {formattedValue}
              </motion.div>
              
              {trend && (
                <motion.div 
                  className={cn(
                    "flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full",
                    getTrendColor(trend.direction),
                    trend.direction === 'up' && "bg-green-100 text-green-700",
                    trend.direction === 'down' && "bg-red-100 text-red-700",
                    trend.direction === 'stable' && "figma-glass-card figma-body"
                  )}
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                >
                  {TrendIcon && <TrendIcon className="h-4 w-4" />}
                  <span>
                    {trend.direction === 'up' ? '+' : trend.direction === 'down' ? '-' : ''}
                    {formatNumber(trend.value)}
                  </span>
                  {trend.label && (
                    <span className="text-xs opacity-75">{trend.label}</span>
                  )}
                </motion.div>
              )}
            </div>
            
            {status && (
              <motion.div
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <Badge 
                  className={cn(
                    "capitalize text-xs font-semibold px-3 py-1 border-0 shadow-lg bg-gradient-to-r text-white",
                    statusGradient
                  )}
                >
                  {status}
                </Badge>
              </motion.div>
            )}
          </div>
        </CardContent>
        
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