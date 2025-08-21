import React, { createContext, useContext, ReactNode } from 'react';
import { useNotifications, UseNotificationsReturn } from '../hooks/useNotifications';

interface NotificationContextType extends UseNotificationsReturn {}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const notificationState = useNotifications();

  return (
    <NotificationContext.Provider value={notificationState}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotificationContext = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotificationContext deve ser usado dentro de um NotificationProvider');
  }
  return context;
};

export default NotificationContext;