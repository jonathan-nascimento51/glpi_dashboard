# 🔍 Guia de Debug do Ranking de Técnicos

## Problema Identificado
O ranking de técnicos desaparece após o primeiro refresh da interface, causando inconsistência no funcionamento.

## Ferramentas de Debug Implementadas

### 1. 📊 Painel de Debug Visual
- **Localização**: Botão "Debug Ranking" no canto inferior direito da tela
- **Funcionalidades**:
  - Visualização de logs em tempo real
  - Filtros por categoria (ranking, cache, API, etc.)
  - Auto-refresh dos logs
  - Exportação de logs
  - Análise do fluxo do ranking

### 2. 🧪 Script de Teste Automatizado
- **Acesso**: Console do navegador (F12)
- **Comandos disponíveis**:
  ```javascript
  // Executar todos os testes
  testRanking.runAll()
  
  // Executar teste específico
  testRanking.runSingle('refresh_simulation')
  
  // Ver resultados dos testes
  testRanking.getResults()
  
  // Limpar resultados
  testRanking.clearResults()
  ```

### 3. 📝 Sistema de Logs Detalhado
- **Rastreamento completo** do fluxo de dados do ranking
- **Logs categorizados** por fonte (API, cache, componentes)
- **Timestamps precisos** para análise temporal
- **Dados estruturados** para facilitar debugging

## Como Diagnosticar o Problema

### Passo 1: Ativar o Painel de Debug
1. Abra a aplicação no navegador
2. Clique no botão "Debug Ranking" (canto inferior direito)
3. O painel de debug será exibido

### Passo 2: Observar o Carregamento Inicial
1. Recarregue a página (F5)
2. Observe os logs no painel de debug
3. Verifique se aparecem logs relacionados ao ranking:
   - `ranking_data_loaded`
   - `component_data_received`
   - `api_data_mapped`

### Passo 3: Simular o Problema
1. Aguarde o carregamento completo
2. Faça um refresh da página (F5)
3. Compare os logs antes e depois do refresh
4. Procure por diferenças nos dados do ranking

### Passo 4: Executar Testes Automatizados
1. Abra o console do navegador (F12)
2. Execute: `testRanking.runAll()`
3. Aguarde a conclusão dos testes
4. Analise o relatório gerado

### Passo 5: Analisar Resultados
1. Verifique o relatório de testes
2. Identifique cenários que falharam
3. Examine os logs detalhados
4. Foque nos problemas de cache e API

## Cenários de Teste Implementados

### 1. `initial_load`
- **Objetivo**: Verificar se o ranking carrega corretamente na primeira vez
- **Indicadores**: Presença de dados de ranking nos logs

### 2. `refresh_simulation`
- **Objetivo**: Simular o refresh da página e verificar se o ranking persiste
- **Indicadores**: Dados de ranking após limpeza de cache

### 3. `cache_behavior`
- **Objetivo**: Analisar eficiência e comportamento do cache
- **Indicadores**: Taxa de acerto/erro do cache

### 4. `api_calls_analysis`
- **Objetivo**: Verificar confiabilidade das chamadas de API
- **Indicadores**: Taxa de sucesso das requisições

## Possíveis Causas do Problema

### 1. 🗄️ Problemas de Cache
- Cache sendo invalidado incorretamente no refresh
- TTL (Time To Live) muito baixo
- Chaves de cache inconsistentes

### 2. 🌐 Problemas de API
- Requisições falhando após refresh
- Dados não sendo retornados corretamente
- Timeout de requisições

### 3. ⚛️ Problemas de Estado React
- Estado não sendo preservado entre renders
- useEffect executando incorretamente
- Dependências de hooks mal configuradas

### 4. 🔄 Problemas de Sincronização
- Race conditions entre requisições
- Dados sendo sobrescritos
- Ordem de execução incorreta

## Soluções Potenciais

### 1. Melhorar Cache
```typescript
// Aumentar TTL do cache
const CACHE_TTL = 300000; // 5 minutos

// Implementar cache persistente
localStorage.setItem('ranking_cache', JSON.stringify(data));
```

### 2. Implementar Retry
```typescript
// Retry automático para chamadas de API
const fetchWithRetry = async (url, options, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url, options);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

### 3. Melhorar Gerenciamento de Estado
```typescript
// Usar useCallback para estabilizar funções
const loadRanking = useCallback(async () => {
  // lógica de carregamento
}, [filters]);

// Usar useMemo para dados derivados
const processedRanking = useMemo(() => {
  return ranking.map(/* processamento */);
}, [ranking]);
```

## Comandos Úteis para Debug

```javascript
// Ver todos os logs
RankingDebugger.getLogs()

// Analisar fluxo do ranking
RankingDebugger.analyzeRankingFlow()

// Exportar logs para arquivo
RankingDebugger.exportLogs()

// Limpar logs
RankingDebugger.clearLogs()

// Executar análise específica
testRanking.runSingle('cache_behavior')
```

## Próximos Passos

1. **Execute os testes** usando as ferramentas implementadas
2. **Identifique o cenário** que está falhando
3. **Analise os logs** para encontrar a causa raiz
4. **Implemente a correção** baseada nos achados
5. **Valide a solução** executando os testes novamente

## Suporte

Se precisar de ajuda adicional:
1. Execute `testRanking.runAll()` no console
2. Copie o relatório gerado
3. Compartilhe os logs do painel de debug
4. Descreva o comportamento observado

---

**Nota**: Todas as ferramentas de debug são carregadas apenas em modo de desenvolvimento e não afetam a performance em produção.