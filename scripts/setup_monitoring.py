#!/usr/bin/env python3
"""
Advanced Monitoring Setup Script for GLPI Dashboard

This script configures comprehensive monitoring including:
- Application performance monitoring (APM)
- Security monitoring and alerting
- Infrastructure monitoring
- Log aggregation and analysis
- Custom metrics and dashboards
- Health checks and uptime monitoring

Usage:
    python scripts/setup_monitoring.py [--environment prod|dev|staging] [--enable-all]
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import requests
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MonitoringSetup:
    """Advanced monitoring configuration for GLPI Dashboard."""
    
    def __init__(self, environment: str = "dev", project_root: str = None):
        self.environment = environment
        self.project_root = Path(project_root or os.getcwd())
        self.monitoring_dir = self.project_root / "monitoring"
        self.monitoring_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.monitoring_dir / "prometheus").mkdir(exist_ok=True)
        (self.monitoring_dir / "grafana").mkdir(exist_ok=True)
        (self.monitoring_dir / "alertmanager").mkdir(exist_ok=True)
        (self.monitoring_dir / "loki").mkdir(exist_ok=True)
        (self.monitoring_dir / "jaeger").mkdir(exist_ok=True)
        
        # Monitoring stack configuration
        self.monitoring_stack = {
            "prometheus": {
                "port": 9090,
                "description": "Metrics collection and storage"
            },
            "grafana": {
                "port": 3000,
                "description": "Visualization and dashboards"
            },
            "alertmanager": {
                "port": 9093,
                "description": "Alert routing and management"
            },
            "loki": {
                "port": 3100,
                "description": "Log aggregation"
            },
            "jaeger": {
                "port": 16686,
                "description": "Distributed tracing"
            },
            "node_exporter": {
                "port": 9100,
                "description": "System metrics"
            }
        }
    
    def create_prometheus_config(self) -> str:
        """Create Prometheus configuration."""
        logger.info("Creating Prometheus configuration...")
        
        config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "rule_files": [
                "alert_rules.yml"
            ],
            "alerting": {
                "alertmanagers": [{
                    "static_configs": [{
                        "targets": ["alertmanager:9093"]
                    }]
                }]
            },
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [{
                        "targets": ["localhost:9090"]
                    }]
                },
                {
                    "job_name": "glpi-backend",
                    "static_configs": [{
                        "targets": ["backend:5000"]
                    }],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                },
                {
                    "job_name": "glpi-frontend",
                    "static_configs": [{
                        "targets": ["frontend:3000"]
                    }],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                },
                {
                    "job_name": "node-exporter",
                    "static_configs": [{
                        "targets": ["node-exporter:9100"]
                    }]
                },
                {
                    "job_name": "redis",
                    "static_configs": [{
                        "targets": ["redis:6379"]
                    }]
                },
                {
                    "job_name": "postgres",
                    "static_configs": [{
                        "targets": ["postgres:5432"]
                    }]
                },
                {
                    "job_name": "nginx",
                    "static_configs": [{
                        "targets": ["nginx:80"]
                    }],
                    "metrics_path": "/nginx_status"
                }
            ]
        }
        
        config_file = self.monitoring_dir / "prometheus" / "prometheus.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Prometheus config created: {config_file}")
        return str(config_file)
    
    def create_alert_rules(self) -> str:
        """Create Prometheus alert rules."""
        logger.info("Creating Prometheus alert rules...")
        
        rules = {
            "groups": [
                {
                    "name": "glpi_dashboard_alerts",
                    "rules": [
                        {
                            "alert": "HighErrorRate",
                            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) > 0.1",
                            "for": "5m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "High error rate detected",
                                "description": "Error rate is above 10% for 5 minutes"
                            }
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1",
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High response time detected",
                                "description": "95th percentile response time is above 1 second"
                            }
                        },
                        {
                            "alert": "ServiceDown",
                            "expr": "up == 0",
                            "for": "1m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "Service is down",
                                "description": "{{ $labels.instance }} has been down for more than 1 minute"
                            }
                        },
                        {
                            "alert": "HighCPUUsage",
                            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100) > 80",
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High CPU usage detected",
                                "description": "CPU usage is above 80% for 5 minutes on {{ $labels.instance }}"
                            }
                        },
                        {
                            "alert": "HighMemoryUsage",
                            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85",
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High memory usage detected",
                                "description": "Memory usage is above 85% for 5 minutes on {{ $labels.instance }}"
                            }
                        },
                        {
                            "alert": "DiskSpaceLow",
                            "expr": "(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90",
                            "for": "5m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "Disk space is running low",
                                "description": "Disk usage is above 90% on {{ $labels.instance }}"
                            }
                        },
                        {
                            "alert": "SecurityVulnerabilityDetected",
                            "expr": "security_vulnerabilities_total > 0",
                            "for": "0m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "Security vulnerability detected",
                                "description": "{{ $value }} security vulnerabilities detected in the application"
                            }
                        },
                        {
                            "alert": "FailedLoginAttempts",
                            "expr": "rate(failed_login_attempts_total[5m]) > 10",
                            "for": "2m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High number of failed login attempts",
                                "description": "More than 10 failed login attempts per minute detected"
                            }
                        }
                    ]
                }
            ]
        }
        
        rules_file = self.monitoring_dir / "prometheus" / "alert_rules.yml"
        with open(rules_file, 'w') as f:
            yaml.dump(rules, f, default_flow_style=False)
        
        logger.info(f"Alert rules created: {rules_file}")
        return str(rules_file)
    
    def create_alertmanager_config(self) -> str:
        """Create Alertmanager configuration."""
        logger.info("Creating Alertmanager configuration...")
        
        config = {
            "global": {
                "smtp_smarthost": "localhost:587",
                "smtp_from": "alerts@glpi-dashboard.local"
            },
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "web.hook",
                "routes": [
                    {
                        "match": {
                            "severity": "critical"
                        },
                        "receiver": "critical-alerts"
                    },
                    {
                        "match": {
                            "severity": "warning"
                        },
                        "receiver": "warning-alerts"
                    }
                ]
            },
            "receivers": [
                {
                    "name": "web.hook",
                    "webhook_configs": [
                        {
                            "url": "http://localhost:5001/alerts"
                        }
                    ]
                },
                {
                    "name": "critical-alerts",
                    "email_configs": [
                        {
                            "to": "admin@glpi-dashboard.local",
                            "subject": "CRITICAL: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ],
                    "slack_configs": [
                        {
                            "api_url": "YOUR_SLACK_WEBHOOK_URL",
                            "channel": "#alerts",
                            "title": "Critical Alert: {{ .GroupLabels.alertname }}",
                            "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ]
                },
                {
                    "name": "warning-alerts",
                    "email_configs": [
                        {
                            "to": "team@glpi-dashboard.local",
                            "subject": "WARNING: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ]
                }
            ]
        }
        
        config_file = self.monitoring_dir / "alertmanager" / "alertmanager.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Alertmanager config created: {config_file}")
        return str(config_file)
    
    def create_grafana_dashboards(self) -> List[str]:
        """Create Grafana dashboard configurations."""
        logger.info("Creating Grafana dashboards...")
        
        dashboards = []
        
        # Application Performance Dashboard
        app_dashboard = {
            "dashboard": {
                "id": None,
                "title": "GLPI Dashboard - Application Performance",
                "tags": ["glpi", "performance"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total[5m])",
                                "legendFormat": "{{ method }} {{ status }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "95th percentile"
                            },
                            {
                                "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "50th percentile"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "singlestat",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
                                "legendFormat": "Error Rate %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Active Users",
                        "type": "singlestat",
                        "targets": [
                            {
                                "expr": "active_users_total",
                                "legendFormat": "Active Users"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 8}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "5s"
            }
        }
        
        app_dashboard_file = self.monitoring_dir / "grafana" / "app_performance_dashboard.json"
        with open(app_dashboard_file, 'w') as f:
            json.dump(app_dashboard, f, indent=2)
        dashboards.append(str(app_dashboard_file))
        
        # Security Dashboard
        security_dashboard = {
            "dashboard": {
                "id": None,
                "title": "GLPI Dashboard - Security Monitoring",
                "tags": ["glpi", "security"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Failed Login Attempts",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(failed_login_attempts_total[5m])",
                                "legendFormat": "Failed Logins/min"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Security Vulnerabilities",
                        "type": "singlestat",
                        "targets": [
                            {
                                "expr": "security_vulnerabilities_total",
                                "legendFormat": "Vulnerabilities"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Suspicious Activities",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(suspicious_activities_total[5m])",
                                "legendFormat": "Suspicious Activities/min"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    }
                ],
                "time": {
                    "from": "now-24h",
                    "to": "now"
                },
                "refresh": "30s"
            }
        }
        
        security_dashboard_file = self.monitoring_dir / "grafana" / "security_dashboard.json"
        with open(security_dashboard_file, 'w') as f:
            json.dump(security_dashboard, f, indent=2)
        dashboards.append(str(security_dashboard_file))
        
        # Infrastructure Dashboard
        infra_dashboard = {
            "dashboard": {
                "id": None,
                "title": "GLPI Dashboard - Infrastructure",
                "tags": ["glpi", "infrastructure"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                                "legendFormat": "{{ instance }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
                                "legendFormat": "{{ instance }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Disk Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100",
                                "legendFormat": "{{ instance }} - {{ mountpoint }}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Network I/O",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(node_network_receive_bytes_total[5m])",
                                "legendFormat": "{{ instance }} - RX"
                            },
                            {
                                "expr": "rate(node_network_transmit_bytes_total[5m])",
                                "legendFormat": "{{ instance }} - TX"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "10s"
            }
        }
        
        infra_dashboard_file = self.monitoring_dir / "grafana" / "infrastructure_dashboard.json"
        with open(infra_dashboard_file, 'w') as f:
            json.dump(infra_dashboard, f, indent=2)
        dashboards.append(str(infra_dashboard_file))
        
        logger.info(f"Created {len(dashboards)} Grafana dashboards")
        return dashboards
    
    def create_loki_config(self) -> str:
        """Create Loki configuration for log aggregation."""
        logger.info("Creating Loki configuration...")
        
        config = {
            "auth_enabled": False,
            "server": {
                "http_listen_port": 3100
            },
            "ingester": {
                "lifecycler": {
                    "address": "127.0.0.1",
                    "ring": {
                        "kvstore": {
                            "store": "inmemory"
                        },
                        "replication_factor": 1
                    }
                },
                "chunk_idle_period": "5m",
                "chunk_retain_period": "30s"
            },
            "schema_config": {
                "configs": [
                    {
                        "from": "2020-10-24",
                        "store": "boltdb",
                        "object_store": "filesystem",
                        "schema": "v11",
                        "index": {
                            "prefix": "index_",
                            "period": "168h"
                        }
                    }
                ]
            },
            "storage_config": {
                "boltdb": {
                    "directory": "/tmp/loki/index"
                },
                "filesystem": {
                    "directory": "/tmp/loki/chunks"
                }
            },
            "limits_config": {
                "enforce_metric_name": False,
                "reject_old_samples": True,
                "reject_old_samples_max_age": "168h"
            }
        }
        
        config_file = self.monitoring_dir / "loki" / "loki.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Loki config created: {config_file}")
        return str(config_file)
    
    def create_docker_compose(self) -> str:
        """Create Docker Compose file for monitoring stack."""
        logger.info("Creating Docker Compose for monitoring stack...")
        
        compose_config = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "prometheus",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./monitoring/prometheus:/etc/prometheus",
                        "prometheus_data:/prometheus"
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=200h",
                        "--web.enable-lifecycle"
                    ],
                    "restart": "unless-stopped"
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "grafana",
                    "ports": ["3000:3000"],
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./monitoring/grafana:/etc/grafana/provisioning"
                    ],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "admin123",
                        "GF_USERS_ALLOW_SIGN_UP": "false"
                    },
                    "restart": "unless-stopped"
                },
                "alertmanager": {
                    "image": "prom/alertmanager:latest",
                    "container_name": "alertmanager",
                    "ports": ["9093:9093"],
                    "volumes": [
                        "./monitoring/alertmanager:/etc/alertmanager"
                    ],
                    "restart": "unless-stopped"
                },
                "loki": {
                    "image": "grafana/loki:latest",
                    "container_name": "loki",
                    "ports": ["3100:3100"],
                    "volumes": [
                        "./monitoring/loki:/etc/loki"
                    ],
                    "command": "-config.file=/etc/loki/loki.yml",
                    "restart": "unless-stopped"
                },
                "promtail": {
                    "image": "grafana/promtail:latest",
                    "container_name": "promtail",
                    "volumes": [
                        "/var/log:/var/log:ro",
                        "./monitoring/promtail:/etc/promtail"
                    ],
                    "command": "-config.file=/etc/promtail/promtail.yml",
                    "restart": "unless-stopped"
                },
                "jaeger": {
                    "image": "jaegertracing/all-in-one:latest",
                    "container_name": "jaeger",
                    "ports": [
                        "16686:16686",
                        "14268:14268"
                    ],
                    "environment": {
                        "COLLECTOR_ZIPKIN_HTTP_PORT": "9411"
                    },
                    "restart": "unless-stopped"
                },
                "node-exporter": {
                    "image": "prom/node-exporter:latest",
                    "container_name": "node-exporter",
                    "ports": ["9100:9100"],
                    "volumes": [
                        "/proc:/host/proc:ro",
                        "/sys:/host/sys:ro",
                        "/:/rootfs:ro"
                    ],
                    "command": [
                        "--path.procfs=/host/proc",
                        "--path.rootfs=/rootfs",
                        "--path.sysfs=/host/sys",
                        "--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)"
                    ],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "prometheus_data": {},
                "grafana_data": {}
            },
            "networks": {
                "monitoring": {
                    "driver": "bridge"
                }
            }
        }
        
        compose_file = self.monitoring_dir / "docker-compose.monitoring.yml"
        with open(compose_file, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False)
        
        logger.info(f"Docker Compose file created: {compose_file}")
        return str(compose_file)
    
    def create_health_check_script(self) -> str:
        """Create health check script for monitoring services."""
        logger.info("Creating health check script...")
        
        health_check_script = '''
#!/usr/bin/env python3
"""
Health Check Script for GLPI Dashboard Monitoring

Checks the health of all monitoring services and the main application.
"""

import requests
import sys
import json
from datetime import datetime

def check_service(name, url, timeout=5):
    """Check if a service is healthy."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return {"service": name, "status": "healthy", "response_time": response.elapsed.total_seconds()}
        else:
            return {"service": name, "status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"service": name, "status": "unhealthy", "error": str(e)}

def main():
    services = [
        ("Prometheus", "http://localhost:9090/-/healthy"),
        ("Grafana", "http://localhost:3000/api/health"),
        ("Alertmanager", "http://localhost:9093/-/healthy"),
        ("Loki", "http://localhost:3100/ready"),
        ("Jaeger", "http://localhost:16686/"),
        ("Node Exporter", "http://localhost:9100/metrics"),
        ("GLPI Backend", "http://localhost:5000/health"),
        ("GLPI Frontend", "http://localhost:3000/")
    ]
    
    results = []
    for name, url in services:
        result = check_service(name, url)
        results.append(result)
        print(f"{result['service']}: {result['status']}")
        if result['status'] == 'unhealthy':
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    # Generate health report
    healthy_services = [r for r in results if r['status'] == 'healthy']
    unhealthy_services = [r for r in results if r['status'] == 'unhealthy']
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "total_services": len(services),
        "healthy_services": len(healthy_services),
        "unhealthy_services": len(unhealthy_services),
        "health_percentage": (len(healthy_services) / len(services)) * 100,
        "services": results
    }
    
    # Save health report
    with open("health_report.json", "w") as f:
        json.dump(health_report, f, indent=2)
    
    print(f"\nHealth Summary:")
    print(f"Healthy: {len(healthy_services)}/{len(services)} ({health_report['health_percentage']:.1f}%)")
    
    if unhealthy_services:
        print(f"Unhealthy services: {', '.join([s['service'] for s in unhealthy_services])}")
        sys.exit(1)
    else:
        print("All services are healthy!")
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
        
        health_check_file = self.monitoring_dir / "health_check.py"
        with open(health_check_file, 'w') as f:
            f.write(health_check_script)
        
        # Make script executable
        os.chmod(health_check_file, 0o755)
        
        logger.info(f"Health check script created: {health_check_file}")
        return str(health_check_file)
    
    def setup_monitoring_stack(self) -> Dict[str, Any]:
        """Set up complete monitoring stack."""
        logger.info("Setting up complete monitoring stack...")
        
        setup_results = {
            "prometheus_config": self.create_prometheus_config(),
            "alert_rules": self.create_alert_rules(),
            "alertmanager_config": self.create_alertmanager_config(),
            "grafana_dashboards": self.create_grafana_dashboards(),
            "loki_config": self.create_loki_config(),
            "docker_compose": self.create_docker_compose(),
            "health_check": self.create_health_check_script()
        }
        
        # Create monitoring documentation
        self.create_monitoring_documentation()
        
        logger.info("Monitoring stack setup completed successfully!")
        return setup_results
    
    def create_monitoring_documentation(self) -> str:
        """Create monitoring documentation."""
        logger.info("Creating monitoring documentation...")
        
        documentation = f'''
# GLPI Dashboard - Advanced Monitoring Setup

## Overview
This monitoring setup provides comprehensive observability for the GLPI Dashboard application including:

- **Metrics Collection**: Prometheus for application and infrastructure metrics
- **Visualization**: Grafana dashboards for performance and security monitoring
- **Alerting**: Alertmanager for intelligent alert routing
- **Log Aggregation**: Loki for centralized log management
- **Distributed Tracing**: Jaeger for request tracing
- **Health Monitoring**: Automated health checks

## Quick Start

### 1. Start Monitoring Stack
```bash
# Start all monitoring services
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Check service health
python monitoring/health_check.py
```

### 2. Access Dashboards
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Jaeger**: http://localhost:16686

### 3. Import Dashboards
Grafana dashboards are available in `monitoring/grafana/` directory:
- Application Performance Dashboard
- Security Monitoring Dashboard
- Infrastructure Dashboard

## Configuration

### Environment: {self.environment}

### Services Configuration
'''
        
        for service, config in self.monitoring_stack.items():
            documentation += f"\n- **{service.title()}**: Port {config['port']} - {config['description']}"
        
        documentation += '''

## Metrics and Alerts

### Application Metrics
- Request rate and response times
- Error rates and status codes
- Active user sessions
- Database query performance
- Cache hit rates

### Security Metrics
- Failed login attempts
- Security vulnerability counts
- Suspicious activity detection
- Authentication events

### Infrastructure Metrics
- CPU, Memory, and Disk usage
- Network I/O
- Container resource utilization
- Service availability

### Alert Rules
- High error rate (>10% for 5 minutes)
- High response time (>1 second 95th percentile)
- Service downtime
- Resource exhaustion (CPU >80%, Memory >85%, Disk >90%)
- Security incidents

## Maintenance

### Regular Tasks
1. Review and update alert thresholds
2. Clean up old metrics data
3. Update monitoring stack components
4. Review security dashboards
5. Test alert notifications

### Troubleshooting

#### Service Not Starting
```bash
# Check service logs
docker-compose -f monitoring/docker-compose.monitoring.yml logs [service_name]

# Restart specific service
docker-compose -f monitoring/docker-compose.monitoring.yml restart [service_name]
```

#### Missing Metrics
1. Verify application is exposing metrics endpoint
2. Check Prometheus targets status
3. Validate scrape configuration

#### Alert Not Firing
1. Check alert rule syntax
2. Verify metric availability
3. Test alert expression in Prometheus

## Security Considerations

1. **Access Control**: Configure authentication for Grafana and Prometheus
2. **Network Security**: Use reverse proxy with SSL/TLS
3. **Data Retention**: Configure appropriate retention policies
4. **Backup**: Regular backup of configuration and dashboards

## Performance Tuning

1. **Prometheus**: Adjust scrape intervals based on requirements
2. **Grafana**: Optimize dashboard queries for better performance
3. **Loki**: Configure log retention and compression
4. **Storage**: Monitor disk usage and configure cleanup policies

## Integration

### Application Integration
Add these metrics to your application:

```python
# Python/Flask example
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Security metrics
FAILED_LOGINS = Counter('failed_login_attempts_total', 'Failed login attempts')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
```

### Custom Alerts
Add custom alert rules to `monitoring/prometheus/alert_rules.yml`:

```yaml
- alert: CustomAlert
  expr: your_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom alert description"
```

## Support

For issues and questions:
1. Check service logs
2. Review configuration files
3. Consult official documentation
4. Contact system administrator
'''
        
        doc_file = self.monitoring_dir / "README.md"
        with open(doc_file, 'w') as f:
            f.write(documentation)
        
        logger.info(f"Monitoring documentation created: {doc_file}")
        return str(doc_file)

def main():
    parser = argparse.ArgumentParser(description="Setup advanced monitoring for GLPI Dashboard")
    parser.add_argument("--environment", choices=["dev", "staging", "prod"], default="dev",
                       help="Target environment")
    parser.add_argument("--enable-all", action="store_true",
                       help="Enable all monitoring components")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    monitoring_setup = MonitoringSetup(args.environment, args.project_root)
    
    # Setup monitoring stack
    results = monitoring_setup.setup_monitoring_stack()
    
    logger.info("\n=== Monitoring Setup Summary ===")
    logger.info(f"Environment: {args.environment}")
    logger.info(f"Configuration files created:")
    
    for component, file_path in results.items():
        if isinstance(file_path, list):
            logger.info(f"  {component}: {len(file_path)} files")
            for fp in file_path:
                logger.info(f"    - {fp}")
        else:
            logger.info(f"  {component}: {file_path}")
    
    logger.info("\nNext steps:")
    logger.info("1. Review and customize configuration files")
    logger.info("2. Start monitoring stack: docker-compose -f monitoring/docker-compose.monitoring.yml up -d")
    logger.info("3. Access Grafana at http://localhost:3000 (admin/admin123)")
    logger.info("4. Import dashboards and configure alerts")
    logger.info("5. Run health check: python monitoring/health_check.py")
    
    logger.info("\nMonitoring setup completed successfully!")

if __name__ == "__main__":
    main()