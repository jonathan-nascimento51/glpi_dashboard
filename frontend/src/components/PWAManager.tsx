import React, { useEffect, useState } from 'react';
import { Wifi, WifiOff, Download, RefreshCw } from 'lucide-react';
import useServiceWorker from '../hooks/useServiceWorker';

interface PWAManagerProps {
  className?: string;
}

const PWAManager: React.FC<PWAManagerProps> = ({ className = '' }) => {
  const {
    isSupported,
    isRegistered,
    isInstalling,
    isControlling,
    error,
    register,
    clearCache
  } = useServiceWorker();

  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  // Detectar status de conexão
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Detectar prompt de instalação PWA
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Registrar Service Worker automaticamente
  useEffect(() => {
    if (isSupported && !isRegistered) {
      register();
    }
  }, [isSupported, isRegistered, register]);

  const handleInstallPWA = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('PWA instalado');
      }
      
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    }
  };

  const handleClearCache = async () => {
    try {
      await clearCache();
      window.location.reload();
    } catch (error) {
      console.error('Erro ao limpar cache:', error);
    }
  };

  if (!isSupported) {
    return null;
  }

  return (
    <div className={`pwa-manager ${className}`}>
      {/* Status de Conexão */}
      <div className="flex items-center gap-2 text-sm">
        {isOnline ? (
          <>
            <Wifi className="w-4 h-4 text-green-500" />
            <span className="text-green-600">Online</span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4 text-red-500" />
            <span className="text-red-600">Offline</span>
          </>
        )}
      </div>

      {/* Status do Service Worker */}
      {isRegistered && (
        <div className="flex items-center gap-2 text-sm text-blue-600">
          <RefreshCw className={`w-4 h-4 ${isInstalling ? 'animate-spin' : ''}`} />
          <span>
            {isInstalling ? 'Atualizando...' : isControlling ? 'Cache ativo' : 'Registrado'}
          </span>
        </div>
      )}

      {/* Botão de Instalação PWA */}
      {showInstallPrompt && (
        <button
          onClick={handleInstallPWA}
          className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          <Download className="w-4 h-4" />
          Instalar App
        </button>
      )}

      {/* Botão de Limpar Cache */}
      {isControlling && (
        <button
          onClick={handleClearCache}
          className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
          title="Limpar cache e recarregar"
        >
          <RefreshCw className="w-4 h-4" />
          Limpar Cache
        </button>
      )}

      {/* Erro */}
      {error && (
        <div className="text-sm text-red-600" title={error}>
          Erro no SW
        </div>
      )}
    </div>
  );
};

export default PWAManager;
