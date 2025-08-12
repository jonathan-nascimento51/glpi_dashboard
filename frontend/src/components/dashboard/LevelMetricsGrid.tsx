import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus, Users, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from "@/lib/utils";

interface LevelData {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
}

interface LevelMetrics {
  geral?: LevelData;
  n1?: LevelData;
  n2?: LevelData;
  n3?: LevelData;
  n4?: LevelData;
}

interface LevelMetricsGridProps {
  metrics?: {
    niveis?: LevelMetrics;
  } | null;
  className?: string;
}

const levelConfig = {
  geral: {
    title: "Geral",
    icon: Users,
    color: "bg-blue-500",
    bgColor: "bg-blue-50",
    textColor: "text-blue-700"
  },
  n1: {
    title: "Nível 1",
    icon: AlertCircle,
    color: "bg-green-500",
    bgColor: "bg-green-50",
    textColor: "text-green-700"
  },
  n2: {
    title: "Nível 2",
    icon: Clock,
    color: "bg-yellow-500",
    bgColor: "bg-yellow-50",
    textColor: "text-yellow-700"
  },
  n3: {
    title: "Nível 3",
    icon: TrendingUp,
    color: "bg-orange-500",
    bgColor: "bg-orange-50",
    textColor: "text-orange-700"
  },
  n4: {
    title: "Nível 4",
    icon: CheckCircle,
    color: "bg-red-500",
    bgColor: "bg-red-50",
    textColor: "text-red-700"
  }
} as const;

type LevelKey = keyof typeof levelConfig;

const formatNumber = (value: number | undefined): string => {
  if (value === undefined || value === null || isNaN(value)) return '0';
  return value.toLocaleString('pt-BR');
};

const getTrendIcon = (value: number) => {
  if (value > 0) return <TrendingUp className="w-3 h-3" />;
  if (value < 0) return <TrendingDown className="w-3 h-3" />;
  return <Minus className="w-3 h-3" />;
};

const getTrendColor = (value: number) => {
  if (value > 0) return "text-green-600";
  if (value < 0) return "text-red-600";
  return "text-gray-500";
};

export const LevelMetricsGrid: React.FC<LevelMetricsGridProps> = ({ metrics, className }) => {
  console.log('🔍 LevelMetricsGrid - Dados recebidos:', {
    metrics,
    metricsType: typeof metrics,
    metricsKeys: metrics ? Object.keys(metrics) : 'null',
    hasNiveis: !!(metrics?.niveis),
    niveisType: typeof metrics?.niveis,
    niveisKeys: metrics?.niveis ? Object.keys(metrics.niveis) : 'niveis não encontrado'
  });

  const processedData = useMemo(() => {
    console.log('🔄 LevelMetricsGrid useMemo - Iniciando processamento...');
    
    // Validação robusta dos dados de entrada
    if (!metrics) {
      console.warn('❌ LevelMetricsGrid - metrics é null/undefined');
      return [];
    }

    if (!metrics.niveis) {
      console.warn('❌ LevelMetricsGrid - metrics.niveis não encontrado');
      console.log('📋 Estrutura completa de metrics:', JSON.stringify(metrics, null, 2));
      return [];
    }

    if (typeof metrics.niveis !== 'object') {
      console.error('❌ LevelMetricsGrid - metrics.niveis não é um objeto:', typeof metrics.niveis);
      return [];
    }

    const niveis = metrics.niveis;
    console.log('✅ LevelMetricsGrid - Dados de níveis encontrados:', niveis);

    // Processar cada nível configurado
    const result = Object.entries(levelConfig).map(([key, config]) => {
      const levelKey = key as LevelKey;
      const rawLevelData = niveis[levelKey];
      
      console.log(`📊 Processando nível ${levelKey}:`, {
        rawData: rawLevelData,
        dataType: typeof rawLevelData,
        hasData: !!rawLevelData
      });
      
      // Validar e processar dados do nível
      const validatedData = validateLevelData(rawLevelData);
      
      console.log(`✅ Nível ${levelKey} processado:`, validatedData);
      
      return {
        key: levelKey,
        config,
        data: validatedData
      };
    });
    
    console.log('🎯 LevelMetricsGrid - Processamento concluído:', {
      totalLevels: result.length,
      processedData: result
    });
    
    return result;
  }, [metrics]);

  // Estado de loading
  if (!metrics) {
    console.log('🔄 LevelMetricsGrid - Renderizando estado de loading');
    return (
      <Card className={cn("figma-glass-card shadow-none", className)}>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            Métricas por Nível
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-500 mb-2">
              <Users className="w-12 h-12 mx-auto opacity-50 animate-pulse" />
            </div>
            <p className="text-gray-600">Carregando métricas...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Estado de erro/dados indisponíveis
  if (!metrics.niveis || processedData.length === 0) {
    console.log('❌ LevelMetricsGrid - Renderizando estado de erro');
    return (
      <Card className={cn("figma-glass-card shadow-none", className)}>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            Métricas por Nível
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-500 mb-2">
              <AlertCircle className="w-12 h-12 mx-auto opacity-50" />
            </div>
            <p className="text-gray-600">Dados não disponíveis</p>
            <p className="text-sm text-gray-500 mt-1">Verifique a conexão com o servidor</p>
            <div className="mt-4 p-3 bg-gray-50 rounded-lg text-left">
              <p className="text-xs text-gray-500 font-mono">
                Debug: {metrics.niveis ? 'niveis existe mas vazio' : 'niveis não encontrado'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Filtrar apenas os níveis que têm dados válidos
  const levelsWithData = processedData.filter(({ data }) => {
    return data.total > 0 || data.novos > 0 || data.pendentes > 0 || data.progresso > 0 || data.resolvidos > 0;
  });

  console.log('🎯 LevelMetricsGrid - Níveis com dados para renderizar:', levelsWithData.map(({ key }) => key));

  if (levelsWithData.length === 0) {
    return (
      <Card className={cn("figma-glass-card shadow-none", className)}>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            Métricas por Nível
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-500 mb-2">
              <AlertCircle className="w-12 h-12 mx-auto opacity-50" />
            </div>
            <p className="text-gray-600">Nenhum dado disponível</p>
            <p className="text-sm text-gray-500 mt-1">Todos os níveis estão zerados</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("figma-glass-card shadow-none", className)}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">
          Métricas por Nível
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className={cn(
          "grid gap-4",
          levelsWithData.length === 1 ? "grid-cols-1" :
          levelsWithData.length === 2 ? "grid-cols-2" :
          levelsWithData.length === 3 ? "grid-cols-3" :
          "grid-cols-2"
        )}>
          {levelsWithData.map(({ key, config, data }) => {
            const Icon = config.icon;
            
            return (
              <div
                key={key}
                className={cn(
                  "p-4 rounded-lg border transition-all duration-200 hover:shadow-md",
                  config.bgColor
                )}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={cn("p-2 rounded-full", config.color)}>
                      <Icon className="w-4 h-4 text-white" />
                    </div>
                    <h3 className={cn("font-semibold text-sm", config.textColor)}>
                      {config.title}
                    </h3>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    Total: {formatNumber(data.total)}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Novos:</span>
                    <span className="font-medium">{formatNumber(data.novos)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pendentes:</span>
                    <span className="font-medium">{formatNumber(data.pendentes)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Em Progresso:</span>
                    <span className="font-medium">{formatNumber(data.progresso)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resolvidos:</span>
                    <span className="font-medium text-green-600">{formatNumber(data.resolvidos)}</span>
                  </div>
                </div>
                
                {data.total > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600">Taxa de Resolução:</span>
                      <span className="font-semibold text-green-600">
                        {Math.round((data.resolvidos / data.total) * 100)}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

// Função para validar e processar dados de nível
function validateLevelData(data: any): LevelData {
  if (!data || typeof data !== 'object') {
    console.warn('🔍 LevelMetricsGrid - Dados de nível inválidos:', data);
    return {
      novos: 0,
      pendentes: 0,
      progresso: 0,
      resolvidos: 0,
      total: 0
    };
  }

  const safeNumber = (value: any): number => {
    const num = Number(value);
    return isNaN(num) ? 0 : num;
  };

  return {
    novos: safeNumber(data.novos),
    pendentes: safeNumber(data.pendentes),
    progresso: safeNumber(data.progresso),
    resolvidos: safeNumber(data.resolvidos),
    total: safeNumber(data.total)
  };
}



