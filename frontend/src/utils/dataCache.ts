/**
 * Sistema de cache inteligente para dados do dashboard
 * Implementa estratégias de cache com validação de integridade
 */

import { MetricsData, SystemStatus, TechnicianRanking } from '../types';
import { validateAllData, DataIntegrityReport } from './dataValidation';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  validationReport: DataIntegrityReport | null;
  isValid: boolean;
}

interface DashboardCache {
  metrics: CacheEntry<MetricsData> | null;
  systemStatus: CacheEntry<SystemStatus> | null;
  technicianRanking: CacheEntry<TechnicianRanking[]> | null;
}

class DataCacheManager {
  private cache: DashboardCache = {
    metrics: null,
    systemStatus: null,
    technicianRanking: null
  };

  private readonly CACHE_DURATION = 300000; // 5 minutos - aumentado para reduzir consultas
  private readonly MAX_STALE_DURATION = 600000; // 10 minutos

  /**
   * Armazena dados no cache com validação
   */
  set(
    metrics: any,
    systemStatus: any,
    technicianRanking: any
  ): DataIntegrityReport {
    const timestamp = Date.now();
    
    // Validar todos os dados
    const validationReport = validateAllData(metrics, systemStatus, technicianRanking);
    
    // Armazenar no cache
    this.cache.metrics = {
      data: validationReport.metrics.data,
      timestamp,
      validationReport,
      isValid: validationReport.metrics.isValid
    };
    
    this.cache.systemStatus = {
      data: validationReport.systemStatus.data,
      timestamp,
      validationReport,
      isValid: validationReport.systemStatus.isValid
    };
    
    this.cache.technicianRanking = {
      data: validationReport.technicianRanking.data,
      timestamp,
      validationReport,
      isValid: validationReport.technicianRanking.isValid
    };
    
    console.log('📦 Dados armazenados no cache:', {
      timestamp: new Date(timestamp).toISOString(),
      isValid: validationReport.overallValid,
      errors: validationReport.metrics.errors.length + 
              validationReport.systemStatus.errors.length + 
              validationReport.technicianRanking.errors.length,
      warnings: validationReport.metrics.warnings.length + 
                validationReport.systemStatus.warnings.length + 
                validationReport.technicianRanking.warnings.length
    });
    
    return validationReport;
  }

  /**
   * Recupera dados do cache se ainda válidos
   */
  get(): {
    metrics: MetricsData | null;
    systemStatus: SystemStatus | null;
    technicianRanking: TechnicianRanking[];
    validationReport: DataIntegrityReport | null;
    isFromCache: boolean;
    cacheStatus: 'fresh' | 'stale' | 'expired' | 'empty';
  } {
    const now = Date.now();
    
    // Verificar se há dados no cache
    if (!this.cache.metrics || !this.cache.systemStatus || !this.cache.technicianRanking) {
      return {
        metrics: null,
        systemStatus: null,
        technicianRanking: [],
        validationReport: null,
        isFromCache: false,
        cacheStatus: 'empty'
      };
    }
    
    const age = now - this.cache.metrics.timestamp;
    
    // Determinar status do cache
    let cacheStatus: 'fresh' | 'stale' | 'expired';
    if (age <= this.CACHE_DURATION) {
      cacheStatus = 'fresh';
    } else if (age <= this.MAX_STALE_DURATION) {
      cacheStatus = 'stale';
    } else {
      cacheStatus = 'expired';
    }
    
    // Se expirado, limpar cache
    if (cacheStatus === 'expired') {
      this.clear();
      return {
        metrics: null,
        systemStatus: null,
        technicianRanking: [],
        validationReport: null,
        isFromCache: false,
        cacheStatus: 'expired'
      };
    }
    
    console.log(`📦 Dados recuperados do cache (${cacheStatus}):`, {
      age: Math.round(age / 1000) + 's',
      isValid: (this.cache.metrics?.validationReport?.metrics?.isValid ?? false) && 
                (this.cache.systemStatus?.validationReport?.systemStatus?.isValid ?? false) && 
                (this.cache.technicianRanking?.validationReport?.technicianRanking?.isValid ?? false)
    });
    
    return {
      metrics: this.cache.metrics.data,
      systemStatus: this.cache.systemStatus.data,
      technicianRanking: this.cache.technicianRanking.data,
      validationReport: this.cache.metrics.validationReport,
      isFromCache: true,
      cacheStatus
    };
  }

  /**
   * Verifica se o cache está válido e fresco
   */
  isFresh(): boolean {
    if (!this.cache.metrics) return false;
    
    const age = Date.now() - this.cache.metrics.timestamp;
    return age <= this.CACHE_DURATION;
  }

  /**
   * Verifica se o cache existe mas está obsoleto
   */
  isStale(): boolean {
    if (!this.cache.metrics) return false;
    
    const age = Date.now() - this.cache.metrics.timestamp;
    return age > this.CACHE_DURATION && age <= this.MAX_STALE_DURATION;
  }

  /**
   * Limpa o cache
   */
  clear(): void {
    this.cache = {
      metrics: null,
      systemStatus: null,
      technicianRanking: null
    };
    console.log('🗑️ Cache limpo');
  }

  /**
   * Obtém informações sobre o estado do cache
   */
  getInfo(): {
    hasData: boolean;
    age: number;
    status: 'fresh' | 'stale' | 'expired' | 'empty';
    isValid: boolean;
    lastUpdate: Date | null;
  } {
    if (!this.cache.metrics) {
      return {
        hasData: false,
        age: 0,
        status: 'empty',
        isValid: false,
        lastUpdate: null
      };
    }
    
    const age = Date.now() - this.cache.metrics.timestamp;
    let status: 'fresh' | 'stale' | 'expired';
    
    if (age <= this.CACHE_DURATION) {
      status = 'fresh';
    } else if (age <= this.MAX_STALE_DURATION) {
      status = 'stale';
    } else {
      status = 'expired';
    }
    
    return {
      hasData: true,
      age,
      status,
      isValid: (this.cache.metrics?.validationReport?.metrics?.isValid ?? false) && 
                (this.cache.systemStatus?.validationReport?.systemStatus?.isValid ?? false) && 
                (this.cache.technicianRanking?.validationReport?.technicianRanking?.isValid ?? false),
      lastUpdate: new Date(this.cache.metrics.timestamp)
    };
  }

  /**
   * Força uma atualização do cache invalidando os dados atuais
   */
  invalidate(): void {
    if (this.cache.metrics) {
      // Marcar como expirado sem limpar completamente
      this.cache.metrics.timestamp = 0;
      this.cache.systemStatus!.timestamp = 0;
      this.cache.technicianRanking!.timestamp = 0;
      console.log('⚠️ Cache invalidado');
    }
  }

  /**
   * Estratégia inteligente de recuperação de dados
   * Retorna dados do cache se disponíveis, senão busca novos dados
   */
  async getOrFetch(
    fetchFunction: () => Promise<{
      metrics: any;
      systemStatus: any;
      technicianRanking: any;
    }>
  ): Promise<{
    metrics: MetricsData;
    systemStatus: SystemStatus;
    technicianRanking: TechnicianRanking[];
    validationReport: DataIntegrityReport;
    isFromCache: boolean;
    cacheStatus: string;
  }> {
    const cached = this.get();
    
    // Se temos dados frescos, usar do cache
    if (cached.cacheStatus === 'fresh' && cached.metrics && cached.validationReport) {
      return {
        metrics: cached.metrics,
        systemStatus: cached.systemStatus!,
        technicianRanking: cached.technicianRanking,
        validationReport: cached.validationReport,
        isFromCache: true,
        cacheStatus: cached.cacheStatus
      };
    }
    
    // Se temos dados obsoletos, usar enquanto busca novos em background
    if (cached.cacheStatus === 'stale' && cached.metrics && cached.validationReport) {
      // Buscar novos dados em background (não aguardar)
      fetchFunction().then(newData => {
        this.set(newData.metrics, newData.systemStatus, newData.technicianRanking);
      }).catch(error => {
        console.warn('Falha ao atualizar cache em background:', error);
      });
      
      return {
        metrics: cached.metrics,
        systemStatus: cached.systemStatus!,
        technicianRanking: cached.technicianRanking,
        validationReport: cached.validationReport,
        isFromCache: true,
        cacheStatus: cached.cacheStatus
      };
    }
    
    // Buscar dados frescos
    const newData = await fetchFunction();
    const validationReport = this.set(
      newData.metrics,
      newData.systemStatus,
      newData.technicianRanking
    );
    
    return {
      metrics: validationReport.metrics.data,
      systemStatus: validationReport.systemStatus.data,
      technicianRanking: validationReport.technicianRanking.data,
      validationReport,
      isFromCache: false,
      cacheStatus: 'fresh'
    };
  }
}

// Instância singleton do gerenciador de cache
export const dataCacheManager = new DataCacheManager();

// Utilitários para debugging
export const debugCache = {
  info: () => dataCacheManager.getInfo(),
  clear: () => dataCacheManager.clear(),
  invalidate: () => dataCacheManager.invalidate()
};

// Expor no window para debugging em desenvolvimento
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).debugCache = debugCache;
}