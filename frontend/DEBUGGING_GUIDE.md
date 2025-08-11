# Guia de Diagnóstico do Problema do Ranking

Este guia contém instruções para diagnosticar o problema onde o ranking de técnicos desaparece após o refresh da página.

## 🛠️ Ferramentas de Diagnóstico Implementadas

Foram criadas várias ferramentas de diagnóstico que estão disponíveis no console do navegador:

### 1. Monitor Automático do Ranking
- **Ativo automaticamente** quando a aplicação carrega
- Monitora mudanças no DOM e estado do ranking em tempo real
- Detecta quando os dados desaparecem

### 2. Verificação Rápida
- `quickRankingCheck()` ou `qrc()` - Verifica o estado atual do ranking
- `testApiQuick()` - Testa se a API está respondendo
- `forceRankingRefresh()` ou `frr()` - Força um refresh dos dados
- `watchRankingChanges(10000)` ou `wrc(10000)` - Monitora por 10 segundos

### 3. Diagnóstico Completo
- `runRankingDiagnostic()` - Executa um diagnóstico completo
- `rankingReport()` - Gera relatório do monitor

## 📋 Como Reproduzir e Diagnosticar o Problema

### Passo 1: Abrir o Console do Navegador
1. Abra o dashboard no navegador: http://localhost:3001/
2. Pressione F12 para abrir as ferramentas de desenvolvedor
3. Vá para a aba "Console"

### Passo 2: Verificar Estado Inicial
```javascript
// Verificar se o ranking está sendo exibido
qrc()
```

### Passo 3: Reproduzir o Problema
1. **Certifique-se de que o ranking está visível** na primeira carga
2. **Pressione F5 ou Ctrl+R** para fazer refresh da página
3. **Observe se o ranking desaparece**

### Passo 4: Diagnosticar Após o Refresh
```javascript
// Verificação rápida após o refresh
qrc()

// Diagnóstico completo
runRankingDiagnostic()

// Verificar relatório do monitor
rankingReport()
```

### Passo 5: Tentar Forçar Recuperação
```javascript
// Tentar forçar refresh dos dados
frr()

// Aguardar alguns segundos e verificar novamente
setTimeout(() => qrc(), 3000)
```

## 🔍 O Que Observar

### Indicadores de Problema
- ✅ **Dados visíveis: NÃO** - Ranking não está sendo exibido
- 💾 **Dados em cache: X itens** - Mas não aparecem na tela
- 🌐 **API Status: 200 OK** - API funciona mas dados não chegam ao componente

### Possíveis Causas Identificadas
1. **Problema de Cache**: Dados existem no cache mas não são carregados
2. **Problema de Renderização**: React não está re-renderizando o componente
3. **Problema de Estado**: Hook `useDashboard` não está atualizando o estado
4. **Problema de Dependências**: `useEffect` não está sendo disparado corretamente

## 🚨 Logs Importantes

O monitor automático registra logs importantes. Procure por:

```
🔍 [RANKING MONITOR] initial: { hasData: true, dataLength: 5, ... }
🔍 [RANKING MONITOR] after_load: { hasData: false, dataLength: 0, ... }
⚠️ DADOS DO RANKING DESAPARECERAM!
```

## 🔧 Comandos de Emergência

### Limpar Todo o Cache
```javascript
// Limpar localStorage
localStorage.clear()

// Limpar cache do navegador (se necessário)
caches.keys().then(names => {
  names.forEach(name => caches.delete(name))
})
```

### Forçar Recarregamento Completo
```javascript
// Refresh forçado (ignora cache)
location.reload(true)
```

### Monitoramento Contínuo
```javascript
// Monitorar por 30 segundos
wrc(30000)

// Parar monitoramento
stopRankingMonitor()
```

## 📊 Interpretando os Resultados

### Cenário 1: API OK, Cache OK, DOM Vazio
**Problema**: Renderização do React
**Solução**: Verificar dependências do `useEffect` no `useDashboard`

### Cenário 2: API OK, Cache Vazio, DOM Vazio
**Problema**: Dados não estão sendo salvos no cache
**Solução**: Verificar função `getTechnicianRanking`

### Cenário 3: API Erro, Cache Vazio, DOM Vazio
**Problema**: Backend não está respondendo
**Solução**: Verificar se o backend está rodando

### Cenário 4: API OK, Cache OK, DOM OK
**Problema**: Falso positivo - ranking está funcionando
**Solução**: Verificar se o problema é visual/CSS

## 🎯 Próximos Passos

Com base nos resultados do diagnóstico:

1. **Se o problema for de renderização**: Verificar `RankingTable.tsx` e `ModernDashboard.tsx`
2. **Se o problema for de estado**: Verificar `useDashboard.ts`
3. **Se o problema for de API**: Verificar `api.ts` e backend
4. **Se o problema for de cache**: Verificar lógica de cache no `useDashboard`

## 📞 Suporte

Se precisar de ajuda adicional:
1. Execute `runRankingDiagnostic()` e copie o resultado
2. Execute `rankingReport()` e copie o relatório
3. Forneça os logs do console junto com a descrição do problema