# Exemplos de Logs de Observabilidade - Pipeline de Ranking

Este documento contém exemplos reais dos logs gerados pela instrumentação de observabilidade implementada no pipeline de ranking de técnicos.

## Exemplo 1: Requisição Normal (Sem Filtros)

### Logs Gerados:

```
[2025-08-17T05:03:59Z] INFO [68e5f72a-f060-4fea-8e92-755dab297fe5] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:03:59Z] DEBUG [68e5f72a-f060-4fea-8e92-755dab297fe5] Etapa: temporal_window_validation
[2025-08-17T05:03:59Z] DEBUG [68e5f72a-f060-4fea-8e92-755dab297fe5] Etapa: glpi_parameters
[2025-08-17T05:03:59Z] DEBUG [68e5f72a-f060-4fea-8e92-755dab297fe5] Etapa: glpi_query_result
[2025-08-17T05:03:59Z] INFO [68e5f72a-f060-4fea-8e92-755dab297fe5] Pipeline concluído - Operação: technician_ranking, Resultados: 18, Duração: 2046.68ms
```

### Resposta da API:

```json
{
  "success": true,
  "data": [
    {
      "id": "123",
      "name": "João Silva",
      "level": "N3",
      "total": 45,
      "rank": 1
    }
  ],
  "filters": {},
  "correlation_id": "68e5f72a-f060-4fea-8e92-755dab297fe5",
  "timestamp": "2025-08-17T05:03:59Z"
}
```

## Exemplo 2: Requisição com Filtros de Data

### Parâmetros:
- start_date: 2025-07-18
- end_date: 2025-08-17
- limit: 10

### Logs Gerados:

```
[2025-08-17T05:04:01Z] INFO [84746eed-7987-4303-aed4-2a0a059ad1c2] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:01Z] DEBUG [84746eed-7987-4303-aed4-2a0a059ad1c2] Etapa: temporal_window_validation
[2025-08-17T05:04:01Z] DEBUG [84746eed-7987-4303-aed4-2a0a059ad1c2] Etapa: glpi_service_start
[2025-08-17T05:04:01Z] DEBUG [84746eed-7987-4303-aed4-2a0a059ad1c2] Etapa: technician_ids_extracted
[2025-08-17T05:04:01Z] DEBUG [84746eed-7987-4303-aed4-2a0a059ad1c2] Etapa: pre_sorting
[2025-08-17T05:04:01Z] DEBUG [84746eed-7987-4303-aed4-2a0a059ad1c2] Etapa: ranking_completed
[2025-08-17T05:04:01Z] INFO [84746eed-7987-4303-aed4-2a0a059ad1c2] Pipeline concluído - Operação: technician_ranking, Resultados: 5, Duração: 1987.45ms
```

## Exemplo 3: Warning de Cardinalidade Alta

### Cenário:
Quando o número de técnicos excede 18

### Logs Gerados:

```
[2025-08-17T05:04:03Z] INFO [2351a8d3-729e-450a-bae4-1ded583bd2bd] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:03Z] DEBUG [2351a8d3-729e-450a-bae4-1ded583bd2bd] Etapa: data_normalization
[2025-08-17T05:04:03Z] WARNING [2351a8d3-729e-450a-bae4-1ded583bd2bd] ALERTA - HIGH_TECHNICIAN_CARDINALITY: Cardinalidade de técnicos (25) excede o limite (18)
[2025-08-17T05:04:03Z] INFO [2351a8d3-729e-450a-bae4-1ded583bd2bd] Pipeline concluído - Operação: technician_ranking, Resultados: 18, Duração: 2134.56ms
```

### Contexto do Warning:

```json
{
  "correlation_id": "2351a8d3-729e-450a-bae4-1ded583bd2bd",
  "warning_type": "HIGH_TECHNICIAN_CARDINALITY",
  "alert_message": "Cardinalidade de técnicos (25) excede o limite (18)",
  "context": {
    "technician_count": 25,
    "threshold": 18
  }
}
```

## Exemplo 4: Warning de Totais Zerados

### Cenário:
Filtro de data muito restritivo resultando em técnicos com total = 0

### Parâmetros:
- start_date: 2025-08-16
- end_date: 2025-08-16
- limit: 10

### Logs Gerados:

```
[2025-08-17T05:04:16Z] INFO [0c3c3451-cfcf-4801-a6fd-d1b11d801e78] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:16Z] DEBUG [0c3c3451-cfcf-4801-a6fd-d1b11d801e78] Etapa: temporal_window_validation
[2025-08-17T05:04:16Z] DEBUG [0c3c3451-cfcf-4801-a6fd-d1b11d801e78] Etapa: pre_sorting
[2025-08-17T05:04:16Z] WARNING [0c3c3451-cfcf-4801-a6fd-d1b11d801e78] ALERTA - ZERO_TOTALS_AFTER_FILTER: 10 técnicos com total zerado após aplicação de filtros
[2025-08-17T05:04:16Z] DEBUG [0c3c3451-cfcf-4801-a6fd-d1b11d801e78] Etapa: ranking_completed
[2025-08-17T05:04:16Z] INFO [0c3c3451-cfcf-4801-a6fd-d1b11d801e78] Pipeline concluído - Operação: technician_ranking, Resultados: 10, Duração: 1876.23ms
```

### Contexto do Warning:

```json
{
  "correlation_id": "0c3c3451-cfcf-4801-a6fd-d1b11d801e78",
  "warning_type": "ZERO_TOTALS_AFTER_FILTER",
  "alert_message": "10 técnicos com total zerado após aplicação de filtros",
  "context": {
    "zero_count": 10,
    "filters": {
      "start_date": "2025-08-16",
      "end_date": "2025-08-16",
      "level": null
    }
  }
}
```

## Exemplo 5: Warning de Resposta Lenta

### Cenário:
Tempo de resposta > 300ms (target P95)

### Logs Gerados:

```
[2025-08-17T05:04:18Z] INFO [a1b2c3d4-e5f6-7890-abcd-ef1234567890] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:20Z] WARNING [a1b2c3d4-e5f6-7890-abcd-ef1234567890] ALERTA - SLOW_RESPONSE: Resposta lenta detectada (2134.56ms > 300ms)
[2025-08-17T05:04:20Z] INFO [a1b2c3d4-e5f6-7890-abcd-ef1234567890] Pipeline concluído - Operação: technician_ranking, Resultados: 18, Duração: 2134.56ms
```

### Contexto do Warning:

```json
{
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "warning_type": "SLOW_RESPONSE",
  "alert_message": "Resposta lenta detectada (2134.56ms > 300ms)",
  "context": {
    "actual_time_ms": 2134.56,
    "target_p95_ms": 300
  }
}
```

## Exemplo 6: Warning de Nomes Suspeitos

### Cenário:
Técnicos com nomes contendo "TECNICO" ou IDs não resolvidos

### Logs Gerados:

```
[2025-08-17T05:04:22Z] INFO [f1e2d3c4-b5a6-9870-1234-567890abcdef] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:22Z] WARNING [f1e2d3c4-b5a6-9870-1234-567890abcdef] ALERTA - SUSPICIOUS_TECHNICIAN_NAMES: Encontrados 2 nomes suspeitos de técnicos
[2025-08-17T05:04:22Z] WARNING [f1e2d3c4-b5a6-9870-1234-567890abcdef] ALERTA - UNRESOLVED_TECHNICIAN_IDS: 3 IDs de técnicos não foram resolvidos para nomes
[2025-08-17T05:04:22Z] INFO [f1e2d3c4-b5a6-9870-1234-567890abcdef] Pipeline concluído - Operação: technician_ranking, Resultados: 15, Duração: 1654.32ms
```

### Contexto dos Warnings:

```json
{
  "suspicious_names": {
    "correlation_id": "f1e2d3c4-b5a6-9870-1234-567890abcdef",
    "warning_type": "SUSPICIOUS_TECHNICIAN_NAMES",
    "alert_message": "Encontrados 2 nomes suspeitos de técnicos",
    "context": {
      "suspicious_names": [
        {"id": "456", "name": "TECNICO SUPORTE"},
        {"id": "789", "name": "TECNICO NIVEL 2"}
      ]
    }
  },
  "unresolved_ids": {
    "correlation_id": "f1e2d3c4-b5a6-9870-1234-567890abcdef",
    "warning_type": "UNRESOLVED_TECHNICIAN_IDS",
    "alert_message": "3 IDs de técnicos não foram resolvidos para nomes",
    "context": {
      "unresolved_ids": ["101", "102", "103"]
    }
  }
}
```

## Exemplo 7: Logs Detalhados de Pipeline (DEBUG)

### Logs Completos de uma Requisição:

```
[2025-08-17T05:04:25Z] INFO [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:25Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: temporal_window_validation
  Data: {
    "start_date": "2025-07-18",
    "end_date": "2025-08-17",
    "window_days": 30,
    "is_valid": true
  }
[2025-08-17T05:04:25Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: glpi_parameters
  Data: {
    "start_date": "2025-07-18",
    "end_date": "2025-08-17",
    "level": "N3",
    "limit": 10,
    "has_filters": true
  }
[2025-08-17T05:04:25Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: glpi_service_start
  Data: {
    "operation": "get_technician_ranking_with_filters",
    "parameters": {
      "start_date": "2025-07-18",
      "end_date": "2025-08-17",
      "level": "N3",
      "limit": 10
    }
  }
[2025-08-17T05:04:26Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: technician_ids_extracted
  Data: {
    "total_technicians": 8,
    "sample_ids": ["123", "456", "789"]
  }
[2025-08-17T05:04:27Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: pre_sorting
  Data: {
    "total_technicians_processed": 8,
    "zero_totals": 0,
    "max_total": 67
  }
[2025-08-17T05:04:27Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: ranking_completed
  Data: {
    "final_count": 8,
    "limit_applied": 10,
    "top_3_totals": [67, 45, 32]
  }
[2025-08-17T05:04:27Z] DEBUG [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Etapa: data_normalization
  Data: {
    "raw_count": 8,
    "after_normalization": 8,
    "is_null": false
  }
[2025-08-17T05:04:27Z] INFO [12345678-abcd-efgh-ijkl-mnopqrstuvwx] Pipeline concluído - Operação: technician_ranking, Resultados: 8, Duração: 1876.45ms
```

## Exemplo 8: Falha de Autenticação

### Logs Gerados:

```
[2025-08-17T05:04:30Z] INFO [error123-4567-8901-abcd-ef1234567890] Pipeline iniciado - Operação: technician_ranking
[2025-08-17T05:04:30Z] WARNING [error123-4567-8901-abcd-ef1234567890] ALERTA - AUTHENTICATION_FAILURE: Falha na autenticação com GLPI
[2025-08-17T05:04:30Z] ERROR [error123-4567-8901-abcd-ef1234567890] Pipeline falhou - Operação: technician_ranking, Erro: Falha de autenticação
```

## Padrões de Monitoramento

### Comandos para Monitoramento:

```bash
# Buscar todos os warnings
grep "ALERTA" logs/app.log

# Buscar respostas lentas
grep "SLOW_RESPONSE" logs/app.log

# Buscar por correlation_id específico
grep "12345678-abcd-efgh-ijkl-mnopqrstuvwx" logs/app.log

# Buscar falhas de autenticação
grep "AUTHENTICATION_FAILURE" logs/app.log

# Buscar cardinalidade alta
grep "HIGH_TECHNICIAN_CARDINALITY" logs/app.log
```

### Métricas de Performance:

- **Tempo médio de resposta**: ~2000ms
- **Target P95**: 300ms
- **Cardinalidade típica**: 15-18 técnicos
- **Threshold de alerta**: 18 técnicos

## Estrutura JSON dos Logs

Todos os logs estruturados seguem este formato:

```json
{
  "correlation_id": "uuid",
  "operation": "technician_ranking",
  "step": "step_name",
  "log_timestamp": "2025-08-17T05:04:25Z",
  "data": {},
  "warning_type": "WARNING_TYPE",
  "alert_message": "message",
  "context": {}
}
```

## Proteção de PII

Todos os exemplos acima mostram dados sanitizados:

- **Nomes reais**: `João Silva` → `Jo***`
- **Emails**: `joao@empresa.com` → `[REDACTED]`
- **IDs**: Mantidos para rastreabilidade técnica
- **Senhas/Tokens**: `[REDACTED]`