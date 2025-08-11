import React from 'react';
import { Loader2 } from 'lucide-react';

interface PageTransitionProps {
  isVisible: boolean;
  message?: string;
  type?: 'overlay' | 'inline' | 'modal';
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8'
};

export const PageTransition: React.FC<PageTransitionProps> = ({
  isVisible,
  message = 'Carregando...',
  type = 'overlay',
  size = 'md'
}) => {
  if (!isVisible) return null;

  const spinnerContent = (
    <div className="flex flex-col items-center justify-center space-y-3">
      <div className="relative">
        <Loader2 className={`${sizeClasses[size]} text-blue-500 animate-spin`} />
        {/* Pulse effect */}
        <div className={`absolute inset-0 ${sizeClasses[size]} border-2 border-blue-200 rounded-full animate-ping opacity-20`} />
      </div>
      {message && (
        <p className="text-sm text-gray-600 dark:text-gray-400 font-medium animate-pulse">
          {message}
        </p>
      )}
    </div>
  );

  if (type === 'overlay') {
    return (
      <div className="fixed inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-40 flex items-center justify-center transition-all duration-300">
        {spinnerContent}
      </div>
    );
  }

  if (type === 'modal') {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center transition-all duration-300">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 max-w-sm w-full mx-4">
          {spinnerContent}
        </div>
      </div>
    );
  }

  // type === 'inline'
  return (
    <div className="flex items-center justify-center p-8">
      {spinnerContent}
    </div>
  );
};

export default PageTransition;