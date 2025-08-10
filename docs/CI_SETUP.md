# CI/CD Setup Guide

Este guia explica como configurar todas as variáveis de ambiente e tokens necessários para o pipeline de CI/CD funcionar completamente.

##  Variáveis de Ambiente Obrigatórias

### GitHub Secrets

Configure as seguintes secrets no GitHub (Settings  Secrets and variables  Actions):

#### SonarQube
```bash
SONAR_TOKEN=your_sonar_token_here
SONAR_HOST_URL=https://sonarcloud.io  # ou sua instância SonarQube
```

#### Chromatic (Visual Regression)
```bash
CHROMATIC_PROJECT_TOKEN=your_chromatic_project_token_here
```

#### GLPI API (para testes de integração)
```bash
GLPI_API_URL=https://your-glpi-instance.com/apirest.php
GLPI_APP_TOKEN=your_glpi_app_token
GLPI_USER_TOKEN=your_glpi_user_token
```

#### Sentry (opcional)
```bash
SENTRY_AUTH_TOKEN=your_sentry_auth_token
SENTRY_ORG=your_sentry_org
SENTRY_PROJECT=your_sentry_project
```

##  Como Obter os Tokens

### 1. CHROMATIC_PROJECT_TOKEN

1. **Acesse o Chromatic**: https://www.chromatic.com/
2. **Faça login** com sua conta GitHub
3. **Crie um novo projeto**:
   - Clique em "Add project"
   - Conecte seu repositório GitHub
   - Selecione o repositório `glpi_dashboard`
4. **Obtenha o token**:
   - Após criar o projeto, vá para "Manage"  "Configure"
   - Copie o `CHROMATIC_PROJECT_TOKEN`
   - Adicione como secret no GitHub

### 2. SONAR_TOKEN

#### Para SonarCloud (Recomendado)
1. **Acesse**: https://sonarcloud.io/
2. **Faça login** com GitHub
3. **Importe o projeto**:
   - Clique em "+"  "Analyze new project"
   - Selecione seu repositório
4. **Gere o token**:
   - Vá para "My Account"  "Security"
   - Clique em "Generate Tokens"
   - Nome: `glpi_dashboard_ci`
   - Copie o token gerado

#### Para SonarQube Self-Hosted
1. **Acesse sua instância SonarQube**
2. **Vá para**: Administration  Security  Users
3. **Gere token** para o usuário de CI
4. **Configure** `SONAR_HOST_URL` com sua URL

### 3. GLPI Tokens

1. **Acesse seu GLPI** como administrador
2. **Vá para**: Setup  General  API
3. **Ative a API REST** se não estiver ativa
4. **Crie App Token**:
   - Setup  General  API  API clients
   - Adicione novo cliente com nome `ci_tests`
5. **Crie User Token**:
   - Administration  Users  [seu usuário]
   - Aba "Remote access keys"
   - Gere nova chave

### 4. Sentry Tokens (Opcional)

1. **Acesse**: https://sentry.io/
2. **Vá para**: Settings  Account  API  Auth Tokens
3. **Crie token** com escopo `project:releases`
4. **Obtenha org/project**:
   - URL do projeto: `https://sentry.io/organizations/{org}/projects/{project}/`

##  Configuração Local

### Arquivo `.env.local` (para desenvolvimento)

```bash
# Frontend
VITE_GLPI_API_URL=http://localhost:8000
VITE_UNLEASH_PROXY_URL=http://localhost:4242/proxy
VITE_UNLEASH_PROXY_CLIENT_KEY=your_unleash_key
VITE_UNLEASH_APP_NAME=glpi_dashboard_dev

# Feature Flags (fallback local)
VITE_FLAG_USE_V2_KPIS=false

# Backend
GLPI_API_URL=https://your-glpi-instance.com/apirest.php
GLPI_APP_TOKEN=your_dev_app_token
GLPI_USER_TOKEN=your_dev_user_token
REDIS_URL=redis://localhost:6379

# Sentry (opcional)
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=development
```

##  Verificação da Configuração

### 1. Teste Local

```bash
# Backend
cd backend
python -m pytest tests/ -v
ruff check .
mypy .
bandit -r .
safety check

# Frontend
cd frontend
npm run lint
npm run type-check
npm test
npm run build
npm run storybook:build
npm run check:drift
```

### 2. Teste CI

1. **Faça um commit** pequeno
2. **Abra um PR** para testar o pipeline
3. **Verifique** se todos os jobs passam:
   -  Frontend: lint, types, tests, storybook
   -  Backend: lint, types, tests, security
   -  Integration: API tests
   -  SonarQube: quality gate
   -  Chromatic: visual regression (se configurado)

##  Quality Gates

### Critérios de Bloqueio

O pipeline **bloqueia** o merge se:

-  **Lint** falhar (frontend ou backend)
-  **Type check** falhar
-  **Testes unitários** falharem
-  **Cobertura** abaixo do limiar (80%)
-  **SonarQube** reprovar (bugs, vulnerabilidades, code smells)
-  **Security scan** encontrar vulnerabilidades críticas
-  **API fuzzing** encontrar erros críticos
-  **Testes de integração** falharem
-  **Build** falhar (frontend ou backend)
-  **Orval drift** detectado (API mudou sem atualizar cliente)

### Aprovação Manual Necessária

-  **Visual regression**: Mudanças visuais no Chromatic
-  **Code review**: Pelo menos 1 aprovação de reviewer

##  Monitoramento

### Dashboards

- **SonarQube**: Qualidade do código, cobertura, vulnerabilidades
- **Chromatic**: Regressão visual, componentes
- **GitHub Actions**: Status do pipeline, tempo de execução
- **Sentry**: Erros em produção, performance

### Métricas Importantes

- **Cobertura de testes**: > 80% (global), > 85% (components/services), > 90% (hooks)
- **Quality Gate**: A (SonarQube)
- **Vulnerabilidades**: 0 críticas, < 5 altas
- **Performance**: Build < 5min, testes < 2min
- **Visual regression**: 0 mudanças não aprovadas

##  Troubleshooting

### Problemas Comuns

1. **SonarQube falha**:
   - Verifique se `SONAR_TOKEN` está correto
   - Confirme se projeto existe no SonarCloud

2. **Chromatic falha**:
   - Verifique se `CHROMATIC_PROJECT_TOKEN` está configurado
   - Confirme se Storybook build está funcionando

3. **Testes de integração falham**:
   - Verifique tokens GLPI
   - Confirme se API está acessível

4. **Orval drift detectado**:
   ```bash
   cd frontend
   npm run orval:generate
   git add .
   git commit -m "fix: update API client after schema changes"
   ```

### Logs Úteis

```bash
# Ver logs do CI
gh run list
gh run view [run-id]

# Logs locais detalhados
npm run test -- --verbose
pytest -v --tb=long
```

##  Suporte

Para problemas com a configuração:

1. **Verifique** este guia primeiro
2. **Consulte** os logs do CI
3. **Abra issue** com:
   - Descrição do problema
   - Logs relevantes
   - Passos para reproduzir

---

**Última atualização**: $(Get-Date -Format "yyyy-MM-dd")
**Versão**: 1.0.0
