import { useState, useEffect, useCallback, useRef } from 'react';
import notificationService, { WebSocketNotification, NotificationEventType } from '../services/websocket/notificationService';
import { NotificationData } from '../types';

export interface UseNotificationsReturn {
  notifications: WebSocketNotification[];
  unreadCount: number;
  connectionStatus: 'connected' | 'disconnected' | 'error' | 'reconnecting';
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  addNotification: (notification: Partial<NotificationData>) => void;
  isConnected: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
}

export const useNotifications = (): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<WebSocketNotification[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error' | 'reconnecting'>('disconnected');
  const unsubscribeRefs = useRef<(() => void)[]>([]);
  const maxNotifications = 50; // Limite máximo de notificações

  // Conectar ao serviço WebSocket
  const connect = useCallback(async () => {
    try {
      await notificationService.connect();
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
    }
  }, []);

  // Desconectar do serviço WebSocket
  const disconnect = useCallback(() => {
    notificationService.disconnect();
  }, []);

  // Adicionar notificação manualmente (para compatibilidade com sistema existente)
  const addNotification = useCallback((notification: Partial<NotificationData>) => {
    const completeNotification: WebSocketNotification = {
      id: notification.id || Date.now().toString(),
      title: notification.title || 'Nova Notificação',
      message: notification.message || '',
      type: notification.type || 'info',
      timestamp: notification.timestamp || new Date(),
      duration: notification.duration,
      read: false,
      category: 'general'
    };

    setNotifications(prev => {
      const updated = [completeNotification, ...prev];
      return updated.slice(0, maxNotifications); // Manter apenas as mais recentes
    });
  }, []);

  // Marcar notificação como lida
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    );
  }, []);

  // Marcar todas as notificações como lidas
  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  // Remover notificação específica
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Limpar todas as notificações
  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Configurar listeners do WebSocket
  useEffect(() => {
    // Limpar listeners anteriores
    unsubscribeRefs.current.forEach(unsubscribe => unsubscribe());
    unsubscribeRefs.current = [];

    // Listener para status de conexão
    const unsubscribeStatus = notificationService.subscribe('connection_status', (status: string) => {
      setConnectionStatus(status as any);
    });
    unsubscribeRefs.current.push(unsubscribeStatus);

    // Listeners para diferentes tipos de notificação
    const eventTypes: NotificationEventType[] = ['ticket_update', 'system_alert', 'maintenance', 'general'];
    
    eventTypes.forEach(eventType => {
      const unsubscribe = notificationService.subscribe(eventType, (notification: WebSocketNotification) => {
        setNotifications(prev => {
          // Verificar se a notificação já existe
          const exists = prev.some(n => n.id === notification.id);
          if (exists) return prev;

          const updated = [notification, ...prev];
          return updated.slice(0, maxNotifications); // Manter apenas as mais recentes
        });
      });
      unsubscribeRefs.current.push(unsubscribe);
    });

    // Tentar conectar automaticamente
    connect();

    // Cleanup na desmontagem
    return () => {
      unsubscribeRefs.current.forEach(unsubscribe => unsubscribe());
      unsubscribeRefs.current = [];
    };
  }, [connect]);

  // Auto-remover notificações com duração definida
  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];

    notifications.forEach(notification => {
      if (notification.duration && notification.duration > 0 && !notification.read) {
        const timer = setTimeout(() => {
          setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, notification.duration);
        timers.push(timer);
      }
    });

    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [notifications]);

  // Calcular contagem de não lidas
  const unreadCount = notifications.filter(n => !n.read).length;
  const isConnected = notificationService.isConnected();

  return {
    notifications,
    unreadCount,
    connectionStatus,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAllNotifications,
    addNotification,
    isConnected,
    connect,
    disconnect
  };
};

export default useNotifications;