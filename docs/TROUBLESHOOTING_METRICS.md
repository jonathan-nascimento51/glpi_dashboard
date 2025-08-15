# Guia de Troubleshooting - Métricas GLPI

> **Documentação Viva** - Atualizada automaticamente
> **Última Atualização**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Problemas Críticos e Soluções

### 1. Dados Zerados no Dashboard

#### Sintomas

- Todos os cards exibem "0"
- Gráficos vazios ou sem dados
- API retorna arrays vazios

#### Diagnóstico Rápido

```bash
# 1. Validação completa do sistema
python enhanced_validation.py

# 2. Teste específico de autenticação
python backend/debug_glpi_auth.py

# 3. Verificar descoberta de campos
python backend/debug_discover_field.py

# 4. Testar endpoint direto
curl -X GET "http://localhost:8000/api/tickets/summary" | jq .
```

#### Causas Possíveis e Soluções

##### Problema de Autenticação

**Verificação**:

```bash
# Testar tokens GLPI
curl -H "Authorization: user_token YOUR_TOKEN" \
     -H "App-Token: YOUR_APP_TOKEN" \
     "https://your-glpi.com/apirest.php/initSession"
```

**Solução**:

1. Renovar `user_token` no GLPI
2. Verificar `app_token` válido
3. Confirmar permissões do usuário
4. Atualizar `.env` com novos tokens

##### Descoberta de Campos Falhando

**Verificação**:

```python
# Executar descoberta manual
from backend.adapters.glpi.service import GLPIService
service = GLPIService()
fields = service.discover_field_ids()
print(f"Campos encontrados: {fields}")
```

**Solução**:

1. Verificar se campos existem no GLPI
2. Confirmar nomes exatos dos campos
3. Atualizar mapeamento se necessário
4. Implementar fallbacks para campos ausentes

##### Filtros de Data Muito Restritivos

**Verificação**:

```python
# Testar sem filtros de data
from datetime import datetime, timedelta
start_date = datetime.now() - timedelta(days=365)
end_date = datetime.now()
print(f"Período: {start_date} até {end_date}")
```

**Solução**:

1. Expandir período de busca
2. Verificar formato de data GLPI
3. Testar consulta sem filtros
4. Validar timezone

### 2. Performance Lenta

#### Sintomas/Problemas

- Dashboard carrega > 30 segundos
- Timeouts em requisições
- Alta utilização de CPU/memória

#### Diagnóstico

```bash
# 1. Monitorar performance
top -p $(pgrep -f "python.*main")

# 2. Verificar logs de performance
tail -f backend/logs/app.log | grep -i "slow\|timeout\|error"

# 3. Testar cache Redis
redis-cli ping
redis-cli info memory

# 4. Profiling de queries
python backend/debug_glpi_service.py --profile
```

#### Soluções

##### Otimização de Cache

```python
# Verificar hit rate do cache
import redis
r = redis.Redis()
info = r.info()
print(f"Cache hits: {info['keyspace_hits']}")
print(f"Cache misses: {info['keyspace_misses']}")
```

**Ações**:

1. Aumentar TTL do cache para dados estáveis
2. Implementar cache em camadas
3. Pre-aquecer cache em horários de baixo uso
4. Monitorar hit rate continuamente

##### Otimização de Queries GLPI

```python
# Exemplo de query otimizada
params = {
    "criteria": [
        {"field": "12", "searchtype": "equals", "value": "open"},
        {"field": "15", "searchtype": "morethan", "value": start_date}
    ],
    "range": "0-999",  # Limitar resultados
    "forcedisplay": ["1", "12", "15"]  # Apenas campos necessários
}
```

**Ações**:

1. Limitar campos retornados
2. Usar paginação eficiente
3. Implementar filtros no servidor
4. Cachear agregações pesadas

### 3. Erros de Conectividade

#### Sintomas do erro

- "Connection refused"
- "Timeout errors"
- "SSL certificate errors"

#### Diagnóstico básico

```bash
# 1. Testar conectividade básica
ping your-glpi-server.com
telnet your-glpi-server.com 443

# 2. Verificar certificados SSL
openssl s_client -connect your-glpi-server.com:443

# 3. Testar DNS
nslookup your-glpi-server.com

# 4. Verificar proxy/firewall
curl -v https://your-glpi-server.com/apirest.php/
```

#### Soluções básicas

##### Problemas de Rede

1. Verificar configuração de proxy
2. Confirmar regras de firewall
3. Testar de diferentes redes
4. Implementar retry com backoff

##### Problemas SSL

1. Atualizar certificados
2. Configurar verificação SSL
3. Implementar fallback HTTP (dev only)
4. Verificar cadeia de certificados

### 4. Inconsistências de Dados

#### Sintomas do problema

- Totais não batem
- Dados duplicados
- Métricas conflitantes

#### Diagnóstico básico a se fazer

```python
# Script de verificação de consistência
from backend.services.metrics_service import MetricsService

service = MetricsService()

# Verificar totais
total_tickets = service.get_total_tickets()
sum_by_level = sum(service.get_tickets_by_level().values())

print(f"Total geral: {total_tickets}")
print(f"Soma por nível: {sum_by_level}")
print(f"Diferença: {abs(total_tickets - sum_by_level)}")

if total_tickets != sum_by_level:
    print(" INCONSISTÊNCIA DETECTADA!")
```

#### Soluções básicas a fazer

##### Validação de Integridade

1. Implementar checksums de dados
2. Comparar múltiplas fontes
3. Validar agregações
4. Detectar duplicatas

##### Reconciliação Automática

```python
# Exemplo de reconciliação
def reconcile_metrics():
    raw_data = glpi_service.get_raw_tickets()
    processed_data = metrics_service.process_tickets(raw_data)
    
    # Validar totais
    assert len(raw_data) == sum(processed_data.values())
    
    # Validar categorias
    for category, count in processed_data.items():
        expected = len([t for t in raw_data if t.category == category])
        assert count == expected, f"Inconsistência em {category}"
```

## Ferramentas de Diagnóstico

### Scripts Disponíveis

```bash
# Validação completa
python enhanced_validation.py

# Diagnóstico específico
python backend/debug_glpi.py
python backend/debug_discover_field.py
python backend/debug_glpi_auth.py

# Testes de performance
python scripts/performance_analysis.py

# Atualização de documentação
python scripts/update_docs.py
```

### Logs Estruturados

```bash
# Filtrar por tipo de erro
tail -f backend/logs/app.log | jq 'select(.level == "ERROR")'

# Monitorar métricas específicas
tail -f backend/logs/app.log | jq 'select(.component == "metrics")'

# Rastrear requests específicos
tail -f backend/logs/app.log | jq 'select(.request_id == "abc123")'
```

### Monitoramento Contínuo

```python
# Script de monitoramento
import time
import requests
from datetime import datetime

def monitor_health():
    while True:
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"[{datetime.now()}]  Sistema saudável: {data}")
            else:
                print(f"[{datetime.now()}]  Problema detectado: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}]  Erro crítico: {e}")
        
        time.sleep(60)  # Verificar a cada minuto

if __name__ == "__main__":
    monitor_health()
```

## Checklist de Troubleshooting

### Antes de Investigar

- [ ] Executar `python enhanced_validation.py`
- [ ] Verificar logs recentes
- [ ] Confirmar serviços rodando
- [ ] Testar conectividade básica

### Durante a Investigação

- [ ] Isolar o problema (frontend vs backend vs GLPI)
- [ ] Reproduzir em ambiente controlado
- [ ] Coletar evidências (logs, screenshots, payloads)
- [ ] Documentar passos de reprodução

### Após a Resolução

- [ ] Validar correção com testes
- [ ] Atualizar Knowledge Graph
- [ ] Documentar lição aprendida
- [ ] Implementar prevenção

## Knowledge Graph Integration

```python
# Registrar problema no Knowledge Graph
run_mcp("mcp.config.usrlocalmcp.Persistent Knowledge Graph", 
        "add_observations", {
            "observations": [{
                "entityName": "Dados Zerados Problem",
                "contents": [
                    f"Resolvido em {datetime.now()}: Causa foi tokens expirados",
                    "Solução: Renovação automática implementada",
                    "Prevenção: Monitoramento de saúde dos tokens"
                ]
            }]
        })

# Buscar soluções conhecidas
run_mcp("mcp.config.usrlocalmcp.Persistent Knowledge Graph", 
        "search_nodes", {"query": "performance lenta"})
```

---

**Mantenha este guia atualizado**: Execute `python scripts/update_docs.py` após resolver novos problemas.
