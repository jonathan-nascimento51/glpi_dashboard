# 🤖 Configuração MCP para Trae AI - GLPI Dashboard

> Guia completo para configurar um stack de MCPs (Model Context Protocol) que torna o Trae AI "cirúrgico" e consistente em cada iteração

## 🎯 Objetivo

Este guia configura um conjunto curado de MCPs que garantem:
1. **Grounding de documentação/API** - Reduz alucinações
2. **Operações seguras no repositório** - Controle de mudanças
3. **Validação contra base/observabilidade** - Consistência de dados

## 🎯 Configuração Específica para GLPI Dashboard

Este projeto utiliza:
- **Backend**: Flask (Python) na porta 5000
- **Frontend**: React + Vite na porta 3001 (acesso via 127.0.0.1:3001)
- **Banco**: MySQL/MariaDB (GLPI) na porta 3306
- **API**: OpenAPI/Swagger em `http://localhost:5000/openapi.json`
- **Endpoints principais**:
  - `/api/technicians/ranking` - Ranking de técnicos
  - `/api/tickets/metrics` - Métricas de tickets
  - `/api/tickets/priority-distribution` - Distribuição por prioridade

---

## 📦 MCPs Recomendados

### 1. Context7 (Grounding de Documentação)
**Função**: Busca documentação atualizada e exemplos de código das bibliotecas utilizadas (React, Flask, MySQL, etc.)
- ✅ Reduz alucinações e APIs inventadas pelo modelo, especialmente para React 18+, Flask 2.x, e integrações GLPI
- ✅ Essencial para refatorações e implementação de novas features
- ✅ Configuração: Nenhuma necessária
- 🔗 [GitHub](https://github.com/upstash/context7-mcp)

### 2. Filesystem MCP (Operações Seguras)
**Função**: Leitura/edição dentro de pasta delimitada
- ✅ Busca, patch, criar arquivo, etc.
- ✅ Base para qualquer refactor automatizado
- 🔗 [Glama](https://glama.ai/mcp/servers/filesystem) | [Playbooks](https://playbooks.com)

### 3. GitHub MCP (Fluxo Branch/PR/Issue)
**Função**: Permite abrir branch, PR, comentar diff e gerenciar issues
- ✅ Essencial para consistência e rastreabilidade
- ✅ Controle de versão automatizado
- 🔗 [GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/github)

### 4. Firecrawl MCP (Web/Source-of-Truth Externo)
**Função**: Busca/scrape estruturado com render JS
- ✅ Documentação GLPI/outros sistemas
- ✅ Ótimo para grounding de integrações
- 🔗 [GitHub](https://github.com/firecrawl-dev/firecrawl-mcp) | [Docs](https://docs.firecrawl.dev)

### 5. OpenAPI/Swagger MCP (Contratos do Backend Flask)
**Função**: Carrega especificação OpenAPI do backend Flask e transforma endpoints em ferramentas
- ✅ Validação automática de contratos, testes de API e debugging de inconsistências entre frontend/backend
- ✅ Endpoints validados: ranking, métricas, distribuição de prioridades
- ✅ Configuração: URL do OpenAPI spec (`http://localhost:5000/openapi.json`)
- 🔗 [Glama](https://glama.ai/mcp/servers/openapi) | [GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/openapi)

### 6. PostgreSQL/MySQL MCP (Fonte de Verdade dos Dados GLPI)
**Função**: Acesso read-only ao banco MySQL do GLPI para validação de dados
- ✅ Permite verificar dados na fonte (glpi_tickets, glpi_users) e debuggar inconsistências nos KPIs
- ✅ Tabelas principais: glpi_tickets, glpi_users, glpi_entities, glpi_itilcategories
- ✅ Configuração: Credenciais do banco MySQL (porta 3306, database 'glpi')
- 🔗 [Docker Hub](https://hub.docker.com/r/postgres/postgres) | [Cursor Directory](https://cursor.directory)

### 7. Prometheus/Grafana MCP (Observabilidade)
**Função**: PromQL, inspeção de dashboards
- ✅ "API up, latência X, série retornando Y"
- ✅ Separar dado zerado vs. serviço off
- 🔗 [GitHub Prometheus](https://github.com/prometheus/prometheus) | [AWS Labs](https://awslabs.github.io)

---

## ⚙️ Configuração no Trae

### Passo 1: Acessar Configuração MCP
1. Vá em **Agents → ⚙️ AI Management → MCP → Configure Manually**
2. Cole a configuração JSON abaixo

### Passo 2: Configuração JSON Completa

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "MCP_FS_ROOT": ".",
        "MCP_FS_READONLY": "false"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "github-mcp-server"],
      "env": {
        "GITHUB_TOKEN": "YOUR_GH_TOKEN"
      }
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc_YOUR_API_KEY"
      }
    },
    "openapi": {
      "command": "npx",
      "args": ["-y", "openapi-mcp-server"],
      "env": {
        "OPENAPI_SPEC_URL": "http://localhost:5000/openapi.json"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "mcp-postgres"],
      "env": {
        "PGHOST": "localhost",
        "PGPORT": "3306",
        "PGDATABASE": "glpi",
        "PGUSER": "readonly",
        "PGPASSWORD": "********",
        "PG_READONLY": "true"
      }
    },
    "prometheus": {
      "command": "npx",
      "args": ["-y", "prometheus-mcp-server"],
      "env": {
        "PROMETHEUS_BASE_URL": "http://localhost:9090"
      }
    },
    "grafana": {
      "command": "npx",
      "args": ["-y", "grafana-mcp"],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_TOKEN": "YOUR_GRAFANA_TOKEN"
      }
    }
  }
}
```

### Passo 3: Configurar Tokens e Credenciais

#### GitHub Token
1. Vá em GitHub → Settings → Developer settings → Personal access tokens
2. Gere token com permissões: `repo`, `issues`, `pull_requests`
3. Substitua `YOUR_GH_TOKEN` na configuração

#### Firecrawl API Key
1. Registre-se em [firecrawl.dev](https://firecrawl.dev)
2. Obtenha sua API key
3. Substitua `fc_YOUR_API_KEY` na configuração

#### Grafana Token
1. Acesse Grafana → Configuration → API Keys
2. Crie token com permissão de leitura
3. Substitua `YOUR_GRAFANA_TOKEN` na configuração

#### Configurações do Projeto GLPI Dashboard
- **OpenAPI URL**: `http://localhost:5000/openapi.json` (Flask backend)
- **PostgreSQL**: Ajuste host/porta conforme seu setup MySQL/PostgreSQL
- **Prometheus**: `http://localhost:9090` (se configurado)
- **Grafana**: `http://localhost:3000` (se configurado)

---

## 🚀 Como Usar (Padrões de Prompt)

### Inicialização Padrão
Cole no início de cada tarefa:

```
#Workspace
#Folder frontend
#Folder backend
use context7
```

### Padrões de Validação

#### 1. Validar KPIs contra API
```
Carregue o spec no `openapi` e **chame** `GET /api/metrics` para os mesmos filtros do front; compare com o DOM (#kpi-total, #kpi-n1..4). Se divergir, explique onde (fetch/transform/state/render).
```

#### 2. Bater com a Base de Dados
```
Via `postgres`, rode SELECTs equivalentes aos agregados do endpoint e compare com a resposta da API. Gere um diff comentado.
```

#### 3. Checar Saúde/Latência
```
Via `prometheus`, execute PromQL `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` do backend. Via `grafana`, me dê o painel e alertas associados.
```

#### 4. Fluxo Git Disciplinado
```
Use `github` para abrir branch `fix/kpis-zero`, commitar o patch mínimo e abrir PR com checklist de testes (inclua screenshot do dashboard).
```

#### 5. Docs Sempre Atuais
```
`use context7` ao pedir exemplos/códigos de libs (React, FastAPI, axios, etc.) para reduzir drift de versão.
```

---

## 🔧 Configurações Específicas do Projeto

### Backend Flask (app.py)
Para habilitar OpenAPI no Flask:

```python
from flask import Flask
from flask_restx import Api

app = Flask(__name__)
api = Api(app, doc='/docs/', version='1.0', title='GLPI Dashboard API')

# Endpoint para OpenAPI spec
@app.route('/openapi.json')
def openapi_spec():
    return api.__schema__
```

### Frontend React
Para melhor debugging com MCPs:

```typescript
// Adicionar IDs únicos nos elementos de métricas
<div id="kpi-total" className="metric-card">
  {metrics.total}
</div>
<div id="kpi-n1" className="metric-card">
  {metrics.niveis.n1.total}
</div>
```

### Docker Compose
Para habilitar Prometheus/Grafana:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 📋 Checklist de Verificação

### Antes de Usar
- [ ] Todos os tokens configurados
- [ ] Backend rodando em `localhost:5000`
- [ ] Frontend rodando em `localhost:3001`
- [ ] Banco de dados acessível
- [ ] MCPs instalados e funcionando

### Durante o Desenvolvimento
- [ ] Usar `context7` para documentação de libs
- [ ] Validar mudanças via `openapi` MCP
- [ ] Verificar dados via `postgres` MCP
- [ ] Monitorar via `prometheus`/`grafana` MCPs
- [ ] Criar branches/PRs via `github` MCP

### Após Mudanças
- [ ] KPIs batem entre frontend/backend/banco
- [ ] Métricas de performance OK
- [ ] Documentação atualizada
- [ ] Testes passando
- [ ] PR criado com contexto

---

## 🐛 Troubleshooting

### MCPs Não Carregam
1. Verificar se Node.js está instalado
2. Testar `npx -y @upstash/context7-mcp` manualmente
3. Verificar logs do Trae AI

### Tokens Inválidos
1. Regenerar tokens com permissões corretas
2. Verificar se não expiraram
3. Testar acesso manual às APIs

### Conexões de Banco
1. Verificar credenciais e conectividade
2. Testar com cliente SQL manual
3. Verificar firewall/rede

### Performance
1. Monitorar uso de CPU/memória dos MCPs
2. Ajustar timeouts se necessário
3. Considerar cache local para docs

---

## 📚 Referências

- [Trae AI MCP Documentation](https://docs.trae.ai)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP Server Directory](https://glama.ai/mcp)
- [Context7 GitHub](https://github.com/upstash/context7-mcp)
- [Firecrawl Documentation](https://docs.firecrawl.dev)

---

**Última atualização**: 2024-12-29  
**Versão**: 1.0.0  
**Maintainer**: Equipe GLPI Dashboard