# Guia de Desenvolvimento - Sistema de Performance

## Introdução

Este guia fornece instruções detalhadas para desenvolvedores que desejam implementar, estender ou manter o sistema de monitoramento de performance do GLPI Dashboard.

## Estrutura do Código

### Frontend

```
src/
├── hooks/
│   ├── usePerformanceMonitoring.ts    # Hook principal
│   ├── useFilterPerformance.ts        # Performance de filtros
│   ├── useApiPerformance.ts           # Performance de API
│   ├── usePerformanceReports.ts       # Relatórios
│   ├── usePerformanceDebug.ts         # Debug tools
│   └── useRenderTracker.ts            # Tracking de renders
├── components/
│   ├── PerformanceDashboard.tsx       # Dashboard principal
│   └── PerformanceMonitor.tsx         # Monitor em background
├── utils/
│   ├── performanceMonitor.ts          # Classe de monitoramento
│   └── performanceTestSuite.ts        # Suite de testes
└── __tests__/
    ├── unit/hooks/                    # Testes unitários
    └── integration/                   # Testes de integração
```

### Backend

```
backend/
├── routes/
│   └── performance.py                 # Endpoints de performance
├── utils/
│   ├── performance.py                 # Monitor backend
│   └── prometheus_metrics.py          # Métricas Prometheus
└── tests/
    └── test_performance.py            # Testes backend
```

## Implementação de Novos Hooks

### Template Base para Hook de Performance

```typescript
import { useState, useEffect, useCallback } from 'react';
import { performanceMonitor } from '../utils/performanceMonitor';

interface MyPerformanceMetrics {
  // Defina suas métricas aqui
  customMetric: number;
  timestamp: number;
}

interface UseMyPerformanceReturn {
  metrics: MyPerformanceMetrics | null;
  isLoading: boolean;
  error: string | null;
  measureCustomOperation: (operation: () => Promise<any>) => Promise<any>;
}

export const useMyPerformance = (): UseMyPerformanceReturn => {
  const [metrics, setMetrics] = useState<MyPerformanceMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const measureCustomOperation = useCallback(async (operation: () => Promise<any>) => {
    const startTime = performance.now();
    
    try {
      const result = await operation();
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      setMetrics(prev => ({
        ...prev,
        customMetric: duration,
        timestamp: Date.now()
      }));
      
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  useEffect(() => {
    // Inicialização do hook
    setIsLoading(true);
    
    // Cleanup
    return () => {
      // Limpeza necessária
    };
  }, []);

  return {
    metrics,
    isLoading,
    error,
    measureCustomOperation
  };
};
```

### Padrões de Implementação

1. **Nomenclatura**: Use prefixo `usePerformance` ou sufixo `Performance`
2. **Tipos**: Defina interfaces TypeScript para todas as métricas
3. **Error Handling**: Sempre implemente tratamento de erro
4. **Cleanup**: Use useEffect cleanup para evitar memory leaks
5. **Memoização**: Use useCallback para funções que podem ser passadas como props

## Adicionando Novas Métricas

### 1. Definir Interface da Métrica

```typescript
interface CustomMetric {
  name: string;
  value: number;
  unit: 'ms' | 'bytes' | 'count' | 'percentage';
  timestamp: number;
  category: 'frontend' | 'backend' | 'network';
  tags?: Record<string, string>;
}
```

### 2. Implementar Coleta

```typescript
class CustomPerformanceCollector {
  private metrics: CustomMetric[] = [];
  
  collectMetric(name: string, value: number, unit: CustomMetric['unit']) {
    const metric: CustomMetric = {
      name,
      value,
      unit,
      timestamp: Date.now(),
      category: 'frontend',
      tags: {
        component: 'unknown',
        user: 'anonymous'
      }
    };
    
    this.metrics.push(metric);
    this.sendToBackend(metric);
  }
  
  private async sendToBackend(metric: CustomMetric) {
    try {
      await fetch('/api/performance/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('Failed to send metric to backend:', error);
    }
  }
}
```

### 3. Integrar com Hook Existente

```typescript
export const usePerformanceMonitoring = () => {
  const collector = useMemo(() => new CustomPerformanceCollector(), []);
  
  const trackCustomMetric = useCallback((name: string, value: number, unit: CustomMetric['unit']) => {
    collector.collectMetric(name, value, unit);
  }, [collector]);
  
  return {
    // ... outras funcionalidades
    trackCustomMetric
  };
};
```

## Implementação de Novos Endpoints Backend

### Template para Endpoint de Performance

```python
from flask import Blueprint, request, jsonify
from utils.performance import PerformanceMonitor
from utils.auth import require_auth
import logging

performance_bp = Blueprint('performance', __name__)
logger = logging.getLogger(__name__)

@performance_bp.route('/api/performance/custom-metric', methods=['POST'])
@require_auth
def collect_custom_metric():
    """Endpoint para coletar métricas customizadas"""
    try:
        data = request.get_json()
        
        # Validação
        required_fields = ['name', 'value', 'unit', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # Processamento
        monitor = PerformanceMonitor()
        result = monitor.collect_metric(
            name=data['name'],
            value=data['value'],
            unit=data['unit'],
            category=data['category'],
            tags=data.get('tags', {})
        )
        
        logger.info(f"Collected custom metric: {data['name']} = {data['value']} {data['unit']}")
        
        return jsonify({
            'success': True,
            'metric_id': result['id'],
            'timestamp': result['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error collecting custom metric: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@performance_bp.route('/api/performance/custom-metric/<metric_name>', methods=['GET'])
@require_auth
def get_custom_metric(metric_name):
    """Endpoint para buscar métricas específicas"""
    try:
        # Parâmetros de query
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 100))
        
        monitor = PerformanceMonitor()
        metrics = monitor.get_metrics(
            name=metric_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return jsonify({
            'metrics': metrics,
            'count': len(metrics),
            'metric_name': metric_name
        })
        
    except Exception as e:
        logger.error(f"Error fetching custom metric {metric_name}: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
```

## Testes

### Template para Teste de Hook

```typescript
import { renderHook, act } from '@testing-library/react';
import { useMyPerformance } from '../useMyPerformance';

// Mock do performance.now
Object.defineProperty(window, 'performance', {
  value: {
    now: jest.fn()
  }
});

describe('useMyPerformance', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (performance.now as jest.Mock).mockReturnValue(1000);
  });

  it('deve inicializar com estado padrão', () => {
    const { result } = renderHook(() => useMyPerformance());
    
    expect(result.current.metrics).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(typeof result.current.measureCustomOperation).toBe('function');
  });

  it('deve medir operação customizada com sucesso', async () => {
    const { result } = renderHook(() => useMyPerformance());
    
    const mockOperation = jest.fn().mockResolvedValue('success');
    (performance.now as jest.Mock)
      .mockReturnValueOnce(1000) // start
      .mockReturnValueOnce(1500); // end
    
    let operationResult;
    await act(async () => {
      operationResult = await result.current.measureCustomOperation(mockOperation);
    });
    
    expect(operationResult).toBe('success');
    expect(result.current.metrics?.customMetric).toBe(500);
    expect(mockOperation).toHaveBeenCalledTimes(1);
  });

  it('deve tratar erros na operação', async () => {
    const { result } = renderHook(() => useMyPerformance());
    
    const mockOperation = jest.fn().mockRejectedValue(new Error('Test error'));
    
    await act(async () => {
      try {
        await result.current.measureCustomOperation(mockOperation);
      } catch (error) {
        expect(error.message).toBe('Test error');
      }
    });
    
    expect(result.current.error).toBe('Test error');
  });
});
```

### Template para Teste de Endpoint

```python
import pytest
import json
from app import create_app
from utils.performance import PerformanceMonitor

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    return {'Authorization': 'Bearer test-token'}

def test_collect_custom_metric_success(client, auth_headers):
    """Teste de coleta de métrica customizada com sucesso"""
    data = {
        'name': 'test_metric',
        'value': 123.45,
        'unit': 'ms',
        'category': 'frontend',
        'tags': {'component': 'test'}
    }
    
    response = client.post(
        '/api/performance/custom-metric',
        data=json.dumps(data),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'metric_id' in result
    assert 'timestamp' in result

def test_collect_custom_metric_missing_fields(client, auth_headers):
    """Teste de validação de campos obrigatórios"""
    data = {
        'name': 'test_metric'
        # Campos obrigatórios faltando
    }
    
    response = client.post(
        '/api/performance/custom-metric',
        data=json.dumps(data),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result
    assert 'required' in result

def test_get_custom_metric_success(client, auth_headers):
    """Teste de busca de métrica específica"""
    response = client.get(
        '/api/performance/custom-metric/test_metric?limit=50',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'metrics' in result
    assert 'count' in result
    assert result['metric_name'] == 'test_metric'
```

## Debugging e Troubleshooting

### Ferramentas de Debug

```typescript
// Debug hook para desenvolvimento
export const usePerformanceDebug = () => {
  const [debugInfo, setDebugInfo] = useState<any>(null);
  
  const logPerformance = useCallback((label: string, data: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.group(`🔍 Performance Debug: ${label}`);
      console.log('Data:', data);
      console.log('Timestamp:', new Date().toISOString());
      console.log('Memory:', (performance as any).memory);
      console.groupEnd();
      
      setDebugInfo(prev => ({
        ...prev,
        [label]: {
          data,
          timestamp: Date.now(),
          memory: (performance as any).memory
        }
      }));
    }
  }, []);
  
  return { debugInfo, logPerformance };
};
```

### Logs Estruturados

```python
import logging
import json
from datetime import datetime

class PerformanceLogger:
    def __init__(self):
        self.logger = logging.getLogger('performance')
        
    def log_metric(self, metric_name, value, unit, category, tags=None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'category': category,
            'tags': tags or {},
            'level': 'INFO'
        }
        
        self.logger.info(json.dumps(log_data))
        
    def log_error(self, error_message, context=None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_message': error_message,
            'context': context or {},
            'level': 'ERROR'
        }
        
        self.logger.error(json.dumps(log_data))
```

## Otimizações

### Batching de Métricas

```typescript
class MetricsBatcher {
  private batch: CustomMetric[] = [];
  private batchSize = 10;
  private flushInterval = 5000; // 5 segundos
  private timer: NodeJS.Timeout | null = null;
  
  addMetric(metric: CustomMetric) {
    this.batch.push(metric);
    
    if (this.batch.length >= this.batchSize) {
      this.flush();
    } else if (!this.timer) {
      this.timer = setTimeout(() => this.flush(), this.flushInterval);
    }
  }
  
  private async flush() {
    if (this.batch.length === 0) return;
    
    const metricsToSend = [...this.batch];
    this.batch = [];
    
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    
    try {
      await fetch('/api/performance/metrics/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metrics: metricsToSend })
      });
    } catch (error) {
      console.warn('Failed to send metrics batch:', error);
      // Re-adicionar métricas para retry
      this.batch.unshift(...metricsToSend);
    }
  }
}
```

### Cache Inteligente

```typescript
class PerformanceCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  
  set(key: string, data: any, ttl: number = 300000) { // 5 minutos padrão
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get(key: string): any | null {
    const entry = this.cache.get(key);
    
    if (!entry) return null;
    
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }
  
  // TTL dinâmico baseado na frequência de acesso
  adaptiveTTL(key: string, baseTime: number = 300000): number {
    const accessCount = this.getAccessCount(key);
    
    if (accessCount > 10) return baseTime * 2; // Cache mais tempo para dados frequentes
    if (accessCount < 3) return baseTime / 2;  // Cache menos tempo para dados raros
    
    return baseTime;
  }
  
  private getAccessCount(key: string): number {
    // Implementar contador de acesso
    return 0;
  }
}
```

## Melhores Práticas

### 1. Performance
- Use `useCallback` e `useMemo` apropriadamente
- Evite re-renderizações desnecessárias
- Implemente lazy loading para componentes pesados
- Use Web Workers para cálculos intensivos

### 2. Monitoramento
- Colete apenas métricas necessárias
- Implemente sampling para reduzir overhead
- Use batching para reduzir requests
- Configure alertas para métricas críticas

### 3. Testes
- Teste todos os cenários de erro
- Use mocks apropriados para APIs externas
- Implemente testes de performance automatizados
- Mantenha cobertura de testes > 80%

### 4. Documentação
- Documente todas as métricas coletadas
- Mantenha exemplos de uso atualizados
- Documente configurações e limitações
- Inclua troubleshooting guides

## Contribuindo

Para contribuir com o sistema de performance:

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** seguindo os padrões estabelecidos
4. **Adicione** testes apropriados
5. **Documente** as mudanças
6. **Submeta** um Pull Request

### Checklist para Pull Requests

- [ ] Código segue padrões estabelecidos
- [ ] Testes unitários adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Performance não degradada
- [ ] Compatibilidade mantida
- [ ] Logs apropriados adicionados

## Recursos Adicionais

- [Web Performance API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Performance)
- [React Performance Best Practices](https://react.dev/learn/render-and-commit)
- [Prometheus Metrics Guidelines](https://prometheus.io/docs/practices/naming/)
- [Testing Library Best Practices](https://testing-library.com/docs/guiding-principles/)