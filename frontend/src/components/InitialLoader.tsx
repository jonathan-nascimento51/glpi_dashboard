import React, { useEffect, useState } from 'react';
import { Loader2, BarChart3, Users, Clock, CheckCircle } from 'lucide-react';

interface InitialLoaderProps {
  isVisible: boolean;
  progress?: number;
  message?: string;
}

const loadingSteps = [
  { icon: BarChart3, text: 'Carregando métricas...', delay: 0 },
  { icon: Users, text: 'Sincronizando dados...', delay: 800 },
  { icon: Clock, text: 'Processando informações...', delay: 1600 },
  { icon: CheckCircle, text: 'Finalizando...', delay: 2400 }
];

export const InitialLoader: React.FC<InitialLoaderProps> = ({
  isVisible,
  progress = 0,
  message
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setShowContent(true);
      const interval = setInterval(() => {
        setCurrentStep(prev => {
          if (prev < loadingSteps.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 800);

      return () => clearInterval(interval);
    } else {
      // Delay para permitir animação de saída
      const timeout = setTimeout(() => setShowContent(false), 300);
      return () => clearTimeout(timeout);
    }
  }, [isVisible]);

  if (!showContent) return null;

  return (
    <div 
      className={`fixed inset-0 z-50 transition-all duration-500 ${
        isVisible 
          ? 'opacity-100 backdrop-blur-sm' 
          : 'opacity-0 pointer-events-none'
      }`}
      style={{
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%)'
      }}
    >
      {/* Background overlay */}
      <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80" />
      
      {/* Loading content */}
      <div className="relative flex items-center justify-center min-h-screen p-4">
        <div 
          className={`bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 max-w-md w-full transform transition-all duration-500 ${
            isVisible ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4'
          }`}
        >
          {/* Logo/Brand area */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              GLPI Dashboard
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Carregando seu painel de controle
            </p>
          </div>

          {/* Progress indicator */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Progresso
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {Math.round((currentStep + 1) / loadingSteps.length * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${((currentStep + 1) / loadingSteps.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Current step */}
          <div className="flex items-center space-x-3 mb-6">
            <div className="relative">
              <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
            </div>
            <div className="flex-1">
              <p className="text-gray-900 dark:text-white font-medium">
                {message || loadingSteps[currentStep]?.text || 'Carregando...'}
              </p>
            </div>
          </div>

          {/* Loading steps */}
          <div className="space-y-3">
            {loadingSteps.map((step, index) => {
              const Icon = step.icon;
              const isCompleted = index < currentStep;
              const isCurrent = index === currentStep;
              const isPending = index > currentStep;
              
              return (
                <div 
                  key={index}
                  className={`flex items-center space-x-3 p-2 rounded-lg transition-all duration-300 ${
                    isCurrent ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                  }`}
                >
                  <div 
                    className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                      isCompleted 
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' 
                        : isCurrent 
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500'
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <Icon className={`w-4 h-4 ${isCurrent ? 'animate-pulse' : ''}`} />
                    )}
                  </div>
                  <span 
                    className={`text-sm transition-all duration-300 ${
                      isCompleted 
                        ? 'text-green-600 dark:text-green-400 line-through' 
                        : isCurrent 
                        ? 'text-blue-600 dark:text-blue-400 font-medium' 
                        : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {step.text}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Additional info */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              Aguarde enquanto preparamos tudo para você...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InitialLoader;