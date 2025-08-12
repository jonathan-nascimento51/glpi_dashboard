# GLPI Dashboard

AplicaÃ§Ã£o completa para dashboard de mÃ©tricas do GLPI, com backend Flask e frontend React.

## Estrutura do Projeto

```
.
â”œâ”€â”€ backend/                # Backend Flask
â”‚   â”œâ”€â”€ api/               # Endpoints da API
â”‚   â”‚   â”œâ”€â”€ __init__.py    # Inicializador do mÃ³dulo API
â”‚   â”‚   â””â”€â”€ routes.py      # Rotas da API
â”‚   â”œâ”€â”€ config/            # ConfiguraÃ§Ãµes
â”‚   â”‚   â”œâ”€â”€ __init__.py    # Inicializador do mÃ³dulo de configuraÃ§Ã£o
â”‚   â”‚   â””â”€â”€ settings.py    # ConfiguraÃ§Ãµes centralizadas
â”‚   â”œâ”€â”€ schemas/           # Schemas de validaÃ§Ã£o
â”‚   â”‚   â”œâ”€â”€ __init__.py    # Inicializador do mÃ³dulo de schemas
â”‚   â”‚   â””â”€â”€ dashboard.py   # Schemas do dashboard
â”‚   â”œâ”€â”€ services/          # ServiÃ§os de integraÃ§Ã£o
â”‚   â”‚   â”œâ”€â”€ __init__.py    # Inicializador do mÃ³dulo de serviÃ§os
â”‚   â”‚   â”œâ”€â”€ api_service.py # ServiÃ§o para APIs externas
â”‚   â”‚   â””â”€â”€ glpi_service.py # ServiÃ§o para integraÃ§Ã£o com GLPI
â”‚   â”œâ”€â”€ utils/             # UtilitÃ¡rios
â”‚   â”‚   â”œâ”€â”€ __init__.py    # Inicializador do mÃ³dulo de utilitÃ¡rios
â”‚   â”‚   â”œâ”€â”€ performance.py # Monitoramento de performance
â”‚   â”‚   â””â”€â”€ response_formatter.py # FormataÃ§Ã£o de respostas
â”‚   â””â”€â”€ __init__.py        # Inicializador do pacote backend
â”œâ”€â”€ frontend/              # Frontend React + TypeScript
â”‚   â”œâ”€â”€ src/               # CÃ³digo fonte do frontend
â”‚   â”‚   â”œâ”€â”€ components/    # Componentes React
â”‚   â”‚   â”œâ”€â”€ hooks/         # Hooks customizados
â”‚   â”‚   â”œâ”€â”€ services/      # ServiÃ§os do frontend
â”‚   â”‚   â”œâ”€â”€ types/         # DefiniÃ§Ãµes de tipos TypeScript
â”‚   â”‚   â””â”€â”€ utils/         # UtilitÃ¡rios do frontend
â”‚   â”œâ”€â”€ package.json       # DependÃªncias Node.js
â”‚   â””â”€â”€ vite.config.ts     # ConfiguraÃ§Ã£o do Vite
â”œâ”€â”€ docs/                  # DocumentaÃ§Ã£o do projeto
â”‚   â”œâ”€â”€ AUDITORIA_COMPLETA_RESULTADOS.md # Resultados da auditoria
â”‚   â””â”€â”€ GUIA_IMPLEMENTACAO_FILTROS_DATA_GLPI.md # Guia de filtros
â”œâ”€â”€ scripts/               # Scripts auxiliares
â”‚   â”œâ”€â”€ debug/             # Scripts de debug
â”‚   â”œâ”€â”€ tests/             # Scripts e arquivos de teste
â”‚   â”œâ”€â”€ validation/        # Scripts de validaÃ§Ã£o
â”‚   â””â”€â”€ README.md          # DocumentaÃ§Ã£o dos scripts
â”œâ”€â”€ app.py                 # Ponto de entrada do backend
â”œâ”€â”€ pyproject.toml         # ConfiguraÃ§Ã£o e dependÃªncias Python
â”œâ”€â”€ .env.example           # Exemplo de variÃ¡veis de ambiente
â””â”€â”€ README.md              # Este arquivo
```

## ConfiguraÃ§Ã£o

As configuraÃ§Ãµes do projeto estÃ£o centralizadas no arquivo `backend/config/settings.py`. As configuraÃ§Ãµes podem ser sobrescritas atravÃ©s de variÃ¡veis de ambiente.

### Arquivo .env

Para facilitar a configuraÃ§Ã£o, vocÃª pode criar um arquivo `.env` na raiz do projeto com suas variÃ¡veis de ambiente. Use o arquivo `.env.example` como modelo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configuraÃ§Ãµes especÃ­ficas.

### VariÃ¡veis de Ambiente

- `FLASK_ENV`: Ambiente de execuÃ§Ã£o (`dev`, `prod`, `test`). PadrÃ£o: `dev`
- `SECRET_KEY`: Chave secreta para Flask. PadrÃ£o: `dev-secret-key-change-in-production`
- `FLASK_DEBUG`: Modo debug (`true`, `false`). PadrÃ£o: `false`
- `PORT`: Porta do servidor. PadrÃ£o: `5000`

## Scripts Auxiliares

O projeto inclui diversos scripts organizados na pasta `scripts/` para debug, testes e validaÃ§Ã£o.

### ExecuÃ§Ã£o RÃ¡pida

Use o script `run_scripts.py` para executar facilmente qualquer script auxiliar:

```bash
# Listar todos os scripts disponÃ­veis
python run_scripts.py

# Executar scripts de debug
python run_scripts.py debug metrics
python run_scripts.py debug trends

# Executar scripts de validaÃ§Ã£o
python run_scripts.py validation frontend_trends
python run_scripts.py validation trends_math

# Executar scripts de teste
python run_scripts.py tests trends
```

### ExecuÃ§Ã£o Manual

VocÃª tambÃ©m pode executar os scripts diretamente:

```bash
# Scripts de debug
python scripts/debug/debug_metrics.py
python scripts/debug/debug_trends.py

# Scripts de validaÃ§Ã£o
python scripts/validation/validate_frontend_trends.py
python scripts/validation/validate_trends_math.py

# Scripts de teste
python scripts/tests/test_trends.py
```

Para mais detalhes sobre os scripts, consulte `scripts/README.md`.
- `HOST`: Host do servidor. PadrÃ£o: `0.0.0.0`
- `GLPI_URL`: URL da API do GLPI. PadrÃ£o: `http://10.73.0.79/glpi/apirest.php`
- `GLPI_USER_TOKEN`: Token de usuÃ¡rio do GLPI.
- `GLPI_APP_TOKEN`: Token de aplicaÃ§Ã£o do GLPI.
- `LOG_LEVEL`: NÃ­vel de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). PadrÃ£o: `INFO`

## InstalaÃ§Ã£o e ExecuÃ§Ã£o

### PrÃ©-requisitos

- Python 3.11+
- Node.js 16+
- npm ou yarn

### 1. ConfiguraÃ§Ã£o do Backend (Flask)

```bash
# Criar e ativar ambiente virtual
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instalar dependÃªncias
pip install flask flask-cors flask-caching flask-sqlalchemy gunicorn psycopg2-binary python-dotenv requests email-validator
```

### 2. ConfiguraÃ§Ã£o das VariÃ¡veis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `.env` com suas configuraÃ§Ãµes especÃ­ficas do GLPI.

### 3. Executar o Backend

```bash
# Com o ambiente virtual ativado
python app.py
```

O backend serÃ¡ executado em `http://localhost:5000`

### 4. Configurar e Executar o Frontend

Em um novo terminal:

```bash
# Navegar para a pasta frontend
cd frontend

# Instalar dependÃªncias
npm install

# Executar servidor de desenvolvimento
npm run dev
```

O frontend serÃ¡ executado em `http://localhost:3000` (ou prÃ³xima porta disponÃ­vel)

### 5. Acessar a AplicaÃ§Ã£o

- **Frontend (Interface)**: `http://localhost:3000`
- **Backend (API)**: `http://localhost:5000`

## Feature Flags

O projeto utiliza feature flags para permitir deploys seguros e migraÃ§Ã£o gradual de funcionalidades.

### Sistema de Flags

- **Backend**: Utiliza Unleash com fallback para variÃ¡veis de ambiente
- **Frontend**: IntegraÃ§Ã£o com Unleash via `@unleash/proxy-client-js`

### ConfiguraÃ§Ã£o

#### Backend

As flags sÃ£o configuradas em `backend/app/flags.py` e podem ser controladas via:

1. **Unleash** (produÃ§Ã£o): Configure as variÃ¡veis de ambiente do Unleash
2. **Fallback** (desenvolvimento): Use variÃ¡veis de ambiente diretas

```bash
# Exemplo: ativar flag v2 de KPIs localmente
export FLAG_USE_V2_KPIS=true
```

#### Frontend

Configure as variÃ¡veis de ambiente no arquivo `.env.local`:

```bash
# ConfiguraÃ§Ã£o do Unleash (quando disponÃ­vel)
VITE_UNLEASH_PROXY_URL=
VITE_UNLEASH_PROXY_CLIENT_KEY=
```

### Flags DisponÃ­veis

#### `use_v2_kpis`

- **DescriÃ§Ã£o**: MigraÃ§Ã£o dos KPIs da API v1 para v2
- **Comportamento**: 
  - `false` (padrÃ£o): Usa endpoint `/v1/kpis`
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
3. A mudanÃ§a Ã© transparente para o usuÃ¡rio final
4. Permite rollback instantÃ¢neo em caso de problemas

## Observabilidade

O projeto inclui integraÃ§Ã£o com Sentry para monitoramento de erros e OpenTelemetry para observabilidade, ativados condicionalmente via variÃ¡veis de ambiente.

### ConfiguraÃ§Ã£o

#### Backend

As ferramentas de observabilidade sÃ£o inicializadas apenas se as variÃ¡veis de ambiente estiverem definidas:

- **Sentry**: Requer `SENTRY_DSN`
- **OpenTelemetry**: Requer `OTEL_EXPORTER_OTLP_ENDPOINT`

```bash
# Exemplo de configuraÃ§Ã£o no .env
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

O Sentry Ã© inicializado apenas se `VITE_SENTRY_DSN` estiver definido:

```bash
# Exemplo de configuraÃ§Ã£o no .env.local
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
VITE_ENVIRONMENT=production
VITE_RELEASE=1.0.0
VITE_SENTRY_TRACES_SAMPLE_RATE=0.1
VITE_SENTRY_REPLAYS_SESSION_SAMPLE_RATE=0.1
VITE_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE=1.0
```

### Sourcemaps

Para melhor debugging em produÃ§Ã£o, configure sourcemaps no build:

```bash
# Frontend - gerar sourcemaps
npm run build -- --sourcemap

# Upload automÃ¡tico via GitHub Actions (opcional)
# Descomente a seÃ§Ã£o "Create Sentry release" no arquivo .github/workflows/ci.yml
```

### CritÃ©rios

- **Sem DSN**: Nenhum trÃ¡fego de eventos Ã© enviado
- **Com DSN**: Eventos de erro e performance sÃ£o capturados e enviados
- **Desenvolvimento**: Observabilidade desabilitada por padrÃ£o para nÃ£o poluir o ambiente

## Endpoints da API

### MÃ©tricas

```
GET /api/metrics
```

Retorna as mÃ©tricas do dashboard do GLPI.

### KPIs

```
GET /v1/kpis
GET /v2/kpis  # DisponÃ­vel quando flag use_v2_kpis estÃ¡ ativa
```

Retorna os indicadores-chave de performance.

### Status

```
GET /api/status
```

Retorna o status do sistema e da conexÃ£o com o GLPI.
##  Metodologia de RevisÃ£o em Ciclos

Este projeto implementa uma metodologia estruturada de revisÃ£o baseada em ciclos iterativos de trÃªs fases, focando na modularidade e melhoria contÃ­nua.

###  Ciclos de RevisÃ£o

#### Ciclo A - ConfiguraÃ§Ã£o e Ambiente
- **Objetivo**: Garantir que variÃ¡veis de ambiente e dependÃªncias estejam corretas
- **Foco**: .env.local, CORS, state management React
- **CritÃ©rios**: API responde, frontend exibe dados, sem variÃ¡veis ausentes

#### Ciclo B - Backend
- **Objetivo**: Validar implementaÃ§Ã£o do backend e qualidade de cÃ³digo
- **Foco**: Testes, linting (ruff), type checking (mypy), seguranÃ§a (bandit)
- **CritÃ©rios**: Cobertura >80%, todos os testes verdes, sem vulnerabilidades

#### Ciclo C - Frontend
- **Objetivo**: Garantir qualidade do frontend e integraÃ§Ã£o com API
- **Foco**: ESLint, Prettier, TypeScript, testes (Vitest), build
- **CritÃ©rios**: Zero warnings, cobertura >80%, build funcional

###  Quality Gates

O projeto implementa Quality Gates automÃ¡ticos no CI/CD que impedem merge de cÃ³digo que nÃ£o atenda aos critÃ©rios de qualidade:

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

###  ValidaÃ§Ã£o Local

Antes de fazer push, execute a validaÃ§Ã£o local para garantir que seu cÃ³digo passarÃ¡ pelos Quality Gates:

#### Windows (PowerShell)
```powershell
# ValidaÃ§Ã£o completa
.\scripts\validate-quality-gates.ps1

# Pular validaÃ§Ãµes especÃ­ficas
.\scripts\validate-quality-gates.ps1 -SkipBackend
.\scripts\validate-quality-gates.ps1 -SkipFrontend
```

#### Linux/macOS (Bash)
```bash
# ValidaÃ§Ã£o completa
./scripts/validate-quality-gates.sh

# Pular validaÃ§Ãµes especÃ­ficas
./scripts/validate-quality-gates.sh --skip-backend
./scripts/validate-quality-gates.sh --skip-frontend
./scripts/validate-quality-gates.sh --skip-integration
```

###  DocumentaÃ§Ã£o da Metodologia

- **[Metodologia Completa](docs/METODOLOGIA_REVISAO_CICLOS.md)**: Guia detalhado dos ciclos de revisÃ£o
- **[Quality Gates CI](docs/QUALITY_GATES_CI.md)**: ConfiguraÃ§Ã£o dos Quality Gates para CI/CD
- **[E2E Coverage Guide](docs/E2E_COVERAGE_GUIDE.md)**: Guia de testes E2E e cobertura

###  Diretrizes para Prompts Futuros

1. **Checagem Visual**: Sempre validar que o frontend renderiza dados reais
2. **Ambiente Saneado**: Verificar .env.local antes de cada ciclo
3. **Feedback RÃ¡pido**: Corrigir erros comuns (setState assÃ­ncrono)
4. **DocumentaÃ§Ã£o**: Atualizar README apÃ³s mudanÃ§as significativas

###  MÃ©tricas de Sucesso

#### Quantitativas
- Cobertura de cÃ³digo: >80% (backend e frontend)
- Tempo de build: <5 minutos
- Testes passando: 100%
- Vulnerabilidades: 0 crÃ­ticas/altas

#### Qualitativas
- Interface funcional com dados reais
- Setup rÃ¡pido e claro
- CÃ³digo limpo e bem documentado
- CI/CD estÃ¡vel


##  Estrutura do Projeto

Este projeto segue uma estrutura organizada e padronizada. Para detalhes completos sobre a organização de arquivos e diretrizes, consulte:

 **[Guia de Estrutura do Projeto](docs/ESTRUTURA_PROJETO.md)**

### Estrutura Principal
```
 backend/              # API Python/FastAPI
?? frontend/             # Interface React/TypeScript  
?? scripts/              # Scripts de automação
    analysis/        # Análise e validação
    deployment/      # Deploy e CI/CD
¦   +-- validation/      # Quality Gates
?? docs/                 # Documentação
?? config/               # Configurações
?? tools/                # Ferramentas auxiliares
?? monitoring/           # Observabilidade
```

#
##  Segurança

Este projeto implementa múltiplas camadas de segurança para proteger contra vulnerabilidades comuns:

### Headers de Segurança
- **X-Frame-Options**: Proteção contra clickjacking
- **Content-Security-Policy**: Prevenção de XSS e injeção de código
- **X-Content-Type-Options**: Prevenção de MIME sniffing
- **Strict-Transport-Security**: Força uso de HTTPS

### Análise Estática (SAST)
- **Bandit**: Análise de segurança para Python
- **Semgrep**: Detecção de padrões inseguros
- **Safety**: Verificação de vulnerabilidades em dependências

### Detecção de Segredos
- **GitLeaks**: Detecção de credenciais em commits
- **TruffleHog**: Verificação de segredos em repositório

### Comandos de Segurança
```bash
# Verificação completa de segurança
make security

# Verificação rápida
make security-quick

# Ferramentas individuais
make security-bandit
make security-safety
make security-gitleaks

# Pre-commit hooks
make pre-commit
```

### Documentação Detalhada
Para informações completas sobre implementações de segurança, consulte:
**[ Documentação de Segurança](SECURITY.md)**
## Scripts Principais
- **Validação Local**: `scripts/validate-quality-gates.ps1`
- **Ambiente Preview**: `scripts/start-preview.ps1`
- **Monitoramento**: `scripts/monitor-quality.ps1`
- **Dashboard**: `docs/quality-dashboard.html`

