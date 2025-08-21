/**
 * Hook React para gerenciar alertas de performance
 * 
 * Este hook fornece uma interface reativa para o serviço de alertas,
 * permitindo que componentes React respondam automaticamente a novos alertas.
 */

import { useState, useEffect, useCallback } from 'react';
import { alertService, Alert, AlertConfig } from '../services/alertService';

export interface UseAlertsReturn {
  alerts: Alert[];
  activeAlerts: Alert[];
  config: AlertConfig;
  isRunning: boolean;
  resolveAlert: (alertId: string) => void;
  resolveAllAlerts: () => void;
  clearOldAlerts: (maxAge?: number) => void;
  updateConfig: (newConfig: Partial<AlertConfig>) => void;
  createAlert: (
    type: Alert['type'],
    category: Alert['category'],
    title: string,
    message: string,
    metadata?: Record<string, any>
  ) => void;
  startMonitoring: () => void;
  stopMonitoring: () => void;
}

/**
 * Hook para gerenciar alertas de performance
 */
export function useAlerts(): UseAlertsReturn {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [config, setConfig] = useState<AlertConfig>(alertService.getConfig());
  const [isRunning, setIsRunning] = useState(true);

  // Atualizar estado quando novos alertas chegarem
  useEffect(() => {
    const updateAlerts = () => {
      setAlerts(alertService.getAlerts());
    };

    // Listener para novos alertas
    const handleNewAlert = (alert: Alert) => {
      setAlerts(prev => [alert, ...prev]);
    };

    // Configurar listeners
    alertService.addListener(handleNewAlert);
    updateAlerts();

    return () => {
      alertService.removeListener(handleNewAlert);
    };
  }, []);

  // Calcular alertas ativos
  const activeAlerts = alerts.filter(alert => !alert.resolved);

  // Resolver alerta específico
  const resolveAlert = useCallback((alertId: string) => {
    alertService.resolveAlert(alertId);
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, resolved: true } : alert
      )
    );
  }, []);

  // Resolver todos os alertas
  const resolveAllAlerts = useCallback(() => {
    alertService.resolveAllAlerts();
    setAlerts(prev => 
      prev.map(alert => ({ ...alert, resolved: true }))
    );
  }, []);

  // Limpar alertas antigos
  const clearOldAlerts = useCallback((maxAge?: number) => {
    alertService.clearOldAlerts(maxAge);
    setAlerts(alertService.getAlerts());
  }, []);

  // Atualizar configuração
  const updateConfig = useCallback((newConfig: Partial<AlertConfig>) => {
    alertService.updateConfig(newConfig);
    setConfig(alertService.getConfig());
  }, []);

  // Criar alerta manual
  const createAlert = useCallback((
    type: Alert['type'],
    category: Alert['category'],
    title: string,
    message: string,
    metadata?: Record<string, any>
  ) => {
    alertService.createAlert(type, category, title, message, metadata);
  }, []);

  // Iniciar monitoramento
  const startMonitoring = useCallback(() => {
    alertService.start();
    setIsRunning(true);
  }, []);

  // Parar monitoramento
  const stopMonitoring = useCallback(() => {
    alertService.stop();
    setIsRunning(false);
  }, []);

  return {
    alerts,
    activeAlerts,
    config,
    isRunning,
    resolveAlert,
    resolveAllAlerts,
    clearOldAlerts,
    updateConfig,
    createAlert,
    startMonitoring,
    stopMonitoring
  };
}

/**
 * Hook para alertas filtrados por categoria
 */
export function useAlertsByCategory(category: Alert['category']): {
  alerts: Alert[];
  activeAlerts: Alert[];
  count: number;
  activeCount: number;
} {
  const { alerts, activeAlerts } = useAlerts();

  const filteredAlerts = alerts.filter(alert => alert.category === category);
  const filteredActiveAlerts = activeAlerts.filter(alert => alert.category === category);

  return {
    alerts: filteredAlerts,
    activeAlerts: filteredActiveAlerts,
    count: filteredAlerts.length,
    activeCount: filteredActiveAlerts.length
  };
}

/**
 * Hook para alertas filtrados por tipo
 */
export function useAlertsByType(type: Alert['type']): {
  alerts: Alert[];
  activeAlerts: Alert[];
  count: number;
  activeCount: number;
} {
  const { alerts, activeAlerts } = useAlerts();

  const filteredAlerts = alerts.filter(alert => alert.type === type);
  const filteredActiveAlerts = activeAlerts.filter(alert => alert.type === type);

  return {
    alerts: filteredAlerts,
    activeAlerts: filteredActiveAlerts,
    count: filteredAlerts.length,
    activeCount: filteredActiveAlerts.length
  };
}

/**
 * Hook para estatísticas de alertas
 */
export function useAlertStats(): {
  total: number;
  active: number;
  resolved: number;
  byType: Record<Alert['type'], number>;
  byCategory: Record<Alert['category'], number>;
  recentCount: number;
} {
  const { alerts, activeAlerts } = useAlerts();

  const byType = alerts.reduce((acc, alert) => {
    acc[alert.type] = (acc[alert.type] || 0) + 1;
    return acc;
  }, {} as Record<Alert['type'], number>);

  const byCategory = alerts.reduce((acc, alert) => {
    acc[alert.category] = (acc[alert.category] || 0) + 1;
    return acc;
  }, {} as Record<Alert['category'], number>);

  // Alertas das últimas 24 horas
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
  const recentCount = alerts.filter(alert => alert.timestamp > oneDayAgo).length;

  return {
    total: alerts.length,
    active: activeAlerts.length,
    resolved: alerts.length - activeAlerts.length,
    byType,
    byCategory,
    recentCount
  };
}

/**
 * Hook para alertas críticos
 */
export function useCriticalAlerts(): {
  alerts: Alert[];
  count: number;
  hasUnresolved: boolean;
} {
  const { alerts } = useAlerts();

  const criticalAlerts = alerts.filter(alert => alert.type === 'critical');
  const unresolvedCritical = criticalAlerts.filter(alert => !alert.resolved);

  return {
    alerts: criticalAlerts,
    count: criticalAlerts.length,
    hasUnresolved: unresolvedCritical.length > 0
  };
}

/**
 * Hook para configuração de alertas com persistência
 */
export function useAlertConfig(): {
  config: AlertConfig;
  updateConfig: (newConfig: Partial<AlertConfig>) => void;
  resetConfig: () => void;
  isModified: boolean;
} {
  const { config, updateConfig: baseUpdateConfig } = useAlerts();
  const [originalConfig] = useState<AlertConfig>(config);

  const resetConfig = useCallback(() => {
    baseUpdateConfig(originalConfig);
  }, [baseUpdateConfig, originalConfig]);

  const isModified = JSON.stringify(config) !== JSON.stringify(originalConfig);

  return {
    config,
    updateConfig: baseUpdateConfig,
    resetConfig,
    isModified
  };
}

/**
 * Hook para notificações de alertas
 */
export function useAlertNotifications(): {
  hasPermission: boolean;
  requestPermission: () => Promise<boolean>;
  enableNotifications: () => void;
  disableNotifications: () => void;
  notificationsEnabled: boolean;
} {
  const { config, updateConfig } = useAlerts();
  const [hasPermission, setHasPermission] = useState(
    'Notification' in window && Notification.permission === 'granted'
  );

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      const granted = permission === 'granted';
      setHasPermission(granted);
      return granted;
    } catch (error) {
      console.error('Erro ao solicitar permissão para notificações:', error);
      return false;
    }
  }, []);

  const enableNotifications = useCallback(() => {
    updateConfig({ enableBrowserNotifications: true });
  }, [updateConfig]);

  const disableNotifications = useCallback(() => {
    updateConfig({ enableBrowserNotifications: false });
  }, [updateConfig]);

  return {
    hasPermission,
    requestPermission,
    enableNotifications,
    disableNotifications,
    notificationsEnabled: config.enableBrowserNotifications
  };
}