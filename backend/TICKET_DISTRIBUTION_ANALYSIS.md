# Análise da Distribuição de Tickets GLPI

## Resumo Executivo

A investigação revelou uma discrepância significativa entre o total geral de tickets (9.823) e os tickets categorizados nos grupos de nível de serviço N1-N4 (apenas 27 tickets, representando 0,27% do total).

## Descobertas Principais

### 1. Distribuição Atual dos Tickets

- **Total geral de tickets**: 9.823
- **Tickets em grupos N1-N4**: 27 (0,27%)
- **Tickets não categorizados**: 9.796 (99,73%)

### 2. Detalhamento por Nível

| Nível | Grupo GLPI | Quantidade | Percentual |
|-------|------------|------------|------------|
| N1    | 89         | 1          | 0,01%      |
| N2    | 90         | 12         | 0,12%      |
| N3    | 91         | 4          | 0,04%      |
| N4    | 92         | 10         | 0,10%      |
| **Total N1-N4** | | **27** | **0,27%** |

### 3. Problemas Identificados

#### 3.1 Baixa Categorização
- 99,73% dos tickets não estão associados aos grupos de nível de serviço
- Isso indica que a maioria dos tickets não possui classificação de nível de serviço

#### 3.2 Impacto no Dashboard
- O dashboard mostra métricas baseadas apenas em 0,27% dos tickets reais
- As estatísticas por nível não representam a realidade operacional
- Métricas de performance podem estar distorcidas

## Possíveis Causas

### 1. Configuração de Grupos
- Os grupos N1-N4 podem não estar sendo utilizados na prática
- Pode haver outros grupos ou categorias sendo utilizados
- Configuração incorreta dos IDs de grupo (89, 90, 91, 92)

### 2. Processo Operacional
- Tickets podem estar sendo criados sem associação a grupos
- Falta de treinamento para categorização adequada
- Processo de triagem pode não estar funcionando

### 3. Configuração do GLPI
- Campo de grupo pode não ser obrigatório
- Outros campos podem estar sendo utilizados para categorização
- Integração com outros sistemas pode estar criando tickets sem grupo

## Recomendações

### 1. Investigação Adicional

#### 1.1 Verificar Outros Grupos
```sql
-- Consulta para identificar todos os grupos utilizados
SELECT groups_id, COUNT(*) as total_tickets 
FROM glpi_tickets 
WHERE groups_id IS NOT NULL 
GROUP BY groups_id 
ORDER BY total_tickets DESC;
```

#### 1.2 Analisar Campos Alternativos
- Verificar se existe outro campo sendo usado para categorização
- Investigar campos customizados que possam indicar nível de serviço
- Analisar categorias e subcategorias dos tickets

### 2. Melhorias no Dashboard

#### 2.1 Exibir Dados Reais
- Mostrar o percentual real de tickets categorizados
- Adicionar alertas sobre baixa categorização
- Incluir métricas de tickets não categorizados

#### 2.2 Filtros Adicionais
- Permitir visualização por outros critérios (categoria, status, etc.)
- Adicionar opção para ver todos os tickets, não apenas os categorizados
- Implementar drill-down para investigar tickets não categorizados

### 3. Melhorias Operacionais

#### 3.1 Processo de Categorização
- Implementar regras automáticas de categorização
- Tornar o campo de grupo obrigatório
- Criar workflow de triagem automática

#### 3.2 Treinamento
- Capacitar equipe sobre importância da categorização
- Criar guias de classificação por nível de serviço
- Implementar validações no momento da criação do ticket

## Próximos Passos

1. **Imediato**: Investigar quais outros grupos existem no GLPI
2. **Curto prazo**: Implementar visualização de dados reais no dashboard
3. **Médio prazo**: Revisar processo de categorização de tickets
4. **Longo prazo**: Implementar categorização automática

## Impacto Técnico

### Código Afetado
- `GLPIService.get_dashboard_metrics()`: Retorna dados de apenas 0,27% dos tickets
- Frontend: Exibe métricas não representativas
- Relatórios: Baseados em amostra muito pequena

### Correções Necessárias
- Adicionar validação de percentual de categorização
- Implementar fallback para outros critérios de agrupamento
- Criar alertas para baixa categorização

---

**Data da Análise**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Responsável**: Sistema de Análise Automatizada
**Status**: Investigação Concluída - Aguardando Ações Corretivas