# Guia de Testes E2E e Cobertura

## Visão Geral

Este documento descreve a infraestrutura de testes End-to-End (E2E) e cobertura de código implementada no projeto GLPI Dashboard.

## Testes E2E com Playwright

### Estrutura dos Testes

Os testes E2E estão localizados em `frontend/e2e/` e cobrem os seguintes cenários:

#### Testes Principais (`kpi-updates.spec.ts`)
-  Seleção de período e atualização de KPIs
-  Exibição de estado de carregamento
-  Simulação de falha da API (marcado como skip)
-  Verificação de feature flags (marcado como skip)
-  Tratamento de timeout de rede (marcado como skip)
-  Retry de requisições falhadas (marcado como skip)

#### Testes Avançados (`kpi-advanced.spec.ts`)
-  Tratamento de erros de API
-  Comportamento baseado em feature flags
-  Timeout de rede
-  Retry de requisições
-  Validação de acessibilidade
-  Mudanças rápidas de filtros
-  Manutenção de estado durante navegação

### Executando os Testes E2E

```bash
# Instalar dependências do Playwright
cd frontend
npx playwright install

# Executar todos os testes E2E
npm run test:e2e

# Executar testes em modo interativo
npx playwright test --ui

# Executar testes específicos
npx playwright test kpi-updates.spec.ts

# Executar com relatório HTML
npx playwright test --reporter=html
```

### Configuração do Ambiente

Os testes E2E requerem:
1. Servidor backend rodando em `http://localhost:8000`
2. Servidor frontend rodando em `http://localhost:3001`
3. Navegadores instalados (Chromium, Firefox, WebKit)

## Cobertura de Código

### Frontend (Vitest)

#### Configuração
- **Provider**: V8
- **Formatos**: text, json, html, lcov
- **Diretório**: `frontend/coverage`

#### Limiares de Cobertura
- **Global**: 80% (branches, functions, lines, statements)
- **Por arquivo**: 70% (branches, functions, lines, statements)
- **Componentes**: 85%
- **Hooks**: 90%
- **Services**: 85%

#### Executando Cobertura Frontend

```bash
cd frontend

# Executar testes com cobertura
npm run test:coverage

# Visualizar relatório HTML
npm run coverage:open

# Verificar limiares
npm run test:coverage -- --reporter=verbose
```

### Backend (pytest-cov)

#### Configuração
- **Source**: `backend/`
- **Branch coverage**: Habilitado
- **Formato**: term-missing, html, xml, lcov
- **Diretório**: `backend/htmlcov`

#### Limiares de Cobertura
- **Global**: 80%
- **Por arquivo**: 70%

#### Executando Cobertura Backend

```bash
cd backend

# Executar testes com cobertura
pytest --cov=backend --cov-report=html --cov-report=term-missing

# Verificar limiares
pytest --cov=backend --cov-fail-under=80

# Gerar relatório LCOV para SonarQube
pytest --cov=backend --cov-report=lcov
```

## Verificação de Drift da API

### Script check:drift

O script `frontend/scripts/check-api-drift.js` verifica se a API mudou sem atualização do cliente.

#### Funcionamento
1. Faz backup dos arquivos gerados atuais
2. Gera nova versão da API com orval
3. Compara as versões
4. Falha se houver diferenças

#### Executando

```bash
cd frontend

# Verificar drift da API
npm run check:drift

# Gerar nova versão da API
npm run generate:api
```

#### Integração no CI

O script é executado automaticamente no pipeline CI/CD como parte do job `orval-drift-check`.

## Integração com SonarQube

### Configuração

O arquivo `sonar-project.properties` está configurado para:
- Coletar relatórios de cobertura do frontend e backend
- Aplicar exclusões apropriadas
- Definir limiares de qualidade

### Relatórios Esperados
- `frontend/coverage/lcov.info`
- `backend/coverage.xml`
- Relatórios de execução de testes

## Integração no CI/CD

### Jobs Relacionados

1. **frontend-tests**: Executa testes unitários com cobertura
2. **backend-tests**: Executa testes unitários com cobertura
3. **orval-drift-check**: Verifica drift da API
4. **integration-tests**: Executa testes de integração
5. **sonarqube-analysis**: Analisa cobertura e qualidade

### Critérios de Bloqueio

- Cobertura abaixo dos limiares definidos
- Drift da API detectado
- Falhas nos testes E2E (quando habilitados)
- Quality Gate do SonarQube falhando

## Ambiente Preview

### Status Atual

Os testes E2E estão marcados como `skip` até que o ambiente preview esteja disponível.

### Quando Habilitar

1. Ambiente preview configurado
2. URLs de preview disponíveis
3. Dados de teste consistentes
4. Infraestrutura estável

### Configuração Futura

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: process.env.PREVIEW_URL || 'http://localhost:3001',
  },
  projects: [
    {
      name: 'preview',
      use: {
        baseURL: process.env.PREVIEW_URL,
      },
    },
  ],
});
```

## Métricas e Monitoramento

### Métricas Coletadas

- Taxa de cobertura por módulo
- Tempo de execução dos testes
- Taxa de sucesso/falha
- Drift da API detectado

### Dashboards

- SonarQube: Qualidade e cobertura
- CI/CD: Tempo de execução e taxa de sucesso
- Grafana: Métricas de performance dos testes

## Troubleshooting

### Problemas Comuns

1. **Testes E2E falhando**
   - Verificar se os servidores estão rodando
   - Verificar URLs de configuração
   - Verificar dados de teste

2. **Cobertura baixa**
   - Identificar arquivos não cobertos
   - Adicionar testes para funcionalidades críticas
   - Revisar exclusões de cobertura

3. **Drift da API**
   - Revisar mudanças na API
   - Atualizar tipos do cliente
   - Testar compatibilidade

### Logs e Debugging

```bash
# Debug testes E2E
DEBUG=pw:api npx playwright test

# Debug cobertura
npm run test:coverage -- --reporter=verbose

# Debug drift da API
DEBUG=1 npm run check:drift
```

## Próximos Passos

1.  Infraestrutura E2E implementada
2.  Cobertura configurada com limiares
3.  Verificação de drift operante
4.  Ambiente preview para habilitar testes E2E
5.  Testes de regressão visual
6.  Testes de performance
