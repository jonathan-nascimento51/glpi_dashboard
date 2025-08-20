# Guia de Integração com IA - GLPI Dashboard

Este documento fornece diretrizes e recursos para otimizar a integração com assistentes de IA durante o desenvolvimento do projeto GLPI Dashboard.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Documentação Orientada à IA](#documentação-orientada-à-ia)
3. [Prompts Contextuais Automáticos](#prompts-contextuais-automáticos)
4. [Sandbox para Testes](#sandbox-para-testes)
5. [Melhores Práticas](#melhores-práticas)
6. [Recursos Adicionais](#recursos-adicionais)

## 🎯 Visão Geral

O projeto GLPI Dashboard foi otimizado para facilitar a colaboração com assistentes de IA, fornecendo:

- **Documentação estruturada** com contexto técnico detalhado
- **Prompts automáticos** para tarefas comuns de desenvolvimento
- **Ambiente de sandbox** para testes seguros
- **Padrões de código** consistentes e bem documentados

## 📚 Documentação Orientada à IA

### Estrutura de Arquivos

```
docs/ai/
├── context/                    # Contexto do projeto
│   ├── architecture.md         # Arquitetura do sistema
│   ├── business_rules.md        # Regras de negócio
│   ├── api_contracts.md         # Contratos de API
│   └── data_models.md          # Modelos de dados
├── prompts/                    # Prompts automáticos
│   ├── development.md          # Prompts para desenvolvimento
│   ├── debugging.md            # Prompts para debug
│   ├── testing.md              # Prompts para testes
│   └── refactoring.md          # Prompts para refatoração
├── sandbox/                    # Ambiente de testes
│   ├── test_data/              # Dados de teste
│   ├── mock_configs/           # Configurações mock
│   └── examples/               # Exemplos de código
└── templates/                  # Templates de código
    ├── component.tsx.template  # Template React
    ├── service.py.template     # Template Python
    └── test.spec.ts.template   # Template de teste
```

### Metadados de Contexto

Cada arquivo importante do projeto deve incluir metadados para IA:

```python
"""
AI Context:
- Purpose: Serviço principal para integração com GLPI API
- Dependencies: requests, flask, redis
- Key Functions: get_metrics, authenticate, cache_data
- Related Files: api/routes.py, config/settings.py
- Testing: tests/unit/test_glpi_service.py
- Last Updated: 2024-01-15
"""
```

## 🤖 Prompts Contextuais Automáticos

### Sistema de Prompts

O projeto inclui prompts pré-definidos para tarefas comuns:

#### 1. Desenvolvimento de Features
```markdown
**Contexto**: Desenvolvendo nova feature para GLPI Dashboard
**Arquitetura**: Backend Flask + Frontend React + TypeScript
**Padrões**: Clean Architecture, TDD, Observabilidade
**Requisitos**: Seguir padrões existentes, incluir testes, documentar APIs
```

#### 2. Debug e Troubleshooting
```markdown
**Contexto**: Debug de issue no GLPI Dashboard
**Logs**: Verificar backend/logs/ e observabilidade
**Ferramentas**: Prometheus metrics, structured logging
**Checklist**: API status, cache Redis, GLPI connectivity
```

#### 3. Refatoração
```markdown
**Contexto**: Refatoração de código no GLPI Dashboard
**Princípios**: SOLID, DRY, Clean Code
**Testes**: Manter cobertura >80%, incluir testes de regressão
**Observabilidade**: Preservar métricas e logs estruturados
```

### Configuração Automática

O arquivo `.ai-context.yml` na raiz do projeto fornece contexto automático:

```yaml
project:
  name: "GLPI Dashboard"
  type: "Full-stack Web Application"
  stack: ["Python", "Flask", "React", "TypeScript"]
  
architecture:
  pattern: "Clean Architecture"
  backend: "Flask REST API"
  frontend: "React SPA"
  database: "GLPI MySQL"
  cache: "Redis"
  
standards:
  code_style: "PEP8 (Python), ESLint (TypeScript)"
  testing: "pytest, Jest, Playwright"
  documentation: "Markdown, JSDoc, Sphinx"
  
key_files:
  - "backend/api/routes.py"
  - "backend/services/glpi_service.py"
  - "frontend/src/services/api.ts"
  - "frontend/src/components/Dashboard.tsx"
```

## 🧪 Sandbox para Testes

### Ambiente Isolado

O sandbox permite testes seguros sem afetar o ambiente de produção:

```bash
# Ativar modo sandbox
export FLASK_ENV=sandbox
export USE_MOCK_DATA=true
export GLPI_URL=http://localhost:8080/mock-glpi

# Executar com dados mock
python scripts/sandbox/run_sandbox.py
```

### Dados de Teste

Dados sintéticos para desenvolvimento:

```json
{
  "metrics": {
    "total": 150,
    "novos": 25,
    "pendentes": 45,
    "progresso": 60,
    "resolvidos": 20,
    "niveis": {
      "n1": 30,
      "n2": 45,
      "n3": 50,
      "n4": 25
    }
  }
}
```

### Mock Services

Serviços mock para desenvolvimento offline:

```python
class MockGLPIService:
    """Mock service para desenvolvimento sem GLPI real"""
    
    def get_metrics(self, filters=None):
        return self._load_mock_data('metrics.json')
    
    def get_tickets(self, filters=None):
        return self._load_mock_data('tickets.json')
```

## ✅ Melhores Práticas

### 1. Documentação de Código

- **Docstrings detalhadas** com exemplos de uso
- **Comentários explicativos** para lógica complexa
- **Metadados de contexto** para IA
- **Links para documentação** relacionada

### 2. Estrutura de Prompts

- **Contexto claro** do problema
- **Requisitos específicos** e restrições
- **Exemplos de entrada/saída** esperados
- **Critérios de aceitação** definidos

### 3. Testes e Validação

- **Testes unitários** para toda nova funcionalidade
- **Testes de integração** para fluxos completos
- **Validação de contratos** de API
- **Testes de regressão** automatizados

### 4. Observabilidade

- **Logs estruturados** em JSON
- **Métricas de performance** com Prometheus
- **Tracing distribuído** para debug
- **Alertas automáticos** para anomalias

## 📖 Recursos Adicionais

### Documentação Técnica

- [Arquitetura do Sistema](./context/architecture.md)
- [Guia de API](./context/api_contracts.md)
- [Modelos de Dados](./context/data_models.md)
- [Regras de Negócio](./context/business_rules.md)

### Templates e Exemplos

- [Templates de Código](./templates/)
- [Exemplos de Implementação](./sandbox/examples/)
- [Dados de Teste](./sandbox/test_data/)

### Ferramentas de Desenvolvimento

- **Scripts de Debug**: `scripts/debug/`
- **Validação Automática**: `scripts/validation/`
- **Testes de Performance**: `scripts/tests/`
- **Monitoramento**: `backend/monitoring_system.py`

---

**Última Atualização**: 2024-01-15
**Versão**: 1.0.0
**Mantido por**: Equipe de Desenvolvimento GLPI Dashboard