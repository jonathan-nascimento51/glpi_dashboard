import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface RefreshControlProps {
  onRefresh: () => void;
  isLoading?: boolean;
  lastUpdated?: Date | null;
  className?: string;
}

export const RefreshControl: React.FC<RefreshControlProps> = ({
  onRefresh,
  isLoading = false,
  lastUpdated,
  className = ''
}) => {
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(true);
  const [timeUntilNextRefresh, setTimeUntilNextRefresh] = useState(300); // 5 minutos

  // Controlar o estado do auto-refresh no localStorage
  useEffect(() => {
    const savedState = localStorage.getItem('autoRefreshEnabled');
    if (savedState !== null) {
      setIsAutoRefreshEnabled(JSON.parse(savedState));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('autoRefreshEnabled', JSON.stringify(isAutoRefreshEnabled));
  }, [isAutoRefreshEnabled]);

  // Countdown para próximo refresh
  useEffect(() => {
    if (!isAutoRefreshEnabled) {
      setTimeUntilNextRefresh(0);
      return;
    }

    const interval = setInterval(() => {
      const lastInteraction = localStorage.getItem('lastUserInteraction');
      const now = Date.now();
      const timeSinceInteraction = lastInteraction ? now - parseInt(lastInteraction) : Infinity;
      
      if (timeSinceInteraction > 120000) { // 2 minutos sem interação
        const nextRefreshTime = 300 - Math.floor((now % 300000) / 1000); // 5 minutos
        setTimeUntilNextRefresh(nextRefreshTime);
      } else {
        setTimeUntilNextRefresh(0); // Pausado por interação
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isAutoRefreshEnabled]);

  const toggleAutoRefresh = () => {
    setIsAutoRefreshEnabled(!isAutoRefreshEnabled);
  };

  const handleManualRefresh = () => {
    // Marcar como interação do usuário
    localStorage.setItem('lastUserInteraction', Date.now().toString());
    onRefresh();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatLastUpdated = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return `${diff}s atrás`;
    if (diff < 3600) return `${Math.floor(diff / 60)}min atrás`;
    return `${Math.floor(diff / 3600)}h atrás`;
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Status do Auto-refresh */}
      <Badge 
        variant={isAutoRefreshEnabled ? "default" : "secondary"}
        className="flex items-center gap-1"
      >
        {isAutoRefreshEnabled ? (
          <>
            <Play className="w-3 h-3" />
            Auto
          </>
        ) : (
          <>
            <Pause className="w-3 h-3" />
            Pausado
          </>
        )}
      </Badge>

      {/* Countdown */}
      {isAutoRefreshEnabled && timeUntilNextRefresh > 0 && (
        <Badge variant="outline" className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {formatTime(timeUntilNextRefresh)}
        </Badge>
      )}

      {/* Última atualização */}
      {lastUpdated && (
        <Badge variant="outline" className="text-xs">
          {formatLastUpdated(lastUpdated)}
        </Badge>
      )}

      {/* Controles */}
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          onClick={toggleAutoRefresh}
          className="h-8 w-8 p-0"
          title={isAutoRefreshEnabled ? 'Pausar auto-refresh' : 'Ativar auto-refresh'}
        >
          {isAutoRefreshEnabled ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleManualRefresh}
          disabled={isLoading}
          className="h-8 w-8 p-0"
          title="Atualizar agora"
        >
          <RotateCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>
    </div>
  );
};

export default RefreshControl;