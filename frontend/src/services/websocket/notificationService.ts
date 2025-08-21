import { NotificationData } from '../../types';

export interface WebSocketNotification extends NotificationData {
  read?: boolean;
  category?: 'ticket_update' | 'system_alert' | 'maintenance' | 'general';
}

export type NotificationEventType = 'ticket_update' | 'system_alert' | 'maintenance' | 'general' | 'connection_status';

export interface NotificationListener {
  (notification: WebSocketNotification): void;
}

export interface ConnectionStatusListener {
  (status: 'connected' | 'disconnected' | 'error' | 'reconnecting'): void;
}

class NotificationService {
  private ws: WebSocket | null = null;
  private listeners: Map<NotificationEventType, Function[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;
  private connectionStatus: 'connected' | 'disconnected' | 'error' | 'reconnecting' = 'disconnected';

  constructor() {
    this.initializeListeners();
  }

  private initializeListeners() {
    // Inicializar maps para cada tipo de evento
    const eventTypes: NotificationEventType[] = ['ticket_update', 'system_alert', 'maintenance', 'general', 'connection_status'];
    eventTypes.forEach(type => {
      this.listeners.set(type, []);
    });
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.isConnecting = true;
      this.updateConnectionStatus('reconnecting');

      try {
        // URL do WebSocket - pode ser configurada via variável de ambiente
        const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8080/ws/notifications';
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket conectado para notificações');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.updateConnectionStatus('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Erro ao processar mensagem WebSocket:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket desconectado:', event.code, event.reason);
          this.isConnecting = false;
          this.updateConnectionStatus('disconnected');
          
          // Tentar reconectar se não foi fechamento intencional
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('Erro no WebSocket:', error);
          this.isConnecting = false;
          this.updateConnectionStatus('error');
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        this.updateConnectionStatus('error');
        reject(error);
      }
    });
  }

  private scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Backoff exponencial
    
    console.log(`Tentando reconectar em ${delay}ms (tentativa ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect().catch(console.error);
      }
    }, delay);
  }

  private handleMessage(data: any) {
    // Processar diferentes tipos de mensagem
    if (data.type && data.notification) {
      const notification: WebSocketNotification = {
        id: data.notification.id || Date.now().toString(),
        title: data.notification.title || 'Nova Notificação',
        message: data.notification.message || '',
        type: data.notification.type || 'info',
        timestamp: new Date(data.notification.timestamp || Date.now()),
        duration: data.notification.duration,
        read: false,
        category: data.type
      };

      this.emit(data.type, notification);
    }
  }

  private updateConnectionStatus(status: 'connected' | 'disconnected' | 'error' | 'reconnecting') {
    this.connectionStatus = status;
    this.emit('connection_status', status);
  }

  subscribe(type: NotificationEventType, callback: Function): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    
    this.listeners.get(type)!.push(callback);
    
    // Retornar função de unsubscribe
    return () => {
      const callbacks = this.listeners.get(type);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  private emit(type: NotificationEventType, data: any) {
    const callbacks = this.listeners.get(type) || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Erro ao executar callback para ${type}:`, error);
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Desconexão intencional');
      this.ws = null;
    }
    this.updateConnectionStatus('disconnected');
  }

  getConnectionStatus(): 'connected' | 'disconnected' | 'error' | 'reconnecting' {
    return this.connectionStatus;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // Método para simular notificações (útil para desenvolvimento)
  simulateNotification(type: NotificationEventType, notification: Partial<WebSocketNotification>) {
    const mockNotification: WebSocketNotification = {
      id: Date.now().toString(),
      title: 'Notificação de Teste',
      message: 'Esta é uma notificação simulada',
      type: 'info',
      timestamp: new Date(),
      read: false,
      category: type,
      ...notification
    };

    this.emit(type, mockNotification);
  }
}

// Singleton instance
const notificationService = new NotificationService();

export default notificationService;
export { NotificationService };