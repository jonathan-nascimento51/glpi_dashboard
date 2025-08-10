# GLPI Dashboard - Sistema de Monitoramento

Este diret�rio cont�m a configura��o completa do sistema de monitoramento em tempo real para o GLPI Dashboard, utilizando Prometheus, Grafana e Alertmanager.

## Componentes

### 1. Prometheus
- **Porta**: 9090
- **Fun��o**: Coleta e armazenamento de m�tricas
- **Configura��o**: `prometheus.yml`
- **Regras de Alerta**: `rules/glpi-alerts.yml`

### 2. Grafana
- **Porta**: 3000
- **Fun��o**: Visualiza��o de m�tricas e dashboards
- **Login padr�o**: admin/admin123
- **Dashboards**: Provisionados automaticamente

### 3. Alertmanager
- **Porta**: 9093
- **Fun��o**: Gerenciamento e roteamento de alertas
- **Configura��o**: `alertmanager.yml`

### 4. Exporters
- **Node Exporter** (9100): M�tricas do sistema
- **Redis Exporter** (9121): M�tricas do Redis
- **Nginx Exporter** (9113): M�tricas do Nginx

## Como Usar

### 1. Iniciar o Sistema de Monitoramento

```bash
# No diret�rio raiz do projeto
docker-compose -f monitoring.yml up -d
```

### 2. Acessar os Servi�os

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### 3. Configurar Alertas

Edite o arquivo `alertmanager.yml` para configurar:
- Endere�os de email
- Webhooks do Slack
- Outros canais de notifica��o

### 4. Personalizar Dashboards

Os dashboards est�o em `grafana/dashboards/` e podem ser editados diretamente ou atrav�s da interface do Grafana.

## M�tricas Monitoradas

### Sistema
- Uso de CPU
- Uso de mem�ria
- Espa�o em disco
- Carga do sistema
- Rede

### Aplica��o
- Tempo de resposta da API
- Taxa de erro HTTP
- Throughput de requisi��es
- Status dos servi�os

### GLPI
- Conectividade com a API
- Performance das consultas
- Status dos endpoints

### Frontend
- Core Web Vitals
- Tempo de carregamento
- Erros JavaScript

## Alertas Configurados

### Cr�ticos
- Servi�o indispon�vel
- Alta taxa de erro (>5%)
- Pouco espa�o em disco (>90%)
- Falha na conex�o com GLPI

### Warnings
- Alta lat�ncia da API (>500ms)
- Alto uso de CPU (>80%)
- Alto uso de mem�ria (>85%)

## Personaliza��o

### Adicionar Novas M�tricas

1. Edite `prometheus.yml` para adicionar novos targets
2. Configure os exporters necess�rios
3. Atualize as regras de alerta em `rules/glpi-alerts.yml`

### Criar Novos Dashboards

1. Crie arquivos JSON em `grafana/dashboards/`
2. Ou use a interface do Grafana e exporte o JSON

### Configurar Notifica��es

1. Edite `alertmanager.yml`
2. Configure os receivers apropriados
3. Teste as notifica��es

## Troubleshooting

### Verificar Status dos Servi�os

```bash
docker-compose -f monitoring.yml ps
```

### Ver Logs

```bash
# Prometheus
docker-compose -f monitoring.yml logs prometheus

# Grafana
docker-compose -f monitoring.yml logs grafana

# Alertmanager
docker-compose -f monitoring.yml logs alertmanager
```

### Validar Configura��es

```bash
# Validar configura��o do Prometheus
docker run --rm -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus:latest promtool check config /etc/prometheus/prometheus.yml

# Validar regras de alerta
docker run --rm -v $(pwd)/monitoring/rules:/etc/prometheus/rules prom/prometheus:latest promtool check rules /etc/prometheus/rules/*.yml
```

## Backup e Restore

### Backup

```bash
# Backup dos dados do Prometheus
docker run --rm -v glpi_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# Backup dos dados do Grafana
docker run --rm -v glpi_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

### Restore

```bash
# Restore dos dados do Prometheus
docker run --rm -v glpi_prometheus_data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-backup.tar.gz -C /data

# Restore dos dados do Grafana
docker run --rm -v glpi_grafana_data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-backup.tar.gz -C /data
```

## Seguran�a

- Altere as senhas padr�o
- Configure HTTPS em produ��o
- Restrinja o acesso �s portas de monitoramento
- Use autentica��o adequada

## Performance

- Ajuste os intervalos de coleta conforme necess�rio
- Configure reten��o de dados apropriada
- Monitore o uso de recursos dos pr�prios servi�os de monitoramento
