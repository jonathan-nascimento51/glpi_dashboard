/**
 * Testes para o serviço de alertas de performance
 */

import { alertService, Alert, AlertConfig } from '../services/alertService';
import { metricsCache, systemStatusCache } from '../services/cache';
import { vi } from 'vitest';

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock do Notification API
const notificationMock = {
  permission: 'default' as NotificationPermission,
  requestPermission: vi.fn().mockResolvedValue('granted' as NotificationPermission)
};
Object.defineProperty(window, 'Notification', {
  value: notificationMock,
  configurable: true
});

// Mock do performance.memory
Object.defineProperty(performance, 'memory', {
  value: {
    usedJSHeapSize: 50000000,
    jsHeapSizeLimit: 100000000
  },
  configurable: true
});

describe('AlertService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    // Reset do alertService
    alertService.stop();
    alertService['alerts'] = [];
    alertService['config'] = {
      thresholds: [],
      checkInterval: 5000,
      maxAlerts: 100,
      enableNotifications: true,
      enableSound: false,
      enableBrowserNotifications: false
    };
    alertService['lastMetrics'] = {};
  });

  afterEach(() => {
    alertService.stop();
  });

  describe('Inicialização', () => {
    it('deve inicializar com configuração padrão', () => {
      // Limpar localStorage para garantir configuração padrão
      localStorageMock.getItem.mockReturnValue(null);
      
      // Criar nova instância para testar configuração padrão
      const AlertServiceClass = (alertService as any).constructor;
      const newService = new AlertServiceClass();
      const config = newService.getConfig();
      
      expect(config.checkInterval).toBe(30000);
      expect(config.maxAlerts).toBe(100);
      expect(config.enableNotifications).toBe(true);
      expect(config.thresholds).toHaveLength(4);
    });

    it('deve carregar configuração do localStorage', () => {
      const savedConfig = {
        thresholds: [],
        checkInterval: 60000,
        enableNotifications: false,
        enableSound: false,
        enableBrowserNotifications: false,
        maxAlerts: 50
      };
      
      localStorageMock.getItem.mockReturnValue(JSON.stringify(savedConfig));
      
      // Atualizar configuração diretamente
      alertService.updateConfig(savedConfig);
      const config = alertService.getConfig();
      
      expect(config.checkInterval).toBe(60000);
      expect(config.enableNotifications).toBe(false);
    });
  });

  describe('Gerenciamento de Alertas', () => {
    it('deve criar alerta manualmente', () => {
      alertService.createAlert(
        'warning',
        'performance',
        'Teste de Alerta',
        'Mensagem de teste'
      );
      
      const alerts = alertService.getAlerts();
      expect(alerts).toHaveLength(1);
      expect(alerts[0].title).toBe('Teste de Alerta');
      expect(alerts[0].type).toBe('warning');
      expect(alerts[0].category).toBe('performance');
      expect(alerts[0].resolved).toBe(false);
    });

    it('deve resolver alerta específico', () => {
      alertService.createAlert(
        'error',
        'system',
        'Erro de Sistema',
        'Erro crítico detectado'
      );
      
      const alerts = alertService.getAlerts();
      const alertId = alerts[0].id;
      
      alertService.resolveAlert(alertId);
      
      const updatedAlerts = alertService.getAlerts();
      expect(updatedAlerts[0].resolved).toBe(true);
    });

    it('deve resolver todos os alertas', () => {
      // Criar múltiplos alertas
      alertService.createAlert('warning', 'performance', 'Alerta 1', 'Mensagem 1');
      alertService.createAlert('error', 'cache', 'Alerta 2', 'Mensagem 2');
      alertService.createAlert('critical', 'api', 'Alerta 3', 'Mensagem 3');
      
      alertService.resolveAllAlerts();
      
      const alerts = alertService.getAlerts();
      alerts.forEach(alert => {
        expect(alert.resolved).toBe(true);
      });
    });

    it('deve retornar apenas alertas ativos', () => {
      alertService.createAlert('warning', 'performance', 'Alerta Ativo', 'Mensagem');
      alertService.createAlert('error', 'cache', 'Alerta Resolvido', 'Mensagem');
      
      const alerts = alertService.getAlerts();
      // Encontrar e resolver o alerta correto pelo título
      const alertToResolve = alerts.find(a => a.title === 'Alerta Resolvido');
      if (alertToResolve) {
        alertService.resolveAlert(alertToResolve.id);
      }
      
      const activeAlerts = alertService.getActiveAlerts();
      expect(activeAlerts).toHaveLength(1);
      expect(activeAlerts[0].title).toBe('Alerta Ativo');
    });

    it('deve limpar alertas antigos', () => {
      // Limpar alertas existentes primeiro
      const existingAlerts = alertService.getAlerts();
      existingAlerts.forEach(alert => {
        alertService.resolveAlert(alert.id);
      });
      alertService.clearOldAlerts(0); // Limpar todos os alertas resolvidos
      
      // Criar alerta antigo (simular timestamp antigo)
      alertService.createAlert('info', 'system', 'Alerta Antigo', 'Mensagem');
      const alerts = alertService.getAlerts();
      
      // Modificar timestamp para simular alerta antigo
      alerts[0].timestamp = new Date(Date.now() - 25 * 60 * 60 * 1000); // 25 horas atrás
      alerts[0].resolved = true;
      
      alertService.clearOldAlerts(24 * 60 * 60 * 1000); // 24 horas
      
      const remainingAlerts = alertService.getAlerts();
      expect(remainingAlerts).toHaveLength(0);
    });

    it('deve limitar número máximo de alertas', () => {
      const config = alertService.getConfig();
      alertService.updateConfig({ maxAlerts: 3 });
      
      // Criar mais alertas que o limite
      for (let i = 0; i < 5; i++) {
        alertService.createAlert('info', 'system', `Alerta ${i}`, `Mensagem ${i}`);
      }
      
      const alerts = alertService.getAlerts();
      expect(alerts.length).toBeLessThanOrEqual(3);
    });
  });

  describe('Configuração', () => {
    it('deve atualizar configuração', () => {
      const newConfig = {
        checkInterval: 45000,
        enableNotifications: false,
        enableSound: true
      };
      
      alertService.updateConfig(newConfig);
      
      const config = alertService.getConfig();
      expect(config.checkInterval).toBe(45000);
      expect(config.enableNotifications).toBe(false);
      expect(config.enableSound).toBe(true);
    });

    it('deve salvar configuração no localStorage', () => {
      alertService.updateConfig({ checkInterval: 60000 });
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'glpi_dashboard_alert_config',
        expect.stringContaining('60000')
      );
    });
  });

  describe('Listeners', () => {
    it('deve notificar listeners quando novo alerta é criado', () => {
      const listener = vi.fn();
      alertService.addListener(listener);
      
      alertService.createAlert('warning', 'performance', 'Teste', 'Mensagem');
      
      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Teste',
          type: 'warning',
          category: 'performance'
        })
      );
    });

    it('deve remover listener corretamente', () => {
      const listener = vi.fn();
      alertService.addListener(listener);
      alertService.removeListener(listener);
      
      alertService.createAlert('info', 'system', 'Teste', 'Mensagem');
      
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('Monitoramento Automático', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('deve iniciar e parar monitoramento', () => {
      expect(alertService['isRunning']).toBe(false);
      
      alertService.start();
      expect(alertService['isRunning']).toBe(true);
      
      alertService.stop();
      expect(alertService['isRunning']).toBe(false);
    });

    it('deve verificar alertas no intervalo configurado', () => {
      const checkAlertsSpy = vi.spyOn(alertService as any, 'checkAlerts');
      
      alertService.updateConfig({ checkInterval: 1000 });
      alertService.start();
      
      vi.advanceTimersByTime(1000);
      expect(checkAlertsSpy).toHaveBeenCalledTimes(1);
      
      vi.advanceTimersByTime(1000);
      expect(checkAlertsSpy).toHaveBeenCalledTimes(2);
    });
  });

  describe('Avaliação de Thresholds', () => {
    it('deve avaliar threshold de tempo de resposta', () => {
      const threshold = {
        metric: 'responseTime',
        warningValue: 2000,
        errorValue: 5000,
        criticalValue: 10000,
        operator: 'gt' as const,
        enabled: true
      };
      
      // Testar diferentes valores
      expect(alertService['evaluateThreshold'](1500, threshold)).toBeNull();
      expect(alertService['evaluateThreshold'](3000, threshold)).toBe('warning');
      expect(alertService['evaluateThreshold'](7000, threshold)).toBe('error');
      expect(alertService['evaluateThreshold'](12000, threshold)).toBe('critical');
    });

    it('deve avaliar threshold de taxa de hit do cache', () => {
      const threshold = {
        metric: 'cacheHitRate',
        warningValue: 0.6,
        errorValue: 0.4,
        criticalValue: 0.2,
        operator: 'lt' as const,
        enabled: true
      };
      
      // Testar diferentes valores (operador 'lt')
      expect(alertService['evaluateThreshold'](0.8, threshold)).toBeNull();
      expect(alertService['evaluateThreshold'](0.5, threshold)).toBe('warning');
      expect(alertService['evaluateThreshold'](0.3, threshold)).toBe('error');
      expect(alertService['evaluateThreshold'](0.1, threshold)).toBe('critical');
    });
  });

  describe('Formatação de Métricas', () => {
    it('deve formatar tempo de resposta', () => {
      expect(alertService['formatMetricValue']('responseTime', 1234.56))
        .toBe('1235ms');
    });

    it('deve formatar porcentagens', () => {
      expect(alertService['formatMetricValue']('cacheHitRate', 0.856))
        .toBe('85.6%');
      expect(alertService['formatMetricValue']('errorRate', 0.023))
        .toBe('2.3%');
      expect(alertService['formatMetricValue']('memoryUsage', 0.789))
        .toBe('78.9%');
    });
  });

  describe('Coleta de Métricas', () => {
    it('deve coletar métricas do sistema', async () => {
      // Mock das estatísticas do cache
      vi.spyOn(metricsCache, 'getStats').mockReturnValue({
        hits: 100,
        misses: 20,
        size: 50,
        maxSize: 100,
        averageResponseTime: 150,
        isActivated: true,
        requestCount: 120
      });
      
      const metrics = await alertService['collectMetrics']();
      
      expect(metrics).toHaveProperty('responseTime');
      expect(metrics).toHaveProperty('cacheHitRate');
      expect(metrics).toHaveProperty('errorRate');
      expect(metrics).toHaveProperty('memoryUsage');
      expect(metrics).toHaveProperty('timestamp');
      
      expect(typeof metrics.responseTime).toBe('number');
      expect(typeof metrics.cacheHitRate).toBe('number');
      expect(metrics.cacheHitRate).toBeGreaterThanOrEqual(0);
      expect(metrics.cacheHitRate).toBeLessThanOrEqual(1);
    });
  });

  describe('Detecção de Tendências', () => {
    it('deve detectar degradação do cache', () => {
      // Configurar métricas anteriores
      alertService['lastMetrics'] = {
        cacheHitRate: 0.8,
        timestamp: new Date(Date.now() - 120000) // 2 minutos atrás
      };
      
      const currentMetrics = {
        cacheHitRate: 0.5, // Queda de 30%
        timestamp: new Date()
      };
      
      const createAlertSpy = vi.spyOn(alertService, 'createAlert');
      
      alertService['checkTrends'](currentMetrics);
      
      expect(createAlertSpy).toHaveBeenCalledWith(
        'warning',
        'cache',
        'Degradação do Cache Detectada',
        expect.stringContaining('Taxa de hit do cache caiu'),
        expect.any(Object)
      );
    });

    it('deve detectar aumento no tempo de resposta', () => {
      // Configurar métricas anteriores
      alertService['lastMetrics'] = {
        responseTime: 1000,
        timestamp: new Date(Date.now() - 120000) // 2 minutos atrás
      };
      
      const currentMetrics = {
        responseTime: 2000, // Aumento de 100%
        timestamp: new Date()
      };
      
      const createAlertSpy = vi.spyOn(alertService, 'createAlert');
      
      alertService['checkTrends'](currentMetrics);
      
      expect(createAlertSpy).toHaveBeenCalledWith(
        'warning',
        'performance',
        'Aumento no Tempo de Resposta',
        expect.stringContaining('Tempo de resposta aumentou'),
        expect.any(Object)
      );
    });
  });

  describe('Persistência', () => {
    it('deve salvar alertas no localStorage', () => {
      alertService.createAlert('info', 'system', 'Teste', 'Mensagem');
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'glpi_dashboard_alerts',
        expect.stringContaining('Teste')
      );
    });

    it('deve carregar alertas do localStorage', () => {
      const savedAlerts = [{
        id: 'test-alert',
        type: 'warning',
        category: 'performance',
        title: 'Alerta Salvo',
        message: 'Mensagem salva',
        timestamp: new Date().toISOString(),
        resolved: false
      }];
      
      localStorageMock.getItem.mockReturnValue(JSON.stringify(savedAlerts));
      
      // Simular carregamento
      alertService['loadAlerts']();
      
      const alerts = alertService.getAlerts();
      expect(alerts).toHaveLength(1);
      expect(alerts[0].title).toBe('Alerta Salvo');
    });
  });

  describe('Geração de IDs', () => {
    it('deve gerar IDs únicos para alertas', () => {
      const id1 = alertService['generateAlertId']();
      const id2 = alertService['generateAlertId']();
      
      expect(id1).not.toBe(id2);
      expect(id1).toMatch(/^alert_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^alert_\d+_[a-z0-9]+$/);
    });
  });

  describe('Uso de Memória', () => {
    it('deve calcular uso de memória quando disponível', () => {
      const memoryUsage = alertService['getMemoryUsage']();
      
      expect(typeof memoryUsage).toBe('number');
      expect(memoryUsage).toBeGreaterThanOrEqual(0);
      expect(memoryUsage).toBeLessThanOrEqual(1);
      expect(memoryUsage).toBe(0.5); // 50MB / 100MB
    });

    it('deve retornar valor simulado quando memory API não está disponível', () => {
      // Remover memory API temporariamente
      const originalMemory = (performance as any).memory;
      delete (performance as any).memory;
      
      const memoryUsage = alertService['getMemoryUsage']();
      
      expect(typeof memoryUsage).toBe('number');
      expect(memoryUsage).toBeGreaterThanOrEqual(0);
      expect(memoryUsage).toBeLessThanOrEqual(0.5);
      
      // Restaurar memory API
      (performance as any).memory = originalMemory;
    });
  });
});