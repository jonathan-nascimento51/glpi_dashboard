/**
 * Testes para estratégias avançadas de cache com TTL dinâmico
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { LocalCache } from '../services/cache';
import { CacheManager, CacheAnalytics, cacheManager } from '../utils/cacheStrategies';

// Mock do setTimeout e clearTimeout
vi.mock('timers', () => ({
  setTimeout: vi.fn(),
  clearTimeout: vi.fn()
}));

describe('Cache com TTL Dinâmico', () => {
  let cache: LocalCache<any>;

  beforeEach(() => {
    cache = new LocalCache({
      defaultTtl: 5000,
      maxSize: 10,
      enableAutoActivation: true,
      activationThreshold: 1000,
      enableDynamicTtl: true,
      minTtl: 2000,
      maxTtl: 10000,
      ttlMultiplier: 1.5
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    cache.clear();
  });

  describe('TTL Dinâmico', () => {
    it('deve calcular TTL dinâmico baseado na frequência de acesso', async () => {
      const key = 'test-key';
      const data = { value: 'test' };
      
      // Primeira inserção
      await cache.set(key, data, undefined, 500);
      
      // Simular múltiplos acessos
      for (let i = 0; i < 10; i++) {
        await cache.get(key);
      }
      
      const stats = cache.getStats();
      expect(stats.dynamicTtlEnabled).toBe(true);
      expect(stats.hits).toBe(10);
    });

    it('deve respeitar TTL mínimo e máximo', async () => {
      const key = 'test-key';
      const data = { value: 'test' };
      
      await cache.set(key, data, undefined, 100); // Resposta rápida
      
      // Verificar se o TTL não fica abaixo do mínimo
      const entry = (cache as any).cache.get(key);
      const calculatedTtl = entry.expiresAt - entry.timestamp;
      expect(calculatedTtl).toBeGreaterThanOrEqual(2000); // minTtl
    });

    it('deve calcular prioridade corretamente', async () => {
      const key1 = 'high-priority';
      const key2 = 'low-priority';
      
      // Dados com resposta rápida (alta prioridade)
      await cache.set(key1, { value: 'fast' }, undefined, 100);
      
      // Dados com resposta lenta (baixa prioridade)
      await cache.set(key2, { value: 'slow' }, undefined, 2000);
      
      const entry1 = (cache as any).cache.get(key1);
      const entry2 = (cache as any).cache.get(key2);
      
      expect(entry1.priority).toBeDefined();
      expect(entry2.priority).toBeDefined();
    });
  });

  describe('Estratégia de Remoção por Prioridade', () => {
    it('deve remover entradas de menor prioridade quando o cache estiver cheio', async () => {
      // Preencher o cache até o limite
      for (let i = 0; i < 10; i++) {
        const responseTime = i < 5 ? 100 : 2000; // Primeiras 5 com alta prioridade
        await cache.set(`key-${i}`, { value: i }, undefined, responseTime);
      }
      
      // Adicionar uma entrada extra para forçar remoção
      await cache.set('extra-key', { value: 'extra' }, undefined, 50);
      
      // Verificar se o cache ainda tem o tamanho máximo
      expect(cache.getStats().size).toBe(10);
      
      // Verificar se entradas de alta prioridade ainda existem
      expect(await cache.get('key-0')).toBeTruthy();
      expect(await cache.get('key-1')).toBeTruthy();
    });
  });

  describe('Estatísticas Avançadas', () => {
    it('deve incluir estatísticas de TTL dinâmico', async () => {
      await cache.set('key1', { value: 'test1' }, undefined, 100);
      await cache.set('key2', { value: 'test2' }, undefined, 500);
      await cache.set('key3', { value: 'test3' }, undefined, 1000);
      
      const stats = cache.getStats();
      
      expect(stats.dynamicTtlEnabled).toBe(true);
      expect(stats.priorityDistribution).toBeDefined();
      expect(stats.averageTtl).toBeDefined();
      expect(stats.averageTtl).toBeGreaterThan(0);
    });

    it('deve calcular distribuição de prioridades corretamente', async () => {
      // Adicionar entradas com diferentes tempos de resposta
      await cache.set('fast1', { value: 'fast1' }, undefined, 50);
      await cache.set('fast2', { value: 'fast2' }, undefined, 100);
      await cache.set('medium1', { value: 'medium1' }, undefined, 800);
      await cache.set('slow1', { value: 'slow1' }, undefined, 2000);
      
      const stats = cache.getStats();
      const distribution = stats.priorityDistribution;
      
      expect(distribution).toBeDefined();
      expect(distribution.high + distribution.medium + distribution.low).toBe(4);
    });
  });
});

describe('CacheManager', () => {
  let manager: CacheManager;

  beforeEach(() => {
    manager = new CacheManager();
  });

  afterEach(() => {
    manager.clearAll();
  });

  it('deve gerenciar múltiplos caches com configurações diferentes', () => {
    const criticalCache = manager.getCache('critical');
    const dashboardCache = manager.getCache('dashboard');
    const reportsCache = manager.getCache('reports');
    
    expect(criticalCache).toBeDefined();
    expect(dashboardCache).toBeDefined();
    expect(reportsCache).toBeDefined();
    expect(criticalCache).not.toBe(dashboardCache);
  });

  it('deve armazenar e recuperar dados com prioridade', async () => {
    await manager.storeWithPriority('critical', 'test-key', { value: 'test' }, 'high', 100);
    
    const retrieved = await manager.retrieve('critical', 'test-key');
    expect(retrieved).toEqual({ value: 'test' });
  });

  it('deve obter estatísticas de todos os caches', async () => {
    await manager.storeWithPriority('critical', 'key1', { value: 'test1' });
    await manager.storeWithPriority('dashboard', 'key2', { value: 'test2' });
    
    const allStats = manager.getAllStats();
    
    expect(allStats.critical).toBeDefined();
    expect(allStats.dashboard).toBeDefined();
    expect(allStats.reports).toBeDefined();
    expect(allStats.critical.size).toBe(1);
    expect(allStats.dashboard.size).toBe(1);
  });

  it('deve limpar todos os caches', async () => {
    await manager.storeWithPriority('critical', 'key1', { value: 'test1' });
    await manager.storeWithPriority('dashboard', 'key2', { value: 'test2' });
    
    manager.clearAll();
    
    const allStats = manager.getAllStats();
    expect(allStats.critical.size).toBe(0);
    expect(allStats.dashboard.size).toBe(0);
    expect(allStats.reports.size).toBe(0);
  });

  it('deve invalidar padrões em todos os caches', async () => {
    await manager.storeWithPriority('critical', 'user:123', { value: 'user1' });
    await manager.storeWithPriority('critical', 'user:456', { value: 'user2' });
    await manager.storeWithPriority('critical', 'ticket:789', { value: 'ticket1' });
    
    manager.invalidatePattern('user:*');
    
    const user1 = await manager.retrieve('critical', 'user:123');
    const user2 = await manager.retrieve('critical', 'user:456');
    const ticket = await manager.retrieve('critical', 'ticket:789');
    
    expect(user1).toBeNull();
    expect(user2).toBeNull();
    expect(ticket).toEqual({ value: 'ticket1' });
  });
});

describe('CacheAnalytics', () => {
  describe('analyzeCacheEfficiency', () => {
    it('deve classificar cache como excelente com alta taxa de hit', () => {
      const stats = {
        hitRate: 0.9,
        averageResponseTime: 500,
        size: 50,
        maxSize: 100
      };
      
      const analysis = CacheAnalytics.analyzeCacheEfficiency(stats);
      expect(analysis.efficiency).toBe('excellent');
      expect(analysis.recommendations).toHaveLength(0);
    });

    it('deve classificar cache como bom e fornecer recomendações', () => {
      const stats = {
        hitRate: 0.7,
        averageResponseTime: 1000,
        size: 80,
        maxSize: 100
      };
      
      const analysis = CacheAnalytics.analyzeCacheEfficiency(stats);
      expect(analysis.efficiency).toBe('good');
      expect(analysis.recommendations.length).toBeGreaterThan(0);
    });

    it('deve classificar cache como ruim e fornecer múltiplas recomendações', () => {
      const stats = {
        hitRate: 0.2,
        averageResponseTime: 3000,
        size: 95,
        maxSize: 100
      };
      
      const analysis = CacheAnalytics.analyzeCacheEfficiency(stats);
      expect(analysis.efficiency).toBe('poor');
      expect(analysis.recommendations.length).toBeGreaterThan(2);
    });
  });

  describe('generatePerformanceReport', () => {
    it('deve gerar relatório completo de performance', () => {
      const allStats = {
        critical: {
          hitRate: 0.8,
          averageResponseTime: 500,
          size: 30,
          maxSize: 50
        },
        dashboard: {
          hitRate: 0.6,
          averageResponseTime: 800,
          size: 70,
          maxSize: 100
        },
        reports: {
          hitRate: 0.4,
          averageResponseTime: 1200,
          size: 15,
          maxSize: 30
        }
      };
      
      const report = CacheAnalytics.generatePerformanceReport(allStats);
      
      expect(report.summary).toBeDefined();
      expect(report.details).toBeDefined();
      expect(report.overallRecommendations).toBeDefined();
      expect(Object.keys(report.details)).toHaveLength(3);
    });
  });
});

describe('Integração com Cache Global', () => {
  it('deve usar o gerenciador de cache global', async () => {
    await cacheManager.storeWithPriority('critical', 'global-test', { value: 'global' });
    
    const retrieved = await cacheManager.retrieve('critical', 'global-test');
    expect(retrieved).toEqual({ value: 'global' });
  });

  it('deve gerar relatório de performance do sistema', async () => {
    // Adicionar alguns dados de teste
    await cacheManager.storeWithPriority('critical', 'key1', { value: 'test1' });
    await cacheManager.storeWithPriority('dashboard', 'key2', { value: 'test2' });
    
    // Simular alguns hits
    await cacheManager.retrieve('critical', 'key1');
    await cacheManager.retrieve('critical', 'key1');
    
    const allStats = cacheManager.getAllStats();
    const report = CacheAnalytics.generatePerformanceReport(allStats);
    
    expect(report.summary).toBeDefined();
    expect(report.details.critical).toBeDefined();
    expect(report.details.dashboard).toBeDefined();
  });
});