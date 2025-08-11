# 🤝 Guia de Contribuição - GLPI Dashboard

## 📋 Índice
- [Configuração do Ambiente](#-configuração-do-ambiente)
- [Padrões de Código](#-padrões-de-código)
- [Fluxo de Desenvolvimento](#-fluxo-de-desenvolvimento)
- [Testes](#-testes)
- [Documentação](#-documentação)
- [Code Review](#-code-review)

## 🛠️ Configuração do Ambiente

### Pré-requisitos
- Node.js 18+ 
- Python 3.9+
- Docker & Docker Compose
- Git
- Redis (para desenvolvimento local)

### Setup Inicial

#### 1. Clone e Configuração
```bash
git clone <repository-url>
cd glpi_dashboard
cp .env.example .env
# Editar .env com suas configurações
```

#### 2. Backend Setup
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente (Windows)
.venv\Scripts\activate
# Ativar ambiente (Linux/Mac)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar testes
pytest

# Iniciar servidor
python app.py
```

#### 3. Frontend Setup
```bash
cd frontend

# Instalar dependências
npm install

# Executar testes
npm test

# Iniciar desenvolvimento
npm run dev
```

#### 4. Docker (Opcional)
```bash
# Desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Produção
docker-compose up -d
```

## 📝 Padrões de Código

### Frontend (TypeScript/React)

#### Estrutura de Componentes
```typescript
// ✅ Bom
import React from 'react';
import { cn } from '@/lib/utils';

interface ComponentProps {
  title: string;
  isLoading?: boolean;
  onAction?: () => void;
}

export const Component: React.FC<ComponentProps> = ({ 
  title, 
  isLoading = false, 
  onAction 
}) => {
  return (
    <div className={cn('base-styles', { 'loading': isLoading })}>
      <h2>{title}</h2>
      {onAction && (
        <button onClick={onAction}>Action</button>
      )}
    </div>
  );
};
```

#### Hooks Customizados
```typescript
// ✅ Bom
import { useState, useEffect, useCallback } from 'react';
import { debounce } from '@/utils/debounce';

export const useSearch = (initialQuery = '') => {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const debouncedSearch = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      try {
        const data = await searchAPI(searchQuery);
        setResults(data);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    []
  );

  useEffect(() => {
    debouncedSearch(query);
  }, [query, debouncedSearch]);

  return { query, setQuery, results, isLoading };
};
```

#### Gerenciamento de Estado
```typescript
// ✅ Bom - Context para estado global
import React, { createContext, useContext, useReducer } from 'react';

interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

type AppAction = 
  | { type: 'SET_USER'; payload: User }
  | { type: 'TOGGLE_THEME' }
  | { type: 'ADD_NOTIFICATION'; payload: Notification };

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};
```

### Backend (Python/Flask)

#### Estrutura de Serviços
```python
# ✅ Bom
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TechnicianMetrics:
    technician_id: int
    name: str
    total_tickets: int
    resolved_tickets: int
    avg_resolution_time: float
    performance_score: float

class TechnicianService:
    def __init__(self, db_connection, cache_service):
        self.db = db_connection
        self.cache = cache_service
    
    async def get_technician_ranking(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 10
    ) -> List[TechnicianMetrics]:
        """Obtém ranking de técnicos por performance.
        
        Args:
            start_date: Data inicial do período
            end_date: Data final do período
            limit: Número máximo de resultados
            
        Returns:
            Lista de métricas de técnicos ordenada por performance
            
        Raises:
            ValueError: Se as datas forem inválidas
            DatabaseError: Se houver erro na consulta
        """
        if start_date >= end_date:
            raise ValueError("Data inicial deve ser anterior à data final")
        
        cache_key = f"technician_ranking:{start_date}:{end_date}:{limit}"
        
        # Tentar cache primeiro
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for {cache_key}")
            return cached_result
        
        try:
            # Consulta ao banco
            query = """
            SELECT 
                t.id,
                t.name,
                COUNT(tk.id) as total_tickets,
                COUNT(CASE WHEN tk.status = 'resolved' THEN 1 END) as resolved_tickets,
                AVG(TIMESTAMPDIFF(HOUR, tk.created_at, tk.resolved_at)) as avg_resolution_time
            FROM technicians t
            LEFT JOIN tickets tk ON t.id = tk.technician_id
            WHERE tk.created_at BETWEEN %s AND %s
            GROUP BY t.id, t.name
            ORDER BY resolved_tickets DESC, avg_resolution_time ASC
            LIMIT %s
            """
            
            results = await self.db.fetch_all(query, (start_date, end_date, limit))
            
            metrics = [
                TechnicianMetrics(
                    technician_id=row['id'],
                    name=row['name'],
                    total_tickets=row['total_tickets'],
                    resolved_tickets=row['resolved_tickets'],
                    avg_resolution_time=row['avg_resolution_time'] or 0,
                    performance_score=self._calculate_performance_score(row)
                )
                for row in results
            ]
            
            # Cache por 15 minutos
            await self.cache.set(cache_key, metrics, ttl=900)
            
            logger.info(f"Retrieved {len(metrics)} technician metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error fetching technician ranking: {e}")
            raise
    
    def _calculate_performance_score(self, row: Dict[str, Any]) -> float:
        """Calcula score de performance baseado em métricas."""
        if row['total_tickets'] == 0:
            return 0.0
        
        resolution_rate = row['resolved_tickets'] / row['total_tickets']
        time_factor = max(0, 1 - (row['avg_resolution_time'] or 0) / 100)
        
        return (resolution_rate * 0.7) + (time_factor * 0.3)
```

#### Tratamento de Erros
```python
# ✅ Bom
from flask import jsonify
from functools import wraps
import traceback

def handle_api_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return jsonify({
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        except DatabaseError as e:
            logger.error(f"Database error in {f.__name__}: {e}")
            return jsonify({
                'error': 'Database Error',
                'message': 'Internal server error'
            }), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
    return decorated_function
```

## 🔄 Fluxo de Desenvolvimento

### 1. Criação de Branch
```bash
# Nomenclatura de branches
feat/nome-da-funcionalidade     # Nova funcionalidade
fix/nome-do-bug                 # Correção de bug
refactor/nome-da-refatoracao    # Refatoração
test/nome-do-teste              # Adição de testes
docs/nome-da-documentacao       # Documentação

# Exemplo
git checkout -b feat/technician-performance-chart
```

### 2. Desenvolvimento

#### Checklist de Desenvolvimento
- [ ] Código segue padrões estabelecidos
- [ ] Testes unitários implementados
- [ ] Documentação atualizada
- [ ] Performance considerada
- [ ] Segurança validada
- [ ] Acessibilidade verificada

#### Commits
```bash
# Usar Conventional Commits
feat: adiciona gráfico de performance de técnicos
fix: corrige cálculo de tempo médio de resolução
refactor: reorganiza estrutura de componentes
test: adiciona testes para TechnicianService
docs: atualiza documentação da API
style: aplica formatação ESLint
perf: otimiza consulta de ranking de técnicos
ci: adiciona workflow de deploy automático
```

### 3. Testes Obrigatórios

#### Frontend
```bash
# Executar todos os testes
npm test

# Testes com coverage
npm run test:coverage

# Testes específicos
npm test -- MetricsGrid

# Testes em modo watch
npm test -- --watch
```

#### Backend
```bash
# Executar todos os testes
pytest

# Testes com coverage
pytest --cov=backend --cov-report=html

# Testes específicos
pytest tests/test_technician_service.py

# Testes com verbose
pytest -v
```

### 4. Build e Validação
```bash
# Frontend build
npm run build
npm run preview

# Linting
npm run lint
npm run lint:fix

# Type checking
npm run type-check

# Backend validation
flake8 backend/
black backend/ --check
mypy backend/
```

## 🧪 Testes

### Estratégia de Testes

#### Pirâmide de Testes
```
    /\     E2E Tests (10%)
   /  \    
  /____\   Integration Tests (20%)
 /______\  
/________\ Unit Tests (70%)
```

#### Frontend - Testes Unitários
```typescript
// ✅ Exemplo de teste de componente
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { MetricsGrid } from '../MetricsGrid';

describe('MetricsGrid', () => {
  const mockMetrics = {
    totalTickets: 100,
    resolvedTickets: 80,
    avgResolutionTime: 24.5,
    trends: {
      totalTickets: 5.2,
      resolvedTickets: 3.1,
      avgResolutionTime: -2.3
    }
  };

  it('should render metrics correctly', () => {
    render(<MetricsGrid metrics={mockMetrics} />);
    
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('80')).toBeInTheDocument();
    expect(screen.getByText('24.5h')).toBeInTheDocument();
  });

  it('should show loading skeleton when metrics is null', () => {
    render(<MetricsGrid metrics={null} />);
    
    expect(screen.getAllByTestId('skeleton')).toHaveLength(3);
  });

  it('should call onFilterByStatus when status card is clicked', async () => {
    const mockOnFilter = vi.fn();
    render(
      <MetricsGrid 
        metrics={mockMetrics} 
        onFilterByStatus={mockOnFilter}
      />
    );
    
    fireEvent.click(screen.getByTestId('resolved-tickets-card'));
    
    await waitFor(() => {
      expect(mockOnFilter).toHaveBeenCalledWith('resolved');
    });
  });
});
```

#### Backend - Testes Unitários
```python
# ✅ Exemplo de teste de serviço
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from backend.services.technician_service import TechnicianService

@pytest.fixture
def technician_service():
    db_mock = AsyncMock()
    cache_mock = AsyncMock()
    return TechnicianService(db_mock, cache_mock)

@pytest.mark.asyncio
async def test_get_technician_ranking_success(technician_service):
    # Arrange
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    technician_service.cache.get.return_value = None
    technician_service.db.fetch_all.return_value = [
        {
            'id': 1,
            'name': 'João Silva',
            'total_tickets': 50,
            'resolved_tickets': 45,
            'avg_resolution_time': 12.5
        }
    ]
    
    # Act
    result = await technician_service.get_technician_ranking(
        start_date, end_date, limit=10
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].name == 'João Silva'
    assert result[0].total_tickets == 50
    assert result[0].resolved_tickets == 45
    
    technician_service.cache.set.assert_called_once()

@pytest.mark.asyncio
async def test_get_technician_ranking_invalid_dates(technician_service):
    # Arrange
    start_date = datetime(2024, 1, 31)
    end_date = datetime(2024, 1, 1)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Data inicial deve ser anterior"):
        await technician_service.get_technician_ranking(start_date, end_date)
```

### Cobertura de Testes

#### Metas de Cobertura
- **Crítico**: 95% (serviços core, APIs principais)
- **Importante**: 85% (componentes principais, utils)
- **Geral**: 80% (todo o projeto)

#### Relatórios
```bash
# Frontend coverage
npm run test:coverage
open coverage/index.html

# Backend coverage
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

## 📚 Documentação

### Documentação de Código

#### TypeScript/JSDoc
```typescript
/**
 * Hook para gerenciar dados do dashboard com cache e filtros
 * 
 * @param initialFilters - Filtros iniciais para aplicar
 * @returns Objeto com dados, loading state e funções de controle
 * 
 * @example
 * ```tsx
 * const { data, isLoading, applyFilters } = useDashboard({
 *   startDate: new Date('2024-01-01'),
 *   endDate: new Date('2024-01-31')
 * });
 * ```
 */
export const useDashboard = (initialFilters: DashboardFilters) => {
  // implementação
};
```

#### Python/Docstrings
```python
def calculate_performance_metrics(
    tickets: List[Ticket], 
    period_days: int = 30
) -> PerformanceMetrics:
    """Calcula métricas de performance para um conjunto de tickets.
    
    Args:
        tickets: Lista de tickets para análise
        period_days: Período em dias para cálculo de tendências
        
    Returns:
        PerformanceMetrics: Objeto com métricas calculadas
        
    Raises:
        ValueError: Se a lista de tickets estiver vazia
        
    Example:
        >>> tickets = get_tickets_from_db()
        >>> metrics = calculate_performance_metrics(tickets, 30)
        >>> print(f"Resolução média: {metrics.avg_resolution_time}h")
    """
```

### README de Componentes
Cada componente complexo deve ter um README.md:

```markdown
# MetricsGrid Component

## Descrição
Componente responsável por exibir métricas principais do dashboard em formato de grid.

## Props
| Prop | Tipo | Obrigatório | Descrição |
|------|------|-------------|----------|
| metrics | MetricsData \| null | Sim | Dados das métricas |
| onFilterByStatus | (status: string) => void | Não | Callback para filtrar por status |

## Exemplo de Uso
```tsx
<MetricsGrid 
  metrics={dashboardData.metrics}
  onFilterByStatus={(status) => setStatusFilter(status)}
/>
```

## Testes
- ✅ Renderização com dados
- ✅ Estado de loading
- ✅ Interações de filtro
- ✅ Acessibilidade
```

## 👀 Code Review

### Checklist do Reviewer

#### Funcionalidade
- [ ] Código atende aos requisitos
- [ ] Funcionalidade funciona conforme esperado
- [ ] Edge cases são tratados
- [ ] Performance é adequada

#### Qualidade do Código
- [ ] Código é legível e bem estruturado
- [ ] Nomes de variáveis/funções são descritivos
- [ ] Não há código duplicado
- [ ] Padrões do projeto são seguidos

#### Testes
- [ ] Testes cobrem funcionalidade principal
- [ ] Testes cobrem edge cases
- [ ] Mocks são apropriados
- [ ] Cobertura atende aos padrões

#### Segurança
- [ ] Inputs são validados
- [ ] Não há vazamento de dados sensíveis
- [ ] Autenticação/autorização adequada
- [ ] Logs não expõem informações sensíveis

#### Documentação
- [ ] Código está documentado
- [ ] README atualizado se necessário
- [ ] Changelog atualizado
- [ ] API docs atualizadas

### Processo de Review

1. **Auto-review**: Autor revisa próprio código antes do PR
2. **Automated checks**: CI executa testes e linting
3. **Peer review**: Pelo menos 1 aprovação necessária
4. **Final check**: Verificação antes do merge

### Feedback Construtivo

#### ✅ Bom Feedback
```
"Considere usar useMemo aqui para otimizar a performance, 
já que este cálculo é executado a cada render:

const expensiveValue = useMemo(() => 
  calculateComplexValue(data), [data]
);"
```

#### ❌ Feedback Ruim
```
"Este código está ruim."
```

---

## 🚀 Deploy e Release

### Ambientes
- **Development**: Branch `develop`
- **Staging**: Branch `staging` 
- **Production**: Branch `main`

### Processo de Release
1. Merge para `develop`
2. Testes em staging
3. Tag de versão
4. Deploy para produção
5. Monitoramento pós-deploy

---

**Dúvidas?** Abra uma issue ou entre em contato com a equipe!

**Última atualização**: 2024-12-29