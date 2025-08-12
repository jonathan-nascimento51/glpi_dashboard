# Diagnóstico Completo - GLPI Dashboard

##  Resumo Executivo

Este documento apresenta um diagnóstico completo dos problemas identificados no projeto GLPI Dashboard, incluindo correções necessárias, melhorias e implementação de testes robustos.

##  Problemas Críticos Identificados

### 1. Erro no Health Check - MetricsLevelsResponse

**Problema:** `'MetricsLevelsResponse' object has no attribute 'get'`

**Localização:** `backend/api/v1/metrics_levels.py:180`

**Causa:** O código está tentando usar `.get()` em um objeto Pydantic `MetricsLevelsResponse` como se fosse um dicionário.

**Correção:**
```python
# ANTES (linha 180)
status = "healthy" if result.get("status") == "healthy" else "unhealthy"

# DEPOIS
status = "healthy" if hasattr(result, 'aggregated_metrics') and result.aggregated_metrics else "unhealthy"
```

### 2. Problemas de Importação nos Testes

**Problema:** `ModuleNotFoundError: No module named 'backend'`

**Causa:** Estrutura de importações inconsistente entre desenvolvimento e testes.

**Correção:** Padronizar importações relativas e configurar PYTHONPATH corretamente.

### 3. Falhas Massivas nos Testes do Frontend

**Problema:** 65 testes falhando de 426 total (15% de falha)

**Causa:** Problemas de configuração do ambiente de teste e dependências.

##  Análise de Qualidade de Código

### Backend - Ruff Lint Results
- **80 erros encontrados**
- **51 corrigíveis automaticamente**
- **18 correções unsafe disponíveis**

**Principais problemas:**
- Imports não utilizados
- Variáveis não utilizadas
- Problemas de formatação

### Cobertura de Testes
- **Meta configurada:** 80% (arquivo .coveragerc)
- **Status atual:** Não medido devido a problemas de execução

##  Plano de Correções

### Fase 1: Correções Críticas (Prioridade Alta)

#### 1.1 Corrigir Health Check
```python
# Arquivo: backend/api/v1/metrics_levels.py
@router.get("/levels/health")
async def metrics_levels_health() -> JSONResponse:
    try:
        query_params = MetricsLevelsQueryParams()
        use_case = MetricsLevelsUseCase()
        result = await use_case.get_metrics_by_level(query_params)
        
        # Correção: verificar se o resultado é válido
        is_healthy = (
            result is not None and 
            hasattr(result, 'aggregated_metrics') and 
            result.aggregated_metrics is not None
        )
        
        status = "healthy" if is_healthy else "unhealthy"
        status_code = 200 if is_healthy else 503
        
        return JSONResponse(
            content={
                "status": status,
                "service": "metrics-levels",
                "timestamp": datetime.now().isoformat(),
                "test_result": {
                    "success": is_healthy,
                    "total_levels": len(result.metrics_by_level) if is_healthy else 0
                }
            },
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "metrics-levels",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            },
            status_code=503
        )
```

#### 1.2 Corrigir Estrutura de Testes
```python
# Arquivo: backend/tests/conftest.py
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importações corrigidas
from services.glpi_service import GLPIService
```

#### 1.3 Corrigir Problemas de Lint
```bash
# Executar correções automáticas
python -m ruff check . --fix
python -m ruff format .
```

### Fase 2: Melhorias de Robustez (Prioridade Média)

#### 2.1 Implementar Testes para MetricsLevelsUseCase
```python
# Arquivo: backend/tests/unit/usecases/test_metrics_levels_usecase.py
import pytest
from unittest.mock import Mock, patch
from backend.usecases.metrics_levels_usecase import MetricsLevelsUseCase
from backend.schemas.metrics_levels import MetricsLevelsQueryParams, ServiceLevel

class TestMetricsLevelsUseCase:
    @pytest.fixture
    def use_case(self):
        return MetricsLevelsUseCase()
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_level_success(self, use_case):
        """Testa execução bem-sucedida do use case"""
        params = MetricsLevelsQueryParams()
        result = await use_case.get_metrics_by_level(params)
        
        assert result is not None
        assert hasattr(result, 'metrics_by_level')
        assert hasattr(result, 'aggregated_metrics')
        assert len(result.metrics_by_level) > 0
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, use_case):
        """Testa health check bem-sucedido"""
        result = await use_case.health_check()
        
        assert result["status"] == "healthy"
        assert "service" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_specific_levels(self, use_case):
        """Testa filtro por níveis específicos"""
        params = MetricsLevelsQueryParams(
            levels=[ServiceLevel.N1, ServiceLevel.N2]
        )
        result = await use_case.get_metrics_by_level(params)
        
        assert result is not None
        # Verificar se apenas N1 e N2 estão presentes
        levels = [metric.level for metric in result.metrics_by_level]
        assert ServiceLevel.N1 in levels
        assert ServiceLevel.N2 in levels
```

##  Métricas de Qualidade Propostas

### Cobertura de Testes
- **Backend:** Mínimo 85%
- **Frontend:** Mínimo 80%
- **Integração:** 100% dos endpoints críticos

### Performance
- **API Response Time:** < 300ms (P95)
- **Frontend Load Time:** < 2s
- **Health Check:** < 100ms

### Qualidade de Código
- **Ruff:** 0 erros
- **TypeScript:** 0 erros
- **Complexity:** Máximo 10 por função

##  Cronograma de Implementação

### Semana 1: Correções Críticas
- [ ] Corrigir health check do MetricsLevelsResponse
- [ ] Resolver problemas de importação nos testes
- [ ] Executar correções automáticas de lint

### Semana 2: Testes Robustos
- [ ] Implementar testes unitários para MetricsLevelsUseCase
- [ ] Criar testes de integração para APIs críticas
- [ ] Configurar testes E2E básicos

### Semana 3: Melhorias de Infraestrutura
- [ ] Implementar monitoramento de performance
- [ ] Criar script de validação automática
- [ ] Configurar CI/CD completo

### Semana 4: Validação e Documentação
- [ ] Executar validação completa do sistema
- [ ] Documentar processos de troubleshooting
- [ ] Treinar equipe nos novos processos

##  Comandos de Manutenção

### Execução de Testes
```bash
# Backend
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html

# Frontend
cd frontend
npm run test:unit
npm run test:e2e

# Validação completa
python scripts/validate_system.py
```

### Correção de Qualidade
```bash
# Backend
cd backend
python -m ruff check . --fix
python -m ruff format .

# Frontend
cd frontend
npm run lint:fix
npm run format
```

### Monitoramento
```bash
# Verificar logs em tempo real
tail -f backend/logs/app.log

# Verificar métricas de performance
curl http://localhost:8000/api/v1/metrics/performance
```

##  Checklist de Validação

### Antes de Deploy
- [ ] Todos os testes passando
- [ ] Cobertura de testes > 80%
- [ ] Lint sem erros
- [ ] Health checks funcionando
- [ ] Performance dentro dos targets
- [ ] Logs estruturados funcionando
- [ ] Validação E2E bem-sucedida

### Pós Deploy
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Backup de dados
- [ ] Rollback plan testado

---

**Data de criação:** 2025-01-12  
**Versão:** 1.0  
**Responsável:** Equipe de Desenvolvimento  
**Próxima revisão:** 2025-01-19
