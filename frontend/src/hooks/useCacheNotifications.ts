import { useState, useEffect } from 'react';

interface CacheNotification {
  id: string;
  message: string;
  timestamp: number;
}

export const useCacheNotifications = () => {
  const [notifications, setNotifications] = useState<CacheNotification[]>([]);

  useEffect(() => {
    // Intercepta logs do console para detectar ativações de cache
    const originalLog = console.log;

    console.log = (...args: any[]) => {
      const message = args.join(' ');

      // Detecta mensagens de ativação de cache
      if (message.includes('🚀 Cache ativado automaticamente')) {
        const notification: CacheNotification = {
          id: Date.now().toString(),
          message: message.replace('🚀 Cache ativado automaticamente para padrão detectado: ', ''),
          timestamp: Date.now(),
        };

        setNotifications(prev => [...prev, notification]);

        // Remove notificação após 10 segundos
        setTimeout(() => {
          setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 10000);
      }

      // Chama o log original
      originalLog.apply(console, args);
    };

    // Cleanup
    return () => {
      console.log = originalLog;
    };
  }, []);

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  return {
    notifications,
    removeNotification,
    clearAllNotifications,
  };
};
