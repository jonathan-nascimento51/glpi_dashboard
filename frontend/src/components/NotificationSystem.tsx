import React, { useEffect, useMemo, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { NotificationData } from '../types';

interface NotificationSystemProps {
  notifications: NotificationData[];
  onRemoveNotification: (id: string) => void;
}

interface NotificationItemProps {
  notification: NotificationData;
  onRemove: (id: string) => void;
}

// Memoized notification configuration to prevent recreation
const getNotificationConfig = (type: NotificationData['type']) => {
  switch (type) {
    case 'success':
      return {
        icon: CheckCircle,
        bgColor: 'bg-green-50 dark:bg-green-900/20',
        borderColor: 'border-green-200 dark:border-green-800',
        iconColor: 'text-green-600 dark:text-green-400',
        titleColor: 'text-green-900 dark:text-green-100',
        messageColor: 'text-green-700 dark:text-green-300',
      };
    case 'error':
      return {
        icon: AlertCircle,
        bgColor: 'bg-red-50 dark:bg-red-900/20',
        borderColor: 'border-red-200 dark:border-red-800',
        iconColor: 'text-red-600 dark:text-red-400',
        titleColor: 'text-red-900 dark:text-red-100',
        messageColor: 'text-red-700 dark:text-red-300',
      };
    case 'warning':
      return {
        icon: AlertTriangle,
        bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
        borderColor: 'border-yellow-200 dark:border-yellow-800',
        iconColor: 'text-yellow-600 dark:text-yellow-400',
        titleColor: 'text-yellow-900 dark:text-yellow-100',
        messageColor: 'text-yellow-700 dark:text-yellow-300',
      };
    case 'info':
    default:
      return {
        icon: Info,
        bgColor: 'bg-blue-50 dark:bg-blue-900/20',
        borderColor: 'border-blue-200 dark:border-blue-800',
        iconColor: 'text-blue-600 dark:text-blue-400',
        titleColor: 'text-blue-900 dark:text-blue-100',
        messageColor: 'text-blue-700 dark:text-blue-300',
      };
  }
};

const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onRemove }) => {
  // Memoize configuration to prevent recalculation
  const config = useMemo(() => getNotificationConfig(notification.type), [notification.type]);
  const Icon = useMemo(() => config.icon, [config.icon]);

  // Memoize formatted timestamp with safety check
  const formattedTime = useMemo(() => {
    if (!notification.timestamp) {
      return new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    }
    
    const timestamp = notification.timestamp instanceof Date 
      ? notification.timestamp 
      : new Date(notification.timestamp);
      
    return timestamp.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }, [notification.timestamp]);

  // Memoize progress bar color
  const progressBarColor = useMemo(() => {
    switch (notification.type) {
      case 'success': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      default: return 'bg-blue-500';
    }
  }, [notification.type]);

  // Memoize close handler
  const handleClose = useCallback(() => {
    onRemove(notification.id);
  }, [notification.id, onRemove]);

  // Auto-remove after duration
  useEffect(() => {
    if (notification.duration && notification.duration > 0) {
      const timer = setTimeout(() => {
        onRemove(notification.id);
      }, notification.duration);

      return () => clearTimeout(timer);
    }
  }, [notification.id, notification.duration, onRemove]);

  return (
    <div className={`
      ${config.bgColor} ${config.borderColor}
      border rounded-lg shadow-lg p-4 mb-3 max-w-sm w-full
      transform transition-all duration-300 ease-in-out
      hover:shadow-xl
      animate-fade-in
    `}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <Icon className={`w-5 h-5 ${config.iconColor}`} />
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className={`text-sm font-semibold ${config.titleColor} mb-1`}>
            {notification.title}
          </h4>
          <p className={`text-sm ${config.messageColor} break-words`}>
            {notification.message}
          </p>
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            {formattedTime}
          </div>
        </div>
        
        <button
          onClick={handleClose}
          className="flex-shrink-0 p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
          aria-label="Fechar notificação"
        >
          <X className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
        </button>
      </div>
      
      {/* Progress bar for timed notifications */}
      {notification.duration && notification.duration > 0 && (
        <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
          <div 
            className={`h-1 rounded-full transition-all ease-linear ${progressBarColor}`}
            style={{
              animation: `shrink ${notification.duration}ms linear forwards`
            }}
          />
        </div>
      )}
    </div>
  );
};

export const NotificationSystem: React.FC<NotificationSystemProps> = ({
  notifications,
  onRemoveNotification,
}) => {
  if (notifications.length === 0) return null;

  return (
    <>
      {/* Add keyframes for animations */}
      <style>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
        
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
      
      {/* Notification Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onRemove={onRemoveNotification}
          />
        ))}
      </div>
    </>
  );
};