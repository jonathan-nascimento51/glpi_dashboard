import React from 'react';
import { AlertCircle, RefreshCw, Inbox, Loader2 } from 'lucide-react';
import { defaultMessages } from '../types/states';

interface LoadingStateProps {
  message?: string;
  showSpinner?: boolean;
  variant?: 'default' | 'skeleton' | 'minimal';
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = defaultMessages.loading,
  showSpinner = true,
  variant = 'default',
  className = ''
}) => {
  if (variant === 'skeleton') {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (variant === 'minimal') {
    return (
      <div className={`flex items-center justify-center p-2 ${className}`}>
        {showSpinner && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
        <span className="text-sm text-gray-600">{message}</span>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
      {showSpinner && (
        <Loader2 className="w-8 h-8 animate-spin text-blue-500 mb-4" />
      )}
      <p className="text-gray-600 text-center">{message}</p>
    </div>
  );
};

interface ErrorStateProps {
  error?: Error | string | null;
  message?: string;
  onRetry?: () => void;
  retryLabel?: string;
  variant?: 'default' | 'compact' | 'inline';
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  error,
  message,
  onRetry,
  retryLabel = defaultMessages.retry,
  variant = 'default',
  className = ''
}) => {
  const errorMessage = message || 
    (typeof error === 'string' ? error : error?.message) || 
    defaultMessages.error;

  if (variant === 'inline') {
    return (
      <div className={`flex items-center text-red-600 text-sm ${className}`}>
        <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
        <span>{errorMessage}</span>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-2 text-blue-600 hover:text-blue-800 underline"
          >
            {retryLabel}
          </button>
        )}
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-md ${className}`}>
        <div className="flex items-center text-red-700">
          <AlertCircle className="w-5 h-5 mr-2" />
          <span className="text-sm">{errorMessage}</span>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center text-sm text-blue-600 hover:text-blue-800"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            {retryLabel}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
      <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
        <AlertCircle className="w-8 h-8 text-red-500" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao carregar dados</h3>
      <p className="text-gray-600 text-center mb-4 max-w-md">{errorMessage}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          {retryLabel}
        </button>
      )}
    </div>
  );
};

interface EmptyStateProps {
  message?: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
  variant?: 'default' | 'compact' | 'minimal';
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  message = defaultMessages.empty,
  description,
  action,
  icon,
  variant = 'default',
  className = ''
}) => {
  const defaultIcon = <Inbox className="w-8 h-8 text-gray-400" />;

  if (variant === 'minimal') {
    return (
      <div className={`flex items-center justify-center p-4 text-gray-500 text-sm ${className}`}>
        {icon || <Inbox className="w-4 h-4 mr-2" />}
        <span>{message}</span>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`flex flex-col items-center justify-center p-6 ${className}`}>
        {icon || defaultIcon}
        <p className="text-gray-600 text-center mt-2">{message}</p>
        {action && (
          <button
            onClick={action.onClick}
            className="mt-3 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            {action.label}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center justify-center p-12 ${className}`}>
      <div className="flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
        {icon || defaultIcon}
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{message}</h3>
      {description && (
        <p className="text-gray-600 text-center mb-4 max-w-md">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

interface RefreshIndicatorProps {
  isRefetching: boolean;
  onRefresh?: () => void;
  className?: string;
}

export const RefreshIndicator: React.FC<RefreshIndicatorProps> = ({
  isRefetching,
  onRefresh,
  className = ''
}) => {
  if (!isRefetching && !onRefresh) return null;

  return (
    <div className={`flex items-center ${className}`}>
      {isRefetching && (
        <div className="flex items-center text-blue-600 text-sm">
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
          <span>Atualizando...</span>
        </div>
      )}
      {onRefresh && !isRefetching && (
        <button
          onClick={onRefresh}
          className="flex items-center text-sm text-gray-600 hover:text-gray-800 transition-colors"
          title="Atualizar dados"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

/**
 * Componente wrapper que gerencia automaticamente os estados
 */
interface StateWrapperProps {
  isLoading: boolean;
  isError: boolean;
  isEmpty: boolean;
  error?: Error | string | null;
  onRetry?: () => void;
  loadingProps?: Partial<LoadingStateProps>;
  errorProps?: Partial<ErrorStateProps>;
  emptyProps?: Partial<EmptyStateProps>;
  children: React.ReactNode;
  className?: string;
}

export const StateWrapper: React.FC<StateWrapperProps> = ({
  isLoading,
  isError,
  isEmpty,
  error,
  onRetry,
  loadingProps = {},
  errorProps = {},
  emptyProps = {},
  children,
  className = ''
}) => {
  if (isLoading) {
    return <LoadingState {...loadingProps} className={className} />;
  }

  if (isError) {
    return (
      <ErrorState 
        error={error} 
        onRetry={onRetry} 
        {...errorProps} 
        className={className} 
      />
    );
  }

  if (isEmpty) {
    return <EmptyState {...emptyProps} className={className} />;
  }

  return <>{children}</>;
};