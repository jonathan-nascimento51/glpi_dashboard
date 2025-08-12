import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Award, Star, User } from 'lucide-react';
import { StateWrapper } from '../../../shared/components/StateComponents';
import type { TechnicianRankingProps, TechnicianRanking } from '../types/dashboardTypes';
import { ComponentState } from '../../../shared/types/states';

interface ExtendedTechnicianRankingProps extends TechnicianRankingProps {
  state?: ComponentState<TechnicianRanking[]>;
  onRetry?: () => void;
  className?: string;
}

const getRankIcon = (position: number) => {
  switch (position) {
    case 1: return Trophy;
    case 2: return Medal;
    case 3: return Award;
    default: return Star;
  }
};

const getRankColor = (position: number) => {
  switch (position) {
    case 1: return 'text-yellow-500 bg-yellow-50';
    case 2: return 'text-gray-500 bg-gray-50';
    case 3: return 'text-orange-500 bg-orange-50';
    default: return 'text-blue-500 bg-blue-50';
  }
};

const getSatisfactionColor = (score: number) => {
  if (score >= 4.5) return 'text-green-600 bg-green-50';
  if (score >= 4.0) return 'text-yellow-600 bg-yellow-50';
  if (score >= 3.5) return 'text-orange-600 bg-orange-50';
  return 'text-red-600 bg-red-50';
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  }
};

export const TechnicianRankingComponent: React.FC<ExtendedTechnicianRankingProps> = ({
  ranking,
  state,
  onRetry,
  maxItems = 10,
  className = '',
  isLoading = false,
  error
}) => {
  // Determinar estado baseado nas props ou estado explícito
  const rankingState = state || {
    type: isLoading ? 'loading' : error ? 'error' : 'success',
    data: ranking,
    error: error ? new Error(error) : undefined
  } as ComponentState<TechnicianRanking[]>;

  // Verificar se está vazio
  const isEmpty = !isLoading && !error && (!ranking || ranking.length === 0);

  // Limitar número de itens exibidos
  const displayedRanking = React.useMemo(() => {
    if (!ranking) return [];
    return ranking.slice(0, maxItems);
  }, [ranking, maxItems]);

  // Calcular estatísticas
  const stats = React.useMemo(() => {
    if (!ranking || ranking.length === 0) {
      return {
        totalTechnicians: 0,
        avgResolutionTime: 0,
        avgSatisfaction: 0,
        totalResolved: 0
      };
    }

    const totalResolved = ranking.reduce((sum, tech) => sum + tech.resolved_tickets, 0);
    const avgResolutionTime = ranking.reduce((sum, tech) => sum + tech.avg_resolution_time, 0) / ranking.length;
    const avgSatisfaction = ranking.reduce((sum, tech) => sum + tech.satisfaction_score, 0) / ranking.length;

    return {
      totalTechnicians: ranking.length,
      avgResolutionTime: Math.round(avgResolutionTime * 10) / 10,
      avgSatisfaction: Math.round(avgSatisfaction * 10) / 10,
      totalResolved
    };
  }, [ranking]);

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">Ranking de Técnicos</h2>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span>{stats.totalTechnicians} técnicos</span>
            <span>•</span>
            <span>{stats.totalResolved.toLocaleString()} resolvidos</span>
          </div>
        </div>

        <StateWrapper
          isLoading={rankingState.type === 'loading'}
          isError={rankingState.type === 'error'}
          isEmpty={isEmpty}
          error={rankingState.error}
          onRetry={onRetry}
          loadingProps={{ variant: 'skeleton' }}
          errorProps={{ 
            variant: 'default',
            message: 'Erro ao carregar ranking de técnicos'
          }}
          emptyProps={{ 
            variant: 'default',
            message: 'Nenhum técnico encontrado',
            description: 'Não há dados de técnicos para exibir no ranking.'
          }}
        >
          <motion.div
            initial="hidden"
            animate="visible"
            variants={containerVariants}
            className="space-y-4"
          >
            {/* Estatísticas resumidas */}
            <motion.div 
              variants={itemVariants}
              className="bg-gray-50 rounded-lg p-4 mb-6"
            >
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-gray-900">{stats.avgResolutionTime}h</div>
                  <div className="text-sm text-gray-600">Tempo Médio</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">{stats.avgSatisfaction}/5</div>
                  <div className="text-sm text-gray-600">Satisfação Média</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">{stats.totalResolved.toLocaleString()}</div>
                  <div className="text-sm text-gray-600">Total Resolvidos</div>
                </div>
              </div>
            </motion.div>

            {/* Lista de técnicos */}
            <div className="space-y-3">
              {displayedRanking.map((technician, index) => {
                const position = index + 1;
                const RankIcon = getRankIcon(position);
                const rankColor = getRankColor(position);
                const satisfactionColor = getSatisfactionColor(technician.satisfaction_score);

                return (
                  <motion.div
                    key={`${technician.name}-${index}`}
                    variants={itemVariants}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    {/* Posição e nome */}
                    <div className="flex items-center space-x-4">
                      <div className={`p-2 rounded-full ${rankColor}`}>
                        <RankIcon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900">{technician.name}</span>
                          <span className="text-sm text-gray-500">#{position}</span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {technician.resolved_tickets.toLocaleString()} tickets resolvidos
                        </div>
                      </div>
                    </div>

                    {/* Métricas */}
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="text-center">
                        <div className="font-medium text-gray-900">
                          {technician.avg_resolution_time}h
                        </div>
                        <div className="text-gray-500">Tempo médio</div>
                      </div>
                      <div className="text-center">
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${satisfactionColor}`}>
                          <Star className="w-3 h-3 mr-1" />
                          {technician.satisfaction_score.toFixed(1)}
                        </div>
                        <div className="text-gray-500 mt-1">Satisfação</div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Indicador de mais itens */}
            {ranking && ranking.length > maxItems && (
              <motion.div 
                variants={itemVariants}
                className="text-center py-4"
              >
                <div className="text-sm text-gray-500">
                  Mostrando {maxItems} de {ranking.length} técnicos
                </div>
                <button className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium">
                  Ver todos
                </button>
              </motion.div>
            )}
          </motion.div>
        </StateWrapper>
      </div>
    </div>
  );
};

/**
 * Componente compacto para exibir ranking em espaços menores
 */
interface CompactRankingProps {
  ranking: TechnicianRanking[];
  maxItems?: number;
  state?: ComponentState<TechnicianRanking[]>;
  onRetry?: () => void;
  className?: string;
}

export const CompactTechnicianRanking: React.FC<CompactRankingProps> = ({
  ranking,
  maxItems = 5,
  state,
  onRetry,
  className = ''
}) => {
  const rankingState = state || {
    type: 'success',
    data: ranking
  } as ComponentState<TechnicianRanking[]>;

  const isEmpty = !ranking || ranking.length === 0;
  const displayedRanking = ranking?.slice(0, maxItems) || [];

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <h3 className="text-sm font-medium text-gray-700 mb-3">Top Técnicos</h3>
      
      <StateWrapper
        isLoading={rankingState.type === 'loading'}
        isError={rankingState.type === 'error'}
        isEmpty={isEmpty}
        error={rankingState.error}
        onRetry={onRetry}
        loadingProps={{ variant: 'minimal' }}
        errorProps={{ variant: 'inline' }}
        emptyProps={{ variant: 'minimal', message: 'Sem dados' }}
      >
        <div className="space-y-2">
          {displayedRanking.map((technician, index) => {
            const position = index + 1;
            const RankIcon = getRankIcon(position);
            const rankColor = getRankColor(position);

            return (
              <div key={`${technician.name}-${index}`} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`p-1 rounded ${rankColor}`}>
                    <RankIcon className="w-3 h-3" />
                  </div>
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {technician.name}
                  </span>
                </div>
                <div className="text-xs text-gray-600">
                  {technician.resolved_tickets}
                </div>
              </div>
            );
          })}
        </div>
      </StateWrapper>
    </div>
  );
};