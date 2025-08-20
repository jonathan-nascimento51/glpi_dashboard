import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingProgressProps {
  isLoading: boolean;
  text?: string;
  estimatedTime?: number; // em segundos
  showProgress?: boolean;
  showTimeEstimate?: boolean;
  onTimeout?: () => void;
  timeoutDuration?: number; // em segundos
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'minimal' | 'detailed';
}

const sizeClasses = {
  sm: {
    spinner: 'w-4 h-4',
    text: 'text-xs',
    container: 'p-3',
  },
  md: {
    spinner: 'w-6 h-6',
    text: 'text-sm',
    container: 'p-4',
  },
  lg: {
    spinner: 'w-8 h-8',
    text: 'text-base',
    container: 'p-6',
  },
};

export const LoadingProgress: React.FC<LoadingProgressProps> = ({
  isLoading,
  text = 'Carregando dados...',
  estimatedTime = 30,
  showProgress = true,
  showTimeEstimate = true,
  onTimeout,
  timeoutDuration = 60,
  className = '',
  size = 'md',
  variant = 'default',
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [progress, setProgress] = useState(0);

  // Reset states when loading changes
  useEffect(() => {
    if (isLoading) {
      setElapsedTime(0);
      setHasTimedOut(false);
      setProgress(0);
    }
  }, [isLoading]);

  // Timer para elapsed time e progress
  useEffect(() => {
    if (!isLoading) return;

    const interval = setInterval(() => {
      setElapsedTime(prev => {
        const newTime = prev + 1;
        
        // Calcular progresso baseado no tempo estimado
        if (showProgress) {
          const progressPercent = Math.min((newTime / estimatedTime) * 100, 95);
          setProgress(progressPercent);
        }

        // Verificar timeout
        if (newTime >= timeoutDuration && !hasTimedOut) {
          setHasTimedOut(true);
          onTimeout?.();
        }

        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isLoading, estimatedTime, timeoutDuration, hasTimedOut, onTimeout, showProgress]);

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusColor = () => {
    if (hasTimedOut) return 'text-red-600 dark:text-red-400';
    if (elapsedTime > estimatedTime * 0.8) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-blue-600 dark:text-blue-400';
  };

  const getStatusIcon = () => {
    if (hasTimedOut) return AlertCircle;
    if (elapsedTime > estimatedTime) return Clock;
    return Loader2;
  };

  const StatusIcon = getStatusIcon();
  const sizeConfig = sizeClasses[size];

  if (!isLoading) return null;

  if (variant === 'minimal') {
    return (
      <div className={cn('flex items-center space-x-2', className)}>
        <Loader2 className={cn(sizeConfig.spinner, 'animate-spin text-primary-600')} />
        <span className={cn(sizeConfig.text, 'text-gray-600 dark:text-gray-400')}>
          {text}
        </span>
      </div>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className={cn(
          'bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700',
          sizeConfig.container,
          className
        )}
      >
        <div className='flex flex-col items-center space-y-4'>
          {/* Ícone e status principal */}
          <div className='flex items-center space-x-3'>
            <StatusIcon
              className={cn(
                sizeConfig.spinner,
                hasTimedOut ? '' : 'animate-spin',
                getStatusColor()
              )}
            />
            <div className='text-center'>
              <p className={cn('font-medium text-gray-900 dark:text-white', sizeConfig.text)}>
                {hasTimedOut ? 'Requisição demorou mais que o esperado' : text}
              </p>
              {showTimeEstimate && (
                <p className={cn('text-gray-500 dark:text-gray-400', sizeConfig.text)}>
                  {hasTimedOut
                    ? `Tempo limite: ${formatTime(timeoutDuration)}`
                    : `Tempo estimado: ${formatTime(estimatedTime)}`}
                </p>
              )}
            </div>
          </div>

          {/* Barra de progresso */}
          {showProgress && variant === 'detailed' && (
            <div className='w-full space-y-2'>
              <div className='flex justify-between items-center'>
                <span className={cn('text-gray-600 dark:text-gray-400', sizeConfig.text)}>
                  Progresso
                </span>
                <span className={cn('text-gray-600 dark:text-gray-400', sizeConfig.text)}>
                  {Math.round(progress)}%
                </span>
              </div>
              <div className='w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2'>
                <motion.div
                  className={cn(
                    'h-2 rounded-full transition-colors duration-300',
                    hasTimedOut
                      ? 'bg-red-500'
                      : elapsedTime > estimatedTime * 0.8
                      ? 'bg-yellow-500'
                      : 'bg-blue-500'
                  )}
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          )}

          {/* Tempo decorrido */}
          <div className='flex items-center space-x-2 text-gray-500 dark:text-gray-400'>
            <Clock className='w-4 h-4' />
            <span className={sizeConfig.text}>
              Tempo decorrido: {formatTime(elapsedTime)}
            </span>
          </div>

          {/* Mensagem de timeout */}
          {hasTimedOut && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className='bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3 w-full'
            >
              <div className='flex items-center space-x-2'>
                <AlertCircle className='w-4 h-4 text-yellow-600 dark:text-yellow-400' />
                <p className={cn('text-yellow-800 dark:text-yellow-200', sizeConfig.text)}>
                  A requisição está demorando mais que o esperado. Isso pode indicar alta carga no servidor.
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

// Hook personalizado para usar com o LoadingProgress
export const useLoadingProgress = ({
  estimatedTime = 30,
  timeoutDuration = 60,
  onTimeout,
}: {
  estimatedTime?: number;
  timeoutDuration?: number;
  onTimeout?: () => void;
} = {}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [hasTimedOut, setHasTimedOut] = useState(false);

  const startLoading = () => {
    setIsLoading(true);
    setHasTimedOut(false);
  };

  const stopLoading = () => {
    setIsLoading(false);
    setHasTimedOut(false);
  };

  const handleTimeout = () => {
    setHasTimedOut(true);
    onTimeout?.();
  };

  return {
    isLoading,
    hasTimedOut,
    startLoading,
    stopLoading,
    LoadingComponent: (props: Partial<LoadingProgressProps>) => (
      <LoadingProgress
        isLoading={isLoading}
        estimatedTime={estimatedTime}
        timeoutDuration={timeoutDuration}
        onTimeout={handleTimeout}
        {...props}
      />
    ),
  };
};

export default LoadingProgress;