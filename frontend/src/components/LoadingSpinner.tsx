import React from 'react';
import { Loader2, RefreshCw, RotateCw } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  text?: string;
  fullScreen?: boolean;
  className?: string;
  variant?: 'default' | 'dots' | 'pulse' | 'bounce';
  color?: 'blue' | 'green' | 'purple' | 'gray';
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const colorClasses = {
  blue: 'text-blue-500 dark:text-blue-400',
  green: 'text-green-500 dark:text-green-400',
  purple: 'text-purple-500 dark:text-purple-400',
  gray: 'text-gray-500 dark:text-gray-400',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  text,
  fullScreen = false,
  className = '',
  variant = 'default',
  color = 'blue',
}) => {
  const renderSpinner = () => {
    const baseClasses = `${sizeClasses[size]} ${colorClasses[color]}`;
    
    switch (variant) {
      case 'dots':
        return (
          <div className="flex space-x-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full animate-bounce`}
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        );
      
      case 'pulse':
        return (
          <div className={`${baseClasses} rounded-full animate-pulse bg-current`} />
        );
      
      case 'bounce':
        return (
          <RefreshCw className={`${baseClasses} animate-bounce`} />
        );
      
      default:
        return (
          <Loader2 className={`${baseClasses} animate-spin`} />
        );
    }
  };

  const spinnerContent = (
    <div className={`flex flex-col items-center justify-center space-y-3 ${className}`}>
      {renderSpinner()}
      {text && (
        <p className="text-sm text-gray-600 dark:text-gray-400 font-medium animate-pulse">
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white dark:bg-gray-900 bg-opacity-80 dark:bg-opacity-80 backdrop-blur-sm z-50 flex items-center justify-center">
        {spinnerContent}
      </div>
    );
  }

  return spinnerContent;
};

// Skeleton loader for cards
export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
      <div className="animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <div className="w-16 h-4 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div className="space-y-3">
          <div className="w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="w-16 h-8 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div className="mt-4 w-full h-2 bg-gray-200 dark:bg-gray-700 rounded" />
      </div>
    </div>
  );
};

// Skeleton loader for metrics grid
export const SkeletonMetricsGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: 4 }).map((_, index) => (
        <SkeletonCard key={`metrics-skeleton-${index}`} />
      ))}
    </div>
  );
};

// Skeleton loader for levels section
export const SkeletonLevelsSection: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="w-48 h-6 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="w-64 h-4 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div className="w-24 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, index) => (
          <SkeletonCard key={`levels-skeleton-${index}`} />
        ))}
      </div>
      
      <SkeletonCard className="h-48" />
    </div>
  );
};

// Error state component
interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Erro ao carregar dados',
  message = 'Ocorreu um erro inesperado. Tente novamente.',
  onRetry,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center space-y-4 p-8 ${className}`}>
      <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
        <svg 
          className="w-8 h-8 text-red-600 dark:text-red-400" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
          />
        </svg>
      </div>
      
      <div className="text-center space-y-2">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {title}
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          {message}
        </p>
      </div>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-primary flex items-center space-x-2"
        >
          <svg 
            className="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
            />
          </svg>
          <span>Tentar Novamente</span>
        </button>
      )}
    </div>
  );
};