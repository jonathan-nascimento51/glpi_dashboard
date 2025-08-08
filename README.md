# GLPI Dashboard

Dashboard operacional completo para monitoramento e análise de dados do GLPI (Gestão Livre de Parque de Informática), implementado como monorepo com módulos separados.

## 📋 Visão Geral

Este projeto implementa um dashboard completo para visualização de métricas e dados do GLPI, seguindo uma arquitetura monorepo com módulos isolados para diferentes funcionalidades, incluindo um sistema avançado de mapeamento e cache de catálogos.

## Estrutura do Projeto

```
glpi_dashboard/
├── backend/                # API Flask
│   ├── api/               # Endpoints da API
│   │   ├── __init__.py    # Inicializador do módulo API
│   │   └── routes.py      # Rotas da API + Admin endpoints
│   ├── config/            # Configurações
│   │   ├── __init__.py    # Inicializador do módulo de configuração
│   │   └── settings.py    # Configurações centralizadas
│   ├── services/          # Serviços de integração
│   │   ├── __init__.py    # Inicializador do módulo de serviços
│   │   ├── api_service.py # Serviço para APIs externas
│   │   ├── glpi_service.py # Serviço para integração com GLPI
│   │   └── lookup_loader.py # Serviço de carregamento de lookups
│   └── __init__.py        # Inicializador do pacote backend
├── frontend/              # Frontend React + TypeScript
│   ├── src/               # Código fonte do frontend
│   ├── package.json       # Dependências Node.js
│   └── vite.config.ts     # Configuração do Vite
├── worker/                # Tarefas assíncronas (Celery)
├── tools/                 # Ferramentas e utilitários
│   └── glpi_mapping/      # 🆕 Módulo de mapeamento GLPI
│       ├── __init__.py    # Inicializador do módulo
│       ├── cli.py         # Interface de linha de comando
│       ├── mapper.py      # Lógica de mapeamento
│       ├── pyproject.toml # Configuração do pacote
│       ├── crontab        # Configuração de execução programada
│       └── README.md      # Documentação específica
├── data/
│   └── lookups/           # 🆕 Arquivos de lookup/catálogos
├── logs/                  # Arquivos de log
├── docker-compose.yml     # 🆕 Configuração Docker completa
├── app.py                 # Ponto de entrada do backend
├── pyproject.toml         # Configuração e dependências Python
├── .env.example           # Exemplo de variáveis de ambiente (atualizado)
└── README.md              # Este arquivo
```

## 🚀 Funcionalidades

### Dashboard Principal
- **Métricas em tempo real**: Tickets, técnicos, categorias, prioridades
- **Filtros avançados**: Por data, prioridade, categoria, técnico
- **Cache inteligente**: Redis para otimização de performance
- **API RESTful**: Endpoints para todas as funcionalidades
- **Monitoramento**: Health checks e métricas de performance

### 🆕 Módulo de Mapeamento GLPI
- **Extração de catálogos**: Tickets, usuários, grupos, categorias, prioridades, status
- **Múltiplos formatos**: JSON, CSV com metadados completos
- **Detecção de hierarquia**: Estruturas pai-filho automáticas
- **CLI amigável**: Comandos para dump, análise e teste de conexão
- **Cache e retry**: Mecanismos de resiliência e recuperação
- **Execução programada**: Cron jobs para atualização automática semanal
- **Hot-reload**: Endpoints para recarga sem restart do sistema

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

### 5. Configurar o Módulo de Mapeamento GLPI

```bash
# Instalar o módulo de mapeamento
cd tools/glpi_mapping
pip install -e .

# Testar conexão com GLPI
python -m glpi_mapping test-connection

# Executar mapeamento inicial
python -m glpi_mapping dump --out ../../data/lookups
```

### 6. Acessar a Aplicação

- **Frontend (Interface)**: `http://localhost:3000`
- **Backend (API)**: `http://localhost:5000`
- **Admin Lookups**: `http://localhost:5000/api/admin/lookups/health`

## 🐳 Execução com Docker

### Configuração Rápida

```bash
# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações GLPI

# Executar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

### Serviços Disponíveis

- **backend**: API Flask (porta 5000)
- **frontend**: Interface React (porta 3000)
- **redis**: Cache (porta 6379)
- **worker**: Tarefas assíncronas
- **glpi-mapper**: Mapeamento programado com cron
- **nginx**: Proxy reverso (perfil production)

### Perfis Docker Compose

```bash
# Produção (padrão)
docker-compose up -d

# Desenvolvimento (com hot reload)
docker-compose --profile development up -d

# Produção com nginx
docker-compose --profile production up -d
```

### Comandos Úteis

```bash
# Ver logs do mapeamento
docker-compose logs glpi-mapper

# Executar mapeamento manual
docker-compose exec glpi-mapper python -m glpi_mapping dump --out /app/lookups

# Recarregar lookups via API
curl -X POST http://localhost:5000/api/admin/lookups/reload

# Verificar saúde dos lookups
curl http://localhost:5000/api/admin/lookups/health
```

## Endpoints da API

### Métricas Principais

```
GET /api/dashboard/metrics     # Métricas gerais do dashboard
GET /api/tickets/summary       # Resumo de tickets com filtros
GET /api/technicians/ranking   # Ranking de técnicos
GET /api/tickets/new           # Tickets novos
GET /api/alerts                # Alertas do sistema
GET /api/performance/stats     # Estatísticas de performance
GET /api/status                # Status do sistema e GLPI
```

### 🆕 Endpoints de Administração - Lookups

```
POST /api/admin/lookups/reload  # Recarrega catálogos/lookups
GET  /api/admin/lookups/health  # Verifica saúde dos lookups
GET  /api/admin/lookups/stats   # Estatísticas dos catálogos
```

### Filtros Disponíveis

Todos os endpoints de métricas suportam filtros via query parameters:
- `start_date` / `end_date`: Filtro por período (formato: YYYY-MM-DD)
- `priority`: Filtro por prioridade
- `category`: Filtro por categoria
- `technician`: Filtro por técnico
- `limit`: Limite de resultados

Exemplo:
```
GET /api/tickets/summary?start_date=2024-01-01&end_date=2024-01-31&priority=high&limit=10
```

## 🔧 Módulo de Mapeamento GLPI

### Instalação do Módulo

```bash
# Instalar como pacote pip
cd tools/glpi_mapping
pip install -e .

# Ou instalar dependências manualmente
pip install requests python-dotenv click pydantic rich typer
```

### Comandos CLI

```bash
# Testar conexão com GLPI
python -m glpi_mapping test-connection

# Listar catálogos disponíveis
python -m glpi_mapping list-catalogs

# Extrair todos os catálogos
python -m glpi_mapping dump --out ./data/lookups

# Extrair catálogos específicos
python -m glpi_mapping dump --catalogs tickets users --out ./data/lookups

# Analisar estrutura hierárquica
python -m glpi_mapping analyze --catalog categories

# Versão do módulo
python -m glpi_mapping version
```

### Configuração de Execução Programada

O módulo inclui configuração de cron para execução automática:

```cron
# Mapeamento semanal (segunda-feira às 02:00)
0 2 * * 1 python -m glpi_mapping dump --out /app/lookups

# Verificação diária de saúde (06:00)
0 6 * * * python -m glpi_mapping test-connection
```

### Integração com Dashboard

O dashboard carrega automaticamente os lookups gerados:

```python
from backend.services.lookup_loader import get_lookup_loader

loader = get_lookup_loader()

# Obter catálogo de usuários
users = loader.get_catalog('users')

# Obter lookup de prioridades (id -> nome)
priorities = loader.get_lookup('priorities')

# Verificar se dados estão atualizados
is_fresh = loader.is_data_fresh('tickets')

# Forçar recarga de um catálogo
data = loader.get_catalog('categories', force_reload=True)
```