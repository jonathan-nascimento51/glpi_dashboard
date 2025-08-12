# Scripts de Validação do GLPI Dashboard

Este diretório contém scripts para validação automática da qualidade dos dados e funcionamento do GLPI Dashboard.

## Scripts Disponíveis

### 1. `validate_dashboard.py`

Script principal de validação visual automática do GLPI Dashboard.

**Funcionalidades:**
- Verifica se os serviços backend estão rodando
- Faz requisições aos endpoints críticos da API
- Valida consistência dos dados (detecta problemas all-zero)
- Salva artefatos de validação em `artifacts/`
- Gera relatório de validação em JSON

**Como usar:**
```bash
# Certifique-se de que o backend está rodando em localhost:8000
python scripts/validate_dashboard.py
```

**Saída esperada:**
- Exit code 0: Validação passou
- Exit code 1: Validação falhou (problemas detectados)

**Artefatos gerados:**
- `artifacts/backend_data_YYYYMMDD_HHMMSS.json` - Dados completos do backend
- `artifacts/metrics_sample_YYYYMMDD_HHMMSS.json` - Amostra das métricas
- `artifacts/validation_report_YYYYMMDD_HHMMSS.json` - Relatório de validação

### 2. `test_validation_all_zero.py`

Script de teste para verificar se a validação detecta corretamente cenários all-zero.

**Funcionalidades:**
- Força um cenário all-zero usando parâmetro `all_zero=true`
- Testa se a validação detecta o problema corretamente
- Valida que o sistema de qualidade está funcionando

**Como usar:**
```bash
# Certifique-se de que o backend está rodando
python scripts/test_validation_all_zero.py
```

## Configurações

### URLs dos Serviços
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8050` (para futuras validações visuais)

### Timeouts e Retries
- Timeout padrão: 30 segundos
- Máximo de tentativas: 10
- Delay entre tentativas: 3 segundos

## Critérios de Validação

### Validação Passa Quando:
- Backend está disponível (status 200)
- Endpoints críticos respondem corretamente
- Não há problemas críticos de qualidade detectados
- Sistema não detecta cenário all-zero quando há dados válidos

### Validação Falha Quando:
- Backend não está disponível
- Endpoints retornam erro
- Sistema detecta `all_zero=true` com `status=error`
- Há issues críticos na qualidade dos dados

## Troubleshooting

### Backend não está disponível
- Verifique se o backend está rodando: `curl http://localhost:8000/health`
- Verifique logs do backend
- Confirme que não há conflitos de porta

### Validação falha com dados válidos
- Verifique o relatório de validação em `artifacts/`
- Analise os dados de saúde retornados pela API
- Verifique se há issues críticos sendo reportados incorretamente
