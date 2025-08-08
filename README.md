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