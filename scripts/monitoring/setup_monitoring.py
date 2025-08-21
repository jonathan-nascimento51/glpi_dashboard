#!/usr/bin/env python3
"""
Script de Configuração e Automação do Sistema de Monitoramento Avançado
Configura e inicializa todos os componentes do sistema de monitoramento DevSecOps.

Autor: Sistema DevSecOps
Versão: 1.0.0
Data: 2024-01-15
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import requests
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MonitoringSetup:
    """Classe para configuração do sistema de monitoramento."""
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.project_root = Path.cwd()
        self.monitoring_dir = self.project_root / "scripts" / "monitoring"
        self.docker_compose_file = self.project_root / "docker-compose.monitoring.yml"
        
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do monitoramento."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            sys.exit(1)
    
    async def setup_complete_monitoring(self):
        """Configura o sistema completo de monitoramento."""
        logger.info("Starting complete monitoring setup...")
        
        try:
            # 1. Verificar dependências
            await self._check_dependencies()
            
            # 2. Criar estrutura de diretórios
            await self._create_directory_structure()
            
            # 3. Configurar Docker Compose
            await self._setup_docker_compose()
            
            # 4. Configurar Prometheus
            await self._setup_prometheus()
            
            # 5. Configurar Grafana
            await self._setup_grafana()
            
            # 6. Configurar Alertmanager
            await self._setup_alertmanager()
            
            # 7. Configurar Redis
            await self._setup_redis()
            
            # 8. Configurar Jaeger (Tracing)
            await self._setup_jaeger()
            
            # 9. Configurar ELK Stack (opcional)
            if self.config.get("data_sources", {}).get("elasticsearch", {}).get("enabled", False):
                await self._setup_elk_stack()
            
            # 10. Configurar scripts de monitoramento
            await self._setup_monitoring_scripts()
            
            # 11. Configurar systemd services (Linux)
            if os.name == 'posix':
                await self._setup_systemd_services()
            
            # 12. Inicializar serviços
            await self._start_services()
            
            # 13. Verificar saúde dos serviços
            await self._health_check()
            
            # 14. Configurar dashboards
            await self._import_dashboards()
            
            # 15. Configurar alertas
            await self._setup_alerts()
            
            logger.info("Monitoring setup completed successfully!")
            await self._print_access_info()
            
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            raise
    
    async def _check_dependencies(self):
        """Verifica dependências necessárias."""
        logger.info("Checking dependencies...")
        
        required_commands = ['docker', 'docker-compose']
        
        for cmd in required_commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, check=True)
                logger.info(f"{cmd} version: {result.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error(f"{cmd} is not installed or not in PATH")
                raise RuntimeError(f"Missing dependency: {cmd}")
        
        # Verificar Python packages
        required_packages = [
            'prometheus_client', 'redis', 'aiohttp', 'psutil', 
            'structlog', 'pyyaml', 'requests'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"Python package {package} is available")
            except ImportError:
                logger.warning(f"Python package {package} not found, installing...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
    
    async def _create_directory_structure(self):
        """Cria estrutura de diretórios necessária."""
        logger.info("Creating directory structure...")
        
        directories = [
            self.monitoring_dir,
            self.monitoring_dir / "prometheus",
            self.monitoring_dir / "grafana" / "dashboards",
            self.monitoring_dir / "grafana" / "provisioning" / "dashboards",
            self.monitoring_dir / "grafana" / "provisioning" / "datasources",
            self.monitoring_dir / "alertmanager",
            self.monitoring_dir / "logs",
            self.monitoring_dir / "data",
            self.monitoring_dir / "scripts",
            self.monitoring_dir / "runbooks",
            self.project_root / "monitoring_reports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    async def _setup_docker_compose(self):
        """Configura Docker Compose para monitoramento."""
        logger.info("Setting up Docker Compose...")
        
        docker_compose_content = {
            'version': '3.8',
            'services': {
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'container_name': 'glpi-prometheus',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './scripts/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml',
                        './scripts/monitoring/prometheus/rules:/etc/prometheus/rules',
                        'prometheus_data:/prometheus'
                    ],
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus',
                        '--web.console.libraries=/etc/prometheus/console_libraries',
                        '--web.console.templates=/etc/prometheus/consoles',
                        '--storage.tsdb.retention.time=30d',
                        '--web.enable-lifecycle',
                        '--web.enable-admin-api'
                    ],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'container_name': 'glpi-grafana',
                    'ports': ['3000:3000'],
                    'volumes': [
                        'grafana_data:/var/lib/grafana',
                        './scripts/monitoring/grafana/provisioning:/etc/grafana/provisioning',
                        './scripts/monitoring/grafana/dashboards:/var/lib/grafana/dashboards'
                    ],
                    'environment': {
                        'GF_SECURITY_ADMIN_PASSWORD': 'admin123',
                        'GF_USERS_ALLOW_SIGN_UP': 'false',
                        'GF_INSTALL_PLUGINS': 'grafana-piechart-panel,grafana-worldmap-panel'
                    },
                    'restart': 'unless-stopped',
                    'networks': ['monitoring'],
                    'depends_on': ['prometheus']
                },
                'alertmanager': {
                    'image': 'prom/alertmanager:latest',
                    'container_name': 'glpi-alertmanager',
                    'ports': ['9093:9093'],
                    'volumes': [
                        './scripts/monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml',
                        'alertmanager_data:/alertmanager'
                    ],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'redis': {
                    'image': 'redis:alpine',
                    'container_name': 'glpi-redis-monitoring',
                    'ports': ['6379:6379'],
                    'volumes': ['redis_data:/data'],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'node-exporter': {
                    'image': 'prom/node-exporter:latest',
                    'container_name': 'glpi-node-exporter',
                    'ports': ['9100:9100'],
                    'volumes': [
                        '/proc:/host/proc:ro',
                        '/sys:/host/sys:ro',
                        '/:/rootfs:ro'
                    ],
                    'command': [
                        '--path.procfs=/host/proc',
                        '--path.rootfs=/rootfs',
                        '--path.sysfs=/host/sys',
                        '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
                    ],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'cadvisor': {
                    'image': 'gcr.io/cadvisor/cadvisor:latest',
                    'container_name': 'glpi-cadvisor',
                    'ports': ['8080:8080'],
                    'volumes': [
                        '/:/rootfs:ro',
                        '/var/run:/var/run:ro',
                        '/sys:/sys:ro',
                        '/var/lib/docker/:/var/lib/docker:ro',
                        '/dev/disk/:/dev/disk:ro'
                    ],
                    'privileged': True,
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'jaeger': {
                    'image': 'jaegertracing/all-in-one:latest',
                    'container_name': 'glpi-jaeger',
                    'ports': [
                        '16686:16686',
                        '14268:14268'
                    ],
                    'environment': {
                        'COLLECTOR_ZIPKIN_HOST_PORT': ':9411'
                    },
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                }
            },
            'volumes': {
                'prometheus_data': {},
                'grafana_data': {},
                'alertmanager_data': {},
                'redis_data': {}
            },
            'networks': {
                'monitoring': {
                    'driver': 'bridge'
                }
            }
        }
        
        # Adicionar ELK Stack se habilitado
        if self.config.get("data_sources", {}).get("elasticsearch", {}).get("enabled", False):
            docker_compose_content['services'].update({
                'elasticsearch': {
                    'image': 'docker.elastic.co/elasticsearch/elasticsearch:8.11.0',
                    'container_name': 'glpi-elasticsearch',
                    'environment': {
                        'discovery.type': 'single-node',
                        'ES_JAVA_OPTS': '-Xms512m -Xmx512m',
                        'xpack.security.enabled': 'false'
                    },
                    'ports': ['9200:9200'],
                    'volumes': ['elasticsearch_data:/usr/share/elasticsearch/data'],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'kibana': {
                    'image': 'docker.elastic.co/kibana/kibana:8.11.0',
                    'container_name': 'glpi-kibana',
                    'ports': ['5601:5601'],
                    'environment': {
                        'ELASTICSEARCH_HOSTS': 'http://elasticsearch:9200'
                    },
                    'depends_on': ['elasticsearch'],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                },
                'logstash': {
                    'image': 'docker.elastic.co/logstash/logstash:8.11.0',
                    'container_name': 'glpi-logstash',
                    'ports': ['5044:5044'],
                    'volumes': [
                        './scripts/monitoring/logstash/pipeline:/usr/share/logstash/pipeline',
                        './scripts/monitoring/logstash/config:/usr/share/logstash/config'
                    ],
                    'depends_on': ['elasticsearch'],
                    'restart': 'unless-stopped',
                    'networks': ['monitoring']
                }
            })
            docker_compose_content['volumes']['elasticsearch_data'] = {}
        
        with open(self.docker_compose_file, 'w') as f:
            yaml.dump(docker_compose_content, f, default_flow_style=False)
        
        logger.info(f"Docker Compose file created: {self.docker_compose_file}")
    
    async def _setup_prometheus(self):
        """Configura Prometheus."""
        logger.info("Setting up Prometheus...")
        
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'rule_files': [
                '/etc/prometheus/rules/*.yml'
            ],
            'alerting': {
                'alertmanagers': [
                    {
                        'static_configs': [
                            {'targets': ['alertmanager:9093']}
                        ]
                    }
                ]
            },
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [
                        {'targets': ['localhost:9090']}
                    ]
                },
                {
                    'job_name': 'node-exporter',
                    'static_configs': [
                        {'targets': ['node-exporter:9100']}
                    ]
                },
                {
                    'job_name': 'cadvisor',
                    'static_configs': [
                        {'targets': ['cadvisor:8080']}
                    ]
                },
                {
                    'job_name': 'glpi-backend',
                    'static_configs': [
                        {'targets': ['host.docker.internal:5000']}
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'glpi-frontend',
                    'static_configs': [
                        {'targets': ['host.docker.internal:3000']}
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'glpi-monitoring',
                    'static_configs': [
                        {'targets': ['host.docker.internal:8090']}
                    ],
                    'metrics_path': '/metrics'
                }
            ]
        }
        
        prometheus_dir = self.monitoring_dir / "prometheus"
        prometheus_dir.mkdir(exist_ok=True)
        
        with open(prometheus_dir / "prometheus.yml", 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        
        # Criar regras de alerta
        await self._create_alert_rules()
        
        logger.info("Prometheus configuration created")
    
    async def _create_alert_rules(self):
        """Cria regras de alerta para Prometheus."""
        rules_dir = self.monitoring_dir / "prometheus" / "rules"
        rules_dir.mkdir(exist_ok=True)
        
        alert_rules = {
            'groups': [
                {
                    'name': 'system_alerts',
                    'rules': [
                        {
                            'alert': 'HighCPUUsage',
                            'expr': 'system_cpu_usage_percent > 80',
                            'for': '5m',
                            'labels': {'severity': 'warning'},
                            'annotations': {
                                'summary': 'High CPU usage detected',
                                'description': 'CPU usage is above 80% for more than 5 minutes'
                            }
                        },
                        {
                            'alert': 'HighMemoryUsage',
                            'expr': 'system_memory_usage_percent > 85',
                            'for': '5m',
                            'labels': {'severity': 'warning'},
                            'annotations': {
                                'summary': 'High memory usage detected',
                                'description': 'Memory usage is above 85% for more than 5 minutes'
                            }
                        },
                        {
                            'alert': 'DiskSpaceLow',
                            'expr': 'system_disk_usage_percent > 90',
                            'for': '1m',
                            'labels': {'severity': 'critical'},
                            'annotations': {
                                'summary': 'Disk space is running low',
                                'description': 'Disk usage is above 90%'
                            }
                        }
                    ]
                },
                {
                    'name': 'application_alerts',
                    'rules': [
                        {
                            'alert': 'HighErrorRate',
                            'expr': 'application_error_rate > 5',
                            'for': '2m',
                            'labels': {'severity': 'warning'},
                            'annotations': {
                                'summary': 'High error rate detected',
                                'description': 'Application error rate is above 5%'
                            }
                        },
                        {
                            'alert': 'SlowResponseTime',
                            'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2',
                            'for': '5m',
                            'labels': {'severity': 'warning'},
                            'annotations': {
                                'summary': 'Slow response time detected',
                                'description': 'P95 response time is above 2 seconds'
                            }
                        }
                    ]
                },
                {
                    'name': 'security_alerts',
                    'rules': [
                        {
                            'alert': 'HighFailedLogins',
                            'expr': 'rate(security_failed_logins_total[1h]) > 10',
                            'for': '1m',
                            'labels': {'severity': 'critical'},
                            'annotations': {
                                'summary': 'High number of failed login attempts',
                                'description': 'More than 10 failed login attempts per hour'
                            }
                        },
                        {
                            'alert': 'SuspiciousActivity',
                            'expr': 'rate(security_suspicious_requests_total[1h]) > 50',
                            'for': '1m',
                            'labels': {'severity': 'warning'},
                            'annotations': {
                                'summary': 'Suspicious activity detected',
                                'description': 'High number of suspicious requests'
                            }
                        }
                    ]
                },
                {
                    'name': 'business_alerts',
                    'rules': [
                        {
                            'alert': 'SLABreach',
                            'expr': 'business_sla_compliance_percent < 95',
                            'for': '5m',
                            'labels': {'severity': 'critical'},
                            'annotations': {
                                'summary': 'SLA compliance below target',
                                'description': 'SLA compliance is below 95%'
                            }
                        }
                    ]
                }
            ]
        }
        
        with open(rules_dir / "alerts.yml", 'w') as f:
            yaml.dump(alert_rules, f, default_flow_style=False)
        
        logger.info("Alert rules created")
    
    async def _setup_grafana(self):
        """Configura Grafana."""
        logger.info("Setting up Grafana...")
        
        grafana_dir = self.monitoring_dir / "grafana"
        
        # Configurar datasources
        datasources_dir = grafana_dir / "provisioning" / "datasources"
        datasources_dir.mkdir(parents=True, exist_ok=True)
        
        datasources_config = {
            'apiVersion': 1,
            'datasources': [
                {
                    'name': 'Prometheus',
                    'type': 'prometheus',
                    'access': 'proxy',
                    'url': 'http://prometheus:9090',
                    'isDefault': True
                },
                {
                    'name': 'Jaeger',
                    'type': 'jaeger',
                    'access': 'proxy',
                    'url': 'http://jaeger:16686'
                }
            ]
        }
        
        with open(datasources_dir / "datasources.yml", 'w') as f:
            yaml.dump(datasources_config, f, default_flow_style=False)
        
        # Configurar dashboards
        dashboards_provisioning_dir = grafana_dir / "provisioning" / "dashboards"
        dashboards_provisioning_dir.mkdir(parents=True, exist_ok=True)
        
        dashboards_config = {
            'apiVersion': 1,
            'providers': [
                {
                    'name': 'default',
                    'orgId': 1,
                    'folder': '',
                    'type': 'file',
                    'disableDeletion': False,
                    'updateIntervalSeconds': 10,
                    'allowUiUpdates': True,
                    'options': {
                        'path': '/var/lib/grafana/dashboards'
                    }
                }
            ]
        }
        
        with open(dashboards_provisioning_dir / "dashboards.yml", 'w') as f:
            yaml.dump(dashboards_config, f, default_flow_style=False)
        
        logger.info("Grafana configuration created")
    
    async def _setup_alertmanager(self):
        """Configura Alertmanager."""
        logger.info("Setting up Alertmanager...")
        
        alertmanager_dir = self.monitoring_dir / "alertmanager"
        alertmanager_dir.mkdir(exist_ok=True)
        
        notification_config = self.config.get("notification_channels", {})
        
        alertmanager_config = {
            'global': {
                'smtp_smarthost': notification_config.get("email", {}).get("smtp_server", "localhost:587"),
                'smtp_from': notification_config.get("email", {}).get("username", "monitoring@company.com")
            },
            'route': {
                'group_by': ['alertname'],
                'group_wait': '10s',
                'group_interval': '10s',
                'repeat_interval': '1h',
                'receiver': 'web.hook'
            },
            'receivers': [
                {
                    'name': 'web.hook',
                    'email_configs': [
                        {
                            'to': ', '.join(notification_config.get("email", {}).get("recipients", [])),
                            'subject': 'GLPI Alert: {{ .GroupLabels.alertname }}',
                            'body': 'Alert: {{ .GroupLabels.alertname }}\nSummary: {{ .CommonAnnotations.summary }}\nDescription: {{ .CommonAnnotations.description }}'
                        }
                    ]
                }
            ]
        }
        
        # Adicionar Slack se configurado
        if notification_config.get("slack", {}).get("enabled", False):
            slack_config = {
                'name': 'slack',
                'slack_configs': [
                    {
                        'api_url': notification_config["slack"]["webhook_url"],
                        'channel': notification_config["slack"]["channel"],
                        'username': notification_config["slack"]["username"],
                        'title': 'GLPI Alert: {{ .GroupLabels.alertname }}',
                        'text': '{{ .CommonAnnotations.summary }}\n{{ .CommonAnnotations.description }}'
                    }
                ]
            }
            alertmanager_config['receivers'].append(slack_config)
        
        with open(alertmanager_dir / "alertmanager.yml", 'w') as f:
            yaml.dump(alertmanager_config, f, default_flow_style=False)
        
        logger.info("Alertmanager configuration created")
    
    async def _setup_redis(self):
        """Configura Redis para armazenamento de métricas."""
        logger.info("Redis will be configured via Docker Compose")
    
    async def _setup_jaeger(self):
        """Configura Jaeger para tracing."""
        logger.info("Jaeger will be configured via Docker Compose")
    
    async def _setup_elk_stack(self):
        """Configura ELK Stack se habilitado."""
        logger.info("Setting up ELK Stack...")
        
        # Criar configuração do Logstash
        logstash_dir = self.monitoring_dir / "logstash"
        pipeline_dir = logstash_dir / "pipeline"
        config_dir = logstash_dir / "config"
        
        pipeline_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline configuration
        pipeline_config = """
input {
  beats {
    port => 5044
  }
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  if [fields][log_type] == "glpi" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "glpi-logs-%{+YYYY.MM.dd}"
  }
  stdout { codec => rubydebug }
}
"""
        
        with open(pipeline_dir / "logstash.conf", 'w') as f:
            f.write(pipeline_config)
        
        logger.info("ELK Stack configuration created")
    
    async def _setup_monitoring_scripts(self):
        """Configura scripts de monitoramento."""
        logger.info("Setting up monitoring scripts...")
        
        scripts_dir = self.monitoring_dir / "scripts"
        
        # Script de inicialização
        startup_script = """
#!/bin/bash
# GLPI Monitoring Startup Script

echo "Starting GLPI Advanced Monitoring System..."

# Start Docker services
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Start Python monitoring script
python3 scripts/monitoring/advanced_monitoring.py &

echo "Monitoring system started successfully!"
echo "Access points:"
echo "- Grafana: http://localhost:3000 (admin/admin123)"
echo "- Prometheus: http://localhost:9090"
echo "- Alertmanager: http://localhost:9093"
echo "- Jaeger: http://localhost:16686"
"""
        
        with open(scripts_dir / "start_monitoring.sh", 'w') as f:
            f.write(startup_script)
        
        # Tornar executável
        os.chmod(scripts_dir / "start_monitoring.sh", 0o755)
        
        # Script de parada
        stop_script = """
#!/bin/bash
# GLPI Monitoring Stop Script

echo "Stopping GLPI Advanced Monitoring System..."

# Stop Python monitoring script
pkill -f "advanced_monitoring.py"

# Stop Docker services
docker-compose -f docker-compose.monitoring.yml down

echo "Monitoring system stopped."
"""
        
        with open(scripts_dir / "stop_monitoring.sh", 'w') as f:
            f.write(stop_script)
        
        os.chmod(scripts_dir / "stop_monitoring.sh", 0o755)
        
        logger.info("Monitoring scripts created")
    
    async def _setup_systemd_services(self):
        """Configura serviços systemd (Linux apenas)."""
        logger.info("Setting up systemd services...")
        
        service_content = f"""
[Unit]
Description=GLPI Advanced Monitoring System
After=docker.service
Requires=docker.service

[Service]
Type=forking
User=root
WorkingDirectory={self.project_root}
ExecStart={self.project_root}/scripts/monitoring/scripts/start_monitoring.sh
ExecStop={self.project_root}/scripts/monitoring/scripts/stop_monitoring.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/glpi-monitoring.service")
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Recarregar systemd
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            subprocess.run(['systemctl', 'enable', 'glpi-monitoring'], check=True)
            
            logger.info("Systemd service created and enabled")
        except PermissionError:
            logger.warning("Cannot create systemd service (permission denied). Run as root or manually create the service.")
        except Exception as e:
            logger.warning(f"Failed to create systemd service: {e}")
    
    async def _start_services(self):
        """Inicia os serviços de monitoramento."""
        logger.info("Starting monitoring services...")
        
        try:
            # Iniciar Docker Compose
            result = subprocess.run(
                ['docker-compose', '-f', str(self.docker_compose_file), 'up', '-d'],
                capture_output=True, text=True, check=True
            )
            logger.info("Docker services started successfully")
            
            # Aguardar serviços ficarem prontos
            await asyncio.sleep(30)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Docker services: {e.stderr}")
            raise
    
    async def _health_check(self):
        """Verifica saúde dos serviços."""
        logger.info("Performing health checks...")
        
        services = {
            'Prometheus': 'http://localhost:9090/-/healthy',
            'Grafana': 'http://localhost:3000/api/health',
            'Alertmanager': 'http://localhost:9093/-/healthy',
            'Jaeger': 'http://localhost:16686/'
        }
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"{service_name} is healthy")
                else:
                    logger.warning(f"{service_name} returned status {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"{service_name} health check failed: {e}")
    
    async def _import_dashboards(self):
        """Importa dashboards para Grafana."""
        logger.info("Importing Grafana dashboards...")
        
        # Copiar dashboard JSON para o diretório correto
        dashboard_source = self.monitoring_dir / "grafana_dashboard.json"
        dashboard_dest = self.monitoring_dir / "grafana" / "dashboards" / "glpi_dashboard.json"
        
        if dashboard_source.exists():
            import shutil
            shutil.copy2(dashboard_source, dashboard_dest)
            logger.info("Dashboard copied to Grafana directory")
        else:
            logger.warning("Dashboard source file not found")
    
    async def _setup_alerts(self):
        """Configura alertas adicionais."""
        logger.info("Setting up additional alerts...")
        
        # Criar runbooks
        runbooks_dir = self.monitoring_dir / "runbooks"
        
        runbooks = {
            'high_cpu.md': """
# High CPU Usage Runbook

## Alert: HighCPUUsage

### Description
CPU usage is above 80% for more than 5 minutes.

### Investigation Steps
1. Check top processes: `top` or `htop`
2. Identify resource-intensive processes
3. Check for runaway processes
4. Review application logs

### Resolution
1. Kill unnecessary processes
2. Restart problematic services
3. Scale horizontally if needed
4. Optimize application code

### Prevention
- Implement proper resource limits
- Monitor application performance
- Set up auto-scaling
""",
            'security_incident.md': """
# Security Incident Runbook

## Alert: Security Breach Detected

### Description
High number of failed login attempts or suspicious activity detected.

### Immediate Actions
1. **DO NOT PANIC** - Follow the incident response plan
2. Isolate affected systems if necessary
3. Preserve evidence
4. Notify security team

### Investigation Steps
1. Review security logs
2. Identify source IPs
3. Check for data exfiltration
4. Analyze attack patterns

### Response
1. Block malicious IPs
2. Reset compromised accounts
3. Update security rules
4. Document incident

### Post-Incident
1. Conduct post-mortem
2. Update security policies
3. Improve monitoring
4. Train team on lessons learned
"""
        }
        
        for filename, content in runbooks.items():
            with open(runbooks_dir / filename, 'w') as f:
                f.write(content)
        
        logger.info("Runbooks created")
    
    async def _print_access_info(self):
        """Imprime informações de acesso."""
        print("\n" + "="*60)
        print("🚀 GLPI Advanced Monitoring System - Setup Complete!")
        print("="*60)
        print("\n📊 Access Points:")
        print(f"   • Grafana Dashboard: http://localhost:3000")
        print(f"     Username: admin | Password: admin123")
        print(f"   • Prometheus: http://localhost:9090")
        print(f"   • Alertmanager: http://localhost:9093")
        print(f"   • Jaeger Tracing: http://localhost:16686")
        
        if self.config.get("data_sources", {}).get("elasticsearch", {}).get("enabled", False):
            print(f"   • Kibana: http://localhost:5601")
            print(f"   • Elasticsearch: http://localhost:9200")
        
        print("\n🔧 Management Commands:")
        print(f"   • Start: ./scripts/monitoring/scripts/start_monitoring.sh")
        print(f"   • Stop: ./scripts/monitoring/scripts/stop_monitoring.sh")
        print(f"   • Logs: docker-compose -f {self.docker_compose_file} logs -f")
        
        print("\n📁 Important Directories:")
        print(f"   • Configuration: {self.monitoring_dir}")
        print(f"   • Reports: {self.project_root}/monitoring_reports")
        print(f"   • Logs: {self.monitoring_dir}/logs")
        
        print("\n⚠️  Next Steps:")
        print("   1. Access Grafana and explore the dashboards")
        print("   2. Configure notification channels in Alertmanager")
        print("   3. Customize alert thresholds in monitoring_config.json")
        print("   4. Set up log forwarding to ELK (if enabled)")
        print("   5. Review and customize runbooks")
        
        print("\n" + "="*60)

async def main():
    """Função principal."""
    try:
        setup = MonitoringSetup()
        await setup.setup_complete_monitoring()
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())