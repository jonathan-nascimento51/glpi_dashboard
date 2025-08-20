# Refatoração Progressiva - Guia Completo

Este documento descreve a implementação da refatoração progressiva no projeto GLPI Dashboard, permitindo migrar gradualmente do sistema legado para uma nova arquitetura sem interrupções.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Fases da Refatoração](#fases-da-refatoração)
- [Configuração](#configuração)
- [Uso Prático](#uso-prático)
- [Monitoramento](#monitoramento)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

A refatoração progressiva implementa o padrão **Strangler Fig** para permitir uma migração segura e gradual do sistema legado para uma nova arquitetura baseada em:

- **DTOs Pydantic** para estruturas de dados tipadas
- **Query Objects** para isolamento da lógica de consulta
- **Adapters** para abstração de APIs externas
- **Dependency Injection** para flexibilidade e testabilidade

### Benefícios

✅ **Zero Downtime**: Migração sem interrupção do serviço  
✅ **Rollback Seguro**: Possibilidade de voltar ao sistema legado instantaneamente  
✅ **Validação Contínua**: Comparação automática entre sistemas  
✅ **Migração Gradual**: Controle fino sobre o percentual de tráfego migrado  
✅ **Observabilidade**: Monitoramento detalhado de performance e dados  

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Flask Routes  │────│ Progressive Service  │────│  Legacy System  │
└─────────────────┘    └──────────────────────┘    └─────────────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │  New Architecture   │
                        │                     │
                        │ ┌─────────────────┐ │
                        │ │   Query Layer   │ │
                        │ └─────────────────┘ │
                        │ ┌─────────────────┐ │
                        │ │  Adapter Layer  │ │
                        │ └─────────────────┘ │
                        │ ┌─────────────────┐ │
                        │ │   DTO Layer     │ │
                        │ └─────────────────┘ │
                        └─────────────────────┘
```

### Componentes Principais

#### 1. Progressive Refactoring Service
```python
class ProgressiveRefactoringService:
    """Orquestra a migração entre sistemas legado e novo."""
    
    async def get_dashboard_metrics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém métricas usando estratégia baseada na fase atual."""
```

#### 2. Refactoring Controller
```python
class RefactoringController:
    """Integra o serviço de refatoração com rotas Flask."""
    
    async def handle_metrics_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisições de métricas com refatoração."""
```

#### 3. Configuration Management
```python
class RefactoringConfig:
    """Configuração da refatoração progressiva."""
    
    phase: RefactoringPhase
    migration_percentage: float
    enable_validation: bool
    validation_sampling: float
```

## 🔄 Fases da Refatoração

### Fase 1: Legacy Only
```python
RefactoringPhase.LEGACY_ONLY
```

- **Comportamento**: 100% do tráfego vai para o sistema legado
- **Uso**: Estado inicial, sistema em produção atual
- **Risco**: Mínimo
- **Monitoramento**: Baseline de performance

### Fase 2: Strangler Fig
```python
RefactoringPhase.STRANGLER_FIG
```

- **Comportamento**: Migração gradual do tráfego (configurável)
- **Uso**: Migração progressiva com fallback automático
- **Risco**: Baixo a médio (dependendo do percentual)
- **Monitoramento**: Comparação de performance e dados

**Exemplo de progressão:**
```bash
# 5% do tráfego para nova arquitetura
python scripts/configure_refactoring.py --phase strangler_fig --migration-percentage 0.05

# 25% do tráfego
python scripts/configure_refactoring.py --migration-percentage 0.25

# 50% do tráfego
python scripts/configure_refactoring.py --migration-percentage 0.50

# 100% do tráfego
python scripts/configure_refactoring.py --migration-percentage 1.0
```

### Fase 3: Validation
```python
RefactoringPhase.VALIDATION
```

- **Comportamento**: Sistema legado serve requisições, nova arquitetura executa em paralelo
- **Uso**: Validação de dados e performance sem impacto no usuário
- **Risco**: Mínimo (shadow mode)
- **Monitoramento**: Detecção de divergências

```bash
# Habilitar validação com 10% de sampling
python scripts/configure_refactoring.py --phase validation --enable-validation --validation-sampling 0.1
```

### Fase 4: New Architecture
```python
RefactoringPhase.NEW_ARCHITECTURE
```

- **Comportamento**: 100% do tráfego vai para a nova arquitetura
- **Uso**: Estado final da migração
- **Risco**: Médio (nova arquitetura em produção)
- **Monitoramento**: Performance e estabilidade

## ⚙️ Configuração

### Arquivo de Configuração

Crie `config/refactoring_config.json`:

```json
{
  "refactoring": {
    "phase": "legacy_only",
    "migration_percentage": 0.0,
    "endpoints_to_migrate": [],
    "enable_validation": false,
    "validation_sampling": 0.1,
    "enable_fallback": true,
    "fallback_timeout_ms": 5000,
    "log_performance_comparison": true,
    "log_data_differences": true
  },
  "glpi": {
    "base_url": "https://glpi.example.com",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "correlation_sampling": 1.0
  }
}
```

### Variáveis de Ambiente

```bash
# Fase da refatoração
export REFACTORING_PHASE=strangler_fig

# Percentual de migração
export MIGRATION_PERCENTAGE=0.1

# Validação
export ENABLE_VALIDATION=true
export VALIDATION_SAMPLING=0.05

# Fallback
export ENABLE_FALLBACK=true
export FALLBACK_TIMEOUT_MS=5000

# GLPI
export GLPI_BASE_URL=https://glpi.example.com
export GLPI_TIMEOUT=30
```

### Script de Configuração

```bash
# Mostrar status atual
python scripts/configure_refactoring.py --status

# Configurar fase
python scripts/configure_refactoring.py --phase strangler_fig

# Configurar percentual de migração
python scripts/configure_refactoring.py --migration-percentage 0.1

# Habilitar validação
python scripts/configure_refactoring.py --enable-validation --validation-sampling 0.05

# Adicionar endpoint específico para migração
python scripts/configure_refactoring.py --add-endpoint /api/metrics

# Exportar configurações como .env
python scripts/configure_refactoring.py --export-env .env

# Criar plano de migração
python scripts/configure_refactoring.py --create-plan new_architecture
```

## 🚀 Uso Prático

### 1. Integração com Flask

```python
from integration.progressive_refactoring_integration import setup_progressive_refactoring

app = Flask(__name__)

# Configurar refatoração progressiva
setup_progressive_refactoring(
    app=app,
    glpi_config={
        "base_url": "https://glpi.example.com",
        "timeout": 30
    },
    refactoring_phase="strangler_fig",
    migration_percentage=0.1
)
```

### 2. Rotas com Refatoração

```python
from core.application.controllers import create_refactoring_blueprint

# Criar blueprint com refatoração
refactoring_bp = create_refactoring_blueprint(
    legacy_service=legacy_service,
    glpi_config=glpi_config,
    refactoring_config=refactoring_config
)

# Registrar blueprint
app.register_blueprint(refactoring_bp, url_prefix='/api/v2')
```

### 3. Exemplo de Migração Gradual

```python
# Exemplo de aplicação com refatoração
from examples.progressive_refactoring_example import create_example_app

app = create_example_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Endpoints disponíveis:**
- `GET /api/metrics` - Métricas (com refatoração)
- `GET /api/technicians/ranking` - Ranking de técnicos
- `GET /admin/refactoring/status` - Status da refatoração
- `POST /admin/refactoring/phase` - Alterar fase
- `POST /admin/refactoring/migration-percentage` - Alterar percentual

### 4. Plano de Migração Recomendado

#### Semana 1: Preparação
```bash
# 1. Configurar validação com 5% de sampling
python scripts/configure_refactoring.py --phase validation --enable-validation --validation-sampling 0.05

# 2. Monitorar logs por 48h
# 3. Analisar divergências e corrigir
```

#### Semana 2: Migração Inicial
```bash
# 1. Migrar 5% do tráfego
python scripts/configure_refactoring.py --phase strangler_fig --migration-percentage 0.05

# 2. Monitorar por 24h
# 3. Se estável, aumentar para 10%
python scripts/configure_refactoring.py --migration-percentage 0.10
```

#### Semana 3-4: Migração Gradual
```bash
# Aumentar progressivamente
python scripts/configure_refactoring.py --migration-percentage 0.25
# Aguardar 24h, monitorar

python scripts/configure_refactoring.py --migration-percentage 0.50
# Aguardar 48h, monitorar

python scripts/configure_refactoring.py --migration-percentage 0.75
# Aguardar 24h, monitorar
```

#### Semana 5: Finalização
```bash
# Migração completa
python scripts/configure_refactoring.py --phase new_architecture

# Monitorar por 1 semana
# Descomissionar sistema legado (opcional)
```

## 📊 Monitoramento

### Métricas de Performance

```python
# Logs estruturados incluem:
{
  "correlation_id": "req_123456",
  "refactoring_phase": "strangler_fig",
  "migration_percentage": 0.1,
  "architecture_used": "new",
  "execution_time_ms": 150,
  "legacy_time_ms": 200,
  "new_time_ms": 150,
  "fallback_used": false,
  "data_differences": []
}
```

### Alertas Recomendados

1. **Performance**:
   - P95 > 300ms
   - Taxa de erro > 1%
   - Fallback rate > 10%

2. **Dados**:
   - Divergências > 5%
   - Falhas de validação > 2%

3. **Sistema**:
   - Timeout de fallback > 5s
   - Erro de conexão GLPI

### Dashboard de Monitoramento

```bash
# Executar exemplo com monitoramento
python examples/progressive_refactoring_example.py --run-server

# Acessar endpoints de monitoramento
curl http://localhost:5000/admin/refactoring/status
curl http://localhost:5000/health
```

## 🧪 Testes

### Executar Testes Unitários

```bash
# Todos os testes
python -m pytest tests/test_progressive_refactoring.py -v

# Testes específicos
python -m pytest tests/test_progressive_refactoring.py::TestRefactoringPhases -v
python -m pytest tests/test_progressive_refactoring.py::TestFallbackMechanism -v
```

### Testes de Integração

```bash
# Executar aplicação de exemplo
python examples/progressive_refactoring_example.py --run-server --port 5001

# Em outro terminal, executar testes
curl -X POST http://localhost:5001/admin/refactoring/phase \
  -H 'Content-Type: application/json' \
  -d '{"phase": "strangler_fig"}'

curl http://localhost:5001/api/metrics
curl http://localhost:5001/admin/refactoring/status
```

### Testes de Carga

```bash
# Usar Apache Bench para testar performance
ab -n 1000 -c 10 http://localhost:5000/api/metrics

# Ou usar wrk
wrk -t12 -c400 -d30s http://localhost:5000/api/metrics
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Fallback Excessivo

**Sintoma**: Taxa de fallback > 10%

**Possíveis Causas**:
- Timeout muito baixo
- Problemas de conectividade com GLPI
- Bugs na nova arquitetura

**Solução**:
```bash
# Aumentar timeout
python scripts/configure_refactoring.py --glpi-timeout 60

# Reduzir percentual de migração
python scripts/configure_refactoring.py --migration-percentage 0.05

# Voltar para sistema legado temporariamente
python scripts/configure_refactoring.py --phase legacy_only
```

#### 2. Divergências de Dados

**Sintoma**: Logs mostram diferenças entre sistemas

**Investigação**:
```bash
# Habilitar logging detalhado
export LOG_LEVEL=DEBUG

# Executar validação com 100% de sampling
python scripts/configure_refactoring.py --phase validation --validation-sampling 1.0
```

**Análise**:
- Verificar logs de comparação
- Identificar campos com divergências
- Corrigir lógica na nova arquitetura

#### 3. Performance Degradada

**Sintoma**: P95 > 300ms na nova arquitetura

**Investigação**:
- Verificar logs de performance
- Analisar queries GLPI
- Verificar cache e conexões

**Otimização**:
- Implementar cache local
- Otimizar queries
- Ajustar timeouts

### Rollback de Emergência

```bash
# Rollback imediato para sistema legado
python scripts/configure_refactoring.py --phase legacy_only

# Ou via API
curl -X POST http://localhost:5000/admin/refactoring/phase \
  -H 'Content-Type: application/json' \
  -d '{"phase": "legacy_only"}'
```

### Logs de Debug

```bash
# Habilitar logs detalhados
export LOG_LEVEL=DEBUG
export LOG_FORMAT=json

# Filtrar logs de refatoração
tail -f app.log | grep "refactoring"

# Analisar performance
tail -f app.log | grep "performance_comparison"

# Verificar divergências
tail -f app.log | grep "data_difference"
```

## 📚 Referências

- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Progressive Delivery](https://redmonk.com/jgovernor/2018/08/06/towards-progressive-delivery/)
- [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html)
- [Blue-Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)

---

**Próximos Passos**: Após completar a refatoração progressiva, considere implementar:
- Observabilidade avançada (Prometheus + Grafana)
- Testes de contrato automatizados
- CI/CD com validação automática
- Documentação orientada por IA