# Configuração de Dados Mock - Dashboard GLPI

## Resumo das Alterações

Este documento descreve as configurações realizadas para ativar os dados mock e organizar as variáveis de ambiente do projeto.

## Problemas Identificados e Solucionados

### 1. Parâmetros Duplicados
- **Problema**: Existiam arquivos `.env` na raiz, backend e frontend com configurações conflitantes
- **Solução**: 
  - Renomeado `.env` da raiz para `.env.backup` para evitar conflitos
  - Organizadas configurações específicas em `backend/.env` e `frontend/.env`

### 2. Acesso à Rede Interna
- **Problema**: Sem acesso ao servidor GLPI interno (`cau.ppiratini.intra.rs.gov.br`)
- **Solução**: Ativados dados mock através da flag `FLAG_USE_REAL_GLPI_DATA=false`

## Configurações Atuais

### Backend (`backend/.env`)
```env
# Feature Flags - DADOS MOCK ATIVADOS
FLAG_USE_REAL_GLPI_DATA=false
FLAG_USE_V2_KPIS=false

# Environment Configuration
ENVIRONMENT=development
RELEASE=local
API_BASE=http://localhost:8000
PORT=8000

# GLPI Configuration (não utilizadas quando mock está ativo)
GLPI_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
GLPI_USER_TOKEN=WPjwz02rLe4jLt3YzJrpJJTzQmIwIXkKFvDsJpEU
GLPI_APP_TOKEN=c1U4Emxp0n7ClNDz7Kd2jSkcVB5gG4XFTLlnTm85

# Cache Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance Configuration
PERFORMANCE_TARGET_P95=500
PERFORMANCE_MONITORING_ENABLED=true

# Observability (desabilitadas para desenvolvimento)
SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_SERVICE_NAME=gadpi-api
UNLEASH_URL=http://localhost:4242/api
UNLEASH_APP_NAME=gadpi-backend
UNLEASH_INSTANCE_ID=local
```

### Frontend (`frontend/.env`)
```env
# Configuração da API - Backend Local
VITE_API_BASE_URL=http://localhost:8000

# Configurações de desenvolvimento
VITE_LOG_LEVEL=info
VITE_SHOW_PERFORMANCE=true
VITE_SHOW_API_CALLS=true
VITE_SHOW_CACHE_HITS=false

# Environment
VITE_ENVIRONMENT=development
VITE_RELEASE=local

# Configurações de timeout e retry
VITE_API_TIMEOUT=30000
VITE_API_RETRY_ATTEMPTS=3
VITE_API_RETRY_DELAY=1000

# Observability (desabilitadas para desenvolvimento)
VITE_SENTRY_DSN=
VITE_UNLEASH_PROXY_URL=
VITE_UNLEASH_PROXY_CLIENT_KEY=
```

## Dados Mock Disponíveis

### Endpoints com Dados Mock
1. **GET /v1/kpis** - Métricas do dashboard por nível (N1, N2, N3, N4)
2. **GET /v1/system/status** - Status do sistema
3. **GET /v1/technicians/ranking** - Ranking de técnicos
4. **GET /v1/tickets/new** - Novos tickets

### Estrutura dos Dados Mock (KPIs)
```json
{
  "niveis": {
    "geral": { "novos": 45, "progresso": 23, "pendentes": 12, "resolvidos": 156, "total": 236 },
    "n1": { "novos": 12, "progresso": 8, "pendentes": 3, "resolvidos": 42, "total": 65 },
    "n2": { "novos": 15, "progresso": 7, "pendentes": 4, "resolvidos": 38, "total": 64 },
    "n3": { "novos": 10, "progresso": 5, "pendentes": 3, "resolvidos": 41, "total": 59 },
    "n4": { "novos": 8, "progresso": 3, "pendentes": 2, "resolvidos": 35, "total": 48 }
  },
  "tendencias": {
    "novos": "+12.5%", "pendentes": "-8.3%", "progresso": "+15.7%", "resolvidos": "+22.1%"
  }
}
```

## Como Executar

### Backend
```bash
cd backend
python main.py
# Servidor rodando em http://localhost:8000
```

### Frontend
```bash
cd frontend
npm run dev
# Servidor rodando em http://localhost:3000
```

## Status Atual
✅ Dados mock ativados  
✅ Configurações organizadas  
✅ Conflitos de .env resolvidos  
✅ Backend rodando em http://localhost:8000  
✅ Frontend rodando em http://localhost:3000  
✅ Dashboard funcionando com dados mock  

## Para Voltar aos Dados Reais
Quando o acesso à rede interna for restaurado:
1. Alterar `FLAG_USE_REAL_GLPI_DATA=true` no `backend/.env`
2. Reiniciar o backend
3. Verificar conectividade com o servidor GLPI