import React, { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn, formatNumber, getStatusIcon, getTrendIcon, getTrendColor, getStatusBadgeVariant } from '@/lib/utils';
import { type LucideIcon, Info } from 'lucide-react';
import { SimpleTooltip } from '@/components/ui/SimpleTooltip';

interface KPICardProps {
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
  size?: 'small' | 'medium' | 'large' | 'hero';
  priority?: 'critical' | 'high' | 'normal' | 'low';
  onClick?: () => void;
}

// Configurações de tamanho para hierarquia visual
const sizeConfig = {
  small: {
    container: 'col-span-1 row-span-1',
    title: 'text-xs font-medium',
    value: 'text-lg font-bold',
    icon: 'h-4 w-4',
    iconContainer: 'p-1.5',
    padding: 'p-3',
    trend: 'text-xs',
  },
  medium: {
    container: 'col-span-1 row-span-1',
    title: 'text-sm font-medium',
    value: 'text-2xl font-bold',
    icon: 'h-5 w-5',
    iconContainer: 'p-2',
    padding: 'p-4',
    trend: 'text-sm',
  },
  large: {
    container: 'col-span-2 row-span-1',
    title: 'text-base font-semibold',
    value: 'text-3xl font-bold',
    icon: 'h-6 w-6',
    iconContainer: 'p-2.5',
    padding: 'p-5',
    trend: 'text-sm',
  },
  hero: {
    container: 'col-span-2 row-span-2',
    title: 'text-lg font-bold',
    value: 'text-5xl font-bold',
    icon: 'h-8 w-8',
    iconContainer: 'p-3',
    padding: 'p-6',
    trend: 'text-base',
  },
};

// Configurações de prioridade
const priorityConfig = {
  critical: {
    ring: 'ring-2 ring-red-500',
    shadow: 'shadow-lg shadow-red-500/20',
    glow: 'before:absolute before:inset-0 before:rounded-2xl before:bg-red-500/10 before:blur-sm',
  },
  high: {
    ring: 'ring-1 ring-orange-300',
    shadow: 'shadow-md shadow-orange-500/10',
    glow: 'before:absolute before:inset-0 before:rounded-2xl before:bg-orange-500/5 before:blur-sm',
  },
  normal: {
    ring: '',
    shadow: 'shadow-sm',
    glow: '',
  },
  low: {
    ring: '',
    shadow: 'shadow-sm opacity-80',
    glow: '',
  },
};

const getStatusGradient = (status?: string) => {
  switch (status) {
    case 'new':
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

const getTrendExplanation = (trendValue: number, title: string): React.ReactNode => {
  const direction = trendValue > 0 ? 'up' : trendValue < 0 ? 'down' : 'neutral';

  if (direction === 'neutral') {
    return (
      <div className='text-left'>
        <div className='font-semibold mb-2'>📊 Tendência: {title}</div>
        <div className='text-sm space-y-1'>
          <div>• <strong>Variação:</strong> Sem mudança</div>
          <div>• <strong>Período:</strong> Comparação com últimos 7 dias</div>
          <div>• <strong>Status:</strong> Estável</div>
        </div>
      </div>
    );
  }

  return (
    <div className='text-left'>
      <div className='font-semibold mb-2'>📊 Tendência: {title}</div>
      <div className='text-sm space-y-1'>
        <div>• <strong>Variação:</strong> {direction === 'up' ? '↗️' : '↘️'} {Math.abs(trendValue).toFixed(1)}%</div>
        <div>• <strong>Período:</strong> vs. últimos 7 dias</div>
        <div>• <strong>Interpretação:</strong> {direction === 'up' ? 'Crescimento' : 'Redução'} em relação ao período anterior</div>
      </div>
    </div>
  );
};

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
    y: -4,
    scale: 1.02,
    transition: {
      duration: 0.3,
      ease: 'easeInOut' as const,
    },
  },
} as const;

const iconVariants = {
  hover: {
    scale: 1.1,
    rotate: 5,
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

export const KPICard = memo<KPICardProps>(function KPICard({
  title,
  value,
  status,
  trend,
  icon,
  className,
  size = 'medium',
  priority = 'normal',
  onClick,
}) {
  const StatusIcon = useMemo(() => icon || (status ? getStatusIcon(status) : null), [icon, status]);
  const TrendIcon = useMemo(() => (trend ? getTrendIcon(trend.direction) : null), [trend?.direction]);
  const statusGradient = useMemo(() => getStatusGradient(status), [status]);
  const formattedValue = useMemo(() => formatNumber(value), [value]);

  const sizeClasses = sizeConfig[size];
  const priorityClasses = priorityConfig[priority];

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
      className={cn(
        sizeClasses.container,
        priorityClasses.ring,
        priorityClasses.shadow,
        'relative cursor-pointer',
        priorityClasses.glow && 'before:content-[""]',
        className
      )}
    >
      <Card
        className={cn(
          'figma-glass-card relative overflow-hidden rounded-2xl shadow-none h-full',
          sizeClasses.padding
        )}
        onClick={handleCardClick}
      >
        {/* Gradient Background */}
        <div className={cn('absolute inset-0 bg-gradient-to-br opacity-5', statusGradient)} />

        {/* Priority Glow Effect */}
        {priority === 'critical' && (
          <div className='absolute inset-0 rounded-2xl'>
            <div className='absolute inset-0 rounded-2xl bg-gradient-to-r from-red-500/20 via-transparent to-red-500/20 opacity-30 blur-sm' />
          </div>
        )}

        <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2 relative z-10'>
          <CardTitle className={cn('figma-subheading uppercase tracking-wide', sizeClasses.title)}>
            {title}
          </CardTitle>
          {StatusIcon && (
            <motion.div
              variants={iconVariants}
              className={cn(
                'rounded-xl bg-gradient-to-br shadow-lg',
                statusGradient,
                sizeClasses.iconContainer
              )}
            >
              <StatusIcon className={cn('text-white', sizeClasses.icon)} />
            </motion.div>
          )}
        </CardHeader>

        <CardContent className='relative z-10 p-0'>
          <div className='flex items-center justify-between'>
            <div className='space-y-2 flex-1'>
              <motion.div variants={numberVariants} className={cn('figma-numeric', sizeClasses.value)}>
                {formattedValue}
              </motion.div>

              {trend && (
                <div className='flex items-center gap-2'>
                  <motion.div
                    className={cn(
                      'flex items-center gap-2 font-medium px-2 py-1 rounded-full',
                      getTrendColor(trend.direction),
                      trend.direction === 'up' && 'bg-green-100 text-green-700',
                      trend.direction === 'down' && 'bg-red-100 text-red-700',
                      trend.direction === 'stable' && 'figma-glass-card figma-body',
                      sizeClasses.trend
                    )}
                    whileHover={{ scale: 1.05 }}
                    transition={{ duration: 0.2 }}
                  >
                    {TrendIcon && <TrendIcon className='h-3 w-3' />}
                    <span>
                      {trend.value === 0
                        ? 'sem alteração'
                        : `${trend.direction === 'up' ? '+' : trend.direction === 'down' ? '-' : ''}${formatNumber(trend.value)}`}
                    </span>
                    {trend.label && trend.value !== 0 && size !== 'small' && (
                      <span className='text-xs opacity-75'>{trend.label}</span>
                    )}
                  </motion.div>

                  {size !== 'small' && (
                    <SimpleTooltip content={getTrendExplanation(trend.value, title)}>
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        className='cursor-help'
                        onClick={e => {
                          e.preventDefault();
                          e.stopPropagation();
                        }}
                      >
                        <Info className='h-3 w-3 text-gray-400 hover:text-gray-600' />
                      </motion.div>
                    </SimpleTooltip>
                  )}
                </div>
              )}
            </div>

            {status && size !== 'small' && (
              <motion.div whileHover={{ scale: 1.05 }} transition={{ duration: 0.2 }}>
                <Badge
                  variant={getStatusBadgeVariant(status)}
                  className='capitalize text-xs font-semibold px-2 py-1 border shadow-sm'
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