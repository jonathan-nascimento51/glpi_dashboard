# Metodologia de Revisão em Ciclos - GLPI Dashboard

## Visão Geral

Esta metodologia implementa um processo estruturado de revisão baseado em ciclos iterativos de três fases, focando na modularidade e melhoria contínua do projeto GLPI Dashboard.

## Princípios Fundamentais

### 1. Definição de Metas e Escopo
- **Antes de cada ciclo**: esclarecer problemas específicos a resolver
- **Foco direcionado**: evitar revisões sem objetivo claro
- **Priorização**: definir partes críticas do projeto (backend, frontend, infra, CI/CD)

### 2. Modularidade
- **Separação lógica**: backend, frontend, integração, observabilidade, feature flags, e2e
- **Ciclo completo por módulo**: lint, typecheck, testes, build
- **Isolamento de problemas**: facilita debugging e reduz tempo de feedback

### 3. Ciclo Iterativo de Três Fases

#### Fase 1: Preparação
- Coletar documentação e configurações (.env.local)
- Revisar scripts de build e logs existentes
- Definir métricas e critérios de aceite específicos

#### Fase 2: Avaliação
- Executar ferramentas de qualidade (ruff, black, mypy, eslint, prettier, tsc)
- Rodar testes unitários, integração e fuzzing (Schemathesis)
- Construir e validar Storybook
- Identificar falhas e pontos de baixa cobertura

#### Fase 3: Resultados
- Consolidar recomendações e correções prioritárias
- Registrar ações necessárias com commits semânticos
- Abrir issues/PRs com escopo bem definido

### 4. Revisão Contínua
- **Quality Gates no CI**: cobertura mínima, ausência de bugs/vulnerabilidades
- **Documentação de lições aprendidas**
- **Atualização de checklists** para futuros ciclos

---

## Ciclo A  Configuração e Ambiente

### Objetivo
Garantir que variáveis de ambiente e dependências estejam corretas e que a aplicação suba localmente.

### Fase 1: Preparação
- [ ] Verificar arquivos .env.example e .env.local
- [ ] Listar todas as variáveis necessárias
- [ ] Documentar URLs e portas esperadas

### Fase 2: Avaliação

#### Verificar Variáveis de Ambiente
```bash
# Frontend
VITE_API_URL=http://localhost:8000
VITE_UNLEASH_PROXY_URL=
VITE_SENTRY_DSN=

# Backend
API_BASE=http://localhost:8000
PORT=8000
FLAG_USE_V2_KPIS=false
```

#### Testar Aplicação Local
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Testar endpoint diretamente
curl http://localhost:8000/v1/kpis
```

#### Verificar State Management React
- [ ] Validar hooks de dados (useKPIs, useCharts)
- [ ] Verificar atualização assíncrona de estado
- [ ] Testar useEffect para reação a mudanças

#### Corrigir CORS
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Fase 3: Resultados

#### Critérios de Aceite
- [ ] API responde com status 200 e dados válidos
- [ ] Frontend exibe dados ao consumir hooks/serviços
- [ ] Nenhuma variável de ambiente ausente
- [ ] Logs claros sem erros de CORS ou fetch

#### Ações de Correção
- [ ] Criar/atualizar .env.local com todas as variáveis
- [ ] Corrigir baseURL em frontend/src/api/http.ts
- [ ] Ajustar middleware CORS no backend
- [ ] Validar state management nos componentes React

---

## Ciclo B  Backend

### Objetivo
Validar e corrigir a implementação do backend, garantindo qualidade de código e cobertura de testes.

### Fase 1: Preparação
- [ ] Revisar estrutura do projeto backend
- [ ] Verificar configuração de testes (pytest.ini, conftest.py)
- [ ] Listar endpoints e contratos da API

### Fase 2: Avaliação

#### Executar Testes e Qualidade
```bash
cd backend

# Formatação e linting
ruff format .
ruff check .
black .

# Type checking
mypy .

# Testes unitários
pytest tests/ -v --cov=app --cov-report=html

# Fuzzing API
./run_schemathesis.sh
```

#### Validar Integração com Scripts
- [ ] Verificar run_schemathesis.sh aponta para openapi.json correto
- [ ] Testar geração automática de documentação
- [ ] Validar schemas Pydantic

#### Verificar Lógica de KPIs
```python
# Exemplo de teste para endpoint vazio
def test_kpis_empty_response():
    response = client.get("/v1/kpis")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Fase 3: Resultados

#### Critérios de Aceite
- [ ] Todos os testes de backend verdes
- [ ] Fuzzing sem falhas críticas
- [ ] Cobertura mínima >80%
- [ ] Logs estruturados e informativos
- [ ] Documentação OpenAPI atualizada

#### Melhorias Recomendadas
- [ ] Refatorar em services com camadas separadas
- [ ] Implementar schemas Pydantic para validação
- [ ] Adicionar logs estruturados
- [ ] Criar mocks para testes isolados

---

## Ciclo C  Frontend

### Objetivo
Garantir qualidade do código frontend, integração com API e experiência do usuário.

### Fase 1: Preparação
- [ ] Revisar estrutura de componentes
- [ ] Verificar configuração de testes (vitest.config.ts)
- [ ] Listar hooks e adaptadores de dados

### Fase 2: Avaliação

#### Gerar Cliente API
```bash
cd frontend

# Gerar cliente com orval
npm run gen:api

# Verificar qualidade
npm run lint
npm run typecheck
npm run test
npm run test:coverage
```

#### Validar Adaptadores de Dados
```typescript
// Exemplo de teste para adaptador
import { kpiAdapter } from "../adapters/kpiAdapter";

describe("KPI Adapter", () => {
  it("should transform API response correctly", () => {
    const apiResponse = { /* mock data */ };
    const result = kpiAdapter(apiResponse);
    expect(result).toMatchSchema(KPISchema);
  });
});
```

#### Testar Componentes e Hooks
- [ ] Validar hooks de dados (useKPIs, useCharts)
- [ ] Testar componentes com React Testing Library
- [ ] Verificar acessibilidade com axe-core
- [ ] Validar responsividade

#### Construir Storybook
```bash
npm run storybook
npm run build-storybook
```

### Fase 3: Resultados

#### Critérios de Aceite
- [ ] Todos os testes frontend verdes
- [ ] TypeScript sem erros
- [ ] Cobertura mínima >80%
- [ ] Storybook funcional
- [ ] Interface renderiza dados reais
- [ ] Acessibilidade validada

#### Melhorias Recomendadas
- [ ] Implementar error boundaries
- [ ] Adicionar loading states
- [ ] Otimizar re-renders com React.memo
- [ ] Implementar testes E2E com Playwright

---

## Diretrizes para Prompts Futuros

### 1. Checagem de Estado Visual
- **Obrigatório**: validar manualmente que o frontend renderiza dados reais
- **Sub-etapa**: "Verificação de interface" antes de prosseguir
- **Critério**: dados visíveis e funcionais na UI

### 2. Tratamento de Conflitos
- **No prompt P1**: especificar preferência pelo código atual
- **Validação rápida**: rodar aplicação após merges
- **Rollback**: reverter se algo quebrar

### 3. Ambiente Saneado
- **Início de cada prompt**: criar/atualizar .env.local
- **Nunca editar**: .env de produção
- **Validar**: todas as variáveis necessárias

### 4. Feedback Rápido
- **Para cada comando**: fornecer dicas de correção
- **Lembrete**: setState é assíncrono
- **Callbacks**: usar para verificar atualizações de estado

### 5. Documentação e Métricas
- **Ao finalizar**: atualizar README com mudanças
- **Registrar**: métricas de cobertura e qualidade
- **Manter**: changelog atualizado

---

## Quality Gates no CI

### Backend Quality Gates
```yaml
# .github/workflows/ci.yml
backend-quality:
  runs-on: ubuntu-latest
  steps:
    - name: Code Quality
      run: |
        ruff check . --exit-non-zero-on-fix
        mypy .
    
    - name: Tests
      run: |
        pytest --cov=app --cov-fail-under=80
    
    - name: Security
      run: |
        bandit -r app/
```

### Frontend Quality Gates
```yaml
frontend-quality:
  runs-on: ubuntu-latest
  steps:
    - name: Code Quality
      run: |
        npm run lint -- --max-warnings 0
        npm run typecheck
    
    - name: Tests
      run: |
        npm run test:coverage -- --coverage.threshold.global.lines=80
    
    - name: Build
      run: |
        npm run build
```

---

## Checklist de Execução

### Antes de Cada Ciclo
- [ ] Definir problema específico a resolver
- [ ] Escolher módulo/componente alvo
- [ ] Preparar ambiente (.env.local atualizado)
- [ ] Definir critérios de aceite mensuráveis

### Durante o Ciclo
- [ ] Executar fase de preparação completa
- [ ] Rodar todas as ferramentas de avaliação
- [ ] Documentar problemas encontrados
- [ ] Priorizar correções por impacto

### Após o Ciclo
- [ ] Validar critérios de aceite
- [ ] Testar aplicação end-to-end
- [ ] Atualizar documentação
- [ ] Registrar lições aprendidas

---

## Métricas de Sucesso

### Quantitativas
- **Cobertura de código**: >80% (backend e frontend)
- **Tempo de build**: <5 minutos
- **Testes passando**: 100%
- **Vulnerabilidades**: 0 críticas/altas

### Qualitativas
- **Interface funcional**: dados renderizados corretamente
- **Experiência do desenvolvedor**: setup rápido e claro
- **Manutenibilidade**: código limpo e bem documentado
- **Confiabilidade**: CI/CD estável

---

## Próximos Passos

1. **Implementar Quality Gates**: adicionar verificações automáticas no CI
2. **Configurar Ambiente de Preview**: para testes E2E reais
3. **Automatizar Checklist**: criar scripts para validação automática
4. **Monitoramento Contínuo**: métricas de qualidade em dashboard
5. **Treinamento da Equipe**: workshops sobre a metodologia

---

*Documento criado em: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*
*Versão: 1.0*
