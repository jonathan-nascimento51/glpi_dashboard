import React from 'react';
import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn, formatNumber, getStatusIcon, getTrendIcon, getTrendColor, getStatusBadgeVariant } from '@/lib/utils';
import { type LucideIcon, Info, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { SimpleTooltip } from '@/components/ui/SimpleTooltip';

interface StatusCardProps {
  title: string;
  value: number;
  status?: string;
  trend?: {
    direction: 'up' | 'down' | 'stable';
    value: number;
    label?: string;
  };
  icon?: LucideIcon;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed' | 'gradient';
  showProgress?: boolean;
  maxValue?: number;
  onClick?: () => void;
}

// Função auxiliar definida fora do componente para evitar recriação
const getStatusGradient = (status?: string) => {
  switch (status) {
    case 'online':
      return 'from-green-500 to-emerald-600';
    case 'offline':
      return 'from-red-500 to-rose-600';
    case 'active':
      return 'from-blue-500 to-cyan-600';
    case 'progress':
      return 'from-yellow-500 to-orange-600';
    case 'pending':
      return 'from-orange-500 to-red-600';
    case 'resolved':
      return 'from-green-500 to-emerald-600';
    default:
      return 'from-gray-500 to-slate-600';
  }
};

// Função para determinar a direção da tendência
const getTrendDirection = (trendValue: number): 'up' | 'down' | 'neutral' => {
  if (trendValue > 0) return 'up';
  if (trendValue < 0) return 'down';
  return 'neutral';
};

// Função para gerar explicação da tendência
const getTrendExplanation = (trendValue: number, title: string): React.ReactNode => {
  const direction = getTrendDirection(trendValue);

  if (direction === 'neutral') {
    return (
      <div className='text-left'>
        <div className='font-semibold mb-2'>📊 Tendência: {title}</div>
        <div className='text-sm space-y-1'>
          <div>
            • <strong>Variação:</strong> Sem mudança
          </div>
          <div>
            • <strong>Período:</strong> Comparação com últimos 7 dias
          </div>
          <div>
            • <strong>Status:</strong> Estável
          </div>
        </div>
      </div>
    );
  }

  const isExtreme = Math.abs(trendValue) > 500;
  const explanation = isExtreme
    ? 'Valor muito alto devido à comparação entre dados históricos completos vs. período específico de 7 dias'
    : 'Variação normal baseada na comparação com o período anterior';

  return (
    <div className='text-left'>
      <div className='font-semibold mb-2'>📊 Tendência: {title}</div>
      <div className='text-sm space-y-1'>
        <div>
          • <strong>Variação:</strong> {direction === 'up' ? '↗️' : '↘️'}{' '}
          {Math.abs(trendValue).toFixed(1)}%
        </div>
        <div>
          • <strong>Período:</strong> vs. últimos 7 dias
        </div>
        <div>
          • <strong>Interpretação:</strong> {explanation}
        </div>
        {isExtreme && (
          <div className='mt-2 p-2 bg-slate-800 border border-slate-600 rounded text-xs text-slate-200'>
            <strong className='text-amber-400'>💡 Nota:</strong> Percentuais altos são normais
            quando comparamos dados históricos completos com períodos específicos.
          </div>
        )}
      </div>
    </div>
  );
};

// Variantes de animação definidas fora do componente
const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut' as const,
    },
  },
  hover: {
    y: -8,
    scale: 1.03,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const iconVariants = {
  hover: {
    scale: 1.2,
    rotate: 10,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const numberVariants = {
  hidden: { scale: 0 },
  visible: {
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut' as const,
      delay: 0.2,
    },
  },
} as const;

export const StatusCard = memo<StatusCardProps>(function StatusCard({
  title,
  value,
  status,
  trend,
  icon,
  className,
  variant: _ = 'default',
  onClick,
}) {
  // Memoizar ícones para evitar recálculos
  const StatusIcon = useMemo(() => icon || (status ? getStatusIcon(status) : null), [icon, status]);

  const TrendIcon = useMemo(
    () => (trend ? getTrendIcon(trend.direction) : null),
    [trend?.direction]
  );

  // Memoizar gradiente do status
  const statusGradient = useMemo(() => getStatusGradient(status), [status]);

  // Memoizar valor formatado
  const formattedValue = useMemo(() => {
    return formatNumber(value);
  }, [value]);

  // Handler para clique no card
  const handleCardClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onClick?.();
  };

  return (
    <motion.div
      variants={cardVariants}
      initial='hidden'
      animate='visible'
      whileHover='hover'
      className={cn('cursor-pointer', className)}
    >
      <Card
        className='figma-glass-card relative overflow-hidden rounded-2xl shadow-none'
        onClick={handleCardClick}
      >
        {/* Gradient Background */}
        <div className={cn('absolute inset-0 bg-gradient-to-br opacity-5', statusGradient)} />

        {/* Animated Border */}
        <div className='absolute inset-0 rounded-2xl'>
          <div
            className={cn(
              'absolute inset-0 rounded-2xl bg-gradient-to-r opacity-20 blur-sm',
              statusGradient
            )}
          />
        </div>

        <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-3 relative z-10'>
          <CardTitle className='figma-subheading uppercase tracking-wide'>{title}</CardTitle>
          {StatusIcon && (
            <motion.div
              variants={iconVariants}
              className={cn('p-2 rounded-xl bg-gradient-to-br shadow-lg', statusGradient)}
            >
              <StatusIcon className='h-5 w-5 text-white' />
            </motion.div>
          )}
        </CardHeader>

        <CardContent className='relative z-10'>
          <div className='flex items-center justify-between'>
            <div className='space-y-2'>
              <motion.div variants={numberVariants} className='figma-numeric'>
                {formattedValue}
              </motion.div>

              {trend && (
                <div className='flex items-center gap-2'>
                  <motion.div
                    className={cn(
                      'flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full',
                      getTrendColor(trend.direction),
                      trend.direction === 'up' && 'bg-green-100 text-green-700',
                      trend.direction === 'down' && 'bg-red-100 text-red-700',
                      trend.direction === 'stable' && 'figma-glass-card figma-body'
                    )}
                    whileHover={{ scale: 1.05 }}
                    transition={{ duration: 0.2 }}
                  >
                    {TrendIcon && <TrendIcon className='h-4 w-4' />}
                    <span>
                      {trend.value === 0
                        ? 'sem alteração'
                        : `${trend.direction === 'up' ? '+' : trend.direction === 'down' ? '-' : ''}${formatNumber(trend.value)}`}
                    </span>
                    {trend.label && trend.value !== 0 && (
                      <span className='text-xs opacity-75'>{trend.label}</span>
                    )}
                  </motion.div>

                  <SimpleTooltip content={getTrendExplanation(trend.value, title)}>
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className='cursor-help'
                      onClick={e => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      <Info className='h-4 w-4 text-gray-400 hover:text-gray-600' />
                    </motion.div>
                  </SimpleTooltip>
                </div>
              )}
            </div>

            {status && (
              <motion.div whileHover={{ scale: 1.05 }} transition={{ duration: 0.2 }}>
                <Badge
                  variant={getStatusBadgeVariant(status)}
                  className='capitalize text-xs font-semibold px-3 py-1 border shadow-sm'
                >
                  {status}
                </Badge>
              </motion.div>
            )}
          </div>
        </CardContent>

        {/* Shine Effect */}
        <motion.div
          className='absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 opacity-0'
          whileHover={{
            opacity: [0, 1, 0],
            x: [-100, 300],
          }}
          transition={{ duration: 0.6 }}
        />
      </Card>
    </motion.div>
  );
});
