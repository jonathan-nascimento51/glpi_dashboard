# 🤖 Configuração MCP para Trae AI - GLPI Dashboard

> **TL;DR**: Stack de MCPs para tornar o Trae AI "cirúrgico" e consistente no desenvolvimento do GLPI Dashboard

## 🚀 Quick Start

### 1. Teste a Configuração
```powershell
# Execute o script de verificação
PowerShell -ExecutionPolicy Bypass -File setup-mcps.ps1
```

### 2. Configure Tokens
Edite `trae-mcp-config.json` e substitua:
- `YOUR_GH_TOKEN` → [GitHub Personal Access Token](https://github.com/settings/tokens)
- `fc_YOUR_API_KEY` → [Firecrawl API Key](https://firecrawl.dev)
- `YOUR_GRAFANA_TOKEN` → Grafana API Key (opcional)
- Credenciais do banco de dados MySQL/MariaDB

**Configurações específicas do projeto GLPI Dashboard:**
- Backend Flask: `http://localhost:5000`
- Frontend React: `http://127.0.0.1:3001`
- Banco MySQL: `localhost:3306` (database: `glpi`)
- OpenAPI spec: `http://localhost:5000/openapi.json`

### 3. Cole no Trae AI
1. Vá em **Agents → ⚙️ AI Management → MCP → Configure Manually**
2. Cole o conteúdo completo do arquivo `trae-mcp-config.json`
3. Salve e reinicie o Trae AI

### 4. Teste com Prompt
```
#Workspace
#Folder frontend
#Folder backend
use context7

Validar se os KPIs do dashboard estão corretos comparando frontend, backend e banco de dados.
```

## 📋 MCPs Incluídos

| MCP | Função | Status | Configuração Necessária |
|-----|--------|--------|------------------------|
| **Context7** | Docs atualizadas de libs | ✅ Essencial | Nenhuma |
| **Filesystem** | Operações seguras no repo | ✅ Essencial | Nenhuma |
| **GitHub** | Branches, PRs, Issues | ✅ Recomendado | `GITHUB_TOKEN` |
| **OpenAPI** | Validação de contratos API | ✅ Crítico | Backend Flask rodando (porta 5000) |
| **PostgreSQL** | Acesso read-only ao banco MySQL | ✅ Crítico | `MYSQL_PASSWORD` (porta 3306) |
| **Firecrawl** | Scraping de documentação GLPI | 🔶 Opcional | `FIRECRAWL_API_KEY` |
| **Prometheus** | Métricas de performance | 🔶 Opcional | Prometheus local (porta 9090) |
| **Grafana** | Dashboards de monitoramento | 🔶 Opcional | `GRAFANA_TOKEN` (porta 3000) |

## 🎯 Casos de Uso Principais

### ✅ Validação de KPIs
```
Carregue o spec OpenAPI e compare os dados entre:
- API endpoints (/api/metrics, /api/technicians/ranking)
- Estado React (useDashboard.ts)
- Banco de dados (queries SQL)
- DOM renderizado (#kpi-total, #kpi-n1, etc.)
```

### 🔧 Desenvolvimento Seguro
```
Use GitHub MCP para:
1. Criar branch feature/nova-funcionalidade
2. Implementar mudanças
3. Abrir PR com checklist de testes
4. Documentar breaking changes
```

### 📊 Debugging de Performance
```
Use Prometheus + Grafana para:
- Identificar gargalos de performance
- Monitorar latência da API
- Verificar saúde dos serviços
- Correlacionar erros com métricas
```

## 📁 Arquivos Criados

- **`TRAE_MCP_SETUP.md`** → Guia completo e detalhado
- **`trae-mcp-config.json`** → Configuração para colar no Trae
- **`mcp-usage-examples.md`** → Prompts práticos prontos
- **`setup-mcps.ps1`** → Script de verificação automática
- **`README-MCP.md`** → Este resumo executivo

## ⚡ Prompts Essenciais

### Inicialização Padrão
```
#Workspace
#Folder frontend
#Folder backend
use context7
```

### Validação Completa
```
Validar integridade dos dados:
1. Via openapi: testar endpoints
2. Via postgres: verificar queries
3. Via filesystem: analisar código
4. Gerar relatório de divergências
```

### Fluxo Git Automatizado
```
Use github para:
1. Criar branch fix/problema-identificado
2. Implementar correção mínima
3. Abrir PR com contexto completo
4. Adicionar reviewers apropriados
```

## 🔧 Troubleshooting

### MCPs Não Carregam
- ✅ Verificar Node.js instalado
- ✅ Testar `npx -y @upstash/context7-mcp`
- ✅ Verificar logs do Trae AI

### Tokens Inválidos
- ✅ Regenerar com permissões corretas
- ✅ Verificar se não expiraram
- ✅ Testar acesso manual

### Configuração de Tokens

Configure estas variáveis de ambiente ou edite o arquivo `trae-mcp-config.json`:

```powershell
# GitHub (obrigatório para operações Git)
$env:GITHUB_TOKEN="ghp_your_token_here"

# Firecrawl (opcional, para scraping avançado)
$env:FIRECRAWL_API_KEY="fc_your_api_key_here"

# Grafana (opcional, para observabilidade)
$env:GRAFANA_TOKEN="your_grafana_token_here"

# MySQL/MariaDB (ajuste conforme seu ambiente GLPI)
$env:MYSQL_PASSWORD="your_db_password"
```

### Serviços Offline
- ✅ Backend Flask: `python app.py`
- ✅ Frontend React: `cd frontend && npm run dev`
- ✅ Banco de dados: verificar conexão

## 🎯 Benefícios Esperados

### ✅ Antes vs Depois

| Antes | Depois |
|-------|--------|
| "KPIs zerados, não sei por quê" | "KPI zerado: query SQL retorna 0, API OK, problema no frontend" |
| "Código quebrou, não sei onde" | "Breaking change identificado, PR criado com fix" |
| "Documentação desatualizada" | "Docs sempre atuais via Context7" |
| "Performance ruim, causa?" | "Latência 95p: 200ms, gargalo na query X" |

### 📈 Métricas de Sucesso
- ⏱️ **Tempo de debug**: -70%
- 🎯 **Precisão de diagnóstico**: +90%
- 📚 **Consistência de código**: +80%
- 🔄 **Velocidade de iteração**: +60%

## 🚀 Próximos Passos

1. **Execute** `setup-mcps.ps1`
2. **Configure** tokens necessários
3. **Cole** configuração no Trae AI
4. **Teste** com prompt de validação
5. **Documente** resultados e ajustes

---

**💡 Dica**: Sempre inicie prompts com `#Workspace #Folder frontend #Folder backend use context7` para máxima eficácia.

**📞 Suporte**: Consulte `TRAE_MCP_SETUP.md` para documentação completa ou `mcp-usage-examples.md` para prompts específicos.

---

*Última atualização: 2024-12-29 | Versão: 1.0.0 | Projeto: GLPI Dashboard*