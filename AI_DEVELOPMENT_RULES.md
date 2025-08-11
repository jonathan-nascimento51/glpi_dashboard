# 🤖 Regras de Desenvolvimento para IA - GLPI Dashboard

## 🎯 Objetivo
Este documento define regras específicas para assistentes de IA trabalharem neste projeto, garantindo consistência, qualidade e alinhamento com os padrões estabelecidos.

## 📋 Regras Gerais de Atuação

### 1. Análise Antes da Ação
- **SEMPRE** analisar o contexto completo antes de fazer alterações
- Verificar arquivos relacionados que podem ser impactados
- Entender a arquitetura e padrões existentes
- Considerar impactos em performance, segurança e usabilidade

### 2. Priorização de Tarefas
1. **Crítico**: Bugs que quebram funcionalidade
2. **Alto**: Problemas de segurança ou performance
3. **Médio**: Melhorias de código e refatorações
4. **Baixo**: Otimizações e features não essenciais

### 3. Validação Obrigatória
- Executar testes após cada alteração
- Verificar build sem erros
- Confirmar funcionamento da aplicação
- Validar padrões de código

## 🔧 Regras Técnicas Específicas

### Frontend (React + TypeScript)

#### Componentes
```typescript
// ✅ SEMPRE fazer assim
interface ComponentProps {
  // Props tipadas com interface
  data: DataType;
  onAction?: () => void;
}

export const Component: React.FC<ComponentProps> = ({ data, onAction }) => {
  // Implementação
};

// ❌ NUNCA fazer assim
export const Component = (props: any) => {
  // Props sem tipagem
};
```

#### Estado e Efeitos
```typescript
// ✅ SEMPRE usar hooks apropriados
const [state, setState] = useState<StateType>(initialValue);
const memoizedValue = useMemo(() => expensiveCalculation(data), [data]);
const debouncedCallback = useCallback(debounce(callback, 300), []);

// ❌ NUNCA fazer cálculos pesados sem otimização
const expensiveValue = expensiveCalculation(data); // Re-executa a cada render
```

#### Tratamento de Erros
```typescript
// ✅ SEMPRE implementar Error Boundaries e try/catch
try {
  const result = await apiCall();
  setData(result);
} catch (error) {
  console.error('API Error:', error);
  setError('Falha ao carregar dados');
}

// ❌ NUNCA ignorar erros
const result = await apiCall(); // Sem tratamento de erro
```

### Backend (Python + Flask)

#### Estrutura de Funções
```python
# ✅ SEMPRE documentar e tipar
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

async def get_data(
    start_date: datetime,
    end_date: datetime,
    limit: Optional[int] = 10
) -> List[DataModel]:
    """Docstring explicativa.
    
    Args:
        start_date: Data inicial
        end_date: Data final
        limit: Limite de resultados
        
    Returns:
        Lista de dados
        
    Raises:
        ValueError: Se datas inválidas
    """
    if start_date >= end_date:
        raise ValueError("Data inicial deve ser anterior à final")
    
    try:
        # Implementação
        logger.info(f"Fetching data from {start_date} to {end_date}")
        return results
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

# ❌ NUNCA fazer sem documentação/tipagem
def get_data(start, end):
    # Sem documentação, tipagem ou logs
    return db.query()
```

#### Cache e Performance
```python
# ✅ SEMPRE implementar cache para operações custosas
cache_key = f"data:{start_date}:{end_date}"
cached_result = await cache.get(cache_key)
if cached_result:
    return cached_result

result = expensive_operation()
await cache.set(cache_key, result, ttl=900)  # 15 min
return result

# ❌ NUNCA fazer operações custosas sem cache
return expensive_database_query()  # Sempre executa
```

## 🧪 Regras de Testes

### Cobertura Obrigatória
- **Novos componentes**: 90%+ de cobertura
- **Funções críticas**: 95%+ de cobertura
- **APIs**: 100% dos endpoints testados
- **Hooks customizados**: 90%+ de cobertura

### Tipos de Testes Necessários
```typescript
// ✅ SEMPRE implementar estes testes
describe('Component', () => {
  // 1. Renderização básica
  it('should render correctly', () => {});
  
  // 2. Props e estados
  it('should handle props correctly', () => {});
  
  // 3. Interações do usuário
  it('should handle user interactions', () => {});
  
  // 4. Estados de loading/error
  it('should show loading state', () => {});
  it('should handle errors', () => {});
  
  // 5. Edge cases
  it('should handle empty data', () => {});
  it('should handle invalid props', () => {});
});
```

### Mocks e Fixtures
```typescript
// ✅ SEMPRE usar mocks realistas
const mockApiResponse = {
  data: [
    { id: 1, name: 'Test Item', status: 'active' },
    { id: 2, name: 'Test Item 2', status: 'inactive' }
  ],
  total: 2,
  page: 1
};

// ❌ NUNCA usar mocks vazios ou irrealistas
const mockData = {}; // Muito genérico
```

## 📝 Regras de Documentação

### Comentários de Código
```typescript
// ✅ SEMPRE explicar lógica complexa
// Calcula score de performance baseado em:
// - Taxa de resolução (70% do peso)
// - Tempo médio de resolução (30% do peso)
const performanceScore = (resolvedRate * 0.7) + (timeScore * 0.3);

// ❌ NUNCA comentar o óbvio
const total = a + b; // Soma a e b
```

### README de Componentes
```markdown
# ComponentName

## Descrição
Breve descrição do que o componente faz.

## Props
| Prop | Tipo | Obrigatório | Descrição |
|------|------|-------------|----------|

## Exemplo
```tsx
<Component prop="value" />
```

## Testes
- [ ] Renderização
- [ ] Props
- [ ] Interações
- [ ] Estados
```

## 🔒 Regras de Segurança

### Validação de Dados
```python
# ✅ SEMPRE validar inputs
from marshmallow import Schema, fields, validate

class UserInputSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    age = fields.Int(validate=validate.Range(min=0, max=150))

# Usar schema para validar
schema = UserInputSchema()
try:
    result = schema.load(request.json)
except ValidationError as err:
    return jsonify({'errors': err.messages}), 400

# ❌ NUNCA usar dados sem validação
name = request.json.get('name')  # Sem validação
```

### Logs Seguros
```python
# ✅ SEMPRE logar sem dados sensíveis
logger.info(f"User {user_id} performed action {action}")
logger.error(f"Database error: {error_type}")

# ❌ NUNCA logar dados sensíveis
logger.info(f"User password: {password}")  # NUNCA!
logger.info(f"API key: {api_key}")  # NUNCA!
```

## 🚀 Regras de Performance

### Frontend
```typescript
// ✅ SEMPRE otimizar re-renders
const MemoizedComponent = React.memo(Component);

const optimizedCallback = useCallback(() => {
  // Lógica
}, [dependency]);

const expensiveValue = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);

// ❌ NUNCA criar funções/objetos inline em renders
<Component 
  onClick={() => handleClick()}  // Nova função a cada render
  style={{margin: 10}}          // Novo objeto a cada render
/>
```

### Backend
```python
# ✅ SEMPRE usar paginação para listas grandes
def get_items(page: int = 1, per_page: int = 20) -> PaginatedResponse:
    offset = (page - 1) * per_page
    items = db.query().offset(offset).limit(per_page).all()
    total = db.query().count()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )

# ❌ NUNCA retornar listas completas sem paginação
def get_all_items():
    return db.query().all()  # Pode retornar milhões de registros
```

## 🔄 Regras de Refatoração

### Quando Refatorar
1. **Código duplicado** em 3+ lugares
2. **Funções com 50+ linhas** (quebrar em funções menores)
3. **Componentes com 200+ linhas** (quebrar em subcomponentes)
4. **Arquivos com 500+ linhas** (dividir responsabilidades)

### Como Refatorar
```typescript
// ✅ ANTES da refatoração
// 1. Escrever testes para comportamento atual
// 2. Refatorar mantendo testes passando
// 3. Melhorar testes se necessário

// Exemplo: Extrair hook customizado
// ANTES: Lógica no componente
const Component = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    setLoading(true);
    fetchData().then(setData).finally(() => setLoading(false));
  }, []);
  
  return <div>{/* render */}</div>;
};

// DEPOIS: Hook customizado
const useData = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    setLoading(true);
    fetchData().then(setData).finally(() => setLoading(false));
  }, []);
  
  return { data, loading };
};

const Component = () => {
  const { data, loading } = useData();
  return <div>{/* render */}</div>;
};
```

## 🐛 Regras de Debug

### Logs de Debug
```typescript
// ✅ SEMPRE usar logs estruturados
console.group('API Call');
console.log('URL:', url);
console.log('Params:', params);
console.log('Response:', response);
console.groupEnd();

// Para produção, usar logger apropriado
logger.debug('API call', { url, params, responseTime });

// ❌ NUNCA deixar console.log em produção
console.log('debug info'); // Remover antes do commit
```

### Tratamento de Erros
```typescript
// ✅ SEMPRE capturar contexto do erro
try {
  await apiCall(params);
} catch (error) {
  const errorContext = {
    function: 'apiCall',
    params,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  };
  
  logger.error('API call failed', { error, context: errorContext });
  
  // Mostrar erro amigável para usuário
  showNotification('Erro ao carregar dados. Tente novamente.', 'error');
}

// ❌ NUNCA ignorar ou logar erro genérico
try {
  await apiCall();
} catch (error) {
  console.log('error'); // Muito genérico
}
```

## 📊 Regras de Monitoramento

### Métricas Importantes
```typescript
// ✅ SEMPRE monitorar métricas críticas
// Performance
performance.mark('api-call-start');
await apiCall();
performance.mark('api-call-end');
performance.measure('api-call', 'api-call-start', 'api-call-end');

// Erros
window.addEventListener('error', (event) => {
  analytics.track('JavaScript Error', {
    message: event.error.message,
    stack: event.error.stack,
    filename: event.filename,
    lineno: event.lineno
  });
});

// User actions
const handleUserAction = (action: string) => {
  analytics.track('User Action', { action, timestamp: Date.now() });
};
```

## 🎯 Checklist de Qualidade

### Antes de Cada Commit
- [ ] Testes passando (frontend e backend)
- [ ] Build sem erros
- [ ] Linting sem warnings
- [ ] Cobertura de testes adequada
- [ ] Documentação atualizada
- [ ] Performance validada
- [ ] Segurança verificada
- [ ] Logs de debug removidos

### Antes de Cada PR
- [ ] Branch atualizada com main
- [ ] Conflitos resolvidos
- [ ] Descrição clara do PR
- [ ] Screenshots/videos se UI changes
- [ ] Reviewers atribuídos
- [ ] Labels apropriadas

### Antes de Cada Release
- [ ] Todos os testes E2E passando
- [ ] Performance benchmarks OK
- [ ] Security scan limpo
- [ ] Documentação de release atualizada
- [ ] Rollback plan definido
- [ ] Monitoramento configurado

---

## 🚨 Regras Críticas - NUNCA QUEBRAR

1. **NUNCA** fazer commit de código que quebra testes
2. **NUNCA** fazer deploy sem validação completa
3. **NUNCA** expor dados sensíveis em logs
4. **NUNCA** ignorar erros silenciosamente
5. **NUNCA** fazer alterações sem backup/rollback plan
6. **NUNCA** pular validação de segurança
7. **NUNCA** fazer refatoração sem testes
8. **NUNCA** usar dependências não aprovadas
9. **NUNCA** hardcodar valores de configuração
10. **NUNCA** deixar TODOs em código de produção

---

**Lembre-se**: Estas regras existem para garantir qualidade, segurança e manutenibilidade. Quando em dúvida, sempre opte pela abordagem mais segura e bem documentada.

**Última atualização**: 2024-12-29
**Versão**: 1.0.0