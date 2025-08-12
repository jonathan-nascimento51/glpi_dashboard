import { useEffect, useState } from 'react';

interface ServiceWorkerState {
  isSupported: boolean;
  isRegistered: boolean;
  isInstalling: boolean;
  isWaiting: boolean;
  isControlling: boolean;
  error: string | null;
}

interface ServiceWorkerActions {
  register: () => Promise<void>;
  unregister: () => Promise<void>;
  update: () => Promise<void>;
  skipWaiting: () => void;
  clearCache: () => Promise<void>;
}

export function useServiceWorker(): ServiceWorkerState & ServiceWorkerActions {
  const [state, setState] = useState<ServiceWorkerState>({
    isSupported: 'serviceWorker' in navigator,
    isRegistered: false,
    isInstalling: false,
    isWaiting: false,
    isControlling: false,
    error: null
  });

  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  const register = async (): Promise<void> => {
    if (!state.isSupported) {
      setState(prev => ({ ...prev, error: 'Service Worker não suportado' }));
      return;
    }

    try {
      setState(prev => ({ ...prev, isInstalling: true, error: null }));
      
      const reg = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });
      
      setRegistration(reg);
      
      setState(prev => ({
        ...prev,
        isRegistered: true,
        isInstalling: false,
        isControlling: !!navigator.serviceWorker.controller
      }));

      console.log('[SW Hook] Service Worker registrado:', reg.scope);
      
    } catch (error) {
      console.error('[SW Hook] Erro ao registrar Service Worker:', error);
      setState(prev => ({
        ...prev,
        isInstalling: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      }));
    }
  };

  const clearCache = async (): Promise<void> => {
    if (!navigator.serviceWorker.controller) {
      setState(prev => ({ ...prev, error: 'Service Worker não está controlando a página' }));
      return;
    }

    try {
      const messageChannel = new MessageChannel();
      
      const promise = new Promise<void>((resolve, reject) => {
        messageChannel.port1.onmessage = (event) => {
          if (event.data.success) {
            console.log('[SW Hook] Cache limpo com sucesso');
            resolve();
          } else {
            reject(new Error('Falha ao limpar cache'));
          }
        };
      });
      
      navigator.serviceWorker.controller.postMessage(
        { type: 'CLEAR_CACHE' },
        [messageChannel.port2]
      );
      
      await promise;
    } catch (error) {
      console.error('[SW Hook] Erro ao limpar cache:', error);
    }
  };

  useEffect(() => {
    if (!state.isSupported) return;

    const handleControllerChange = () => {
      setState(prev => ({ ...prev, isControlling: !!navigator.serviceWorker.controller }));
    };

    navigator.serviceWorker.addEventListener('controllerchange', handleControllerChange);

    if (navigator.serviceWorker.controller) {
      setState(prev => ({ ...prev, isControlling: true }));
    }

    return () => {
      navigator.serviceWorker.removeEventListener('controllerchange', handleControllerChange);
    };
  }, [state.isSupported]);

  return {
    ...state,
    register,
    unregister: async () => {},
    update: async () => {},
    skipWaiting: () => {},
    clearCache
  };
}

export default useServiceWorker;
