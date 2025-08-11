# 🚀 Guia Passo a Passo: Configuração de MCPs para GLPI Dashboard

## 📋 Pré-requisitos

✅ **Verificar se você tem:**
- Node.js 18+ instalado
- NPX disponível
- Trae AI instalado e funcionando
- Projeto GLPI Dashboard rodando (backend Flask + frontend React)

---

## 🔧 PASSO 1: Configurar Variáveis de Ambiente

### 1.1 Criar arquivo de configuração
```powershell
# No diretório do projeto
cp .env.mcp.example .env.mcp
```

### 1.2 Configurar tokens obrigatórios

#### GitHub Token (OBRIGATÓRIO)
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione as permissões:
   - ✅ `repo` (acesso completo aos repositórios)
   - ✅ `workflow` (atualizar workflows)
   - ✅ `write:packages` (publicar pacotes)
4. Copie o token gerado
5. Edite `.env.mcp`:
```bash
GITHUB_TOKEN=ghp_seu_token_aqui
```

#### Banco MySQL (OBRIGATÓRIO)
1. Configure as credenciais do banco GLPI:
```bash
PGHOST=localhost
PGPORT=3306
PGDATABASE=glpi
PGUSER=seu_usuario_mysql
PGPASSWORD=sua_senha_mysql
PG_READONLY=true
```

### 1.3 Configurar tokens opcionais

#### Firecrawl (Opcional - para scraping)
1. Registre-se em: https://firecrawl.dev
2. Obtenha sua API key
3. Configure:
```bash
FIRECRAWL_API_KEY=fc_sua_api_key_aqui
```

#### Grafana (Opcional - para dashboards)
1. Acesse: http://localhost:3000 (se Grafana estiver rodando)
2. Vá em: Configuration → API Keys
3. Crie uma nova API key
4. Configure:
```bash
GRAFANA_TOKEN=seu_token_grafana_aqui
```

---

## ⚙️ PASSO 2: Configurar MCPs no Trae AI

### 2.1 Abrir configuração do Trae AI
1. Abra o Trae AI
2. Vá em: **Agents → ⚙️ AI Management → MCP → Configure Manually**

### 2.2 Colar configuração JSON
1. Abra o arquivo `trae-mcp-config.json`
2. Copie TODO o conteúdo
3. Cole na interface do Trae AI
4. Clique em **Save**
5. **Reinicie o Trae AI**

### 2.3 Verificar MCPs carregados
Após reiniciar, você deve ver na interface:
- ✅ Context7
- ✅ Filesystem
- ✅ GitHub
- ✅ OpenAPI
- ✅ PostgreSQL
- ✅ Firecrawl (se configurado)
- ✅ Prometheus (se disponível)
- ✅ Grafana (se configurado)

---

## 🧪 PASSO 3: Testar Configuração

### 3.1 Executar script de teste
```powershell
# No diretório do projeto
.\setup-mcps.ps1
```

### 3.2 Verificar resultados esperados

**✅ Deve aparecer:**
```
✅ Node.js: OK (v18.x.x)
✅ NPX: OK
✅ Context7: OK
✅ Filesystem: OK
✅ GitHub: OK (se token configurado)
✅ Backend Flask: OK (Status: 200)
✅ Frontend React: OK (Status: 200)
✅ OpenAPI: OK (Status: 200)
✅ MySQL: Porta 3306 acessível
```

**❌ Se aparecer erro:**
- Verifique se os serviços estão rodando
- Confirme se os tokens estão corretos
- Execute novamente o script

### 3.3 Testar MCPs individualmente

#### Testar Context7
```powershell
npx -y @upstash/context7-mcp
```

#### Testar GitHub (se token configurado)
```powershell
$env:GITHUB_TOKEN="seu_token"
npx -y github-mcp-server
```

#### Testar OpenAPI
```powershell
$env:OPENAPI_SPEC_URL="http://localhost:5000/openapi.json"
npx -y openapi-mcp-server
```

---

## 🎯 PASSO 4: Verificar Serviços do Projeto

### 4.1 Backend Flask
```powershell
# Verificar se está rodando
Invoke-WebRequest -Uri "http://localhost:5000/api/technicians/ranking"

# Se não estiver rodando:
python app.py
```

### 4.2 Frontend React
```powershell
# Verificar se está rodando
Invoke-WebRequest -Uri "http://127.0.0.1:3001"

# Se não estiver rodando:
cd frontend
npm run dev
```

### 4.3 Banco MySQL
```powershell
# Testar conectividade
$tcpClient = New-Object System.Net.Sockets.TcpClient
$tcpClient.Connect("localhost", 3306)
$tcpClient.Close()
```

---

## 🚀 PASSO 5: Usar MCPs no Trae AI

### 5.1 Prompts de teste essenciais

#### Validar dados entre frontend e backend
```
#Workspace
#Folder frontend
#Folder backend
use context7

Carregue o spec OpenAPI do backend Flask e chame GET /api/technicians/ranking. Compare os dados retornados com o que está sendo exibido no frontend React. Identifique divergências nos KPIs.
```

#### Verificar dados no banco
```
#Workspace
use postgres

Execute uma query para contar tickets por técnico na tabela glpi_tickets e compare com a API /api/technicians/ranking.
```

#### Refatorar componente
```
#Workspace
#Folder frontend/src/components
use context7

Refatore o componente MetricsGrid para usar React Query ao invés de useState/useEffect. Mantenha a mesma interface mas melhore o cache e error handling.
```

### 5.2 Fluxo Git automatizado
```
#Workspace
use github

Crie uma branch 'feature/mcp-integration', faça commit das configurações de MCP e abra um PR com descrição detalhada.
```

---

## 🔍 PASSO 6: Troubleshooting

### 6.1 Problemas comuns

#### MCPs não aparecem no Trae AI
- ✅ Verificar se JSON está válido
- ✅ Reiniciar o Trae AI
- ✅ Verificar logs do Trae AI

#### Erro de token GitHub
- ✅ Verificar se token tem permissões corretas
- ✅ Testar token manualmente: `curl -H "Authorization: token SEU_TOKEN" https://api.github.com/user`

#### Erro de conexão com banco
- ✅ Verificar se MySQL está rodando
- ✅ Testar credenciais manualmente
- ✅ Verificar firewall/porta 3306

#### Backend Flask não responde
- ✅ Verificar se está rodando na porta 5000
- ✅ Testar endpoint: `curl http://localhost:5000/api/technicians/ranking`
- ✅ Verificar logs do Flask

### 6.2 Logs úteis

#### Verificar logs do Trae AI
- Procure por erros relacionados a MCPs
- Verifique se todos os MCPs foram carregados

#### Verificar logs do projeto
```powershell
# Backend Flask
python app.py  # Verificar output no terminal

# Frontend React
cd frontend && npm run dev  # Verificar output no terminal
```

---

## ✅ PASSO 7: Validação Final

### 7.1 Checklist de configuração
- [ ] Tokens configurados em `.env.mcp`
- [ ] MCPs carregados no Trae AI
- [ ] Script `setup-mcps.ps1` executado com sucesso
- [ ] Backend Flask rodando (porta 5000)
- [ ] Frontend React rodando (porta 3001)
- [ ] Banco MySQL acessível (porta 3306)
- [ ] Prompts de teste funcionando

### 7.2 Teste final completo
```
#Workspace
use context7
use openapi
use postgres

Faça uma validação completa:
1. Carregue o spec OpenAPI
2. Chame todos os endpoints principais
3. Compare com dados do banco MySQL
4. Gere um relatório de consistência
```

---

## 🎉 Próximos Passos

Com os MCPs configurados, você pode:

1. **Usar prompts do arquivo `mcp-usage-examples.md`**
2. **Implementar novas features com validação automática**
3. **Debuggar problemas com precisão cirúrgica**
4. **Manter fluxo Git disciplinado**
5. **Monitorar performance em tempo real**

**🔥 Dica:** Sempre use `#Workspace` e especifique quais MCPs usar para obter os melhores resultados!

---

## 📞 Suporte

Se encontrar problemas:
1. Execute `./setup-mcps.ps1` novamente
2. Verifique os logs do Trae AI
3. Consulte `README-MCP.md` para referência rápida
4. Use os prompts de exemplo em `mcp-usage-examples.md`