import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn, formatNumber } from '@/lib/utils';
import { Trophy, Medal, Award, Star, Users, Zap, Shield, Wrench, Settings } from 'lucide-react';
import { usePerformanceMonitoring, useRenderTracker } from '../../hooks/usePerformanceMonitoring';
import { performanceMonitor } from '../../utils/performanceMonitor';

interface TechnicianRanking {
  id: string;
  name: string;
  level: string;
  total: number;
  rank: number;
}

interface RankingTableProps {
  data: TechnicianRanking[];
  title?: string;
  className?: string;
  filters?: {
    start_date?: string;
    end_date?: string;
    level?: string;
    limit?: number;
  };
}

// Função auxiliar para obter estilos de nível movida para fora do componente
function getLevelStyle(level?: string) {
  switch (level) {
    case 'N4': // Expert - Azul profissional
      return {
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        accentColor: 'bg-blue-500',
        textColor: 'text-blue-700',
        icon: Zap,
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600',
      };
    case 'N3': // Sênior - Verde confiável
      return {
        bgColor: 'bg-emerald-50',
        borderColor: 'border-emerald-200',
        accentColor: 'bg-emerald-500',
        textColor: 'text-emerald-700',
        icon: Shield,
        iconBg: 'bg-emerald-100',
        iconColor: 'text-emerald-600',
      };
    case 'N2': // Pleno - Laranja equilibrado
      return {
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        accentColor: 'bg-orange-500',
        textColor: 'text-orange-700',
        icon: Wrench,
        iconBg: 'bg-orange-100',
        iconColor: 'text-orange-600',
      };
    case 'N1': // Júnior - Roxo motivacional
      return {
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-200',
        accentColor: 'bg-purple-500',
        textColor: 'text-purple-700',
        icon: Settings,
        iconBg: 'bg-purple-100',
        iconColor: 'text-purple-600',
      };
    default: // Outros - Cinza neutro
      return {
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        accentColor: 'bg-gray-500',
        textColor: 'text-gray-700',
        icon: Star,
        iconBg: 'bg-gray-100',
        iconColor: 'text-gray-600',
      };
  }
}

// Variantes de animação movidas para fora do componente
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
} as const;

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
    y: -2,
    scale: 1.01,
    zIndex: 5,
    transition: {
      duration: 0.3,
      ease: 'easeOut' as const,
    },
  },
} as const;

// const iconVariants = {
//   hover: {
//     scale: 1.3,
//     rotate: 15,
//     transition: {
//       duration: 0.2,
//       ease: "easeOut" as const
//     }
//   }
// } as const

// Componente TechnicianCard memoizado
const TechnicianCard = React.memo<{
  technician: TechnicianRanking;
  index: number;
}>(function TechnicianCard({ technician, index }) {
  const levelStyle = getLevelStyle(technician.level);
  const position = index + 1;
  const isTopThree = position <= 3;

  const formattedName = useMemo(() => {
    const nameParts = technician.name.split(' ');
    const firstName = nameParts[0] || '';
    const lastNameInitial =
      nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0).toUpperCase() + '.' : '';
    return `${firstName} ${lastNameInitial}`.trim();
  }, [technician.name]);

  const performanceIndicators = useMemo(() => {
    return Array.from({ length: Math.min(3, Math.max(1, 4 - Math.ceil(position / 3))) });
  }, [position]);

  return (
    <motion.div
      key={technician.id}
      variants={cardVariants}
      whileHover='hover'
      className={cn(
        'flex-shrink-0 w-48 flex flex-col p-4 rounded-lg border transition-all duration-200',
        'cursor-pointer relative group hover:shadow-md',
        levelStyle.bgColor,
        levelStyle.borderColor,
        isTopThree && 'ring-2 ring-opacity-20',
        isTopThree && position === 1 && 'ring-yellow-400',
        isTopThree && position === 2 && 'ring-gray-400',
        isTopThree && position === 3 && 'ring-amber-400'
      )}
    >
      {/* Header - Posição e Nível */}
      <div className='flex items-center justify-between mb-3'>
        {/* Indicador de posição */}
        <div
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
            isTopThree ? 'text-white' : 'text-gray-600 bg-gray-100',
            position === 1 && 'bg-yellow-500',
            position === 2 && 'bg-gray-400',
            position === 3 && 'bg-amber-500',
            position > 3 && 'bg-gray-100'
          )}
        >
          {position <= 3 && position === 1 && <Trophy className='w-4 h-4' />}
          {position <= 3 && position === 2 && <Medal className='w-4 h-4' />}
          {position <= 3 && position === 3 && <Award className='w-4 h-4' />}
          {position > 3 && position}
        </div>

        {/* Nível */}
        {technician.level && (
          <div className='flex items-center space-x-1'>
            <div className={cn('p-1 rounded-full', levelStyle.iconBg)}>
              <levelStyle.icon className={cn('w-3 h-3', levelStyle.iconColor)} />
            </div>
            <Badge
              className={cn(
                'text-xs font-medium text-white border-0 px-1.5 py-0.5',
                levelStyle.accentColor
              )}
            >
              {technician.level}
            </Badge>
          </div>
        )}
      </div>

      {/* Nome do técnico */}
      <div className='text-center mb-3'>
        <div className='font-medium text-gray-900 text-sm leading-tight'>{formattedName}</div>
      </div>

      {/* Total de chamados */}
      <div className='text-center'>
        <div className={cn('text-2xl font-bold mb-1', levelStyle.textColor)}>
          {formatNumber(technician.total)}
        </div>
        <div className='text-xs text-gray-500 mb-2'>chamados</div>

        {/* Indicador de performance */}
        <div className='flex justify-center space-x-1'>
          {performanceIndicators.map((_, i) => (
            <div key={i} className={cn('w-1.5 h-1.5 rounded-full', levelStyle.accentColor)} />
          ))}
        </div>
      </div>
    </motion.div>
  );
});

export const RankingTable = React.memo<RankingTableProps>(function RankingTable({
  data,
  title: _ = 'Ranking de Técnicos',
  className,
  filters,
}) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('RankingTable');
  const { trackRender } = useRenderTracker('RankingTable');

  // Track component renders
  useEffect(() => {
    trackRender();
    measureRender(() => {
      performanceMonitor.markComponentRender('RankingTable', {
        technicianCount: data.length,
        hasData: data.length > 0,
      });
    });
  }, [data, trackRender, measureRender]);

  // Pegar todos os técnicos e ordenar por número de chamados - memoizado
  const topTechnicians = useMemo(() => {
    return [...data].sort((a, b) => b.total - a.total);
  }, [data]);

  // Estatísticas por nível para o cabeçalho - memoizado
  const levelStats = useMemo(() => {
    return topTechnicians.reduce(
      (acc, tech) => {
        const level = tech.level || 'Outros';
        acc[level] = (acc[level] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>
    );
  }, [topTechnicians]);

  // Callback memoizado para o scroll horizontal
  const handleWheel = useCallback((e: WheelEvent) => {
    e.preventDefault();
    const container = scrollContainerRef.current;
    if (container) {
      container.scrollLeft += e.deltaY;
    }
  }, []);

  // Adicionar scroll horizontal com roda do mouse
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    container.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      container.removeEventListener('wheel', handleWheel);
    };
  }, [handleWheel]);

  return (
    <Card
      className={cn(
        'figma-ranking-tecnicos w-full h-full flex flex-col rounded-2xl shadow-none',
        className
      )}
    >
      <CardHeader className='px-5 pt-4 pb-2 flex-shrink-0'>
        <div className='flex items-center justify-between'>
          <div className='flex flex-col gap-2'>
            <CardTitle className='figma-heading-large flex items-center gap-2'>
              <div className='p-2 rounded-xl bg-gradient-to-br from-slate-500 to-slate-600 shadow-lg'>
                <Users className='h-5 w-5 text-white' />
              </div>
              Ranking de Técnicos
            </CardTitle>
            {filters && (filters.start_date || filters.end_date || filters.level) && (
              <div className='flex items-center gap-2 text-xs text-gray-600'>
                <span className='font-medium'>Filtros aplicados:</span>
                {filters.start_date && (
                  <Badge variant='outline' className='text-xs px-2 py-1'>
                    De: {new Date(filters.start_date).toLocaleDateString('pt-BR')}
                  </Badge>
                )}
                {filters.end_date && (
                  <Badge variant='outline' className='text-xs px-2 py-1'>
                    Até: {new Date(filters.end_date).toLocaleDateString('pt-BR')}
                  </Badge>
                )}
                {filters.level && (
                  <Badge variant='outline' className='text-xs px-2 py-1'>
                    Nível: {filters.level}
                  </Badge>
                )}
              </div>
            )}
          </div>
          <div className='flex items-center gap-2'>
            {Object.entries(levelStats).map(([level, count]) => {
              const style = getLevelStyle(level);
              return (
                <Badge
                  key={`ranking-level-${level}`}
                  className={cn(
                    'text-xs px-2 py-1 border text-white font-medium',
                    style.accentColor
                  )}
                >
                  {level}: {count}
                </Badge>
              );
            })}
          </div>
        </div>
      </CardHeader>

      <CardContent className='px-5 pb-4 pt-0 flex-1 flex flex-col'>
        <motion.div
          variants={containerVariants}
          initial='hidden'
          animate='visible'
          className='flex-1 flex flex-col'
        >
          <div
            ref={scrollContainerRef}
            className='flex w-full flex-1 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent px-2 space-x-3'
          >
            {topTechnicians.map((technician, index) => (
              <TechnicianCard key={technician.id} technician={technician} index={index} />
            ))}
          </div>
        </motion.div>
      </CardContent>
    </Card>
  );
});
