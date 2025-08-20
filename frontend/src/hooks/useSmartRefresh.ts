/**
 * Hook para gerenciar auto-refresh inteligente
 * Coordena múltiplos componentes para evitar requisições simultâneas
 */

import { useEffect, useRef, useCallback } from 'react';
import { requestCoordinator } from '../services/requestCoordinator';

interface SmartRefreshConfig {
  /** Intervalo base em milissegundos (padrão: 5 minutos) */
  intervalMs?: number;
  /** Tempo mínimo sem interação do usuário para permitir refresh (padrão: 2 minutos) */
  minIdleTimeMs?: number;
  /** Chave única para identificar este refresh */
  refreshKey: string;
  /** Função a ser executada no refresh */
  refreshFn: () => Promise<void> | void;
  /** Se deve executar imediatamente na montagem */
  immediate?: boolean;
  /** Se o refresh está habilitado */
  enabled?: boolean;
}

interface UserInteractionTracker {
  lastInteraction: number;
  isIdle: boolean;
}

class SmartRefreshManager {
  private static instance: SmartRefreshManager;
  private activeRefreshers = new Map<string, NodeJS.Timeout>();
  private userInteraction: UserInteractionTracker = {
    lastInteraction: Date.now(),
    isIdle: false,
  };
  private interactionListeners: (() => void)[] = [];

  static getInstance(): SmartRefreshManager {
    if (!SmartRefreshManager.instance) {
      SmartRefreshManager.instance = new SmartRefreshManager();
    }
    return SmartRefreshManager.instance;
  }

  constructor() {
    this.setupInteractionTracking();
  }

  private setupInteractionTracking(): void {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];

    const updateInteraction = () => {
      this.userInteraction.lastInteraction = Date.now();
      this.userInteraction.isIdle = false;
      localStorage.setItem('lastUserInteraction', this.userInteraction.lastInteraction.toString());

      // Notificar listeners
      this.interactionListeners.forEach(listener => listener());
    };

    events.forEach(event => {
      document.addEventListener(event, updateInteraction, { passive: true });
    });

    // Verificar idle state a cada 30 segundos
    setInterval(() => {
      const now = Date.now();
      const timeSinceInteraction = now - this.userInteraction.lastInteraction;
      this.userInteraction.isIdle = timeSinceInteraction > 120000; // 2 minutos
    }, 30000);
  }

  isUserIdle(minIdleTimeMs: number = 120000): boolean {
    const now = Date.now();
    const timeSinceInteraction = now - this.userInteraction.lastInteraction;
    return timeSinceInteraction > minIdleTimeMs;
  }

  isAutoRefreshEnabled(): boolean {
    const setting = localStorage.getItem('autoRefreshEnabled');
    return setting !== 'false';
  }

  registerRefresher(config: SmartRefreshConfig): () => void {
    const {
      refreshKey,
      refreshFn,
      intervalMs = 300000, // 5 minutos
      minIdleTimeMs = 120000, // 2 minutos
      immediate = false,
      enabled = true,
    } = config;

    // Cancelar refresher existente se houver
    this.unregisterRefresher(refreshKey);

    if (!enabled) {
      return () => {};
    }

    // Executar imediatamente se solicitado
    if (immediate) {
      this.executeRefresh(refreshKey, refreshFn, minIdleTimeMs);
    }

    // Configurar intervalo
    const intervalId = setInterval(() => {
      this.executeRefresh(refreshKey, refreshFn, minIdleTimeMs);
    }, intervalMs);

    this.activeRefreshers.set(refreshKey, intervalId);

    console.log(`🔄 Smart refresh registrado: ${refreshKey} (${intervalMs / 1000}s)`);

    // Retornar função de cleanup
    return () => this.unregisterRefresher(refreshKey);
  }

  private async executeRefresh(
    refreshKey: string,
    refreshFn: () => Promise<void> | void,
    minIdleTimeMs: number
  ): Promise<void> {
    // Verificar se auto-refresh está habilitado
    if (!this.isAutoRefreshEnabled()) {
      console.log(`⏸️ Auto-refresh desabilitado para ${refreshKey}`);
      return;
    }

    // Verificar se usuário está idle
    if (!this.isUserIdle(minIdleTimeMs)) {
      console.log(`⏸️ Usuário ativo, pausando refresh de ${refreshKey}`);
      return;
    }

    try {
      console.log(`🔄 Executando smart refresh: ${refreshKey}`);
      await refreshFn();
      console.log(`✅ Smart refresh concluído: ${refreshKey}`);
    } catch (error) {
      console.error(`❌ Erro no smart refresh ${refreshKey}:`, error);
    }
  }

  unregisterRefresher(refreshKey: string): void {
    const intervalId = this.activeRefreshers.get(refreshKey);
    if (intervalId) {
      clearInterval(intervalId);
      this.activeRefreshers.delete(refreshKey);
      console.log(`🛑 Smart refresh removido: ${refreshKey}`);
    }
  }

  getActiveRefreshers(): string[] {
    return Array.from(this.activeRefreshers.keys());
  }

  pauseAllRefreshers(): void {
    localStorage.setItem('autoRefreshEnabled', 'false');
    console.log('⏸️ Todos os auto-refreshers pausados');
  }

  resumeAllRefreshers(): void {
    localStorage.setItem('autoRefreshEnabled', 'true');
    console.log('▶️ Todos os auto-refreshers retomados');
  }

  addInteractionListener(listener: () => void): () => void {
    this.interactionListeners.push(listener);
    return () => {
      const index = this.interactionListeners.indexOf(listener);
      if (index > -1) {
        this.interactionListeners.splice(index, 1);
      }
    };
  }
}

const refreshManager = SmartRefreshManager.getInstance();

/**
 * Hook para auto-refresh inteligente
 */
export function useSmartRefresh(config: SmartRefreshConfig) {
  const cleanupRef = useRef<(() => void) | null>(null);

  const refreshFn = useCallback(async () => {
    // Usar coordenador de requisições para evitar duplicatas
    return requestCoordinator.coordinateRequest(
      `refresh-${config.refreshKey}`,
      async () => {
        await config.refreshFn();
      },
      {
        debounceMs: 1000,
        throttleMs: 5000,
        cacheMs: 0, // Não cachear refreshes
      }
    );
  }, [config.refreshFn, config.refreshKey]);

  useEffect(() => {
    cleanupRef.current = refreshManager.registerRefresher({
      ...config,
      refreshFn,
    });

    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, [config.refreshKey, config.intervalMs, config.enabled, refreshFn]);

  return {
    pauseRefresh: () => refreshManager.pauseAllRefreshers(),
    resumeRefresh: () => refreshManager.resumeAllRefreshers(),
    isAutoRefreshEnabled: () => refreshManager.isAutoRefreshEnabled(),
    isUserIdle: (minIdleTime?: number) => refreshManager.isUserIdle(minIdleTime),
    activeRefreshers: refreshManager.getActiveRefreshers(),
  };
}

export default useSmartRefresh;
