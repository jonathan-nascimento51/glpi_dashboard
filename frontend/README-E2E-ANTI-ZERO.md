# Teste E2E Anti-Zero Guard

## Visão Geral

Este documento descreve o teste E2E **Anti-Zero Guard** implementado para garantir que o dashboard GLPI exiba dados reais e não valores zerados.

## Objetivo

O teste foi criado para:
-  **VALIDAR** que o dashboard exibe dados reais (soma dos cards > 0)
-  **DETECTAR** quando todos os dados estão zerados (anti-zero guard)
-  **CAPTURAR** screenshots para evidência visual
-  **TESTAR** conectividade com backend

## Estrutura do Teste

### Arquivo Principal
```
e2e/anti-zero-guard.spec.ts
```

### Cenários Implementados

#### 1.  PASS: Dashboard com Dados Reais
- **Objetivo**: Validar que dados reais são exibidos corretamente
- **Mock**: Dados simulados com valores > 0
- **Validação**: Soma dos cards principais > 0
- **Screenshot**: `anti-zero-real-data-pass-{timestamp}.png`

#### 2.  FAIL: Dashboard com Dados Zero (Anti-Zero Guard)
- **Objetivo**: Detectar quando todos os dados são zero
- **Mock**: Todos os valores = 0
- **Comportamento**: Deve falhar com "Anti-zero guard triggered"
- **Screenshot**: `anti-zero-zero-data-fail-{timestamp}.png`

#### 3.  Teste de Conectividade
- **Objetivo**: Verificar se backend está respondendo
- **Comportamento**: Tenta API real, fallback para mock
- **Screenshot**: `connectivity-test-{status}-{timestamp}.png`

#### 4.  Validação de Setup
- **Objetivo**: Verificar se ambiente está configurado
- **Validação**: Diretório `artifacts/e2e` existe

## Dados de Teste

### Dados Reais Simulados
```typescript
const realDataMetrics = {
  niveis: {
    N1: { total: 150, resolvidos: 120, pendentes: 30, tempo_medio: 2.5 },
    N2: { total: 80, resolvidos: 65, pendentes: 15, tempo_medio: 4.2 },
    N3: { total: 45, resolvidos: 35, pendentes: 10, tempo_medio: 8.1 },
    N4: { total: 20, resolvidos: 15, pendentes: 5, tempo_medio: 16.3 }
  },
  total_tickets: 295,
  tickets_pendentes: 60,
  tempo_medio_resolucao: 5.2,
  satisfacao_cliente: 4.2
};
```

### Dados Zero (Para Teste Negativo)
```typescript
const zeroDataMetrics = {
  niveis: {
    N1: { total: 0, resolvidos: 0, pendentes: 0, tempo_medio: 0 },
    // ... todos os níveis com valores 0
  },
  total_tickets: 0,
  tickets_pendentes: 0,
  tempo_medio_resolucao: 0,
  satisfacao_cliente: 0
};
```

## Como Executar

### Teste Completo
```bash
npm run test:e2e -- anti-zero-guard.spec.ts
```

### Teste com Interface Visual
```bash
npm run test:e2e:headed -- anti-zero-guard.spec.ts
```

### Teste Específico
```bash
# Apenas teste PASS
npm run test:e2e -- anti-zero-guard.spec.ts --grep "PASS"

# Apenas teste FAIL
npm run test:e2e -- anti-zero-guard.spec.ts --grep "FAIL"
```

### Validação do Setup
```bash
node validate-anti-zero.cjs
```

## Artefatos Gerados

### Screenshots
Todos os screenshots são salvos em `artifacts/e2e/` com timestamp:
- `anti-zero-real-data-pass-{timestamp}.png`
- `anti-zero-zero-data-fail-{timestamp}.png`
- `connectivity-test-{status}-{timestamp}.png`

### Relatório de Validação
```
artifacts/e2e/anti-zero-validation-report.json
```

Contém:
- Status da validação
- Informações dos screenshots
- Próximos passos
- Configuração dos artifacts

## Seletores de Teste

O teste utiliza os seguintes seletores para extrair dados:

```typescript
const cardSelectors = [
  '[data-testid="total-tickets"]',
  '[data-testid="tickets-pendentes"]',
  '[data-testid="n1-total"]',
  '[data-testid="n1-resolvidos"]',
  '[data-testid="n1-pendentes"]',
  // ... outros seletores por nível
];
```

### Fallback para Seletores Genéricos
Se os seletores específicos não forem encontrados:
```typescript
'[data-testid*="card"], .card, .metric-card'
```

## Validações Anti-Zero

### Critérios de Sucesso (PASS)
1. Soma total dos cards > 0
2. Soma total > 100 (dados significativos)
3. Soma próxima da esperada (tolerância 20%)
4. Elementos principais visíveis

### Critérios de Falha (FAIL)
1. Soma total = 0
2. Trigger do "Anti-zero guard triggered"

## Configuração do Playwright

O teste utiliza a configuração padrão do Playwright:
- **Timeout**: 60 segundos
- **Navegadores**: Chrome, Edge, Safari Mobile
- **Screenshots**: Página completa, animações desabilitadas
- **Aguarda**: `networkidle` para estabilização

## Troubleshooting

### Teste Não Encontra Elementos
1. Verificar se dashboard carregou completamente
2. Verificar seletores `data-testid` nos componentes
3. Usar fallback para seletores genéricos

### Screenshots Não São Gerados
1. Verificar se diretório `artifacts/e2e` existe
2. Executar `node validate-anti-zero.cjs` para diagnóstico

### API Não Responde
1. Verificar se backend está rodando
2. Teste usa fallback automático para dados mockados

## Integração com CI/CD

### GitHub Actions
```yaml
- name: Run Anti-Zero E2E Tests
  run: |
    npm run test:e2e -- anti-zero-guard.spec.ts
    
- name: Upload Screenshots
  uses: actions/upload-artifact@v3
  with:
    name: e2e-screenshots
    path: frontend/artifacts/e2e/
```

### Validação Pré-Deploy
```bash
# Validar antes de deploy
node validate-anti-zero.cjs
npm run test:e2e -- anti-zero-guard.spec.ts --grep "PASS"
```

## Próximos Passos

1. **Integrar com CI**: Adicionar ao pipeline de testes
2. **Alertas**: Configurar notificações quando anti-zero é triggered
3. **Métricas**: Coletar dados sobre frequência de zeros
4. **Expansão**: Adicionar mais cenários de validação

## Comandos Úteis

```bash
# Validação completa
node validate-anti-zero.cjs

# Teste rápido
npm run test:e2e -- anti-zero-guard.spec.ts --timeout=30000

# Ver relatório HTML
npm run test:e2e:ui

# Limpar artifacts
Remove-Item -Recurse -Force artifacts/e2e/*.png
```

---

**Criado em**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Versão**: 1.0.0
**Autor**: Trae AI Assistant
