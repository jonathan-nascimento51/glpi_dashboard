# 📅 Guia Completo de Implementação de Filtros de Data para GLPI

## 🎯 Objetivo
Este guia fornece uma base sólida e reutilizável para implementar filtros de data em qualquer consulta ou métrica que envolva dados do GLPI. Serve como referência técnica para garantir consistência e eficiência em todas as implementações.

---

## 📋 Índice
1. [Fundamentos Técnicos](#fundamentos-técnicos)
2. [Estrutura de Implementação](#estrutura-de-implementação)
3. [Backend - Serviço GLPI](#backend---serviço-glpi)
4. [Backend - API Routes](#backend---api-routes)
5. [Frontend - Tipos e Interfaces](#frontend---tipos-e-interfaces)
6. [Frontend - Hooks e Estado](#frontend---hooks-e-estado)
7. [Frontend - Componentes UI](#frontend---componentes-ui)
8. [Frontend - Serviços API](#frontend---serviços-api)
9. [Padrões de Teste](#padrões-de-teste)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Fundamentos Técnicos

### Princípios Base
1. **Formato de Data Padrão**: `YYYY-MM-DD` (ISO 8601)
2. **Parâmetros de Query**: `start_date` e `end_date`
3. **Validação Dupla**: Backend e Frontend
4. **Fallback Gracioso**: Sempre retornar dados válidos
5. **Logs Detalhados**: Para debugging e monitoramento

### Fluxo de Dados
```
Frontend (DateRangeFilter) → Hook (useDashboard) → API Service → Backend Routes → GLPI Service → GLPI API
```

---

## 🏗️ Estrutura de Implementação

### 1. Backend - Serviço GLPI (`glpi_service.py`)

#### Método Base para Filtros de Data
```python
def get_dashboard_metrics_with_date_filter(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
    """
    Método base para obter métricas com filtro de data.
    
    Args:
        start_date: Data inicial no formato YYYY-MM-DD (opcional)
        end_date: Data final no formato YYYY-MM-DD (opcional)
    
    Returns:
        Dict com métricas filtradas ou None em caso de falha
    """
    # 1. Validação de autenticação
    if not self._ensure_authenticated():
        return None
    
    # 2. Descoberta de IDs de campos
    if not self.discover_field_ids():
        return None
    
    # 3. Log da operação
    self.logger.info(f"Buscando métricas com filtro de data: {start_date} até {end_date}")
    
    # 4. Obter métricas com filtro
    raw_metrics = self._get_metrics_by_level_internal(start_date, end_date)
    
    # 5. Processar e formatar dados
    result = self._format_metrics_response(raw_metrics, start_date, end_date)
    
    # 6. Log do resultado
    self.logger.info(f"Métricas formatadas com filtro de data: {result}")
    
    return result
```

#### Método Interno para Consultas com Data
```python
def _get_metrics_by_level_internal(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Dict[str, int]]:
    """
    Método interno para obter métricas por nível com filtro de data.
    
    Args:
        start_date: Data inicial (opcional)
        end_date: Data final (opcional)
    
    Returns:
        Dict com métricas por nível
    """
    metrics = {}
    
    for level_name, group_id in self.service_levels.items():
        level_metrics = {}
        
        for status_name, status_id in self.status_map.items():
            # Chama método com filtro de data
            count = self.get_ticket_count(group_id, status_id, start_date, end_date)
            level_metrics[status_name] = count if count is not None else 0
        
        metrics[level_name] = level_metrics
    
    return metrics
```

#### Método de Contagem com Filtro de Data
```python
def get_ticket_count(self, group_id: int, status_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[int]:
    """
    Conta tickets com filtros opcionais de data.
    
    Args:
        group_id: ID do grupo
        status_id: ID do status
        start_date: Data inicial (YYYY-MM-DD)
        end_date: Data final (YYYY-MM-DD)
    
    Returns:
        Número de tickets ou None em caso de erro
    """
    try:
        # Construir critérios base
        criteria = [
            {'field': self.group_field_id, 'searchtype': 'equals', 'value': group_id},
            {'field': self.status_field_id, 'searchtype': 'equals', 'value': status_id}
        ]
        
        # Adicionar filtros de data se fornecidos
        if start_date:
            criteria.append({
                'field': self.date_field_id,  # Campo de data (ex: date_creation)
                'searchtype': 'morethan',
                'value': start_date
            })
        
        if end_date:
            criteria.append({
                'field': self.date_field_id,
                'searchtype': 'lessthan',
                'value': end_date
            })
        
        # Executar busca
        search_data = {
            'criteria': criteria,
            'metacriteria': []
        }
        
        response = self.session.get(
            f"{self.base_url}/search/Ticket",
            params={'criteria': json.dumps(search_data)}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('totalcount', 0)
        
        return None
        
    except Exception as e:
        self.logger.error(f"Erro ao contar tickets: {e}")
        return None
```

### 2. Backend - API Routes (`routes.py`)

#### Endpoint com Suporte a Filtros de Data
```python
@api_bp.route('/metrics')
def get_metrics():
    """
    Endpoint para obter métricas com suporte opcional a filtros de data.
    
    Query Parameters:
        start_date (str, opcional): Data inicial no formato YYYY-MM-DD
        end_date (str, opcional): Data final no formato YYYY-MM-DD
    
    Returns:
        JSON com métricas e informações de filtro aplicado
    """
    try:
        # 1. Extrair parâmetros de data
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 2. Validar formato das datas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de start_date inválido. Use YYYY-MM-DD",
                    "data": DEFAULT_METRICS
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de end_date inválido. Use YYYY-MM-DD",
                    "data": DEFAULT_METRICS
                }), 400
        
        # 3. Validar ordem das datas
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                return jsonify({
                    "success": False,
                    "error": "Data de início não pode ser posterior à data de fim",
                    "data": DEFAULT_METRICS
                }), 400
        
        # 4. Log da operação
        logger.info(f"Buscando métricas do GLPI com filtro de data: {start_date} até {end_date}")
        
        # 5. Chamar serviço apropriado
        if start_date or end_date:
            metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(start_date, end_date)
        else:
            metrics_data = glpi_service.get_dashboard_metrics()
        
        # 6. Tratar falha do serviço
        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI, usando dados de fallback.")
            fallback_data = DEFAULT_METRICS.copy()
            fallback_data["error"] = "Não foi possível conectar ou obter dados do GLPI."
            if start_date or end_date:
                fallback_data["filtro_data"] = {
                    "data_inicio": start_date,
                    "data_fim": end_date
                }
            return jsonify({
                "success": True,
                "data": fallback_data
            })
        
        # 7. Retornar sucesso
        logger.info(f"Métricas obtidas com sucesso.")
        return jsonify({"success": True, "data": metrics_data})
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar métricas: {e}", exc_info=True)
        fallback_data = DEFAULT_METRICS.copy()
        if request.args.get('start_date') or request.args.get('end_date'):
            fallback_data["filtro_data"] = {
                "data_inicio": request.args.get('start_date'),
                "data_fim": request.args.get('end_date')
            }
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor.",
            "data": fallback_data
        }), 500
```

### 3. Frontend - Tipos e Interfaces (`types/dashboard.ts`)

#### Definições de Tipos
```typescript
// Tipo para intervalo de datas
export interface DateRange {
  startDate: string;  // Formato: YYYY-MM-DD
  endDate: string;    // Formato: YYYY-MM-DD
  label: string;      // Ex: "Últimos 7 dias"
}

// Tipo para resposta da API
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

// Tipo para métricas com filtro
export interface MetricsData {
  total: number;
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  niveis: {
    n1: LevelMetrics;
    n2: LevelMetrics;
    n3: LevelMetrics;
    n4: LevelMetrics;
  };
  tendencias: {
    novos: string;
    pendentes: string;
    progresso: string;
    resolvidos: string;
  };
  filtro_data?: {
    data_inicio: string;
    data_fim: string;
  };
}

export interface LevelMetrics {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
}
```

### 4. Frontend - Hooks e Estado (`hooks/useDashboard.ts`)

#### Hook Principal com Suporte a Filtros
```typescript
export const useDashboard = () => {
  // Estados
  const [data, setData] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<DateRange | null>(null);

  // Função para carregar dados
  const loadData = useCallback(async (range?: DateRange) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🔄 Carregando dados do dashboard...', range ? `com filtro: ${range.startDate} até ${range.endDate}` : 'sem filtro');
      
      const result = await apiService.getMetrics(range);
      setData(result);
      
      console.log('✅ Dados carregados com sucesso:', result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      console.error('❌ Erro ao carregar dados:', errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // Função para atualizar filtro de data
  const updateDateRange = useCallback((range: DateRange | null) => {
    console.log('📅 Atualizando filtro de data:', range);
    setDateRange(range);
    loadData(range);
  }, [loadData]);

  // Carregamento inicial
  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    data,
    loading,
    error,
    dateRange,
    updateDateRange,
    reload: () => loadData(dateRange)
  };
};
```

### 5. Frontend - Componentes UI (`components/DateRangeFilter.tsx`)

#### Componente de Filtro de Data
```typescript
interface DateRangeFilterProps {
  selectedRange?: DateRange | null;
  onRangeChange?: (range: DateRange | null) => void;
  // Props alternativas para compatibilidade
  value?: DateRange | null;
  onChange?: (range: DateRange | null) => void;
}

export const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  selectedRange,
  onRangeChange,
  value,
  onChange
}) => {
  // Normalizar props
  const currentRange = selectedRange || value;
  const handleRangeChange = onRangeChange || onChange || (() => {});

  // Períodos predefinidos
  const predefinedRanges = [
    {
      label: 'Últimos 7 dias',
      days: 7
    },
    {
      label: 'Últimos 30 dias',
      days: 30
    },
    {
      label: 'Últimos 90 dias',
      days: 90
    }
  ];

  // Função para selecionar período predefinido
  const handlePredefinedRangeSelect = (days: number, label: string) => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);

    const range: DateRange = {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
      label
    };

    console.log('📅 Selecionando período predefinido:', range);
    handleRangeChange(range);
  };

  // Função para aplicar período personalizado
  const handleCustomRangeApply = (startDate: string, endDate: string) => {
    if (!startDate || !endDate) {
      console.warn('⚠️ Datas personalizadas incompletas');
      return;
    }

    const range: DateRange = {
      startDate,
      endDate,
      label: `${startDate} até ${endDate}`
    };

    console.log('📅 Aplicando período personalizado:', range);
    handleRangeChange(range);
  };

  // Função para limpar filtro
  const handleClearFilter = () => {
    console.log('🗑️ Limpando filtro de data');
    handleRangeChange(null);
  };

  return (
    <div className="date-range-filter">
      {/* Botões de períodos predefinidos */}
      <div className="predefined-ranges">
        {predefinedRanges.map(({ label, days }) => (
          <button
            key={days}
            onClick={() => handlePredefinedRangeSelect(days, label)}
            className={`range-button ${
              currentRange?.label === label ? 'active' : ''
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Campos de data personalizada */}
      <div className="custom-range">
        <input
          type="date"
          placeholder="Data inicial"
          onChange={(e) => {
            if (customEndDate) {
              handleCustomRangeApply(e.target.value, customEndDate);
            }
          }}
        />
        <input
          type="date"
          placeholder="Data final"
          onChange={(e) => {
            if (customStartDate) {
              handleCustomRangeApply(customStartDate, e.target.value);
            }
          }}
        />
      </div>

      {/* Botão para limpar filtro */}
      {currentRange && (
        <button onClick={handleClearFilter} className="clear-button">
          Limpar Filtro
        </button>
      )}

      {/* Indicador do filtro atual */}
      {currentRange && (
        <div className="current-filter">
          📅 {currentRange.label}
        </div>
      )}
    </div>
  );
};
```

### 6. Frontend - Serviços API (`services/api.ts`)

#### Serviço de API com Suporte a Filtros
```typescript
export const apiService = {
  // Obter métricas com filtro opcional de data
  async getMetrics(dateRange?: DateRange | null): Promise<MetricsData> {
    try {
      let url = '/metrics';
      
      // Adicionar parâmetros de data se fornecidos
      if (dateRange && dateRange.startDate && dateRange.endDate) {
        const params = new URLSearchParams({
          start_date: dateRange.startDate,
          end_date: dateRange.endDate
        });
        url += `?${params.toString()}`;
        console.log('🔍 Chamando API com filtro de data:', {
          start_date: dateRange.startDate,
          end_date: dateRange.endDate
        });
      } else {
        console.log('🔍 Chamando API sem filtro de data');
      }
      
      const response = await api.get(url);
      
      // Verificar estrutura da resposta
      if (response.data && response.data.success && response.data.data) {
        const data = response.data.data;
        console.log('✅ Dados recebidos da API:', data);
        return data;
      } else {
        console.error('❌ API retornou resposta mal formada:', response.data);
        throw new Error('Resposta da API mal formada');
      }
    } catch (error) {
      console.error('❌ Erro ao buscar métricas:', error);
      
      // Retornar dados de fallback em caso de erro
      return {
        novos: 0,
        pendentes: 0,
        progresso: 0,
        resolvidos: 0,
        total: 0,
        niveis: {
          n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
          n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
          n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
          n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 }
        },
        tendencias: { novos: '0', pendentes: '0', progresso: '0', resolvidos: '0' }
      };
    }
  }
};
```

### 7. Integração no Componente Principal (`App.tsx`)

#### Conectando Tudo
```typescript
export default function App() {
  const { data, loading, error, dateRange, updateDateRange } = useDashboard();

  return (
    <div className="app">
      <Header 
        onDateRangeChange={updateDateRange}
        currentDateRange={dateRange}
      />
      
      {loading && <div>Carregando...</div>}
      {error && <div>Erro: {error}</div>}
      
      {data && (
        <>
          <ModernDashboard 
            data={data}
            dateRange={dateRange}
            onDateRangeChange={updateDateRange}
          />
          
          <SimplifiedDashboard 
            data={data}
            dateRange={dateRange}
            onDateRangeChange={updateDateRange}
          />
        </>
      )}
    </div>
  );
}
```

---

## 🧪 Padrões de Teste

### Script de Teste Base
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste base para filtros de data GLPI
"""

import requests
import json
from datetime import datetime, timedelta

def test_date_filters():
    """Testa filtros de data na API"""
    base_url = "http://localhost:5000/api"
    
    print("=== TESTE DE FILTROS DE DATA ===")
    
    # Teste 1: Sem filtro
    print("\n1. TESTE SEM FILTRO:")
    response = requests.get(f"{base_url}/metrics")
    if response.status_code == 200:
        data = response.json().get('data', {})
        print(f"✅ Total: {data.get('total', 0)}")
        print(f"✅ Filtro: {'Nenhum' if not data.get('filtro_data') else data.get('filtro_data')}")
    
    # Teste 2: Com filtro de 7 dias
    print("\n2. TESTE COM FILTRO DE 7 DIAS:")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    params = {'start_date': start_date, 'end_date': end_date}
    response = requests.get(f"{base_url}/metrics", params=params)
    if response.status_code == 200:
        data = response.json().get('data', {})
        filtro = data.get('filtro_data', {})
        print(f"✅ Total: {data.get('total', 0)}")
        print(f"✅ Período: {filtro.get('data_inicio')} até {filtro.get('data_fim')}")
        
        # Verificar se filtro foi aplicado
        if filtro.get('data_inicio') == start_date and filtro.get('data_fim') == end_date:
            print("✅ Filtro aplicado corretamente!")
        else:
            print("❌ Filtro não aplicado corretamente")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_date_filters()
```

---

## 🔍 Troubleshooting

### Problemas Comuns e Soluções

#### 1. Filtros não funcionam
**Sintomas**: API retorna dados sem filtro aplicado
**Verificações**:
- Parâmetros `start_date` e `end_date` estão sendo enviados?
- Formato das datas está correto (YYYY-MM-DD)?
- Backend está processando os parâmetros?

**Solução**:
```python
# Verificar logs do backend
logger.info(f"Parâmetros recebidos: start_date={start_date}, end_date={end_date}")

# Verificar se parâmetros chegam ao serviço
if start_date or end_date:
    metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(start_date, end_date)
else:
    metrics_data = glpi_service.get_dashboard_metrics()
```

#### 2. Datas inválidas
**Sintomas**: Erro 400 com mensagem de formato inválido
**Verificações**:
- Formato está YYYY-MM-DD?
- Data inicial não é posterior à final?

**Solução**:
```python
# Validação robusta
try:
    if start_date:
        datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        datetime.strptime(end_date, '%Y-%m-%d')
    
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        if start_dt > end_dt:
            raise ValueError("Data inicial posterior à final")
except ValueError as e:
    return error_response(str(e))
```

#### 3. Frontend não envia parâmetros
**Sintomas**: Chamadas API sem query parameters
**Verificações**:
- Hook `useDashboard` está recebendo `DateRange`?
- `apiService.getMetrics()` está sendo chamado com parâmetros?
- Componente `DateRangeFilter` está chamando `onRangeChange`?

**Solução**:
```typescript
// Verificar logs no console
console.log('📅 Enviando filtro para API:', dateRange);

// Verificar se parâmetros são adicionados à URL
if (dateRange && dateRange.startDate && dateRange.endDate) {
    const params = new URLSearchParams({
        start_date: dateRange.startDate,
        end_date: dateRange.endDate
    });
    url += `?${params.toString()}`;
    console.log('🔗 URL final:', url);
}
```

#### 4. Incompatibilidade de tipos
**Sintomas**: Erros TypeScript ou props não funcionam
**Verificações**:
- Interface `DateRange` está definida corretamente?
- Props do componente estão tipadas?
- Hook retorna tipos corretos?

**Solução**:
```typescript
// Definir interfaces claras
interface DateRange {
  startDate: string;  // YYYY-MM-DD
  endDate: string;    // YYYY-MM-DD
  label: string;      // Descrição amigável
}

// Normalizar props no componente
const currentRange = selectedRange || value;
const handleRangeChange = onRangeChange || onChange || (() => {});
```

---

## 📚 Checklist de Implementação

### Backend
- [ ] Método com filtro de data no serviço GLPI
- [ ] Validação de formato de data
- [ ] Validação de ordem das datas
- [ ] Logs detalhados
- [ ] Tratamento de erros
- [ ] Fallback para dados padrão
- [ ] Endpoint API com suporte a query parameters
- [ ] Testes unitários

### Frontend
- [ ] Interface `DateRange` definida
- [ ] Hook `useDashboard` com suporte a filtros
- [ ] Componente `DateRangeFilter` funcional
- [ ] Serviço API com parâmetros de data
- [ ] Integração no componente principal
- [ ] Logs de debugging
- [ ] Tratamento de erros
- [ ] Testes de integração

### Testes
- [ ] Script de teste da API
- [ ] Teste sem filtro
- [ ] Teste com filtros predefinidos
- [ ] Teste com filtros personalizados
- [ ] Teste de validação de datas
- [ ] Teste de casos extremos

---

## 🎯 Exemplo de Implementação Completa

### Para Nova Métrica: "Tickets por Categoria"

1. **Backend - Adicionar método no `glpi_service.py`**:
```python
def get_tickets_by_category_with_date_filter(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
    """Obter tickets agrupados por categoria com filtro de data"""
    if not self._ensure_authenticated():
        return {}
    
    categories = {}  # Implementar lógica específica
    return categories
```

2. **Backend - Adicionar endpoint em `routes.py`**:
```python
@api_bp.route('/tickets/by-category')
def get_tickets_by_category():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Validações padrão...
    
    data = glpi_service.get_tickets_by_category_with_date_filter(start_date, end_date)
    return jsonify({"success": True, "data": data})
```

3. **Frontend - Adicionar ao serviço API**:
```typescript
async getTicketsByCategory(dateRange?: DateRange): Promise<CategoryData> {
    // Implementação seguindo padrão estabelecido
}
```

4. **Frontend - Usar no componente**:
```typescript
const { updateDateRange } = useDashboard();

// Componente automaticamente receberá filtros de data
<CategoryChart 
    onDateRangeChange={updateDateRange}
    dateRange={dateRange}
/>
```

---

## 🏁 Conclusão

Este guia fornece uma base sólida e reutilizável para implementar filtros de data em qualquer consulta GLPI. Seguindo estes padrões, você garante:

- **Consistência** em todas as implementações
- **Reutilização** de código e padrões
- **Manutenibilidade** através de estrutura clara
- **Debugging** facilitado com logs detalhados
- **Robustez** com validações e tratamento de erros

**Lembre-se**: Sempre teste cada implementação com o script de teste fornecido e verifique os logs tanto do backend quanto do frontend para garantir que tudo está funcionando corretamente.

---

*Última atualização: Agosto 2025*
*Versão: 1.0*