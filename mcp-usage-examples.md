# 🎯 Exemplos Práticos de Uso dos MCPs - GLPI Dashboard

> Prompts prontos para usar com o stack de MCPs configurado no Trae AI

## 🚀 Prompts de Inicialização

### Prompt Base para Qualquer Tarefa
```
#Workspace
#Folder frontend
#Folder backend
use context7

Contexto: Projeto GLPI Dashboard com React frontend e Flask backend.
Objetivo: [DESCREVA SUA TAREFA AQUI]
```

---

## 🔍 Validação e Debugging

### 1. Validar KPIs contra API do GLPI Dashboard
```
#Workspace
#Folder frontend
#Folder backend
use context7

Carregue o spec OpenAPI do backend Flask (http://localhost:5000/openapi.json) e chame os endpoints:
- GET /api/technicians/ranking
- GET /api/tickets/metrics
- GET /api/tickets/priority-distribution

Compare os dados retornados com o que está sendo exibido no frontend React. Verifique se há divergências nos KPIs mostrados no MetricsGrid e identifique onde pode estar o problema (fetch/transform/state/render).
```

### 2. Validar dados contra banco MySQL do GLPI
```
#Workspace
use postgres

Via `postgres` (configurado para MySQL na porta 3306), execute queries equivalentes aos agregados dos endpoints:

1. Para ranking de técnicos:
```sql
SELECT u.name, COUNT(t.id) as total_tickets 
FROM glpi_tickets t 
JOIN glpi_users u ON t.users_id_assign = u.id 
GROUP BY u.id ORDER BY total_tickets DESC;
```

2. Para distribuição por prioridade:
```sql
SELECT priority, COUNT(*) as count 
FROM glpi_tickets 
GROUP BY priority;
```

3. Total de tickets:
```sql
SELECT COUNT(*) as total_tickets FROM glpi_tickets WHERE is_deleted = 0;
```

Compare com as respostas da API Flask e gere um diff comentado das divergências.
```

### 3. Monitorar performance do GLPI Dashboard
```
#Workspace
use prometheus
use grafana

Via `prometheus` (porta 9090), execute queries PromQL para monitorar:
- Latência do backend Flask: `histogram_quantile(0.95, rate(flask_request_duration_seconds_bucket[5m]))`
- Taxa de erro: `rate(flask_request_exceptions_total[5m])`
- Uso de CPU/memória: `process_cpu_seconds_total`, `process_resident_memory_bytes`

Via `grafana` (porta 3000), verifique dashboards existentes para o GLPI Dashboard e configure alertas para:
- Latência > 2s
- Taxa de erro > 5%
- Indisponibilidade do serviço
```

---

## 🛠️ Desenvolvimento e Refatoração

### 4. Refatorar MetricsGrid com melhores práticas
```
#Workspace
#Folder frontend
use context7

Refatore o componente MetricsGrid do GLPI Dashboard para:
1. Usar React Query/TanStack Query para cache e sincronização
2. Implementar error boundaries para falhas de API
3. Adicionar loading states mais informativos
4. Melhorar a tipagem TypeScript dos dados de tickets
5. Implementar retry automático para falhas de rede

Mantenha a mesma interface visual mas melhore a robustez e UX.
```

### 5. Otimizar queries do backend Flask para GLPI
```
#Workspace
#Folder backend
use context7

Analise as queries SQL no backend Flask que acessam as tabelas do GLPI:
- glpi_tickets
- glpi_users  
- glpi_entities
- glpi_itilcategories

Otimize para:
1. Reduzir tempo de resposta dos endpoints de métricas
2. Adicionar índices apropriados nas colunas mais consultadas
3. Implementar cache Redis para dados que mudam pouco
4. Usar agregações mais eficientes
5. Considerar views materializadas para relatórios complexos
```

---

## 🔄 Fluxo Git e Colaboração

### 6. Criar Branch e PR para Fix
```
#Workspace
use github

Encontrei um bug nos KPIs zerados. Vou:

1. Criar branch `fix/kpis-zero-data`
2. Implementar correção mínima
3. Adicionar testes
4. Abrir PR com:
   - Descrição do problema
   - Solução implementada
   - Screenshots antes/depois
   - Checklist de testes

Use `github` MCP para automatizar este fluxo.
```

### 7. Documentar Mudanças Arquiteturais
```
#Workspace
#Folder frontend
#Folder backend
use github
use filesystem

Após refatoração do estado global, preciso:

1. Atualizar documentação técnica
2. Criar diagramas de arquitetura
3. Documentar breaking changes
4. Atualizar README com novas dependências

Use `filesystem` para organizar docs e `github` para criar issue de tracking.
```

---

## 🧪 Testes e Qualidade

### 8. Implementar Testes Automatizados
```
#Workspace
#Folder frontend
#Folder backend
use context7
use openapi

Implementar suite de testes:

1. Frontend (Jest + Testing Library):
   - Testes unitários dos hooks
   - Testes de integração dos componentes
   - Mocks das chamadas API

2. Backend (pytest):
   - Testes dos endpoints
   - Validação de contratos OpenAPI
   - Testes de integração com banco

Use `context7` para melhores práticas de teste e `openapi` para validar contratos.
```

### 9. Análise de Performance
```
#Workspace
use prometheus
use grafana
use context7

Analisar performance da aplicação:

1. Identificar gargalos via métricas
2. Otimizar queries lentas
3. Implementar cache onde necessário
4. Monitorar bundle size do frontend

Use `context7` para técnicas de otimização React/Flask.
```

---

## 🔧 Troubleshooting Específico

### 10. Debug de CORS Issues
```
#Workspace
#Folder backend
use context7
use openapi

Problema: Frontend não consegue acessar API (CORS).

Investigar:
1. Configuração Flask-CORS
2. Headers de requisição/resposta
3. Diferenças localhost vs 127.0.0.1

Use `context7` para configuração correta de CORS em Flask.
Use `openapi` para testar endpoints diretamente.
```

### 11. Debug de Estado React
```
#Workspace
#Folder frontend
use context7

Problema: Estado não atualiza corretamente no dashboard.

Analisar:
1. Fluxo de dados no `useDashboard.ts`
2. Dependências dos useEffect
3. Mutações de estado
4. Re-renders desnecessários

Use `context7` para padrões de debug React e DevTools.
```

---

## 📊 Relatórios e Análises

### 12. Gerar Relatório de Saúde do Sistema
```
#Workspace
use postgres
use prometheus
use grafana
use github

Gerar relatório completo:

1. Métricas de negócio (via postgres)
2. Performance técnica (via prometheus)
3. Dashboards visuais (via grafana)
4. Issues/PRs recentes (via github)

Consolidar em relatório markdown com gráficos e recomendações.
```

---

## 🎨 Melhorias de UX/UI

### 13. Modernizar Interface
```
#Workspace
#Folder frontend
use context7
use firecrawl

Modernizar dashboard com:
1. Design system atualizado
2. Componentes acessíveis
3. Responsividade mobile
4. Dark mode

Use `context7` para:
- Material-UI ou Chakra UI docs
- Padrões de acessibilidade
- CSS-in-JS moderno

Use `firecrawl` para inspiração em dashboards modernos.
```

---

## 💡 Dicas de Uso

### Combinando MCPs
- **Sempre** inicie com `use context7` para docs atualizadas
- **Valide** mudanças com `openapi` + `postgres`
- **Monitore** com `prometheus` + `grafana`
- **Versione** com `github` MCP
- **Explore** com `firecrawl` para referências externas

### Prompts Eficazes
1. Seja específico sobre o objetivo
2. Mencione arquivos/componentes relevantes
3. Inclua critérios de validação
4. Peça comparações entre camadas
5. Solicite documentação das mudanças

### Troubleshooting MCPs
- Se MCP não responder, teste manualmente primeiro
- Verifique tokens e credenciais
- Confirme que serviços estão rodando
- Use logs do Trae para debug

---

**Última atualização**: 2024-12-29  
**Versão**: 1.0.0  
**Projeto**: GLPI Dashboard