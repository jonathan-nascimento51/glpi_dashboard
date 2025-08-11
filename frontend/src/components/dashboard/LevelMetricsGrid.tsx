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
    title: "Nivel N1",
    color: "from-slate-600 to-slate-700",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  n2: {
    title: "Nivel N2",
    color: "from-slate-700 to-slate-800",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  n3: {
    title: "Nivel N3",
    color: "from-slate-800 to-slate-900",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  n4: {
    title: "Nivel N4",
    color: "from-slate-900 to-black",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-900 dark:text-slate-100 font-bold"
  },
  geral: {
    title: "Geral",
    color: "from-blue-600 to-blue-700",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    textColor: "text-blue-900 dark:text-blue-100 font-bold"
  }
}

const statusConfig = {
  novos: {
    label: "Novos",
    icon: Users,
    color: "text-blue-600",
    bgColor: "bg-blue-100 dark:bg-blue-900/20"
  },
  pendentes: {
    label: "Pendentes",
    icon: Clock,
    color: "text-yellow-600",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/20"
  },
  progresso: {
    label: "Em Progresso",
    icon: AlertCircle,
    color: "text-orange-600",
    bgColor: "bg-orange-100 dark:bg-orange-900/20"
  },
  resolvidos: {
    label: "Resolvidos",
    icon: CheckCircle,
    color: "text-green-600",
    bgColor: "bg-green-100 dark:bg-green-900/20"
  }
}

export const LevelMetricsGrid: React.FC<LevelMetricsGridProps> = ({ 
  metrics, 
  className 
}) => {
  // Debug: Log dos dados recebidos
  console.log(" LevelMetricsGrid - metrics recebido:", metrics);
  console.log(" LevelMetricsGrid - Tipo de metrics:", typeof metrics);
  if (metrics) {
    console.log(" LevelMetricsGrid - Keys de metrics:", Object.keys(metrics));
  } else {
    console.log(" LevelMetricsGrid - metrics e null/undefined");
  }

  const levelMetrics = useMemo(() => {
    if (!metrics) {
      console.log(" LevelMetricsGrid - Sem metrics, retornando objeto vazio");
      return {};
    }
    
    console.log(" LevelMetricsGrid - Processando metrics:", metrics);
    return metrics;
  }, [metrics]);

  if (!metrics) {
    return (
      <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4", className)}>
        {Object.entries(levelConfig).map(([level, config]) => (
          <Card key={level} className="animate-pulse">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {config.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="h-4 bg-muted rounded w-3/4"></div>
              <div className="h-4 bg-muted rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4", className)}>
      {Object.entries(levelConfig).map(([level, config]) => {
        const levelData = levelMetrics[level as keyof typeof levelMetrics] || {
          novos: 0,
          pendentes: 0,
          progresso: 0,
          resolvidos: 0,
          total: 0
        };

        console.log(` LevelMetricsGrid - Dados para ${level}:`, levelData);

        return (
          <motion.div
            key={level}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: Object.keys(levelConfig).indexOf(level) * 0.1 }}
          >
            <Card className={cn(
              "relative overflow-hidden transition-all duration-300 hover:shadow-lg",
              config.bgColor
            )}>
              <div className={cn(
                "absolute inset-0 bg-gradient-to-br opacity-5",
                config.color
              )} />
              
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className={cn(
                    "text-sm font-semibold",
                    config.textColor
                  )}>
                    {config.title}
                  </CardTitle>
                  <Badge variant="outline" className="text-xs">
                    {levelData.total || 0}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                {Object.entries(statusConfig).map(([status, statusConf]) => {
                  const Icon = statusConf.icon;
                  const value = levelData[status as keyof typeof levelData] || 0;
                  
                  return (
                    <div key={status} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={cn(
                          "p-1 rounded-full",
                          statusConf.bgColor
                        )}>
                          <Icon className={cn(
                            "h-3 w-3",
                            statusConf.color
                          )} />
                        </div>
                        <span className="text-xs font-medium text-muted-foreground">
                          {statusConf.label}
                        </span>
                      </div>
                      <span className="text-sm font-semibold">
                        {value}
                      </span>
                    </div>
                  );
                })}
                
                {levelData.total > 0 && (
                  <div className="pt-2 border-t">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Taxa de Resolucao</span>
                      <span className="font-semibold">
                        {Math.round((levelData.resolvidos / levelData.total) * 100)}%
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
};
