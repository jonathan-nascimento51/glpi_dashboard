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
    console.log(" LevelMetricsGrid - metrics.niveis:", metrics.niveis);
    if (metrics.niveis) {
      console.log(" LevelMetricsGrid - Keys de metrics.niveis:", Object.keys(metrics.niveis));
    }
  } else {
    console.log(" LevelMetricsGrid - metrics � null/undefined");
  }

  const levelMetrics = useMemo(() => {
    if (!metrics) {
      console.log(" LevelMetricsGrid - Sem metrics, retornando objeto vazio");
      return {};
    }

    console.log(" LevelMetricsGrid - Processando metrics:", metrics);
    // A API retorna os dados na estrutura: { niveis: { n1: {...}, n2: {...}, ... } }
    const niveisDados = metrics.niveis || {};
    console.log(" LevelMetricsGrid - Dados dos n�veis:", niveisDados);
    return niveisDados;
  }, [metrics]);

  if (!metrics) {
    return null;
  }

  return (
    <div className={cn("grid grid-cols-2 gap-4", className)}>
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

              <CardContent className="p-4">
                <div className="grid grid-cols-2 gap-3">
                  {/* Primeira linha: Novos e Pendentes */}
                  <div className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded-full bg-blue-100 dark:bg-blue-900/20">
                        <Users className="h-3 w-3 text-blue-600" />
                      </div>
                      <span className="text-xs font-medium text-muted-foreground">Novos</span>
                    </div>
                    <span className="text-sm font-semibold">{levelData.novos || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded-full bg-yellow-100 dark:bg-yellow-900/20">
                        <Clock className="h-3 w-3 text-yellow-600" />
                      </div>
                      <span className="text-xs font-medium text-muted-foreground">Pendentes</span>
                    </div>
                    <span className="text-sm font-semibold">{levelData.pendentes || 0}</span>
                  </div>
                  
                  {/* Segunda linha: Em Progresso e Resolvidos */}
                  <div className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded-full bg-orange-100 dark:bg-orange-900/20">
                        <AlertCircle className="h-3 w-3 text-orange-600" />
                      </div>
                      <span className="text-xs font-medium text-muted-foreground">Em Progresso</span>
                    </div>
                    <span className="text-sm font-semibold">{levelData.progresso || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded-full bg-green-100 dark:bg-green-900/20">
                        <CheckCircle className="h-3 w-3 text-green-600" />
                      </div>
                      <span className="text-xs font-medium text-muted-foreground">Resolvidos</span>
                    </div>
                    <span className="text-sm font-semibold">{levelData.resolvidos || 0}</span>
                  </div>
                </div>

                {levelData.total > 0 && (
                  <div className="pt-3 mt-3 border-t">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Taxa de Resolu��o</span>
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



