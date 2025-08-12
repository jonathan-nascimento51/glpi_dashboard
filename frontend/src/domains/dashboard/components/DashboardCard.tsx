import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react';
import { StateWrapper } from '../../../shared/components/StateComponents';
import type { DashboardCardProps } from '../types/dashboardTypes';
import { ComponentState } from '../../../shared/types/states';

interface ExtendedDashboardCardProps extends DashboardCardProps {
  state?: ComponentState<number | string>;
  onRetry?: () => void;
  className?: string;
}

const getTrendIcon = (direction: 'up' | 'down' | 'stable') => {
  switch (direction) {
    case 'up': return TrendingUp;
    case 'down': return TrendingDown;
    default: return Minus;
  }
};

const getTrendColor = (direction: 'up' | 'down' | 'stable') => {
  switch (direction) {
    case 'up': return 'text-green-600';
    case 'down': return 'text-red-600';
    default: return 'text-gray-500';
  }
};

const getVariantStyles = (variant: 'default' | 'compact' | 'detailed') => {
  switch (variant) {
    case 'compact':
      return {
        container: 'p-3',
        title: 'text-sm font-medium text-gray-600',
        value: 'text-lg font-bold text-gray-900',
        subtitle: 'text-xs text-gray-500',
        trend: 'text-xs'
      };
    case 'detailed':
      return {
        container: 'p-6',
        title: 'text-base font-semibold text-gray-700',
        value: 'text-3xl font-bold text-gray-900',
        subtitle: 'text-sm text-gray-600',
        trend: 'text-sm'
      };
    default:
      return {
        container: 'p-4',
        title: 'text-sm font-medium text-gray-600',
        value: 'text-2xl font-bold text-gray-900',
        subtitle: 'text-sm text-gray-500',
        trend: 'text-sm'
      };
  }
};

export const DashboardCard: React.FC<ExtendedDashboardCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon: Icon,
  variant = 'default',
  state,
  onRetry,
  className = '',
  isLoading = false,
  error
}) => {
  const styles = getVariantStyles(variant);
  
  // Determinar estado baseado nas props ou estado explícito
  const cardState = state || {
    type: isLoading ? 'loading' : error ? 'error' : 'success',
    data: value,
    error: error ? new Error(error) : undefined
  } as ComponentState<number | string>;

  const isEmpty = !isLoading && !error && (value === 0 || value === '' || value == null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow ${className}`}
    >
      <StateWrapper
        isLoading={cardState.type === 'loading'}
        isError={cardState.type === 'error'}
        isEmpty={isEmpty}
        error={cardState.error}
        onRetry={onRetry}
        loadingProps={{ variant: 'skeleton' }}
        errorProps={{ variant: 'compact' }}
        emptyProps={{ 
          variant: 'compact',
          message: 'Sem dados disponíveis'
        }}
        className={styles.container}
      >
        <div className={styles.container}>
          {/* Header com título e ícone */}
          <div className="flex items-center justify-between mb-2">
            <h3 className={styles.title}>{title}</h3>
            {Icon && (
              <div className="p-2 bg-blue-50 rounded-lg">
                <Icon className="w-4 h-4 text-blue-600" />
              </div>
            )}
          </div>

          {/* Valor principal */}
          <div className="mb-2">
            <span className={styles.value}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </span>
          </div>

          {/* Subtitle e trend */}
          <div className="flex items-center justify-between">
            {subtitle && (
              <span className={styles.subtitle}>{subtitle}</span>
            )}
            
            {trend && (
              <div className={`flex items-center ${styles.trend} ${getTrendColor(trend.direction)}`}>
                {React.createElement(getTrendIcon(trend.direction), {
                  className: 'w-3 h-3 mr-1'
                })}
                <span>
                  {trend.value > 0 ? '+' : ''}{trend.value}%
                </span>
                {trend.period && (
                  <span className="ml-1 text-gray-400">({trend.period})</span>
                )}
              </div>
            )}
          </div>
        </div>
      </StateWrapper>
    </motion.div>
  );
};

/**
 * Componente especializado para métricas de nível
 */
interface LevelCardProps {
  level: string;
  metrics: {
    total: number;
    abertos: number;
    fechados: number;
    pendentes: number;
    tempo_medio_resolucao: number;
  };
  state?: ComponentState<any>;
  onRetry?: () => void;
  onClick?: () => void;
  className?: string;
}

export const LevelCard: React.FC<LevelCardProps> = ({
  level,
  metrics,
  state,
  onRetry,
  onClick,
  className = ''
}) => {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'N1': return 'bg-blue-50 border-blue-200 text-blue-700';
      case 'N2': return 'bg-green-50 border-green-200 text-green-700';
      case 'N3': return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      case 'N4': return 'bg-purple-50 border-purple-200 text-purple-700';
      default: return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const cardState = state || {
    type: 'success',
    data: metrics
  } as ComponentState<any>;

  const isEmpty = !metrics || metrics.total === 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      className={`bg-white rounded-lg border-2 ${getLevelColor(level)} cursor-pointer hover:shadow-lg transition-all ${className}`}
      onClick={onClick}
    >
      <StateWrapper
        isLoading={cardState.type === 'loading'}
        isError={cardState.type === 'error'}
        isEmpty={isEmpty}
        error={cardState.error}
        onRetry={onRetry}
        loadingProps={{ variant: 'skeleton' }}
        errorProps={{ variant: 'compact' }}
        emptyProps={{ 
          variant: 'compact',
          message: `Sem dados para ${level}`
        }}
      >
        <div className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold">{level}</h3>
            <div className="text-2xl font-bold">
              {metrics.total.toLocaleString()}
            </div>
          </div>

          {/* Métricas detalhadas */}
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Abertos:</span>
              <span className="font-medium">{metrics.abertos}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Fechados:</span>
              <span className="font-medium">{metrics.fechados}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Pendentes:</span>
              <span className="font-medium">{metrics.pendentes}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tempo médio:</span>
              <span className="font-medium">{metrics.tempo_medio_resolucao}h</span>
            </div>
          </div>
        </div>
      </StateWrapper>
    </motion.div>
  );
};