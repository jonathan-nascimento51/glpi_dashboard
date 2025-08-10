# GLPI Dashboard

Aplicação completa para dashboard de métricas do GLPI, com backend Flask e frontend React.

## Estrutura do Projeto

```
.
├── backend/                # Backend Flask
│   ├── api/               # Endpoints da API
│   │   ├── __init__.py    # Inicializador do módulo API
│   │   └── routes.py      # Rotas da API
│   ├── config/            # Configurações
│   │   ├── __init__.py    # Inicializador do módulo de configuração
│   │   └── settings.py    # Configurações centralizadas
│   ├── schemas/           # Schemas de validação
│   │   ├── __init__.py    # Inicializador do módulo de schemas
│   │   └── dashboard.py   # Schemas do dashboard
│   ├── services/          # Serviços de integração
│   │   ├── __init__.py    # Inicializador do módulo de serviços
│   │   ├── api_service.py # Serviço para APIs externas
│   │   └── glpi_service.py # Serviço para integração com GLPI
│   ├── utils/             # Utilitários
│   │   ├── __init__.py    # Inicializador do módulo de utilitários
│   │   ├── performance.py # Monitoramento de performance
│   │   └── response_formatter.py # Formatação de respostas
│   └── __init__.py        # Inicializador do pacote backend
├── frontend/              # Frontend React + TypeScript
│   ├── src/               # Código fonte do frontend
│   │   ├── components/    # Componentes React
│   │   ├── hooks/         # Hooks customizados
│   │   ├── services/      # Serviços do frontend
│   │   ├── types/         # Definições de tipos TypeScript
│   │   └── utils/         # Utilitários do frontend
│   ├── package.json       # Dependências Node.js
│   └── vite.config.ts     # Configuração do Vite
├── docs/                  # Documentação do projeto
│   ├── AUDITORIA_COMPLETA_RESULTADOS.md # Resultados da auditoria
│   └── GUIA_IMPLEMENTACAO_FILTROS_DATA_GLPI.md # Guia de filtros
├── scripts/               # Scripts auxiliares
│   ├── debug/             # Scripts de debug
│   ├── tests/             # Scripts e arquivos de teste
│   ├── validation/        # Scripts de validação
│   └── README.md          # Documentação dos scripts
├── app.py                 # Ponto de entrada do backend
├── pyproject.toml         # Configuração e dependências Python
├── .env.example           # Exemplo de variáveis de ambiente
└── README.md              # Este arquivo
```

## Configuração

As configurações do projeto estão centralizadas no arquivo `backend/config/settings.py`. As configurações podem ser sobrescritas através de variáveis de ambiente.

### Arquivo .env

Para facilitar a configuração, você pode criar um arquivo `.env` na raiz do projeto com suas variáveis de ambiente. Use o arquivo `.env.example` como modelo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações específicas.

### Variáveis de Ambiente

- `FLASK_ENV`: Ambiente de execução (`dev`, `prod`, `test`). Padrão: `dev`
- `SECRET_KEY`: Chave secreta para Flask. Padrão: `dev-secret-key-change-in-production`
- `FLASK_DEBUG`: Modo debug (`true`, `false`). Padrão: `false`
- `PORT`: Porta do servidor. Padrão: `5000`

## Scripts Auxiliares

O projeto inclui diversos scripts organizados na pasta `scripts/` para debug, testes e validação.

### Execução Rápida

Use o script `run_scripts.py` para executar facilmente qualquer script auxiliar:

```bash
# Listar todos os scripts disponíveis
python run_scripts.py

# Executar scripts de debug
python run_scripts.py debug metrics
python run_scripts.py debug trends

# Executar scripts de validação
python run_scripts.py validation frontend_trends
python run_scripts.py validation trends_math

# Executar scripts de teste
python run_scripts.py tests trends
```

### Execução Manual

Você também pode executar os scripts diretamente:

```bash
# Scripts de debug
python scripts/debug/debug_metrics.py
python scripts/debug/debug_trends.py

# Scripts de validação
python scripts/validation/validate_frontend_trends.py
python scripts/validation/validate_trends_math.py

# Scripts de teste
python scripts/tests/test_trends.py
```

Para mais detalhes sobre os scripts, consulte `scripts/README.md`.
- `HOST`: Host do servidor. Padrão: `0.0.0.0`
- `GLPI_URL`: URL da API do GLPI. Padrão: `http://10.73.0.79/glpi/apirest.php`
- `GLPI_USER_TOKEN`: Token de usuário do GLPI.
- `GLPI_APP_TOKEN`: Token de aplicação do GLPI.
- `LOG_LEVEL`: Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Padrão: `INFO`

## Instalação e Execução

### Pré-requisitos

- Python 3.11+
- Node.js 16+
- npm ou yarn

### 1. Configuração do Backend (Flask)

```bash
# Criar e ativar ambiente virtual
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install flask flask-cors flask-caching flask-sqlalchemy gunicorn psycopg2-binary python-dotenv requests email-validator
```

### 2. Configuração das Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `.env` com suas configurações específicas do GLPI.

### 3. Executar o Backend

```bash
# Com o ambiente virtual ativado
python app.py
```

O backend será executado em `http://localhost:5000`

### 4. Configurar e Executar o Frontend

Em um novo terminal:

```bash
# Navegar para a pasta frontend
cd frontend

# Instalar dependências
npm install

# Executar servidor de desenvolvimento
npm run dev
```

O frontend será executado em `http://localhost:3000` (ou próxima porta disponível)

### 5. Acessar a Aplicação

- **Frontend (Interface)**: `http://localhost:3000`
- **Backend (API)**: `http://localhost:5000`

## Feature Flags

O projeto utiliza feature flags para permitir deploys seguros e migração gradual de funcionalidades.

### Sistema de Flags

- **Backend**: Utiliza Unleash com fallback para variáveis de ambiente
- **Frontend**: Integração com Unleash via `@unleash/proxy-client-js`

### Configuração

#### Backend

As flags são configuradas em `backend/app/flags.py` e podem ser controladas via:

1. **Unleash** (produção): Configure as variáveis de ambiente do Unleash
2. **Fallback** (desenvolvimento): Use variáveis de ambiente diretas

```bash
# Exemplo: ativar flag v2 de KPIs localmente
export FLAG_USE_V2_KPIS=true
```

#### Frontend

Configure as variáveis de ambiente no arquivo `.env.local`:

```bash
# Configuração do Unleash (quando disponível)
VITE_UNLEASH_PROXY_URL=
VITE_UNLEASH_PROXY_CLIENT_KEY=
```

### Flags Disponíveis

#### `use_v2_kpis`

- **Descrição**: Migração dos KPIs da API v1 para v2
- **Comportamento**: 
  - `false` (padrão): Usa endpoint `/v1/kpis`
  - `true`: Usa endpoint `/v2/kpis`
- **Teste local**: 
  ```bash
  # Windows PowerShell
  $env:FLAG_USE_V2_KPIS="true"; npm run dev
  
  # Linux/Mac
  export FLAG_USE_V2_KPIS=true && npm run dev
  ```

### Como Funciona

1. O componente `KpiContainer` verifica a flag `use_v2_kpis`
2. O hook `useKpisRaw` alterna automaticamente entre `/v1/kpis` e `/v2/kpis`
3. A mudança é transparente para o usuário final
4. Permite rollback instantâneo em caso de problemas

## Observabilidade

O projeto inclui integração com Sentry para monitoramento de erros e OpenTelemetry para observabilidade, ativados condicionalmente via variáveis de ambiente.

### Configuração

#### Backend

As ferramentas de observabilidade são inicializadas apenas se as variáveis de ambiente estiverem definidas:

- **Sentry**: Requer `SENTRY_DSN`
- **OpenTelemetry**: Requer `OTEL_EXPORTER_OTLP_ENDPOINT`

```bash
# Exemplo de configuração no .env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
RELEASE=1.0.0
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1

# OpenTelemetry
OTEL_SERVICE_NAME=glpi-dashboard-backend
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-otel-endpoint
```

#### Frontend

O Sentry é inicializado apenas se `VITE_SENTRY_DSN` estiver definido:

```bash
# Exemplo de configuração no .env.local
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
VITE_ENVIRONMENT=production
VITE_RELEASE=1.0.0
VITE_SENTRY_TRACES_SAMPLE_RATE=0.1
VITE_SENTRY_REPLAYS_SESSION_SAMPLE_RATE=0.1
VITE_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE=1.0
```

### Sourcemaps

Para melhor debugging em produção, configure sourcemaps no build:

```bash
# Frontend - gerar sourcemaps
npm run build -- --sourcemap

# Upload automático via GitHub Actions (opcional)
# Descomente a seção "Create Sentry release" no arquivo .github/workflows/ci.yml
```

### Critérios

- **Sem DSN**: Nenhum tráfego de eventos é enviado
- **Com DSN**: Eventos de erro e performance são capturados e enviados
- **Desenvolvimento**: Observabilidade desabilitada por padrão para não poluir o ambiente

## Endpoints da API

### Métricas

```
GET /api/metrics
```

Retorna as métricas do dashboard do GLPI.

### KPIs

```
GET /v1/kpis
GET /v2/kpis  # Disponível quando flag use_v2_kpis está ativa
```

Retorna os indicadores-chave de performance.

### Status

```
GET /api/status
```

Retorna o status do sistema e da conexão com o GLPI.
##  Metodologia de Revisão em Ciclos

Este projeto implementa uma metodologia estruturada de revisão baseada em ciclos iterativos de três fases, focando na modularidade e melhoria contínua.

###  Ciclos de Revisão

#### Ciclo A - Configuração e Ambiente
- **Objetivo**: Garantir que variáveis de ambiente e dependências estejam corretas
- **Foco**: .env.local, CORS, state management React
- **Critérios**: API responde, frontend exibe dados, sem variáveis ausentes

#### Ciclo B - Backend
- **Objetivo**: Validar implementação do backend e qualidade de código
- **Foco**: Testes, linting (ruff), type checking (mypy), segurança (bandit)
- **Critérios**: Cobertura >80%, todos os testes verdes, sem vulnerabilidades

#### Ciclo C - Frontend
- **Objetivo**: Garantir qualidade do frontend e integração com API
- **Foco**: ESLint, Prettier, TypeScript, testes (Vitest), build
- **Critérios**: Zero warnings, cobertura >80%, build funcional

###  Quality Gates

O projeto implementa Quality Gates automáticos no CI/CD que impedem merge de código que não atenda aos critérios de qualidade:

#### Backend Quality Gates
-  Code Quality (Ruff)
-  Type Checking (MyPy)
-  Security Scan (Bandit)
-  Dependency Security (Safety)
-  Coverage >80%

#### Frontend Quality Gates
-  Linting (ESLint - zero warnings)
-  Code Formatting (Prettier)
-  Type Checking (TypeScript)
-  Coverage >80%
-  Build Verification
-  Bundle Size Check (<5MB)

#### Integration Quality Gates
-  API Schema Validation
-  Frontend-Backend Integration
-  API Drift Check
-  Security Aggregation

###  Validação Local

Antes de fazer push, execute a validação local para garantir que seu código passará pelos Quality Gates:

#### Windows (PowerShell)
```powershell
# Validação completa
.\scripts\validate-quality-gates.ps1

# Pular validações específicas
.\scripts\validate-quality-gates.ps1 -SkipBackend
.\scripts\validate-quality-gates.ps1 -SkipFrontend
```

#### Linux/macOS (Bash)
```bash
# Validação completa
./scripts/validate-quality-gates.sh

# Pular validações específicas
./scripts/validate-quality-gates.sh --skip-backend
./scripts/validate-quality-gates.sh --skip-frontend
./scripts/validate-quality-gates.sh --skip-integration
```

###  Documentação da Metodologia

- **[Metodologia Completa](docs/METODOLOGIA_REVISAO_CICLOS.md)**: Guia detalhado dos ciclos de revisão
- **[Quality Gates CI](docs/QUALITY_GATES_CI.md)**: Configuração dos Quality Gates para CI/CD
- **[E2E Coverage Guide](docs/E2E_COVERAGE_GUIDE.md)**: Guia de testes E2E e cobertura

###  Diretrizes para Prompts Futuros

1. **Checagem Visual**: Sempre validar que o frontend renderiza dados reais
2. **Ambiente Saneado**: Verificar .env.local antes de cada ciclo
3. **Feedback Rápido**: Corrigir erros comuns (setState assíncrono)
4. **Documentação**: Atualizar README após mudanças significativas

###  Métricas de Sucesso

#### Quantitativas
- Cobertura de código: >80% (backend e frontend)
- Tempo de build: <5 minutos
- Testes passando: 100%
- Vulnerabilidades: 0 críticas/altas

#### Qualitativas
- Interface funcional com dados reais
- Setup rápido e claro
- Código limpo e bem documentado
- CI/CD estável


##  Estrutura do Projeto

Este projeto segue uma estrutura organizada e padronizada. Para detalhes completos sobre a organiza��o de arquivos e diretrizes, consulte:

 **[Guia de Estrutura do Projeto](docs/ESTRUTURA_PROJETO.md)**

### Estrutura Principal
```
 backend/              # API Python/FastAPI
?? frontend/             # Interface React/TypeScript  
?? scripts/              # Scripts de automa��o
    analysis/        # An�lise e valida��o
    deployment/      # Deploy e CI/CD
�   +-- validation/      # Quality Gates
?? docs/                 # Documenta��o
?? config/               # Configura��es
?? tools/                # Ferramentas auxiliares
?? monitoring/           # Observabilidade
```

### Scripts Principais
- **Valida��o Local**: `scripts/validate-quality-gates.ps1`
- **Ambiente Preview**: `scripts/start-preview.ps1`
- **Monitoramento**: `scripts/monitor-quality.ps1`
- **Dashboard**: `docs/quality-dashboard.html`
