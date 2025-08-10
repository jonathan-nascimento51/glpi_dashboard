# GLPI Dashboard - Sistema de Monitoramento

Este diretório contém a configuração completa do sistema de monitoramento em tempo real para o GLPI Dashboard, utilizando Prometheus, Grafana e Alertmanager.

## Componentes

### 1. Prometheus
- **Porta**: 9090
- **Função**: Coleta e armazenamento de métricas
- **Configuração**: `prometheus.yml`
- **Regras de Alerta**: `rules/glpi-alerts.yml`

### 2. Grafana
- **Porta**: 3000
- **Função**: Visualização de métricas e dashboards
- **Login padrão**: admin/admin123
- **Dashboards**: Provisionados automaticamente

### 3. Alertmanager
- **Porta**: 9093
- **Função**: Gerenciamento e roteamento de alertas
- **Configuração**: `alertmanager.yml`

### 4. Exporters
- **Node Exporter** (9100): Métricas do sistema
- **Redis Exporter** (9121): Métricas do Redis
- **Nginx Exporter** (9113): Métricas do Nginx

## Como Usar

### 1. Iniciar o Sistema de Monitoramento

```bash
# No diretório raiz do projeto
docker-compose -f monitoring.yml up -d
```

### 2. Acessar os Serviços

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### 3. Configurar Alertas

Edite o arquivo `alertmanager.yml` para configurar:
- Endereços de email
- Webhooks do Slack
- Outros canais de notificação

### 4. Personalizar Dashboards

Os dashboards estão em `grafana/dashboards/` e podem ser editados diretamente ou através da interface do Grafana.

## Métricas Monitoradas

### Sistema
- Uso de CPU
- Uso de memória
- Espaço em disco
- Carga do sistema
- Rede

### Aplicação
- Tempo de resposta da API
- Taxa de erro HTTP
- Throughput de requisições
- Status dos serviços

### GLPI
- Conectividade com a API
- Performance das consultas
- Status dos endpoints

### Frontend
- Core Web Vitals
- Tempo de carregamento
- Erros JavaScript

## Alertas Configurados

### Críticos
- Serviço indisponível
- Alta taxa de erro (>5%)
- Pouco espaço em disco (>90%)
- Falha na conexão com GLPI

### Warnings
- Alta latência da API (>500ms)
- Alto uso de CPU (>80%)
- Alto uso de memória (>85%)

## Personalização

### Adicionar Novas Métricas

1. Edite `prometheus.yml` para adicionar novos targets
2. Configure os exporters necessários
3. Atualize as regras de alerta em `rules/glpi-alerts.yml`

### Criar Novos Dashboards

1. Crie arquivos JSON em `grafana/dashboards/`
2. Ou use a interface do Grafana e exporte o JSON

### Configurar Notificações

1. Edite `alertmanager.yml`
2. Configure os receivers apropriados
3. Teste as notificações

## Troubleshooting

### Verificar Status dos Serviços

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

### Validar Configurações

```bash
# Validar configuração do Prometheus
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

## Segurança

- Altere as senhas padrão
- Configure HTTPS em produção
- Restrinja o acesso às portas de monitoramento
- Use autenticação adequada

## Performance

- Ajuste os intervalos de coleta conforme necessário
- Configure retenção de dados apropriada
- Monitore o uso de recursos dos próprios serviços de monitoramento
