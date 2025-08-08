# Guia de Testes - GLPI Dashboard

## Visão Geral

Este guia estabelece as práticas de teste para o projeto GLPI Dashboard, incluindo estratégias para prevenir regressões, garantir qualidade e manter a confiabilidade do sistema.

## Pirâmide de Testes

```
    /\     E2E Tests (Poucos)
   /  \    
  /____\   Integration Tests (Alguns)
 /______\  
/________\ Unit Tests (Muitos)
```

### 1. Testes Unitários (70%)
- **Objetivo**: Testar componentes isolados
- **Escopo**: Funções, classes, hooks, componentes
- **Velocidade**: Muito rápida
- **Cobertura**: 80%+ para código crítico

### 2. Testes de Integração (20%)
- **Objetivo**: Testar interação entre componentes
- **Escopo**: APIs, fluxos de dados, serviços
- **Velocidade**: Moderada
- **Cobertura**: Fluxos principais

### 3. Testes End-to-End (10%)
- **Objetivo**: Testar fluxos completos do usuário
- **Escopo**: Jornadas críticas do usuário
- **Velocidade**: Lenta
- **Cobertura**: Cenários de negócio principais

## Estrutura de Testes

### Backend (Python)

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Configurações pytest
│   ├── unit/                    # Testes unitários
│   │   ├── test_glpi_service.py
│   │   ├── test_validators.py
│   │   └── test_utils.py
│   ├── integration/             # Testes de integração
│   │   ├── test_api_routes.py
│   │   ├── test_database.py
│   │   └── test_external_apis.py
│   ├── e2e/                     # Testes end-to-end
│   │   └── test_dashboard_flow.py
│   └── fixtures/                # Dados de teste
│       ├── sample_data.json
│       └── mock_responses.py
```

### Frontend (TypeScript/React)

```
frontend/src/
├── components/
│   └── __tests__/
├── hooks/
│   └── __tests__/
├── services/
│   └── __tests__/
├── utils/
│   └── __tests__/
├── setupTests.ts
└── test-utils.tsx               # Utilitários de teste
```

## Convenções de Nomenclatura

### Arquivos de Teste
- **Backend**: `test_*.py` ou `*_test.py`
- **Frontend**: `*.test.ts`, `*.test.tsx`, `*.spec.ts`

### Funções de Teste
- **Formato**: `test_should_[ação]_when_[condição]`
- **Exemplos**:
  - `test_should_return_metrics_when_valid_dates_provided`
  - `test_should_throw_error_when_invalid_date_format`
  - `test_should_cache_results_when_same_parameters_used`

### Grupos de Teste
- **Classes**: `TestNomeDoComponente`
- **Describe blocks**: `describe('NomeDoComponente', () => {})`

## Padrões de Teste

### 1. Arrange-Act-Assert (AAA)

```python
def test_should_calculate_metrics_when_tickets_provided():
    # Arrange
    tickets = [
        {'id': 1, 'status': 2, 'date': '2024-01-01'},
        {'id': 2, 'status': 5, 'date': '2024-01-02'}
    ]
    service = GLPIService()
    
    # Act
    result = service._calculate_metrics(tickets)
    
    # Assert
    assert result['total_tickets'] == 2
    assert result['open_tickets'] == 1
    assert result['closed_tickets'] == 1
```

### 2. Given-When-Then (BDD)

```typescript
describe('useDashboard Hook', () => {
  it('should load data successfully when valid dates provided', async () => {
    // Given
    const mockMetrics = { total_tickets: 100 };
    mockApiService.fetchDashboardMetrics.mockResolvedValue(mockMetrics);
    
    // When
    const { result } = renderHook(() => useDashboard());
    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });
    
    // Then
    expect(result.current.metrics).toEqual(mockMetrics);
    expect(result.current.error).toBeNull();
  });
});
```

## Estratégias de Mock

### Backend (Python)

```python
# Mock de serviços externos
@patch('services.glpi_service.requests.Session')
def test_glpi_authentication(mock_session):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'session_token': 'test_token'}
    mock_session.return_value.get.return_value = mock_response
    
    service = GLPIService()
    result = service._authenticate()
    
    assert result is True
    assert service.session_token == 'test_token'

# Mock de banco de dados
@pytest.fixture
def mock_db():
    with patch('database.get_connection') as mock_conn:
        yield mock_conn
```

### Frontend (TypeScript)

```typescript
// Mock de módulos
vi.mock('../../services/api', () => ({
  fetchDashboardMetrics: vi.fn(),
  getSystemStatus: vi.fn(),
}));

// Mock de hooks
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

// Mock de APIs
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: () => Promise.resolve({ data: mockData }),
});
```

## Testes de Regressão

### Identificação de Casos Críticos

1. **Funcionalidades Core**
   - Autenticação GLPI
   - Busca de métricas
   - Validação de filtros de data
   - Cálculo de estatísticas

2. **Integrações Externas**
   - API GLPI
   - Banco de dados
   - Cache Redis

3. **Fluxos de Usuário**
   - Login → Dashboard → Filtros → Resultados
   - Navegação entre páginas
   - Tratamento de erros

### Implementação de Testes de Regressão

```python
@pytest.mark.regression
class TestDashboardRegression:
    """Testes de regressão para funcionalidades críticas."""
    
    def test_complete_dashboard_flow(self):
        """Teste de regressão para o fluxo completo do dashboard."""
        # Simula o fluxo completo: autenticação → busca → processamento
        service = GLPIService()
        
        # Autenticação
        auth_result = service._authenticate()
        assert auth_result is True
        
        # Busca de dados
        metrics = service.get_dashboard_metrics('2024-01-01', '2024-01-31')
        
        # Validação da estrutura
        required_fields = ['total_tickets', 'open_tickets', 'closed_tickets']
        for field in required_fields:
            assert field in metrics
            assert isinstance(metrics[field], int)
    
    def test_data_consistency_regression(self):
        """Verifica consistência dos dados após mudanças."""
        # Testa se os totais batem
        metrics = get_test_metrics()
        total = metrics['open_tickets'] + metrics['closed_tickets'] + metrics['pending_tickets']
        assert total == metrics['total_tickets']
```

## Testes de Performance

### Backend

```python
import time
import pytest

@pytest.mark.performance
def test_api_response_time():
    """Testa se a API responde dentro do tempo esperado."""
    start_time = time.time()
    
    response = client.get('/api/dashboard/metrics')
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 2.0  # Máximo 2 segundos

@pytest.mark.performance
def test_memory_usage():
    """Testa uso de memória durante operações."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Executa operação que pode consumir memória
    service = GLPIService()
    service.get_dashboard_metrics('2024-01-01', '2024-12-31')
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Não deve aumentar mais que 100MB
    assert memory_increase < 100 * 1024 * 1024
```

### Frontend

```typescript
describe('Performance Tests', () => {
  it('should render dashboard within acceptable time', async () => {
    const startTime = performance.now();
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
    });
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    expect(renderTime).toBeLessThan(1000); // Máximo 1 segundo
  });
});
```

## Cobertura de Testes

### Configuração

**Backend (pytest-cov)**
```ini
[tool:pytest]
addopts = --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=80
```

**Frontend (Jest)**
```javascript
coverageThreshold: {
  global: {
    branches: 80,
    functions: 80,
    lines: 80,
    statements: 80
  }
}
```

### Métricas de Qualidade

- **Cobertura de Linhas**: ≥ 80%
- **Cobertura de Branches**: ≥ 75%
- **Cobertura de Funções**: ≥ 85%
- **Código Crítico**: ≥ 95%

## Dados de Teste

### Fixtures (Backend)

```python
# conftest.py
@pytest.fixture
def sample_tickets():
    return [
        {
            'id': 1,
            'name': 'Test Ticket 1',
            'status': 2,
            'priority': 3,
            'date': '2024-01-01 10:00:00'
        },
        {
            'id': 2,
            'name': 'Test Ticket 2',
            'status': 5,
            'priority': 4,
            'date': '2024-01-02 11:00:00'
        }
    ]

@pytest.fixture
def mock_glpi_response():
    return {
        'success': True,
        'data': {
            'total_tickets': 100,
            'open_tickets': 25,
            'closed_tickets': 75
        }
    }
```

### Test Utilities (Frontend)

```typescript
// test-utils.tsx
import { render, RenderOptions } from '@testing-library/react';
import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
```

## Integração Contínua

### Pipeline de Testes

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Unit Tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=.
      
      - name: Run Integration Tests
        run: |
          cd backend
          pytest tests/integration/ -v
      
      - name: Frontend Tests
        run: |
          cd frontend
          npm test -- --coverage
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

### Quality Gates

- ✅ Todos os testes passando
- ✅ Cobertura ≥ 80%
- ✅ Sem vulnerabilidades críticas
- ✅ Performance dentro dos limites
- ✅ Sem code smells críticos

## Debugging de Testes

### Técnicas Comuns

```python
# Debug com breakpoints
import pdb; pdb.set_trace()

# Debug com prints
print(f"Debug: {variable_value}")

# Debug com logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {data}")
```

```typescript
// Debug no frontend
console.log('Debug:', data);

// Debug com screen.debug()
import { screen } from '@testing-library/react';
screen.debug(); // Mostra o DOM atual
```

### Ferramentas de Debug

- **Backend**: pytest-pdb, pytest-xdist
- **Frontend**: React DevTools, Testing Library Debug
- **IDE**: Breakpoints, Watch variables

## Melhores Práticas

### ✅ Fazer

1. **Escrever testes antes de corrigir bugs**
2. **Manter testes simples e focados**
3. **Usar nomes descritivos**
4. **Testar casos extremos**
5. **Manter dados de teste pequenos**
6. **Limpar estado entre testes**
7. **Usar mocks para dependências externas**
8. **Documentar testes complexos**

### ❌ Evitar

1. **Testes que dependem de ordem**
2. **Testes que testam implementação**
3. **Testes muito longos ou complexos**
4. **Dados de teste hardcoded**
5. **Testes que fazem chamadas reais para APIs**
6. **Ignorar testes falhando**
7. **Testes sem assertions**
8. **Duplicação de lógica de teste**

## Monitoramento e Métricas

### Métricas de Teste

- **Test Success Rate**: % de testes passando
- **Test Coverage**: % de código coberto
- **Test Execution Time**: Tempo de execução
- **Flaky Test Rate**: % de testes instáveis
- **Bug Detection Rate**: Bugs encontrados por testes

### Relatórios

- **Diário**: Status dos testes na CI/CD
- **Semanal**: Cobertura e tendências
- **Mensal**: Análise de qualidade e ROI

## Recursos e Ferramentas

### Backend
- **pytest**: Framework de testes
- **pytest-cov**: Cobertura de código
- **pytest-mock**: Mocking
- **factory-boy**: Geração de dados de teste
- **freezegun**: Mock de tempo

### Frontend
- **Vitest**: Framework de testes
- **Testing Library**: Utilitários de teste
- **MSW**: Mock Service Worker
- **Playwright**: Testes E2E

### Qualidade
- **SonarQube**: Análise de código
- **Codecov**: Cobertura de código
- **Allure**: Relatórios de teste

## Conclusão

Este guia estabelece as bases para um sistema de testes robusto que:

- **Previne regressões** através de testes abrangentes
- **Garante qualidade** com cobertura adequada
- **Facilita manutenção** com código testável
- **Acelera desenvolvimento** com feedback rápido
- **Aumenta confiança** nas mudanças de código

Lembre-se: **Testes são investimento, não custo**. Eles economizam tempo e reduzem riscos a longo prazo.