import React from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  Server, 
  Database,
  Wifi,
  Activity
} from 'lucide-react';
import { StateWrapper, RefreshIndicator } from '../../../shared/components/StateComponents';
import type { SystemStatusProps, SystemStatus } from '../types/dashboardTypes';
import { ComponentState } from '../../../shared/types/states';

interface ExtendedSystemStatusProps extends SystemStatusProps {
  state?: ComponentState<SystemStatus>;
  onRetry?: () => void;
  isRefetching?: boolean;
  onRefresh?: () => void;
  className?: string;
}

const getStatusConfig = (status: 'online' | 'offline' | 'degraded') => {
  switch (status) {
    case 'online':
      return {
        icon: CheckCircle,
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        label: 'Online',
        description: 'Sistema funcionando normalmente'
      };
    case 'offline':
      return {
        icon: XCircle,
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        label: 'Offline',
        description: 'Sistema indisponível'
      };
    case 'degraded':
      return {
        icon: AlertTriangle,
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        label: 'Degradado',
        description: 'Sistema com problemas de performance'
      };
    default:
      return {
        icon: AlertTriangle,
        color: 'text-gray-600',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        label: 'Desconhecido',
        description: 'Status não disponível'
      };
  }
};

const formatResponseTime = (time: number) => {
  if (time < 1000) return `${Math.round(time)}ms`;
  return `${(time / 1000).toFixed(1)}s`;
};

const formatLastUpdate = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 1) return 'Agora mesmo';
    if (diffMinutes < 60) return `${diffMinutes} min atrás`;
    
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h atrás`;
    
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return 'Data inválida';
  }
};

export const SystemStatusComponent: React.FC<ExtendedSystemStatusProps> = ({
  status,
  state,
  onRetry,
  isRefetching = false,
  onRefresh,
  showDetails = true,
  className = '',
  isLoading = false,
  error
}) => {
  // Determinar estado baseado nas props ou estado explícito
  const statusState = state || {
    type: isLoading ? 'loading' : error ? 'error' : 'success',
    data: status,
    error: error ? new Error(error) : undefined
  } as ComponentState<SystemStatus>;

  // Verificar se está vazio
  const isEmpty = !isLoading && !error && !status;

  // Configurações de status
  const apiConfig = status ? getStatusConfig(status.api) : null;
  const glpiConfig = status ? getStatusConfig(status.glpi) : null;
  const systemConfig = status ? getStatusConfig(status.status) : null;

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">Status do Sistema</h2>
          <RefreshIndicator 
            isRefetching={isRefetching}
            onRefresh={onRefresh}
          />
        </div>

        <StateWrapper
          isLoading={statusState.type === 'loading'}
          isError={statusState.type === 'error'}
          isEmpty={isEmpty}
          error={statusState.error}
          onRetry={onRetry}
          loadingProps={{ variant: 'skeleton' }}
          errorProps={{ 
            variant: 'default',
            message: 'Erro ao carregar status do sistema'
          }}
          emptyProps={{ 
            variant: 'default',
            message: 'Status não disponível',
            description: 'Não foi possível obter informações do sistema.'
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Status geral */}
            {systemConfig && (
              <div className={`p-4 rounded-lg border-2 ${systemConfig.borderColor} ${systemConfig.bgColor}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <systemConfig.icon className={`w-6 h-6 ${systemConfig.color}`} />
                    <div>
                      <h3 className="font-semibold text-gray-900">Sistema Geral</h3>
                      <p className="text-sm text-gray-600">{systemConfig.description}</p>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${systemConfig.color} ${systemConfig.bgColor}`}>
                    {systemConfig.label}
                  </div>
                </div>
              </div>
            )}

            {/* Detalhes dos serviços */}
            {showDetails && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* API Status */}
                {apiConfig && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.1 }}
                    className={`p-4 rounded-lg border ${apiConfig.borderColor} ${apiConfig.bgColor}`}
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <Server className={`w-5 h-5 ${apiConfig.color}`} />
                      <h4 className="font-medium text-gray-900">API</h4>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${apiConfig.color}`}>
                        {apiConfig.label}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">{apiConfig.description}</p>
                  </motion.div>
                )}

                {/* GLPI Status */}
                {glpiConfig && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.2 }}
                    className={`p-4 rounded-lg border ${glpiConfig.borderColor} ${glpiConfig.bgColor}`}
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <Database className={`w-5 h-5 ${glpiConfig.color}`} />
                      <h4 className="font-medium text-gray-900">GLPI</h4>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${glpiConfig.color}`}>
                        {glpiConfig.label}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">
                      {status?.glpi_message || glpiConfig.description}
                    </p>
                    {status?.glpi_response_time && (
                      <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>Tempo de resposta: {formatResponseTime(status.glpi_response_time)}</span>
                      </div>
                    )}
                  </motion.div>
                )}
              </div>
            )}

            {/* Informações adicionais */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.3 }}
              className="bg-gray-50 rounded-lg p-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                {status?.version && (
                  <div className="flex items-center space-x-2">
                    <Activity className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600">Versão:</span>
                    <span className="font-medium text-gray-900">{status.version}</span>
                  </div>
                )}
                
                {status?.sistema_ativo !== undefined && (
                  <div className="flex items-center space-x-2">
                    <Wifi className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600">Sistema ativo:</span>
                    <span className={`font-medium ${
                      status.sistema_ativo ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {status.sistema_ativo ? 'Sim' : 'Não'}
                    </span>
                  </div>
                )}
                
                {(status?.last_update || status?.ultima_atualizacao) && (
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600">Última atualização:</span>
                    <span className="font-medium text-gray-900">
                      {formatLastUpdate(status.last_update || status.ultima_atualizacao)}
                    </span>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        </StateWrapper>
      </div>
    </div>
  );
};

/**
 * Componente compacto para exibir status em espaços menores
 */
interface CompactSystemStatusProps {
  status: SystemStatus;
  state?: ComponentState<SystemStatus>;
  onRetry?: () => void;
  className?: string;
}

export const CompactSystemStatus: React.FC<CompactSystemStatusProps> = ({
  status,
  state,
  onRetry,
  className = ''
}) => {
  const statusState = state || {
    type: 'success',
    data: status
  } as ComponentState<SystemStatus>;

  const isEmpty = !status;
  const systemConfig = status ? getStatusConfig(status.status) : null;

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <h3 className="text-sm font-medium text-gray-700 mb-3">Status</h3>
      
      <StateWrapper
        isLoading={statusState.type === 'loading'}
        isError={statusState.type === 'error'}
        isEmpty={isEmpty}
        error={statusState.error}
        onRetry={onRetry}
        loadingProps={{ variant: 'minimal' }}
        errorProps={{ variant: 'inline' }}
        emptyProps={{ variant: 'minimal', message: 'Sem dados' }}
      >
        {systemConfig && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <systemConfig.icon className={`w-4 h-4 ${systemConfig.color}`} />
              <span className="text-sm font-medium text-gray-900">
                {systemConfig.label}
              </span>
            </div>
            {status.sistema_ativo !== undefined && (
              <div className={`w-2 h-2 rounded-full ${
                status.sistema_ativo ? 'bg-green-500' : 'bg-red-500'
              }`} />
            )}
          </div>
        )}
      </StateWrapper>
    </div>
  );
};