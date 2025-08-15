# 🚀 Guia de Implementação - Refatoração Arquitetural

## 📋 Pré-requisitos

### 🔧 Ferramentas Necessárias
- Python 3.9+
- Node.js 18+
- Git
- Docker (opcional)
- Redis (para cache)

### 📦 Dependências Python
```bash
pip install fastapi uvicorn aiohttp redis pydantic pytest pytest-asyncio
```

### 📦 Dependências Frontend
```bash
npm install @reduxjs/toolkit react-redux @tanstack/react-query
npm install @types/react @types/node typescript
```

---

## 🎯 Execução Passo a Passo

### 1️⃣ **Preparação (5 minutos)**

```bash
# 1. Fazer backup do código atual
git add .
git commit -m "Backup antes da refatoração arquitetural"
git branch backup-pre-refactoring

# 2. Verificar estrutura atual
ls -la backend/
ls -la frontend/src/

# 3. Testar script de migração (simulação)
python migration_script.py --phase 1 --dry-run
```

### 2️⃣ **Fase 1: Fundação (30 minutos)**

```bash
# Executar criação da estrutura base
python migration_script.py --phase 1

# Verificar estrutura criada
tree backend/core/ -I "__pycache__"
tree frontend/src/features/ -I "node_modules"

# Instalar dependências
pip install -r requirements.txt
npm install
```

**✅ Checkpoint 1:**
- [ ] Estrutura de diretórios criada
- [ ] Arquivos `__init__.py` em todas as pastas Python
- [ ] Arquivos `index.ts` nas features TypeScript
- [ ] Dependências instaladas

### 3️⃣ **Fase 2: Domínio (45 minutos)**

```bash
# Executar criação das entidades de domínio
python migration_script.py --phase 2

# Testar entidades criadas
python -c "from backend.core.domain.entities.ticket import Ticket; print('✅ Ticket entity OK')"
python -c "from backend.core.domain.value_objects.ticket_status import TicketStatus; print('✅ TicketStatus OK')"

# Executar testes básicos
pytest backend/tests/unit/domain/ -v
```

**✅ Checkpoint 2:**
- [ ] Entidades de domínio funcionando
- [ ] Value objects implementados
- [ ] Serviços de domínio criados
- [ ] Interfaces de repositório definidas
- [ ] Testes básicos passando

### 4️⃣ **Fase 3: Aplicação (60 minutos)**

```bash
# Executar criação da camada de aplicação
python migration_script.py --phase 3

# Testar DTOs
python -c "from backend.core.application.dto.dashboard_dto import DashboardMetricsDTO; print('✅ DTOs OK')"

# Testar casos de uso
pytest backend/tests/unit/application/ -v
```

**✅ Checkpoint 3:**
- [ ] DTOs implementados
- [ ] Casos de uso criados
- [ ] Interfaces de serviços definidas
- [ ] Validações funcionando

### 5️⃣ **Fase 4: Infraestrutura (90 minutos)**

```bash
# Executar criação da infraestrutura
python migration_script.py --phase 4

# Configurar variáveis de ambiente
cp .env.example .env.new
# Editar .env.new com as configurações da nova arquitetura

# Testar cliente GLPI
python -c "from backend.core.infrastructure.external.glpi.client import GLPIClient; print('✅ GLPI Client OK')"

# Testar cache Redis (se disponível)
python -c "from backend.core.infrastructure.services.redis_cache_service import RedisCacheService; print('✅ Redis Cache OK')"
```

**✅ Checkpoint 4:**
- [ ] Cliente GLPI implementado
- [ ] Repositórios de infraestrutura criados
- [ ] Serviço de cache funcionando
- [ ] Mapeadores de resposta implementados

---

## 🔧 Configuração da Nova Arquitetura

### 📄 **Arquivo de Configuração (.env.new)**

```env
# GLPI Configuration
GLPI_BASE_URL=https://seu-glpi.com/apirest.php
GLPI_APP_TOKEN=seu_app_token
GLPI_USER_TOKEN=seu_user_token

# Cache Configuration
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# Database Configuration (se necessário)
DATABASE_URL=sqlite:///./glpi_dashboard.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_CACHE_ENABLED=true
REACT_APP_REFRESH_INTERVAL=30000
```

### 🏗️ **Arquivo de Injeção de Dependência**

Criar `backend/core/infrastructure/config/dependencies.py`:

```python
from functools import lru_cache
from backend.core.domain.repositories.ticket_repository import TicketRepository
from backend.core.application.interfaces.cache_service import CacheService
from backend.core.application.use_cases.get_dashboard_metrics import GetDashboardMetrics
from backend.core.infrastructure.repositories.glpi_ticket_repository import GLPITicketRepository
from backend.core.infrastructure.services.redis_cache_service import RedisCacheService
from backend.core.infrastructure.external.glpi.client import GLPIClient
from backend.core.domain.services.metric_calculator import MetricCalculator
import os

@lru_cache()
def get_glpi_client() -> GLPIClient:
    return GLPIClient(
        base_url=os.getenv('GLPI_BASE_URL'),
        app_token=os.getenv('GLPI_APP_TOKEN'),
        user_token=os.getenv('GLPI_USER_TOKEN')
    )

@lru_cache()
def get_cache_service() -> CacheService:
    return RedisCacheService(os.getenv('REDIS_URL', 'redis://localhost:6379'))

@lru_cache()
def get_ticket_repository() -> TicketRepository:
    return GLPITicketRepository(
        glpi_client=get_glpi_client(),
        response_mapper=None  # Implementar mapper
    )

@lru_cache()
def get_dashboard_metrics_use_case() -> GetDashboardMetrics:
    return GetDashboardMetrics(
        ticket_repository=get_ticket_repository(),
        cache_service=get_cache_service(),
        metric_calculator=MetricCalculator()
    )
```

---

## 🧪 Estratégia de Testes

### 🔬 **Testes Unitários**

```bash
# Testar domínio
pytest backend/tests/unit/domain/ -v --cov=backend.core.domain

# Testar aplicação
pytest backend/tests/unit/application/ -v --cov=backend.core.application

# Testar infraestrutura
pytest backend/tests/unit/infrastructure/ -v --cov=backend.core.infrastructure
```

### 🔗 **Testes de Integração**

```bash
# Testar integração com GLPI
pytest backend/tests/integration/ -v -m "glpi"

# Testar integração com cache
pytest backend/tests/integration/ -v -m "cache"
```

### 🌐 **Testes E2E**

```bash
# Frontend
npm run test:e2e

# API
pytest backend/tests/e2e/ -v
```

---

## 🚀 Migração Gradual do Código Existente

### 📝 **Checklist de Migração**

#### **Backend - GLPIService → Nova Arquitetura**

- [ ] **Autenticação GLPI**
  - [ ] Migrar para `GLPIClient.authenticate()`
  - [ ] Testar conexão
  - [ ] Validar tokens

- [ ] **Busca de Tickets**
  - [ ] Migrar para `GLPITicketRepository.get_tickets_by_date_range()`
  - [ ] Implementar filtros
  - [ ] Testar paginação

- [ ] **Cálculo de Métricas**
  - [ ] Migrar para `MetricCalculator.calculate_status_metrics()`
  - [ ] Validar consistência
  - [ ] Testar edge cases

- [ ] **Sistema de Cache**
  - [ ] Migrar para `RedisCacheService`
  - [ ] Configurar TTL
  - [ ] Testar invalidação

- [ ] **Ranking de Técnicos**
  - [ ] Criar `TechnicianRankingService`
  - [ ] Implementar classificação por nível
  - [ ] Migrar lógica existente

#### **Frontend - Componentes → Features**

- [ ] **Dashboard Principal**
  - [ ] Migrar `App.tsx` → `features/dashboard/`
  - [ ] Separar responsabilidades
  - [ ] Implementar hooks especializados

- [ ] **Gerenciamento de Estado**
  - [ ] Migrar para Redux Toolkit
  - [ ] Criar slices por feature
  - [ ] Implementar middleware de cache

- [ ] **Componentes de UI**
  - [ ] Migrar para `shared/components/ui/`
  - [ ] Padronizar props
  - [ ] Adicionar testes

---

## 📊 Validação da Migração

### ✅ **Critérios de Sucesso**

1. **Funcionalidade Preservada**
   - [ ] Dashboard carrega corretamente
   - [ ] Métricas são calculadas corretamente
   - [ ] Filtros funcionam
   - [ ] Ranking é exibido

2. **Performance Mantida/Melhorada**
   - [ ] Tempo de carregamento ≤ anterior
   - [ ] Cache funcionando
   - [ ] Sem vazamentos de memória

3. **Qualidade do Código**
   - [ ] Cobertura de testes ≥ 80%
   - [ ] Linting sem erros
   - [ ] Documentação atualizada

4. **Consistência de Dados**
   - [ ] Métricas gerais = soma dos níveis
   - [ ] Sem inconsistências entre endpoints
   - [ ] Validações funcionando

### 🔍 **Scripts de Validação**

Criar `validation_script.py`:

```python
#!/usr/bin/env python3
"""
Script de Validação da Migração
Verifica se a nova arquitetura está funcionando corretamente
"""

import asyncio
import sys
from backend.core.application.use_cases.get_dashboard_metrics import GetDashboardMetrics
from backend.core.infrastructure.config.dependencies import (
    get_dashboard_metrics_use_case,
    get_ticket_repository,
    get_cache_service
)

async def validate_architecture():
    """Valida a nova arquitetura"""
    print("🔍 Validando nova arquitetura...")
    
    try:
        # Testar caso de uso
        use_case = get_dashboard_metrics_use_case()
        metrics = await use_case.execute()
        
        print(f"✅ Métricas obtidas: {metrics.total_tickets} tickets")
        print(f"✅ Métricas gerais: {metrics.general_metrics}")
        
        # Validar consistência
        total_by_levels = sum(
            sum(level_metrics.values()) 
            for level_metrics in metrics.level_metrics.values()
        )
        
        general_total = sum(metrics.general_metrics.values())
        
        if abs(total_by_levels - general_total) < 5:  # Tolerância de 5
            print("✅ Consistência de dados OK")
        else:
            print(f"❌ Inconsistência detectada: {total_by_levels} vs {general_total}")
            return False
        
        # Testar cache
        cache_service = get_cache_service()
        await cache_service.set("test_key", "test_value", 60)
        cached_value = await cache_service.get("test_key")
        
        if cached_value == "test_value":
            print("✅ Cache funcionando")
        else:
            print("❌ Cache não funcionando")
            return False
        
        print("🎉 Validação concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_architecture())
    sys.exit(0 if success else 1)
```

---

## 🎯 Próximos Passos

### 🚀 **Implementação Imediata (Hoje)**
1. Executar Fase 1 (Fundação)
2. Configurar ambiente de desenvolvimento
3. Instalar dependências
4. Executar testes básicos

### 📅 **Esta Semana**
1. Implementar Fases 2 e 3 (Domínio + Aplicação)
2. Migrar funcionalidades críticas
3. Configurar CI/CD para nova estrutura
4. Documentar APIs

### 📅 **Próxima Semana**
1. Implementar Fase 4 (Infraestrutura)
2. Migrar frontend para features
3. Testes de integração completos
4. Deploy em ambiente de teste

### 📅 **Mês Seguinte**
1. Otimizações de performance
2. Monitoramento avançado
3. Documentação completa
4. Deploy em produção

---

## 🆘 Troubleshooting

### ❓ **Problemas Comuns**

**Erro: "Module not found"**
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou instalar em modo desenvolvimento
pip install -e .
```

**Erro: "Redis connection failed"**
```bash
# Instalar e iniciar Redis
sudo apt-get install redis-server
sudo systemctl start redis-server

# Ou usar Docker
docker run -d -p 6379:6379 redis:alpine
```

**Erro: "GLPI authentication failed"**
```bash
# Verificar tokens no .env
echo $GLPI_APP_TOKEN
echo $GLPI_USER_TOKEN

# Testar conexão manual
curl -X GET "$GLPI_BASE_URL/initSession" \
  -H "App-Token: $GLPI_APP_TOKEN" \
  -H "Authorization: user_token $GLPI_USER_TOKEN"
```

### 📞 **Suporte**

Se encontrar problemas:
1. Verificar logs em `backend/logs/`
2. Executar testes de diagnóstico
3. Consultar documentação da API
4. Criar issue no repositório

---

## 🎉 Conclusão

Esta refatoração transformará o projeto em uma base sólida e escalável:

- ✅ **Código modular e testável**
- ✅ **Arquitetura limpa e bem definida**
- ✅ **Facilidade de manutenção**
- ✅ **Preparado para desenvolvimento com IA**
- ✅ **Eliminação de inconsistências**

**Tempo estimado total: 4-6 horas de implementação ativa**

**Resultado: Base arquitetural sólida para desenvolvimento futuro sem problemas recorrentes.**