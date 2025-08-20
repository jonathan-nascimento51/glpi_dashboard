# Prompts de Desenvolvimento - GLPI Dashboard

## 🎯 Prompts Contextuais para Desenvolvimento

Este arquivo contém prompts pré-definidos e contextualizados para acelerar o desenvolvimento com assistentes de IA.

## 🏗️ Desenvolvimento de Features

### Prompt Base para Nova Feature

```markdown
**CONTEXTO DO PROJETO**:
- Nome: GLPI Dashboard
- Stack: Backend Flask + Frontend React/TypeScript
- Arquitetura: Clean Architecture com separação de camadas
- Padrões: RESTful APIs, TDD, Observabilidade

**ESTRUTURA ATUAL**:
- Backend: `backend/` (Flask, Redis, Prometheus)
- Frontend: `frontend/src/` (React, TypeScript, Vite)
- Testes: `backend/tests/` e `frontend/src/__tests__/`
- Docs: `docs/` (Markdown)

**REQUISITOS OBRIGATÓRIOS**:
1. Seguir padrões de código existentes (PEP8, ESLint)
2. Incluir testes unitários e de integração
3. Documentar APIs com schemas TypeScript
4. Implementar logs estruturados com correlation_id
5. Adicionar métricas Prometheus quando aplicável
6. Validar entrada de dados
7. Implementar tratamento de erros

**ARQUIVOS PRINCIPAIS**:
- Backend: `backend/api/routes.py`, `backend/services/glpi_service.py`
- Frontend: `frontend/src/services/api.ts`, `frontend/src/components/`
- Configuração: `backend/config/settings.py`

**TASK**: [Descrever a feature específica aqui]
```

### Prompt para Nova API Endpoint

```markdown
**CONTEXTO**: Criando novo endpoint para GLPI Dashboard

**ESPECIFICAÇÕES**:
- Método HTTP: [GET/POST/PUT/DELETE]
- Endpoint: `/api/[nome]`
- Parâmetros: [listar parâmetros]
- Resposta esperada: [descrever schema]

**CHECKLIST OBRIGATÓRIO**:
- [ ] Validação de entrada com schemas
- [ ] Tratamento de erros com códigos HTTP apropriados
- [ ] Logs estruturados com correlation_id
- [ ] Cache Redis quando aplicável
- [ ] Métricas Prometheus
- [ ] Testes unitários e de integração
- [ ] Documentação da API
- [ ] Integração com frontend

**PADRÕES A SEGUIR**:
- Usar `@observability_logger.monitor_endpoint()` decorator
- Implementar `ResponseFormatter.success()` para respostas
- Adicionar validação com `request_validator`
- Incluir `correlation_id` em todos os logs

**EXEMPLO DE ESTRUTURA**:
```python
@api_bp.route('/api/[nome]', methods=['[MÉTODO]'])
@observability_logger.monitor_endpoint()
@cache.cached(timeout=300)
def [nome]():
    correlation_id = request.headers.get('X-Correlation-ID', generate_correlation_id())
    
    try:
        # Validação
        # Lógica de negócio
        # Resposta
        return ResponseFormatter.success(data, correlation_id)
    except Exception as e:
        return ResponseFormatter.error(str(e), correlation_id)
```
```

### Prompt para Componente React

```markdown
**CONTEXTO**: Criando componente React para GLPI Dashboard

**ESPECIFICAÇÕES**:
- Nome do componente: [Nome]
- Funcionalidade: [Descrever]
- Props esperadas: [Listar props]
- Estado necessário: [Descrever estado]

**PADRÕES OBRIGATÓRIOS**:
- TypeScript com interfaces bem definidas
- Hooks customizados para lógica complexa
- Tailwind CSS para estilização
- Tratamento de loading e error states
- Acessibilidade (ARIA labels, keyboard navigation)
- Testes com Jest e Testing Library

**ESTRUTURA ESPERADA**:
```typescript
interface [Nome]Props {
  // Props aqui
}

export const [Nome]: React.FC<[Nome]Props> = ({ ...props }) => {
  // Hooks
  // Estado local
  // Efeitos
  // Handlers
  
  return (
    <div className="..." role="..." aria-label="...">
      {/* JSX aqui */}
    </div>
  );
};
```

**CHECKLIST**:
- [ ] Interface TypeScript para props
- [ ] Tratamento de loading/error
- [ ] Responsividade (mobile-first)
- [ ] Acessibilidade
- [ ] Testes unitários
- [ ] Storybook story (se aplicável)
```

## 🔧 Integração com GLPI

### Prompt para Nova Integração GLPI

```markdown
**CONTEXTO**: Integrando nova funcionalidade com API GLPI

**INFORMAÇÕES GLPI**:
- Base URL: Configurada em `GLPI_URL`
- Autenticação: App Token + User Token
- Sessão: Gerenciada automaticamente
- Rate Limiting: Implementado

**PADRÕES DE INTEGRAÇÃO**:
1. Usar `GLPIService` existente como base
2. Implementar cache Redis para reduzir chamadas
3. Adicionar retry automático para falhas temporárias
4. Logs detalhados de todas as chamadas
5. Métricas de performance
6. Tratamento de timeouts

**ESTRUTURA PADRÃO**:
```python
class GLPIService:
    def new_method(self, params):
        correlation_id = generate_correlation_id()
        
        try:
            # Cache check
            cache_key = f"glpi:{method}:{hash(params)}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached
            
            # GLPI call
            response = self._make_authenticated_request(
                endpoint='/search/[ItemType]',
                params=params,
                correlation_id=correlation_id
            )
            
            # Process response
            processed_data = self._process_response(response)
            
            # Cache result
            self.cache.set(cache_key, processed_data, timeout=300)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"GLPI integration error", extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "params": params
            })
            raise
```

**TASK**: [Descrever integração específica]
```

## 🧪 Desenvolvimento com TDD

### Prompt para Testes

```markdown
**CONTEXTO**: Implementando testes para GLPI Dashboard

**TIPOS DE TESTE NECESSÁRIOS**:
1. **Unitários**: Funções isoladas, lógica de negócio
2. **Integração**: APIs, banco de dados, cache
3. **E2E**: Fluxos completos usuário
4. **Performance**: Tempo de resposta, throughput

**ESTRUTURA DE TESTES**:

**Backend (pytest)**:
```python
import pytest
from unittest.mock import Mock, patch
from backend.services.glpi_service import GLPIService

class TestGLPIService:
    @pytest.fixture
    def glpi_service(self):
        return GLPIService()
    
    @patch('backend.services.glpi_service.requests.post')
    def test_method_success(self, mock_post, glpi_service):
        # Arrange
        mock_post.return_value.json.return_value = {'data': 'test'}
        
        # Act
        result = glpi_service.method()
        
        # Assert
        assert result == expected_result
        mock_post.assert_called_once()
```

**Frontend (Jest + Testing Library)**:
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Component } from './Component';

describe('Component', () => {
  it('should render correctly', () => {
    render(<Component />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
  
  it('should handle user interaction', async () => {
    const user = userEvent.setup();
    render(<Component />);
    
    await user.click(screen.getByRole('button'));
    
    await waitFor(() => {
      expect(screen.getByText('Expected text')).toBeInTheDocument();
    });
  });
});
```

**CHECKLIST DE TESTES**:
- [ ] Casos de sucesso
- [ ] Casos de erro
- [ ] Validação de entrada
- [ ] Estados de loading
- [ ] Timeouts
- [ ] Cache hit/miss
- [ ] Acessibilidade
```

## 🐛 Debug e Troubleshooting

### Prompt para Debug

```markdown
**CONTEXTO**: Debug de issue no GLPI Dashboard

**INFORMAÇÕES DO SISTEMA**:
- Logs: `backend/logs/` (structured JSON)
- Métricas: `/metrics` endpoint (Prometheus)
- Health Check: `/health` endpoint
- Cache: Redis status em `/health`

**CHECKLIST DE DEBUG**:
1. **Verificar logs estruturados**:
   ```bash
   tail -f backend/logs/app.log | jq .
   ```

2. **Verificar métricas**:
   - Tempo de resposta das APIs
   - Taxa de erro
   - Status do cache
   - Conectividade GLPI

3. **Verificar health checks**:
   ```bash
   curl http://localhost:5000/health
   ```

4. **Verificar cache Redis**:
   ```bash
   redis-cli ping
   redis-cli info memory
   ```

5. **Verificar conectividade GLPI**:
   ```bash
   curl -H "App-Token: $GLPI_APP_TOKEN" $GLPI_URL/initSession
   ```

**LOGS IMPORTANTES**:
- `correlation_id`: Para rastrear requisições
- `execution_time_ms`: Performance
- `cache_hit`: Eficiência do cache
- `glpi_calls`: Número de chamadas externas

**ISSUE**: [Descrever o problema específico]
```

## 🚀 Deploy e Produção

### Prompt para Deploy

```markdown
**CONTEXTO**: Preparando deploy para produção

**CHECKLIST PRÉ-DEPLOY**:
- [ ] Todos os testes passando
- [ ] Cobertura de testes >80%
- [ ] Logs estruturados implementados
- [ ] Métricas Prometheus configuradas
- [ ] Health checks funcionando
- [ ] Variáveis de ambiente configuradas
- [ ] Cache Redis configurado
- [ ] Rate limiting ativo
- [ ] CORS configurado corretamente
- [ ] Documentação atualizada

**CONFIGURAÇÕES DE PRODUÇÃO**:
```python
class ProductionConfig:
    DEBUG = False
    LOG_LEVEL = 'INFO'
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    GLPI_URL = os.getenv('GLPI_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
```

**MONITORAMENTO**:
- Alertas para p95 > 300ms
- Alertas para taxa de erro > 1%
- Alertas para GLPI indisponível
- Alertas para cache Redis down

**TASK**: [Descrever deploy específico]
```

## 📚 Documentação

### Prompt para Documentação

```markdown
**CONTEXTO**: Criando/atualizando documentação

**PADRÕES DE DOCUMENTAÇÃO**:
- Markdown com sintaxe GitHub
- Exemplos de código funcionais
- Diagramas com Mermaid quando necessário
- Links para arquivos relacionados
- Tags de contexto para IA

**ESTRUTURA PADRÃO**:
```markdown
# Título

## Visão Geral
[Descrição concisa]

## Como Usar
[Exemplos práticos]

## Configuração
[Passos de configuração]

## Exemplos
[Código funcional]

## Troubleshooting
[Problemas comuns]

---
**AI Context Tags**: tag1, tag2, tag3
**Related Files**: file1.py, file2.ts
**Last Updated**: YYYY-MM-DD
```

**TASK**: [Descrever documentação específica]
```

---

**AI Context Tags**: `development-prompts`, `tdd`, `clean-architecture`, `glpi-integration`
**Related Files**: `backend/api/routes.py`, `frontend/src/components/`, `backend/tests/`
**Last Updated**: 2024-01-15