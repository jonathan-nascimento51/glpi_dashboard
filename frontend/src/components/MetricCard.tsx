import React, { useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Plus, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { TicketStatus } from '../types';

interface MetricCardProps {
  type: TicketStatus;
  value: number;
  change: string;
  onClick?: () => void;
}

// Funções auxiliares movidas para fora do componente
const getMetricConfig = (type: TicketStatus) => {
  switch (type) {
    case 'new':
      return {
        title: 'Novos',
        icon: Plus,
        bgColor: 'bg-blue-50 dark:bg-blue-900/20',
        iconColor: 'text-blue-600 dark:text-blue-400',
        textColor: 'text-blue-900 dark:text-blue-100',
        borderColor: 'border-blue-200 dark:border-blue-800',
      });
    case 'progress':
      return {
        title: 'Em Progresso',
        icon: Clock,
        bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
        iconColor: 'text-yellow-600 dark:text-yellow-400',
        textColor: 'text-yellow-900 dark:text-yellow-100',
        borderColor: 'border-yellow-200 dark:border-yellow-800',
      };
    case 'pending':
      return {
        title: 'Pendentes',
        icon: AlertCircle,
        bgColor: 'bg-orange-50 dark:bg-orange-900/20',
        iconColor: 'text-orange-600 dark:text-orange-400',
        textColor: 'text-orange-900 dark:text-orange-100',
        borderColor: 'border-orange-200 dark:border-orange-800',
      };
    case 'resolved':
      return {
        title: 'Resolvidos',
        icon: CheckCircle,
        bgColor: 'bg-green-50 dark:bg-green-900/20',
        iconColor: 'text-green-600 dark:text-green-400',
        textColor: 'text-green-900 dark:text-green-100',
        borderColor: 'border-green-200 dark:border-green-800',
      };
    default:
      return {
        title: 'Desconhecido',
        icon: AlertCircle,
        bgColor: 'bg-gray-50 dark:bg-gray-900/20',
        iconColor: 'text-gray-600 dark:text-gray-400',
        textColor: 'text-gray-900 dark:text-gray-100',
        borderColor: 'border-gray-200 dark:border-gray-800',
      };
  }
};

const parseChange = (change: string) => {
  const isPositive = change.startsWith('+');
  const isNegative = change.startsWith('-');
  const numericValue = parseFloat(change.replace(/[+%-]/g, ''));
  
  return {
    isPositive,
    isNegative,
    value: numericValue,
    display: change,
  };
};

// Variantes de animação movidas para fora do componente
const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut"
    }
  },
  hover: {
    y: -8,
    scale: 1.03,
    transition: {
      duration: 0.3,
      ease: "easeInOut"
    }
  }
};

const iconVariants = {
  hover: {
    scale: 1.2,
    rotate: 10,
    transition: {
      duration: 0.3,
      ease: "easeInOut"
    }
  }
};

const numberVariants = {
  hidden: { scale: 0 },
  visible: {
    scale: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut",
      delay: 0.2
    }
  }
};

export const MetricCard = React.memo<MetricCardProps>(function MetricCard({
  type,
  value,
  change,
  onClick,
}) {
  // Memoizar configuração do tipo
  const config = useMemo(() => getMetricConfig(type), [type]);
  
  // Memoizar dados de mudança
  const changeData = useMemo(() => parseChange(change), [change]);
  
  // Memoizar ícones
  const Icon = useMemo(() => config.icon, [config.icon]);
  const TrendIcon = useMemo(() => 
    changeData.isPositive ? TrendingUp : TrendingDown, 
    [changeData.isPositive]
  );
  
  // Memoizar valor formatado
  const formattedValue = useMemo(() => 
    value.toLocaleString('pt-BR'), 
    [value]
  );
  
  // Memoizar estilo da barra de progresso
  const progressBarStyle = useMemo(() => ({
    width: `${Math.min(Math.abs(changeData.value), 100)}%`
  }), [changeData.value]);
  
  // Memoizar callback de teclado
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.();
    }
  }, [onClick]);

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className={`
        metric-card cursor-pointer group relative overflow-hidden
        ${config.bgColor} ${config.borderColor}
        figma-glass-card rounded-2xl
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      <div className="flex items-center justify-between mb-4 relative z-10">
        <motion.div 
          variants={iconVariants}
          className={`p-3 rounded-lg ${config.bgColor} shadow-lg`}
        >
          <Icon className={`w-6 h-6 ${config.iconColor}`} />
        </motion.div>
        <motion.div 
          className="flex items-center space-x-1 min-w-0"
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.2 }}
        >
          <TrendIcon 
            className={`w-4 h-4 flex-shrink-0 ${
              changeData.isPositive 
                ? 'text-green-500' 
                : changeData.isNegative 
                ? 'text-red-500' 
                : 'text-gray-500'
            }`} 
          />
          <span 
            className={`text-xs lg:text-sm font-medium truncate ${
              changeData.isPositive 
                ? 'text-green-600 dark:text-green-400' 
                : changeData.isNegative 
                ? 'text-red-600 dark:text-red-400' 
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            {changeData.display}
          </span>
        </motion.div>
      </div>
      
      <div className="space-y-2 relative z-10">
        <h3 className={`text-sm font-medium ${config.textColor} truncate`}>
          {config.title}
        </h3>
        <div className="flex items-baseline space-x-2 min-w-0">
          <motion.span 
            variants={numberVariants}
            className={`text-2xl lg:text-3xl font-bold ${config.textColor} truncate flex-shrink-0`}
          >
            {formattedValue}
          </motion.span>
          <span className="text-xs lg:text-sm text-gray-500 dark:text-gray-400 truncate flex-shrink">
            chamados
          </span>
        </div>
      </div>
      
      {/* Progress bar based on change */}
      <div className="mt-4">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full transition-all duration-500 ${
              changeData.isPositive 
                ? 'bg-green-500' 
                : changeData.isNegative 
                ? 'bg-red-500' 
                : 'bg-gray-400'
            }`}
            style={progressBarStyle}
          />
        </div>
      </div>
      
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br opacity-5 rounded-2xl ${config.bgColor}`} />
      
      {/* Shine Effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 opacity-0"
        whileHover={{
          opacity: [0, 1, 0],
          x: [-100, 300]
        }}
        transition={{ duration: 0.6 }}
      />
    </motion.div>
  );
};