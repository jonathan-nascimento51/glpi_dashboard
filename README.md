# GLPI Dashboard API

API para integração com o GLPI e fornecimento de métricas para o dashboard.

## Estrutura do Projeto

```
.
├── backend/                # Backend da aplicação
│   ├── api/               # Endpoints da API
│   │   ├── __init__.py    # Inicializador do módulo API
│   │   └── routes.py      # Rotas da API
│   ├── config/            # Configurações
│   │   ├── __init__.py    # Inicializador do módulo de configuração
│   │   └── settings.py    # Configurações centralizadas
│   ├── services/          # Serviços de integração
│   │   ├── __init__.py    # Inicializador do módulo de serviços
│   │   ├── api_service.py # Serviço para APIs externas
│   │   └── glpi_service.py # Serviço para integração com GLPI
│   └── __init__.py        # Inicializador do pacote backend
├── frontend/              # Frontend React
└── app.py                 # Ponto de entrada da aplicação
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
- `HOST`: Host do servidor. Padrão: `0.0.0.0`
- `GLPI_URL`: URL da API do GLPI. Padrão: `http://10.73.0.79/glpi/apirest.php`
- `GLPI_USER_TOKEN`: Token de usuário do GLPI.
- `GLPI_APP_TOKEN`: Token de aplicação do GLPI.
- `LOG_LEVEL`: Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Padrão: `INFO`

## Execução

```bash
python app.py
```

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