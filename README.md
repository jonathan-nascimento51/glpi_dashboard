# GLPI Dashboard

Aplicação completa para dashboard de métricas do GLPI, com backend Flask e frontend React + TypeScript.

## 📋 Funcionalidades

- **Dashboard Interativo**: Visualização em tempo real de métricas do GLPI
- **Ranking de Técnicos**: Classificação por número de chamados resolvidos
- **Monitor de Requisições**: Acompanhamento de performance da API em tempo real
- **Filtros Avançados**: Filtros por período, status e outras categorias
- **Interface Responsiva**: Design moderno e adaptável a diferentes dispositivos
- **Cache Inteligente**: Sistema de cache para otimização de performance
- **Logs Estruturados**: Sistema de monitoramento e observabilidade
- **Sistema de Performance**: Monitoramento completo de performance frontend e backend

## 📊 Sistema de Monitoramento de Performance

O GLPI Dashboard inclui um sistema abrangente de monitoramento de performance que rastreia métricas em tempo real tanto no frontend quanto no backend.

### Funcionalidades do Sistema de Performance

- **Monitoramento de API**: Rastreamento de tempo de resposta e latência
- **Performance de Filtros**: Medição de tempo de aplicação de filtros
- **Métricas de Renderização**: Análise de performance de componentes React
- **Relatórios Automáticos**: Geração de relatórios consolidados
- **Debug Tools**: Ferramentas de debug para desenvolvimento
- **Cache Inteligente**: Sistema de cache com TTL dinâmico

### Hooks de Performance Disponíveis

- `usePerformanceMonitoring`: Hook principal para monitoramento básico
- `useApiPerformance`: Monitoramento específico de chamadas de API
- `useFilterPerformance`: Performance de operações de filtro
- `usePerformanceReports`: Geração e gestão de relatórios
- `usePerformanceDebug`: Ferramentas de debug e análise
- `useRenderTracker`: Rastreamento de renderizações de componentes

### Endpoints de Performance

- `GET /api/performance/metrics`: Métricas atuais do sistema
- `POST /api/performance/cache/clear`: Limpeza de cache
- `GET /api/performance/reports`: Relatórios históricos

### Documentação Detalhada

Para informações completas sobre implementação e uso:

- **[Sistema de Performance](docs/PERFORMANCE_SYSTEM.md)**: Documentação completa do sistema
- **[Guia de Desenvolvimento](docs/PERFORMANCE_DEVELOPMENT_GUIDE.md)**: Guia para desenvolvedores

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **Flask-CORS**: Suporte a CORS
- **Flask-Caching**: Sistema de cache
- **Requests**: Cliente HTTP para integração com GLPI
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

### Frontend
- **React 18**: Biblioteca para interfaces de usuário
- **TypeScript**: Superset tipado do JavaScript
- **Vite**: Build tool e dev server
- **CSS3**: Estilização moderna com Grid e Flexbox
- **Fetch API**: Cliente HTTP nativo

## 🚀 Melhorias Recentes

### Otimizações de Performance
- **Paginação Robusta**: Implementado método `_fetch_all_pages_robust` para melhor tratamento de requisições à API GLPI
- **Redução de Requisições**: Otimizada a busca de dados para reduzir o número de chamadas à API
- **Cache Inteligente**: Melhorado sistema de cache para evitar requisições desnecessárias

### Padronização de Logs
- **Timestamps UTC**: Todos os logs agora utilizam timestamps padronizados em UTC
- **Observabilidade**: Implementado sistema de logs estruturados para melhor monitoramento
- **Rastreabilidade**: Logs detalhados para facilitar debugging e análise de performance

### Limpeza de Código
- **Remoção de Arquivos Obsoletos**: Removidos 63 arquivos de debug e teste temporários
- **Estrutura Limpa**: Eliminados diretórios `__pycache__` e arquivos temporários
- **Código Organizado**: Mantida apenas a estrutura essencial do projeto

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
│   ├── GUIA_IMPLEMENTACAO_FILTROS_DATA_GLPI.md # Guia de filtros
│   ├── PERFORMANCE_SYSTEM.md # Documentação do sistema de performance
│   └── PERFORMANCE_DEVELOPMENT_GUIDE.md # Guia de desenvolvimento de performance
├── scripts/               # Scripts auxiliares
│   ├── debug/             # Scripts de debug
│   ├── tests/             # Scripts e arquivos de teste
│   ├── validation/        # Scripts de validação
│   └── README.md          # Documentação dos scripts

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

### 1. Clone do Repositório

```bash
git clone https://github.com/seu-usuario/glpi_dashboard.git
cd glpi_dashboard
```

### 2. Configuração do Backend (Flask)

```bash
# Criar e ativar ambiente virtual
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate

# Instalar dependências do Python
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

#### Backend
```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `.env` na raiz do projeto com suas configurações específicas do GLPI:

```env
# Configurações do Flask
FLASK_ENV=dev
SECRET_KEY=sua-chave-secreta-aqui
FLASK_DEBUG=true
HOST=0.0.0.0
PORT=5000

# Configurações do GLPI
GLPI_URL=http://seu-servidor-glpi/glpi/apirest.php
GLPI_USER_TOKEN=seu-user-token
GLPI_APP_TOKEN=seu-app-token

# Outras configurações...
```

#### Frontend
```bash
cd frontend
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_LOG_LEVEL=info
```

### 4. Configurar e Executar o Frontend

```bash
# Navegar para a pasta frontend
cd frontend

# Instalar dependências do Node.js
npm install

# Executar servidor de desenvolvimento
npm run dev
```

O frontend será executado em `http://localhost:3001`

### 5. Executar o Backend

Em um novo terminal, na raiz do projeto:

```bash
# Ativar ambiente virtual (se não estiver ativo)
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Executar o backend
python app.py
```

O backend será executado em `http://localhost:5000`

### 6. Acessar a Aplicação

- **Frontend (Interface)**: `http://localhost:3001`
- **Backend (API)**: `http://localhost:5000`
- **API Docs**: `http://localhost:5000/api/status`

## Endpoints da API

### Métricas

```
GET /api/metrics
```

Retorna as métricas do dashboard do GLPI.

### Status

```
GET /api/status
```

Retorna o status do sistema e da conexão com o GLPI.