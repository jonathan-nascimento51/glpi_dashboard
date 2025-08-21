import React from 'react';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface TrendIndicatorProps {
  trend: 'up' | 'down' | 'stable';
  percentage: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showPercentage?: boolean;
}

const TrendIndicator: React.FC<TrendIndicatorProps> = ({
  trend,
  percentage,
  className,
  size = 'md',
  showIcon = true,
  showPercentage = true,
}) => {
  const icons = {
    up: ArrowUp,
    down: ArrowDown,
    stable: Minus,
  };

  const colors = {
    up: 'text-green-600 dark:text-green-400',
    down: 'text-red-600 dark:text-red-400',
    stable: 'text-gray-500 dark:text-gray-400',
  };

  const bgColors = {
    up: 'bg-green-100 dark:bg-green-900/30',
    down: 'bg-red-100 dark:bg-red-900/30',
    stable: 'bg-gray-100 dark:bg-gray-900/30',
  };

  const sizes = {
    sm: {
      icon: 'w-3 h-3',
      text: 'text-xs',
      padding: 'px-1.5 py-0.5',
    },
    md: {
      icon: 'w-4 h-4',
      text: 'text-sm',
      padding: 'px-2 py-1',
    },
    lg: {
      icon: 'w-5 h-5',
      text: 'text-base',
      padding: 'px-3 py-1.5',
    },
  };

  const Icon = icons[trend];
  const sizeConfig = sizes[size];
  const colorClass = colors[trend];
  const bgColorClass = bgColors[trend];

  const formattedPercentage = Math.abs(percentage);
  const sign = percentage > 0 ? '+' : percentage < 0 ? '-' : '';

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1 rounded-full border-0',
        bgColorClass,
        sizeConfig.padding,
        className
      )}
      title={`Tendência: ${trend === 'up' ? 'Crescimento' : trend === 'down' ? 'Declínio' : 'Estável'} de ${formattedPercentage}%`}
    >
      {showIcon && (
        <Icon className={cn(sizeConfig.icon, colorClass)} aria-hidden="true" />
      )}
      {showPercentage && (
        <span className={cn(sizeConfig.text, colorClass, 'font-medium tabular-nums')}>
          {sign}{formattedPercentage}%
        </span>
      )}
    </div>
  );
};

export default TrendIndicator;

// Função utilitária para calcular tendência baseada em valores
export const calculateTrend = (
  currentValue: number,
  previousValue: number
): { trend: 'up' | 'down' | 'stable'; percentage: number } => {
  if (previousValue === 0) {
    return {
      trend: currentValue > 0 ? 'up' : 'stable',
      percentage: currentValue > 0 ? 100 : 0,
    };
  }

  const percentageChange = ((currentValue - previousValue) / previousValue) * 100;
  const roundedPercentage = Math.round(percentageChange * 10) / 10;

  let trend: 'up' | 'down' | 'stable';
  if (Math.abs(roundedPercentage) < 0.1) {
    trend = 'stable';
  } else if (roundedPercentage > 0) {
    trend = 'up';
  } else {
    trend = 'down';
  }

  return {
    trend,
    percentage: roundedPercentage,
  };
};

// Função para converter string de tendência da API para objeto
export const parseTrendFromAPI = (
  trendString: string
): { trend: 'up' | 'down' | 'stable'; percentage: number } => {
  const numericValue = parseFloat(trendString);
  
  if (isNaN(numericValue)) {
    return { trend: 'stable', percentage: 0 };
  }

  let trend: 'up' | 'down' | 'stable';
  if (Math.abs(numericValue) < 0.1) {
    trend = 'stable';
  } else if (numericValue > 0) {
    trend = 'up';
  } else {
    trend = 'down';
  }

  return {
    trend,
    percentage: Math.round(numericValue * 10) / 10,
  };
};