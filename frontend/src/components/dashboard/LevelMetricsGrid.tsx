import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Clock, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import { MetricsData } from '@/types';
import { cn, getStatusBadgeVariant } from '@/lib/utils';
import TrendIndicator, { parseTrendFromAPI } from '@/components/ui/TrendIndicator';

interface LevelMetricsGridProps {
  metrics?: MetricsData & {
    tendencias?: {
      novos: string;
      pendentes: string;
      progresso: string;
      resolvidos: string;
    };
  };
  className?: string;
}

const levelConfig = {
  n1: {
    title: 'Nível N1',
    color: 'from-slate-600 to-slate-700',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
    textColor: 'text-slate-900 dark:text-slate-100 font-bold',
  },
  n2: {
    title: 'Nível N2',
    color: 'from-slate-700 to-slate-800',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
    textColor: 'text-slate-900 dark:text-slate-100 font-bold',
  },
  n3: {
    title: 'Nível N3',
    color: 'from-slate-500 to-slate-600',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
    textColor: 'text-slate-900 dark:text-slate-100 font-bold',
  },
  n4: {
    title: 'Nível N4',
    color: 'from-slate-800 to-slate-900',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
    textColor: 'text-slate-900 dark:text-slate-100 font-bold',
  },
};

const statusConfig = {
  novos: {
    icon: AlertCircle,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30 border-0',
    iconColor: 'text-blue-600 dark:text-blue-400',
    label: 'Novos',
  },
  progresso: {
    icon: Clock,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/30 border-0',
    iconColor: 'text-yellow-600 dark:text-yellow-400',
    label: 'Em Progresso',
  },
  pendentes: {
    icon: Users,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'bg-red-100 dark:bg-red-900/30 border-0',
    iconColor: 'text-red-600 dark:text-red-400',
    label: 'Pendentes',
  },
  resolvidos: {
    icon: CheckCircle,
    color: 'text-gray-900 dark:text-gray-100',
    bgColor: 'bg-green-100 dark:bg-green-900/30 border-0',
    iconColor: 'text-green-600 dark:text-green-400',
    label: 'Resolvidos',
  },
};

// Variantes de animação movidas para fora do componente
const itemVariants = {
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

const statusVariants = {
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: 'easeInOut' as const,
    },
  },
} as const;

// Componente StatusItem memoizado
const StatusItem = React.memo<{
  status: string;
  statusConf: (typeof statusConfig)[keyof typeof statusConfig];
  value: number | undefined;
  trendData?: { trend: 'up' | 'down' | 'stable'; percentage: number };
}>(function StatusItem({ status, statusConf, value, trendData }) {
  const Icon = statusConf.icon;

  return (
    <motion.div
      key={`status-item-${status}`}
      variants={statusVariants}
      whileHover='hover'
      className='flex flex-col items-center justify-center p-2 rounded-lg figma-glass-card min-h-[60px] border border-gray-100/50 dark:border-gray-800/50 cursor-pointer text-center'
    >
      <div className='flex items-center gap-1 mb-1'>
        <motion.div
          className={`p-1 rounded-lg ${statusConf.bgColor} shadow-sm`}
          whileHover={{ scale: 1.1 }}
          transition={{ duration: 0.2 }}
        >
          <Icon className={`h-3 w-3 ${statusConf.iconColor}`} />
        </motion.div>
        <span className='text-xs font-medium text-gray-700 dark:text-gray-300 truncate'>
          {statusConf.label}
        </span>
      </div>
      <div className='flex flex-col items-center gap-1'>
        <Badge
          variant={getStatusBadgeVariant(status)}
          className='text-xs px-2 py-1 font-medium border'
        >
          {value || 0}
        </Badge>
        {trendData && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
          >
            <TrendIndicator
              trend={trendData.trend}
              percentage={trendData.percentage}
              size='sm'
              className='text-xs'
            />
          </motion.div>
        )}
      </div>
    </motion.div>
  );
});

// Componente LevelCard memoizado
const LevelCard = React.memo<{
  level: string;
  levelData: any;
  config: (typeof levelConfig)[keyof typeof levelConfig];
  tendencias?: {
    novos: string;
    pendentes: string;
    progresso: string;
    resolvidos: string;
  };
}>(function LevelCard({ level, levelData, config, tendencias }) {
  const total = useMemo(() => {
    return Object.values(levelData).reduce((sum: number, value) => sum + (Number(value) || 0), 0);
  }, [levelData]);

  return (
    <motion.div
      key={`level-motion-${level}`}
      variants={itemVariants}
      initial='hidden'
      animate='visible'
      whileHover='hover'
      className='h-full flex cursor-pointer'
    >
      <Card className='figma-glass-card border-0 shadow-none h-full w-full flex flex-col relative overflow-hidden'>
        <CardHeader className='pb-3 px-4 pt-4 flex-shrink-0'>
          <div className='flex items-center justify-between relative z-10'>
            <CardTitle className='text-lg font-semibold flex items-center gap-3'>
              <motion.div
                variants={iconVariants}
                className={`p-2 rounded-lg bg-gradient-to-br shadow-sm ${config.color}`}
              >
                <TrendingUp className='h-5 w-5 text-white' />
              </motion.div>
              <span className='whitespace-nowrap'>{config.title}</span>
            </CardTitle>
            <motion.div whileHover={{ scale: 1.05 }} transition={{ duration: 0.2 }}>
              <Badge
                variant={getStatusBadgeVariant('info')}
                className='text-sm px-3 py-1.5 font-bold border'
              >
                {total}
              </Badge>
            </motion.div>
          </div>
        </CardHeader>

        <CardContent className='px-3 pb-3 flex-1 relative z-10'>
          <div className='grid grid-cols-2 gap-2 w-full h-full'>
            {Object.entries(statusConfig).map(([status, statusConf]) => {
              const value = levelData[status as keyof typeof levelData];
              const trendString = tendencias?.[status as keyof typeof tendencias];
              const trendData = trendString ? parseTrendFromAPI(trendString) : undefined;

              return (
                <StatusItem
                  key={`level-${level}-${status}`}
                  status={status}
                  statusConf={statusConf}
                  value={value}
                  trendData={trendData}
                />
              );
            })}
          </div>
        </CardContent>

        {/* Gradient Background */}
        <div
          className={cn('absolute inset-0 bg-gradient-to-br opacity-5 rounded-2xl', config.color)}
        />

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

export const LevelMetricsGrid = React.memo<LevelMetricsGridProps>(function LevelMetricsGrid({
  metrics,
  className,
}) {
  // Verificação de segurança para evitar erros
  if (!metrics || !metrics.niveis) {
    return (
      <Card className={cn('figma-glass-card h-full shadow-none', className)}>
        <CardContent className='flex items-center justify-center h-48'>
          <div className='text-center'>
            <div className='figma-body mb-2'>📊</div>
            <div className='figma-body'>Carregando métricas por nível...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Memoizar as entradas dos níveis
  const levelEntries = useMemo(() => {
    return Object.entries(metrics.niveis || {});
  }, [metrics.niveis]);

  return (
    <div className={cn('h-full flex flex-col overflow-hidden', className)}>
      <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-2 gap-2 sm:gap-3 lg:gap-2 xl:gap-3 h-full overflow-hidden p-1'>
        {levelEntries.map(([level, levelData]) => {
          const config = levelConfig[level as keyof typeof levelConfig];
          if (!config || !levelData) return null;

          return (
            <LevelCard
              key={`level-card-${level}`}
              level={level}
              levelData={levelData}
              config={config}
              tendencias={metrics.tendencias}
            />
          );
        })}
      </div>
    </div>
  );
});
