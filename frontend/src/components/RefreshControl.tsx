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
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Status do Auto-refresh com design melhorado */}
      <div className="flex items-center gap-2">
        <Badge 
           variant={isAutoRefreshEnabled ? "default" : "secondary"}
           className={`flex items-center gap-1.5 px-3 py-1.5 font-medium transition-all duration-200 rounded-md border-0 ${
             isAutoRefreshEnabled 
               ? 'bg-white/20 hover:bg-white/30 text-white shadow-sm backdrop-blur-sm' 
               : 'bg-white/10 hover:bg-white/20 text-white/70 backdrop-blur-sm'
           }`}
        >
          {isAutoRefreshEnabled ? (
            <>
              <Play className="w-3.5 h-3.5" />
              <span className="text-xs font-semibold">Auto</span>
            </>
          ) : (
            <>
              <Pause className="w-3.5 h-3.5" />
              <span className="text-xs font-semibold">Pausado</span>
            </>
          )}
        </Badge>

        {/* Countdown com melhor visual */}
        {isAutoRefreshEnabled && timeUntilNextRefresh > 0 && (
           <Badge 
             variant="outline" 
             className="flex items-center gap-1.5 px-2.5 py-1 bg-white/15 border-white/30 text-white font-mono text-xs backdrop-blur-sm rounded-md"
           >
            <Clock className="w-3 h-3" />
            <span className="font-semibold">{formatTime(timeUntilNextRefresh)}</span>
          </Badge>
        )}
      </div>

      {/* Última atualização com design aprimorado */}
      {lastUpdated && (
        <Badge 
          variant="outline" 
          className="px-2.5 py-1 bg-white/10 border-white/20 text-white/80 text-xs font-medium backdrop-blur-sm rounded-md"
        >
          {formatLastUpdated(lastUpdated)}
        </Badge>
      )}

      {/* Controles com visual moderno */}
      <div className="flex items-center gap-1.5">
        <Button
          variant="outline"
          size="sm"
          onClick={toggleAutoRefresh}
          className={`h-8 w-8 p-0 transition-all duration-200 hover:scale-105 rounded-md border-0 ${
             isAutoRefreshEnabled 
               ? 'bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm' 
               : 'bg-white/5 hover:bg-white/15 text-white/70 backdrop-blur-sm'
           }`}
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
          className="h-8 w-8 p-0 bg-white/10 hover:bg-white/20 text-white transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 rounded-md border-0 backdrop-blur-sm"
          title="Atualizar agora"
        >
          <RotateCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>
    </div>
  );
};

export default RefreshControl;