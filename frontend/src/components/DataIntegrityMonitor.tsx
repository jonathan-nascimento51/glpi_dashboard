import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, X, Eye, EyeOff } from 'lucide-react';
import { DataIntegrityReport } from '../utils/dataValidation';

interface DataIntegrityMonitorProps {
  report: DataIntegrityReport | null;
  isVisible: boolean;
  onToggleVisibility: () => void;
}

const DataIntegrityMonitor: React.FC<DataIntegrityMonitorProps> = ({
  report,
  isVisible,
  onToggleVisibility,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!report) {
    return null;
  }

  const totalErrors = report.metrics.errors.length + 
                     report.systemStatus.errors.length + 
                     report.technicianRanking.errors.length;

  const totalWarnings = report.metrics.warnings.length + 
                       report.systemStatus.warnings.length + 
                       report.technicianRanking.warnings.length;

  const getStatusColor = () => {
    if (totalErrors > 0) return 'text-red-600 bg-red-50 border-red-200';
    if (totalWarnings > 0) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getStatusIcon = () => {
    if (totalErrors > 0) return <AlertTriangle className="w-4 h-4" />;
    if (totalWarnings > 0) return <Info className="w-4 h-4" />;
    return <CheckCircle className="w-4 h-4" />;
  };

  const getStatusText = () => {
    if (totalErrors > 0) return `${totalErrors} erro(s)`;
    if (totalWarnings > 0) return `${totalWarnings} aviso(s)`;
    return 'Dados íntegros';
  };

  if (!isVisible) {
    return (
      <button
        onClick={onToggleVisibility}
        className="fixed bottom-4 right-4 z-50 p-2 bg-gray-800 text-white rounded-full shadow-lg hover:bg-gray-700 transition-colors"
        title="Mostrar monitor de integridade"
      >
        <Eye className="w-5 h-5" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md">
      {/* Compact Status Bar */}
      <div className={`
        flex items-center justify-between p-3 rounded-lg border shadow-lg cursor-pointer
        ${getStatusColor()}
        transition-all duration-200 hover:shadow-xl
      `}
      onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="font-medium text-sm">
            Integridade: {getStatusText()}
          </span>
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-xs opacity-75">
            {new Date(report.timestamp).toLocaleTimeString('pt-BR')}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleVisibility();
            }}
            className="p-1 hover:bg-black/10 rounded"
            title="Ocultar monitor"
          >
            <EyeOff className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-xl max-h-96 overflow-y-auto">
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Relatório de Integridade
              </h3>
              <button
                onClick={() => setIsExpanded(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Metrics Section */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300">
                📊 Métricas
              </h4>
              <div className="pl-4 space-y-1">
                <div className={`text-xs ${
                  report.metrics.isValid ? 'text-green-600' : 'text-red-600'
                }`}>
                  Status: {report.metrics.isValid ? 'Válido' : 'Inválido'}
                </div>
                {report.metrics.errors.map((error, index) => (
                  <div key={`metrics-error-${index}`} className="text-xs text-red-600 flex items-start space-x-1">
                    <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span>{error}</span>
                  </div>
                ))}
                {report.metrics.warnings.map((warning, index) => (
                  <div key={`metrics-warning-${index}`} className="text-xs text-yellow-600 flex items-start space-x-1">
                    <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* System Status Section */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300">
                🔧 Status do Sistema
              </h4>
              <div className="pl-4 space-y-1">
                <div className={`text-xs ${
                  report.systemStatus.isValid ? 'text-green-600' : 'text-red-600'
                }`}>
                  Status: {report.systemStatus.isValid ? 'Válido' : 'Inválido'}
                </div>
                {report.systemStatus.errors.map((error, index) => (
                  <div key={`system-error-${index}`} className="text-xs text-red-600 flex items-start space-x-1">
                    <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span>{error}</span>
                  </div>
                ))}
                {report.systemStatus.warnings.map((warning, index) => (
                  <div key={`system-warning-${index}`} className="text-xs text-yellow-600 flex items-start space-x-1">
                    <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Technician Ranking Section */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300">
                👥 Ranking de Técnicos
              </h4>
              <div className="pl-4 space-y-1">
                <div className={`text-xs ${
                  report.technicianRanking.isValid ? 'text-green-600' : 'text-red-600'
                }`}>
                  Status: {report.technicianRanking.isValid ? 'Válido' : 'Inválido'}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Técnicos válidos: {report.technicianRanking.data.length}
                </div>
                {report.technicianRanking.errors.map((error, index) => (
                  <div key={`ranking-error-${index}`} className="text-xs text-red-600 flex items-start space-x-1">
                    <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span>{error}</span>
                  </div>
                ))}
                {report.technicianRanking.warnings.map((warning, index) => (
                  <div key={`ranking-warning-${index}`} className="text-xs text-yellow-600 flex items-start space-x-1">
                    <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Summary */}
            <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Última verificação: {report.timestamp.toLocaleString('pt-BR')}
              </div>
              <div className={`text-xs font-medium ${
                report.overallValid ? 'text-green-600' : 'text-red-600'
              }`}>
                Status Geral: {report.overallValid ? 'VÁLIDO' : 'REQUER ATENÇÃO'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataIntegrityMonitor;