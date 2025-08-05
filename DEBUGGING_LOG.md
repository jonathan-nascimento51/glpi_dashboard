# Log de Debugging - GLPI Dashboard

## Problemas Resolvidos

### ❌ RESOLVIDO: Dados Zerados no Dashboard (2025-01-XX)
**Sintoma**: Dashboard exibindo dados zerados  
**Causa Real**: `ReferenceError: currentDateRange is not defined`  
**Solução**: Manter variável definida mas não passar para API  
**Arquivos**: `frontend/src/hooks/useDashboard.ts:135,211`  
**Status**: ✅ Corrigido

### ❌ RESOLVIDO: Filtro de Data Automático (2025-01-XX)
**Sintoma**: Métricas retornando vazias com filtro de data  
**Causa Real**: Backend processando filtro incorretamente  
**Solução Temporária**: Remover filtro automático  
**Status**: 🔄 Solução temporária aplicada

## Problemas Conhecidos

### 🔄 EM INVESTIGAÇÃO: Filtro de Data Backend
**Descrição**: `get_dashboard_metrics_with_date_filter` retorna dados zerados  
**Próximos Passos**: Investigar processamento de datas no GLPI Service  
**Arquivos**: `backend/services/glpi_service.py:537-680`