# Guia de Testes - GLPI Dashboard

Este documento descreve a estrutura completa de testes implementada no projeto GLPI Dashboard, incluindo configurações, tipos de testes e melhores práticas.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura de Testes](#estrutura-de-testes)
- [Frontend](#frontend)
- [Backend](#backend)
- [Configurações](#configurações)
- [Execução de Testes](#execução-de-testes)
- [Cobertura de Código](#cobertura-de-código)
- [CI/CD](#cicd)
- [Melhores Práticas](#melhores-práticas)

## 🎯 Visão Geral

O projeto implementa uma estratégia abrangente de testes que inclui:

- **Testes Unitários**: Testam componentes e funções isoladamente
- **Testes de Integração**: Testam a interação entre diferentes partes do sistema
- **Testes E2E**: Testam fluxos completos da aplicação
- **Testes de Performance**: Avaliam a performance da aplicação
- **Testes de Segurança**: Verificam vulnerabilidades de segurança
- **Testes de Acessibilidade**: Garantem conformidade com padrões de acessibilidade
- **Testes Visuais**: Detectam regressões visuais na interface
- **Testes de Mutação**: Avaliam a qualidade dos testes existentes
- **Testes de Contrato**: Verificam a compatibilidade entre frontend e backend

## 🏗️ Estrutura de Testes

### Frontend (`frontend/src/__tests__/`)

```
__tests__/
├── accessibility/           # Testes de acessibilidade
│   └── accessibility.test.tsx
├── contract/               # Testes de contrato API
│   └── api-contract.test.ts
├── e2e/                   # Testes End-to-End
│   ├── global-setup.ts
│   └── global-teardown.ts
├── integration/           # Testes de integração
│   └── api-integration.test.ts
├── mutation/              # Testes de mutação
│   └── mutation.test.ts
├── snapshot/              # Testes de snapshot
│   └── component-snapshots.test.tsx
├── unit/                  # Testes unitários
│   ├── components.test.tsx
│   ├── hooks.test.tsx
│   └── utils.test.ts
└── visual/                # Testes de regressão visual
    └── visual-regression.test.tsx
```

### Backend (`backend/tests/`)

```
tests/
├── integration/           # Testes de integração
├── load/                  # Testes de carga
│   └── test_load_testing.py
├── performance/           # Testes de performance
│   └── test_api_performance.py
├── security/              # Testes de segurança
│   └── test_security.py
└── unit/                  # Testes unitários
```

## 🎨 Frontend

### Tecnologias Utilizadas

- **Jest**: Framework principal de testes
- **React Testing Library**: Testes de componentes React
- **Playwright**: Testes E2E
- **jest-axe**: Testes de acessibilidade
- **jest-image-snapshot**: Testes de regressão visual
- **MSW (Mock Service Worker)**: Mock de APIs

### Tipos de Testes

#### 1. Testes Unitários

**Localização**: `src/__tests__/unit/`

- **Componentes** (`components.test.tsx`): Testa componentes React isoladamente
- **Hooks** (`hooks.test.tsx`): Testa hooks customizados
- **Utilitários** (`utils.test.ts`): Testa funções auxiliares

#### 2. Testes de Integração

**Localização**: `src/__tests__/integration/`

- **API Integration** (`api-integration.test.ts`): Testa integração com APIs
- Fluxos completos entre serviços
- Sincronização de dados

#### 3. Testes E2E

**Localização**: `src/__tests__/e2e/`

- **Setup Global** (`global-setup.ts`): Configuração do ambiente de teste
- **Teardown Global** (`global-teardown.ts`): Limpeza após testes
- Testes de fluxos completos do usuário

#### 4. Testes de Acessibilidade

**Localização**: `src/__tests__/accessibility/`

- Verificação de violações WCAG
- Navegação por teclado
- Screen readers
- Contraste de cores

#### 5. Testes Visuais

**Localização**: `src/__tests__/visual/`

- Detecção de regressões visuais
- Comparação de snapshots
- Testes responsivos

#### 6. Testes de Mutação

**Localização**: `src/__tests__/mutation/`

- Avaliação da qualidade dos testes
- Detecção de código morto
- Verificação de cobertura efetiva

#### 7. Testes de Contrato

**Localização**: `src/__tests__/contract/`

- Validação de schemas de API
- Compatibilidade frontend/backend
- Verificação de tipos de dados

#### 8. Testes de Snapshot

**Localização**: `src/__tests__/snapshot/`

- Captura de mudanças não intencionais
- Versionamento de componentes
- Detecção de breaking changes

### Configurações Frontend

#### Jest (`jest.config.js`)

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
    '!src/**/*.test.{js,jsx,ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

#### Playwright (`playwright.config.ts`)

- Configuração para múltiplos navegadores
- Testes paralelos
- Captura de screenshots e vídeos
- Relatórios detalhados

## 🔧 Backend

### Tecnologias Utilizadas

- **pytest**: Framework principal de testes
- **pytest-cov**: Cobertura de código
- **pytest-asyncio**: Testes assíncronos
- **pytest-mock**: Mocking
- **pytest-benchmark**: Testes de performance
- **FastAPI TestClient**: Testes de API

### Tipos de Testes

#### 1. Testes Unitários

**Localização**: `tests/unit/`

- Testes de funções isoladas
- Mocking de dependências
- Validação de lógica de negócio

#### 2. Testes de Integração

**Localização**: `tests/integration/`

- Testes de APIs
- Integração com banco de dados
- Fluxos completos

#### 3. Testes de Performance

**Localização**: `tests/performance/`

- **API Performance** (`test_api_performance.py`):
  - Tempo de resposta
  - Uso de memória
  - Performance de queries
  - Cache effectiveness

#### 4. Testes de Carga

**Localização**: `tests/load/`

- **Load Testing** (`test_load_testing.py`):
  - Requisições concorrentes
  - Teste de estresse
  - Detecção de vazamentos de memória
  - Carga sustentada

#### 5. Testes de Segurança

**Localização**: `tests/security/`

- **Security Tests** (`test_security.py`):
  - SQL Injection
  - XSS
  - Autenticação e autorização
  - Rate limiting
  - Validação de entrada

### Configurações Backend

#### pytest (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
addopts = 
    --strict-markers
    --cov=.
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=80
    --junitxml=test-results/junit.xml
markers =
    unit: marca testes unitários
    integration: marca testes de integração
    performance: marca testes de performance
    security: marca testes de segurança
```

#### Coverage (`.coveragerc`)

```ini
[run]
source = .
branch = True
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
show_missing = True
fail_under = 80.0
```

## ▶️ Execução de Testes

### Frontend

```bash
# Todos os testes
npm test

# Testes unitários
npm run test:unit

# Testes de integração
npm run test:integration

# Testes E2E
npm run test:e2e

# Testes com cobertura
npm run test:coverage

# Testes em modo watch
npm run test:watch
```

### Backend

```bash
# Todos os testes
pytest

# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Testes de performance
pytest tests/performance/ -m performance

# Testes de segurança
pytest tests/security/ -m security

# Testes com cobertura
pytest --cov=. --cov-report=html

# Testes paralelos
pytest -n auto
```

## 📊 Cobertura de Código

### Metas de Cobertura

- **Global**: 80% mínimo
- **Componentes**: 85% mínimo
- **Hooks**: 90% mínimo
- **Utilitários**: 95% mínimo
- **APIs**: 85% mínimo

### Relatórios

- **HTML**: Relatórios visuais detalhados
- **XML**: Para integração com ferramentas de CI
- **JSON**: Para análise programática
- **LCOV**: Para integração com IDEs

## 🔄 CI/CD

### GitHub Actions

O projeto inclui workflows automatizados que executam:

1. **Testes Unitários**: Em cada push/PR
2. **Testes de Integração**: Em cada push/PR
3. **Testes E2E**: Em PRs para main
4. **Testes de Performance**: Semanalmente
5. **Testes de Segurança**: Diariamente
6. **Análise de Cobertura**: Em cada push

### Configuração

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 📝 Melhores Práticas

### Geral

1. **Nomenclatura Clara**: Use nomes descritivos para testes
2. **Arrange-Act-Assert**: Estruture testes de forma clara
3. **Isolamento**: Cada teste deve ser independente
4. **Mocking**: Use mocks para dependências externas
5. **Dados de Teste**: Use factories ou fixtures

### Frontend

1. **Testing Library**: Prefira queries por papel/texto
2. **User Events**: Simule interações reais do usuário
3. **Async/Await**: Use para operações assíncronas
4. **Cleanup**: Limpe mocks e timers após cada teste
5. **Snapshots**: Use com moderação e mantenha atualizados

### Backend

1. **Fixtures**: Use para setup/teardown de dados
2. **Parametrização**: Teste múltiplos cenários
3. **Marcadores**: Organize testes por categoria
4. **Async Tests**: Use pytest-asyncio para código assíncrono
5. **Database**: Use transações para isolamento

### Performance

1. **Benchmarks**: Estabeleça baselines de performance
2. **Profiling**: Identifique gargalos
3. **Monitoring**: Monitore métricas em produção
4. **Load Testing**: Teste sob carga realística
5. **Memory**: Monitore vazamentos de memória

### Segurança

1. **Input Validation**: Teste todos os inputs
2. **Authentication**: Teste cenários de auth/authz
3. **Injection**: Teste vulnerabilidades de injeção
4. **Rate Limiting**: Teste limites de taxa
5. **HTTPS**: Teste configurações de segurança

## 🔍 Debugging

### Frontend

```bash
# Debug com breakpoints
npm run test:debug

# Executar teste específico
npm test -- --testNamePattern="Button"

# Modo watch com coverage
npm run test:watch -- --coverage
```

### Backend

```bash
# Debug com pdb
pytest --pdb

# Executar teste específico
pytest tests/unit/test_api.py::test_get_metrics

# Verbose output
pytest -v -s
```

## 📈 Métricas e Relatórios

### Métricas Coletadas

- **Cobertura de Código**: Linhas, branches, funções
- **Performance**: Tempo de resposta, throughput
- **Qualidade**: Complexidade ciclomática, duplicação
- **Segurança**: Vulnerabilidades, compliance
- **Acessibilidade**: Violações WCAG, score

### Ferramentas de Análise

- **SonarQube**: Análise de qualidade de código
- **Codecov**: Análise de cobertura
- **Lighthouse**: Performance e acessibilidade
- **OWASP ZAP**: Análise de segurança
- **Axe**: Análise de acessibilidade

## 🚀 Próximos Passos

1. **Testes de Chaos**: Implementar chaos engineering
2. **Testes de Contrato**: Expandir para mais APIs
3. **Testes de Regressão Visual**: Automatizar comparações
4. **Testes de Performance**: Monitoramento contínuo
5. **Testes de Acessibilidade**: Integração com CI

---

**Nota**: Este guia é um documento vivo e deve ser atualizado conforme o projeto evolui. Para dúvidas ou sugestões, consulte a equipe de desenvolvimento.