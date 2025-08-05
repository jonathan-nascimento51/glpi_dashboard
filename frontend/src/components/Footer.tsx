import React from 'react';

interface FooterProps {
  lastUpdated?: Date;
  isOnline: boolean;
}

export const Footer: React.FC<FooterProps> = ({ lastUpdated, isOnline }) => {
  return (
    <footer className="w-full h-8 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
      <div className="grid-container h-full">
        <div className="col-span-12 flex items-center justify-between">
          {/* Texto Institucional */}
          <div className="text-meta text-secondary">
            © 2025 Departamento de Tecnologia do Estado
          </div>
          
          {/* Status + Última Atualização */}
          <div className="flex items-center space-x-4">
            {lastUpdated && (
              <span className="text-meta text-secondary">
                Última atualização: {lastUpdated.toLocaleTimeString('pt-BR')}
              </span>
            )}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-meta text-secondary">
                {isOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};