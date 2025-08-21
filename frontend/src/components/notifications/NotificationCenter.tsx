import React, { useState, useMemo } from 'react';
import { Bell, X, Check, CheckCheck, Trash2, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { useNotificationContext } from '../../contexts/NotificationContext';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface NotificationCenterProps {
  className?: string;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ className = '' }) => {
  const {
    notifications,
    unreadCount,
    connectionStatus,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAllNotifications,
    isConnected
  } = useNotificationContext();

  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  // Filtrar notificações baseado no filtro selecionado
  const filteredNotifications = useMemo(() => {
    if (filter === 'unread') {
      return notifications.filter(n => !n.read);
    }
    return notifications;
  }, [notifications, filter]);

  // Ícone de status de conexão
  const ConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="w-3 h-3 text-green-500" />;
      case 'disconnected':
        return <WifiOff className="w-3 h-3 text-gray-400" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />;
      case 'reconnecting':
        return <div className="w-3 h-3 border border-yellow-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <WifiOff className="w-3 h-3 text-gray-400" />;
    }
  };

  // Obter configuração de estilo para cada tipo de notificação
  const getNotificationStyle = (type: string) => {
    switch (type) {
      case 'success':
        return {
          borderColor: 'border-l-green-500',
          bgColor: 'bg-green-50 dark:bg-green-900/10',
          iconColor: 'text-green-600 dark:text-green-400'
        };
      case 'error':
        return {
          borderColor: 'border-l-red-500',
          bgColor: 'bg-red-50 dark:bg-red-900/10',
          iconColor: 'text-red-600 dark:text-red-400'
        };
      case 'warning':
        return {
          borderColor: 'border-l-yellow-500',
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/10',
          iconColor: 'text-yellow-600 dark:text-yellow-400'
        };
      default:
        return {
          borderColor: 'border-l-blue-500',
          bgColor: 'bg-blue-50 dark:bg-blue-900/10',
          iconColor: 'text-blue-600 dark:text-blue-400'
        };
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Botão de notificações */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
        aria-label="Centro de notificações"
      >
        <Bell className="w-5 h-5" />
        
        {/* Badge de contagem */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        
        {/* Indicador de status de conexão */}
        <div className="absolute -bottom-1 -right-1">
          <ConnectionIcon />
        </div>
      </button>

      {/* Painel de notificações */}
      {isOpen && (
        <>
          {/* Overlay para fechar ao clicar fora */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Painel */}
          <div className="absolute right-0 top-full mt-2 w-96 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 max-h-96 flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Notificações
                </h3>
                <div className="flex items-center gap-2">
                  <ConnectionIcon />
                  <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                    {connectionStatus === 'connected' ? 'Conectado' : 
                     connectionStatus === 'disconnected' ? 'Desconectado' :
                     connectionStatus === 'error' ? 'Erro' : 'Reconectando'}
                  </span>
                </div>
              </div>
              
              {/* Filtros e ações */}
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <button
                    onClick={() => setFilter('all')}
                    className={`px-3 py-1 text-xs rounded-full transition-colors ${
                      filter === 'all'
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    Todas ({notifications.length})
                  </button>
                  <button
                    onClick={() => setFilter('unread')}
                    className={`px-3 py-1 text-xs rounded-full transition-colors ${
                      filter === 'unread'
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    Não lidas ({unreadCount})
                  </button>
                </div>
                
                <div className="flex gap-1">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded transition-colors"
                      title="Marcar todas como lidas"
                    >
                      <CheckCheck className="w-4 h-4" />
                    </button>
                  )}
                  {notifications.length > 0 && (
                    <button
                      onClick={clearAllNotifications}
                      className="p-1 text-gray-500 hover:text-red-600 dark:hover:text-red-400 rounded transition-colors"
                      title="Limpar todas"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Lista de notificações */}
            <div className="flex-1 overflow-y-auto">
              {filteredNotifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                  <Bell className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">
                    {filter === 'unread' ? 'Nenhuma notificação não lida' : 'Nenhuma notificação'}
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredNotifications.map(notification => {
                    const style = getNotificationStyle(notification.type);
                    
                    return (
                      <div
                        key={notification.id}
                        className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors border-l-4 ${
                          style.borderColor
                        } ${!notification.read ? style.bgColor : ''}`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className={`text-sm font-medium text-gray-900 dark:text-white ${
                                !notification.read ? 'font-semibold' : ''
                              }`}>
                                {notification.title}
                              </h4>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                              )}
                            </div>
                            
                            <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                              {notification.message}
                            </p>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {notification.timestamp ? formatDistanceToNow(new Date(notification.timestamp), {
                                  addSuffix: true,
                                  locale: ptBR
                                }) : 'Agora'}
                              </span>
                              
                              {notification.category && (
                                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                                  {notification.category === 'ticket_update' ? 'Ticket' :
                                   notification.category === 'system_alert' ? 'Sistema' :
                                   notification.category === 'maintenance' ? 'Manutenção' : 'Geral'}
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex gap-1">
                            {!notification.read && (
                              <button
                                onClick={() => markAsRead(notification.id)}
                                className="p-1 text-gray-400 hover:text-green-600 dark:hover:text-green-400 rounded transition-colors"
                                title="Marcar como lida"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={() => removeNotification(notification.id)}
                              className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded transition-colors"
                              title="Remover"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export { NotificationCenter };
export default NotificationCenter;