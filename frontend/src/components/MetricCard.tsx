import React from 'react';
import { TrendingUp, TrendingDown, Plus, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { TicketStatus } from '../types';

interface MetricCardProps {
  type: TicketStatus;
  value: number;
  change: string;
  onClick?: () => void;
}

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
      };
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

export const MetricCard: React.FC<MetricCardProps> = ({
  type,
  value,
  change,
  onClick,
}) => {
  const config = getMetricConfig(type);
  const changeData = parseChange(change);
  const Icon = config.icon;
  const TrendIcon = changeData.isPositive ? TrendingUp : TrendingDown;

  return (
    <div
      className={`
        metric-card fade-in cursor-pointer
        ${config.bgColor} ${config.borderColor}
        hover:shadow-lg hover:scale-105
        transition-all duration-300
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${config.bgColor}`}>
          <Icon className={`w-6 h-6 ${config.iconColor}`} />
        </div>
        <div className="flex items-center space-x-1">
          <TrendIcon 
            className={`w-4 h-4 ${
              changeData.isPositive 
                ? 'text-green-500' 
                : changeData.isNegative 
                ? 'text-red-500' 
                : 'text-gray-500'
            }`} 
          />
          <span 
            className={`text-sm font-medium ${
              changeData.isPositive 
                ? 'text-green-600 dark:text-green-400' 
                : changeData.isNegative 
                ? 'text-red-600 dark:text-red-400' 
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            {changeData.display}
          </span>
        </div>
      </div>
      
      <div className="space-y-2">
        <h3 className={`text-sm font-medium ${config.textColor}`}>
          {config.title}
        </h3>
        <div className="flex items-baseline space-x-2">
          <span className={`text-3xl font-bold ${config.textColor}`}>
            {value.toLocaleString('pt-BR')}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
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
            style={{ 
              width: `${Math.min(Math.abs(changeData.value), 100)}%` 
            }}
          />
        </div>
      </div>
      
      {/* Hover effect indicator */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  );
};