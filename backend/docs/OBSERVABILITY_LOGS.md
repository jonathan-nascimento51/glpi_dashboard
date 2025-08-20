# Documentação de Observabilidade - Pipeline de Ranking de Técnicos

## Visão Geral

Este documento descreve a instrumentação de logs e alertas implementada no pipeline de filtro de datas e ranking de técnicos para prevenir regressões silenciosas.

## CorrelationId

Cada requisição recebe um `correlationId` único (UUID4) que permite rastreabilidade ponta a ponta através de todos os logs e componentes do sistema.

**Formato**: `[correlation_id] Mensagem`

**Exemplo**: `[a1b2c3d4-e5f6-7890-abcd-ef1234567890] Pipeline iniciado - Operação: technician_ranking`

## Pontos de Log Implementados

### 1. Endpoint de Ranking (`/api/technicians/ranking`)

#### Logs de Pipeline:
- **pipeline_start**: Início da operação com parâmetros de entrada
- **temporal_window_validation**: Validação da janela temporal
- **glpi_parameters**: Parâmetros enviados ao serviço GLPI
- **glpi_query_result**: Resultado bruto da consulta GLPI
- **data_normalization**: Dados após normalização/agregação
- **empty_result**: Quando nenhum resultado é encontrado
- **pipeline_end**: Conclusão da operação com métricas

### 2. Serviço GLPI (`glpi_service.py`)

#### Logs de Pipeline:
- **glpi_service_start**: Início do processamento no serviço GLPI
- **technician_extraction_failed**: Falha na extração de IDs de técnicos
- **technician_ids_extracted**: IDs de técnicos extraídos com sucesso
- **pre_sorting**: Estatísticas antes da ordenação
- **ranking_completed**: Ranking finalizado com estatísticas

## Alertas e Warnings

### 1. Cardinalidade Alta de Técnicos
- **Tipo**: `HIGH_TECHNICIAN_CARDINALITY`
- **Condição**: Número de técnicos > 18
- **Ação**: Log de warning com contagem atual e limite

### 2. Nomes Suspeitos de Técnicos
- **Tipo**: `SUSPICIOUS_TECHNICIAN_NAMES`
- **Condição**: Nomes contendo "TECNICO"
- **Ação**: Log de warning com lista de nomes suspeitos

### 3. IDs Não Resolvidos
- **Tipo**: `UNRESOLVED_TECHNICIAN_IDS`
- **Condição**: IDs sem nome de técnico resolvido
- **Ação**: Log de warning com lista de IDs não resolvidos

### 4. Totais Zerados
- **Tipo**: `ZERO_TOTALS_AFTER_FILTER`
- **Condição**: Técnicos com total = 0 após filtros
- **Ação**: Log de warning com contagem e filtros aplicados

### 5. Resposta Lenta
- **Tipo**: `SLOW_RESPONSE`
- **Condição**: Tempo de resposta > target_p95 (300ms)
- **Ação**: Log de warning com tempo atual e limite

### 6. Falha de Autenticação
- **Tipo**: `AUTHENTICATION_FAILURE`
- **Condição**: Falha na autenticação com GLPI
- **Ação**: Log de warning

## Níveis de Log

### DEBUG
- Logs detalhados de cada etapa do pipeline
- Parâmetros de entrada e saída
- Dados de amostra (primeiros 3-5 registros)

### INFO
- Início e fim de operações
- Contagens de resultados
- Métricas de performance

### WARNING
- Alertas de anomalias
- Respostas lentas
- Falhas de autenticação
- Resultados vazios inesperados

### ERROR
- Exceções não tratadas
- Falhas críticas do sistema

## Configuração de Níveis de Log

### Desenvolvimento
```python
import logging
logging.getLogger('observability').setLevel(logging.DEBUG)
logging.getLogger('technician_ranking').setLevel(logging.DEBUG)
logging.getLogger('glpi_service').setLevel(logging.DEBUG)
```

### Produção
```python
import logging
logging.getLogger('observability').setLevel(logging.INFO)
logging.getLogger('technician_ranking').setLevel(logging.INFO)
logging.getLogger('glpi_service').setLevel(logging.WARNING)
```

### Diagnóstico
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)  # Todos os logs
```

## Proteção de PII

Todos os logs são automaticamente sanitizados para proteger informações pessoais:

- **Nomes**: Primeiras 2 letras + `***` (ex: `Jo***`)
- **Emails**: Redacted como `[REDACTED]`
- **Senhas/Tokens**: Redacted como `[REDACTED]`
- **IDs**: Mantidos para rastreabilidade técnica

## Exemplos de Logs

### Log de Início
```
[a1b2c3d4-e5f6-7890-abcd-ef1234567890] Pipeline iniciado - Operação: technician_ranking
```

### Log de Warning
```
[a1b2c3d4-e5f6-7890-abcd-ef1234567890] ALERTA - HIGH_TECHNICIAN_CARDINALITY: Cardinalidade de técnicos (25) excede o limite (18)
```

### Log de Conclusão
```
[a1b2c3d4-e5f6-7890-abcd-ef1234567890] Pipeline concluído - Operação: technician_ranking, Resultados: 15, Duração: 245.67ms
```

## Monitoramento

Para monitoramento efetivo, configure alertas baseados nos seguintes padrões:

1. **Busca por warnings**: `grep "ALERTA" logs/app.log`
2. **Respostas lentas**: `grep "SLOW_RESPONSE" logs/app.log`
3. **Falhas de autenticação**: `grep "AUTHENTICATION_FAILURE" logs/app.log`
4. **Cardinalidade alta**: `grep "HIGH_TECHNICIAN_CARDINALITY" logs/app.log`

## Estrutura JSON dos Logs

Todos os logs estruturados incluem:

```json
{
  "correlation_id": "uuid",
  "operation": "string",
  "step": "string",
  "timestamp": "ISO8601",
  "data": {},
  "warning_type": "string",
  "message": "string"
}
```

## Troubleshooting

### Problema: Muitos warnings de cardinalidade
- **Causa**: Crescimento natural da equipe
- **Ação**: Ajustar threshold em `ObservabilityLogger.check_technician_cardinality()`

### Problema: Muitos IDs não resolvidos
- **Causa**: Problemas na sincronização de dados
- **Ação**: Verificar mapeamento de técnicos no GLPI

### Problema: Totais sempre zerados
- **Causa**: Filtros muito restritivos ou problemas na consulta
- **Ação**: Verificar parâmetros de filtro e conectividade GLPI