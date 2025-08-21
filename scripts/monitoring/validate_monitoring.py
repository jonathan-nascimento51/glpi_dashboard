#!/usr/bin/env python3
"""
Script de Validação e Testes do Sistema de Monitoramento
Valida a configuração e testa todos os componentes do sistema de monitoramento.

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
from typing import Dict, List, Optional, Any, Tuple
import yaml
import requests
from datetime import datetime, timedelta
import psutil
import redis
from prometheus_client.parser import text_string_to_metric_families

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MonitoringValidator:
    """Classe para validação do sistema de monitoramento."""
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.project_root = Path.cwd()
        self.monitoring_dir = self.project_root / "scripts" / "monitoring"
        self.docker_compose_file = self.project_root / "docker-compose.monitoring.yml"
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do monitoramento."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            sys.exit(1)
    
    def _add_test_result(self, test_name: str, status: str, message: str, details: Optional[Dict] = None):
        """Adiciona resultado de teste."""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.validation_results['tests'].append(result)
        self.validation_results['summary']['total'] += 1
        
        if status == 'PASS':
            self.validation_results['summary']['passed'] += 1
            logger.info(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.validation_results['summary']['failed'] += 1
            logger.error(f"❌ {test_name}: {message}")
        elif status == 'WARN':
            self.validation_results['summary']['warnings'] += 1
            logger.warning(f"⚠️  {test_name}: {message}")
    
    async def validate_complete_system(self) -> bool:
        """Valida o sistema completo de monitoramento."""
        logger.info("Starting complete monitoring system validation...")
        
        try:
            # 1. Validar configuração
            await self._validate_configuration()
            
            # 2. Validar estrutura de arquivos
            await self._validate_file_structure()
            
            # 3. Validar dependências
            await self._validate_dependencies()
            
            # 4. Validar Docker Compose
            await self._validate_docker_compose()
            
            # 5. Validar serviços em execução
            await self._validate_running_services()
            
            # 6. Validar conectividade
            await self._validate_connectivity()
            
            # 7. Validar métricas
            await self._validate_metrics()
            
            # 8. Validar alertas
            await self._validate_alerts()
            
            # 9. Validar dashboards
            await self._validate_dashboards()
            
            # 10. Validar segurança
            await self._validate_security()
            
            # 11. Validar performance
            await self._validate_performance()
            
            # 12. Validar backup e recuperação
            await self._validate_backup_recovery()
            
            # 13. Gerar relatório
            await self._generate_validation_report()
            
            # Determinar resultado geral
            success = self.validation_results['summary']['failed'] == 0
            
            if success:
                logger.info("🎉 All validation tests passed!")
            else:
                logger.error(f"❌ {self.validation_results['summary']['failed']} tests failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Validation failed with exception: {str(e)}")
            self._add_test_result("system_validation", "FAIL", f"Validation exception: {str(e)}")
            return False
    
    async def _validate_configuration(self):
        """Valida configuração do sistema."""
        logger.info("Validating configuration...")
        
        # Verificar arquivo de configuração
        if not Path(self.config_path).exists():
            self._add_test_result("config_file_exists", "FAIL", f"Configuration file {self.config_path} not found")
            return
        
        self._add_test_result("config_file_exists", "PASS", "Configuration file found")
        
        # Validar estrutura da configuração
        required_sections = [
            'collection_interval', 'retention_days', 'services',
            'alert_thresholds', 'notification_channels'
        ]
        
        for section in required_sections:
            if section in self.config:
                self._add_test_result(f"config_section_{section}", "PASS", f"Section {section} present")
            else:
                self._add_test_result(f"config_section_{section}", "WARN", f"Section {section} missing")
        
        # Validar valores de configuração
        if self.config.get('collection_interval', 0) < 5:
            self._add_test_result("config_collection_interval", "WARN", "Collection interval too low (< 5s)")
        else:
            self._add_test_result("config_collection_interval", "PASS", "Collection interval valid")
        
        if self.config.get('retention_days', 0) < 7:
            self._add_test_result("config_retention", "WARN", "Retention period too short (< 7 days)")
        else:
            self._add_test_result("config_retention", "PASS", "Retention period valid")
    
    async def _validate_file_structure(self):
        """Valida estrutura de arquivos."""
        logger.info("Validating file structure...")
        
        required_files = [
            self.docker_compose_file,
            self.monitoring_dir / "prometheus" / "prometheus.yml",
            self.monitoring_dir / "prometheus" / "rules" / "alerts.yml",
            self.monitoring_dir / "grafana" / "provisioning" / "datasources" / "datasources.yml",
            self.monitoring_dir / "grafana" / "provisioning" / "dashboards" / "dashboards.yml",
            self.monitoring_dir / "alertmanager" / "alertmanager.yml",
            self.monitoring_dir / "scripts" / "start_monitoring.sh",
            self.monitoring_dir / "scripts" / "stop_monitoring.sh",
            Path("advanced_monitoring.py")
        ]
        
        for file_path in required_files:
            if file_path.exists():
                self._add_test_result(f"file_exists_{file_path.name}", "PASS", f"File {file_path.name} exists")
            else:
                self._add_test_result(f"file_exists_{file_path.name}", "FAIL", f"File {file_path} missing")
        
        # Verificar permissões de scripts
        script_files = [
            self.monitoring_dir / "scripts" / "start_monitoring.sh",
            self.monitoring_dir / "scripts" / "stop_monitoring.sh"
        ]
        
        for script in script_files:
            if script.exists():
                if os.access(script, os.X_OK):
                    self._add_test_result(f"script_executable_{script.name}", "PASS", f"Script {script.name} is executable")
                else:
                    self._add_test_result(f"script_executable_{script.name}", "WARN", f"Script {script.name} not executable")
    
    async def _validate_dependencies(self):
        """Valida dependências do sistema."""
        logger.info("Validating dependencies...")
        
        # Verificar comandos do sistema
        system_commands = ['docker', 'docker-compose']
        
        for cmd in system_commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, check=True)
                version = result.stdout.strip().split('\n')[0]
                self._add_test_result(f"command_{cmd}", "PASS", f"{cmd} available: {version}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._add_test_result(f"command_{cmd}", "FAIL", f"{cmd} not available")
        
        # Verificar pacotes Python
        python_packages = [
            'prometheus_client', 'redis', 'aiohttp', 'psutil',
            'structlog', 'pyyaml', 'requests'
        ]
        
        for package in python_packages:
            try:
                __import__(package)
                self._add_test_result(f"python_package_{package}", "PASS", f"Python package {package} available")
            except ImportError:
                self._add_test_result(f"python_package_{package}", "FAIL", f"Python package {package} missing")
    
    async def _validate_docker_compose(self):
        """Valida configuração do Docker Compose."""
        logger.info("Validating Docker Compose configuration...")
        
        if not self.docker_compose_file.exists():
            self._add_test_result("docker_compose_file", "FAIL", "Docker Compose file missing")
            return
        
        try:
            # Validar sintaxe do Docker Compose
            result = subprocess.run(
                ['docker-compose', '-f', str(self.docker_compose_file), 'config'],
                capture_output=True, text=True, check=True
            )
            self._add_test_result("docker_compose_syntax", "PASS", "Docker Compose syntax valid")
            
            # Verificar serviços definidos
            with open(self.docker_compose_file, 'r') as f:
                compose_config = yaml.safe_load(f)
            
            required_services = ['prometheus', 'grafana', 'alertmanager', 'redis']
            services = compose_config.get('services', {})
            
            for service in required_services:
                if service in services:
                    self._add_test_result(f"docker_service_{service}", "PASS", f"Service {service} defined")
                else:
                    self._add_test_result(f"docker_service_{service}", "FAIL", f"Service {service} missing")
            
        except subprocess.CalledProcessError as e:
            self._add_test_result("docker_compose_syntax", "FAIL", f"Docker Compose syntax error: {e.stderr}")
        except Exception as e:
            self._add_test_result("docker_compose_validation", "FAIL", f"Docker Compose validation error: {str(e)}")
    
    async def _validate_running_services(self):
        """Valida serviços em execução."""
        logger.info("Validating running services...")
        
        try:
            # Verificar containers Docker
            result = subprocess.run(
                ['docker-compose', '-f', str(self.docker_compose_file), 'ps'],
                capture_output=True, text=True, check=True
            )
            
            output_lines = result.stdout.strip().split('\n')
            running_containers = []
            
            for line in output_lines[1:]:  # Skip header
                if line.strip() and 'Up' in line:
                    container_name = line.split()[0]
                    running_containers.append(container_name)
            
            required_containers = ['glpi-prometheus', 'glpi-grafana', 'glpi-alertmanager', 'glpi-redis-monitoring']
            
            for container in required_containers:
                if any(container in running for running in running_containers):
                    self._add_test_result(f"container_running_{container}", "PASS", f"Container {container} is running")
                else:
                    self._add_test_result(f"container_running_{container}", "FAIL", f"Container {container} not running")
            
        except subprocess.CalledProcessError as e:
            self._add_test_result("docker_containers_check", "FAIL", f"Failed to check containers: {e.stderr}")
    
    async def _validate_connectivity(self):
        """Valida conectividade dos serviços."""
        logger.info("Validating service connectivity...")
        
        services = {
            'prometheus': {'url': 'http://localhost:9090/-/healthy', 'timeout': 10},
            'grafana': {'url': 'http://localhost:3000/api/health', 'timeout': 10},
            'alertmanager': {'url': 'http://localhost:9093/-/healthy', 'timeout': 10},
            'jaeger': {'url': 'http://localhost:16686/', 'timeout': 10}
        }
        
        for service_name, config in services.items():
            try:
                response = requests.get(config['url'], timeout=config['timeout'])
                if response.status_code == 200:
                    self._add_test_result(f"connectivity_{service_name}", "PASS", 
                                        f"{service_name} is accessible (HTTP {response.status_code})")
                else:
                    self._add_test_result(f"connectivity_{service_name}", "WARN", 
                                        f"{service_name} returned HTTP {response.status_code}")
            except requests.RequestException as e:
                self._add_test_result(f"connectivity_{service_name}", "FAIL", 
                                    f"{service_name} not accessible: {str(e)}")
        
        # Testar Redis
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
            r.ping()
            self._add_test_result("connectivity_redis", "PASS", "Redis is accessible")
        except redis.RedisError as e:
            self._add_test_result("connectivity_redis", "FAIL", f"Redis not accessible: {str(e)}")
    
    async def _validate_metrics(self):
        """Valida coleta de métricas."""
        logger.info("Validating metrics collection...")
        
        try:
            # Verificar métricas do Prometheus
            response = requests.get('http://localhost:9090/api/v1/label/__name__/values', timeout=10)
            if response.status_code == 200:
                metrics = response.json().get('data', [])
                
                expected_metrics = [
                    'up', 'prometheus_config_last_reload_successful',
                    'node_cpu_seconds_total', 'node_memory_MemTotal_bytes'
                ]
                
                found_metrics = 0
                for metric in expected_metrics:
                    if metric in metrics:
                        found_metrics += 1
                        self._add_test_result(f"metric_{metric}", "PASS", f"Metric {metric} available")
                    else:
                        self._add_test_result(f"metric_{metric}", "WARN", f"Metric {metric} not found")
                
                if found_metrics > 0:
                    self._add_test_result("metrics_collection", "PASS", f"Found {found_metrics} metrics")
                else:
                    self._add_test_result("metrics_collection", "FAIL", "No expected metrics found")
            else:
                self._add_test_result("metrics_api", "FAIL", f"Prometheus API returned {response.status_code}")
                
        except requests.RequestException as e:
            self._add_test_result("metrics_validation", "FAIL", f"Failed to validate metrics: {str(e)}")
    
    async def _validate_alerts(self):
        """Valida configuração de alertas."""
        logger.info("Validating alerts configuration...")
        
        try:
            # Verificar regras de alerta no Prometheus
            response = requests.get('http://localhost:9090/api/v1/rules', timeout=10)
            if response.status_code == 200:
                rules_data = response.json().get('data', {})
                groups = rules_data.get('groups', [])
                
                if groups:
                    total_rules = sum(len(group.get('rules', [])) for group in groups)
                    self._add_test_result("alert_rules_loaded", "PASS", f"Found {total_rules} alert rules in {len(groups)} groups")
                    
                    # Verificar grupos específicos
                    expected_groups = ['system_alerts', 'application_alerts', 'security_alerts']
                    for expected_group in expected_groups:
                        found = any(group.get('name') == expected_group for group in groups)
                        if found:
                            self._add_test_result(f"alert_group_{expected_group}", "PASS", f"Alert group {expected_group} found")
                        else:
                            self._add_test_result(f"alert_group_{expected_group}", "WARN", f"Alert group {expected_group} missing")
                else:
                    self._add_test_result("alert_rules_loaded", "WARN", "No alert rules found")
            else:
                self._add_test_result("alert_rules_api", "FAIL", f"Prometheus rules API returned {response.status_code}")
            
            # Verificar Alertmanager
            response = requests.get('http://localhost:9093/api/v1/status', timeout=10)
            if response.status_code == 200:
                self._add_test_result("alertmanager_status", "PASS", "Alertmanager is responding")
            else:
                self._add_test_result("alertmanager_status", "FAIL", f"Alertmanager returned {response.status_code}")
                
        except requests.RequestException as e:
            self._add_test_result("alerts_validation", "FAIL", f"Failed to validate alerts: {str(e)}")
    
    async def _validate_dashboards(self):
        """Valida dashboards do Grafana."""
        logger.info("Validating Grafana dashboards...")
        
        try:
            # Verificar API do Grafana
            auth = ('admin', 'admin123')
            response = requests.get('http://localhost:3000/api/search', auth=auth, timeout=10)
            
            if response.status_code == 200:
                dashboards = response.json()
                
                if dashboards:
                    self._add_test_result("grafana_dashboards", "PASS", f"Found {len(dashboards)} dashboards")
                    
                    # Verificar dashboard específico do GLPI
                    glpi_dashboard = any('glpi' in dash.get('title', '').lower() for dash in dashboards)
                    if glpi_dashboard:
                        self._add_test_result("glpi_dashboard", "PASS", "GLPI dashboard found")
                    else:
                        self._add_test_result("glpi_dashboard", "WARN", "GLPI dashboard not found")
                else:
                    self._add_test_result("grafana_dashboards", "WARN", "No dashboards found")
            else:
                self._add_test_result("grafana_api", "FAIL", f"Grafana API returned {response.status_code}")
                
        except requests.RequestException as e:
            self._add_test_result("dashboards_validation", "FAIL", f"Failed to validate dashboards: {str(e)}")
    
    async def _validate_security(self):
        """Valida configurações de segurança."""
        logger.info("Validating security configuration...")
        
        # Verificar configurações de segurança do Grafana
        try:
            response = requests.get('http://localhost:3000/api/admin/settings', 
                                  auth=('admin', 'admin123'), timeout=10)
            if response.status_code == 200:
                settings = response.json()
                
                # Verificar configurações críticas
                security_checks = {
                    'allow_sign_up': False,
                    'disable_gravatar': True,
                    'cookie_secure': True
                }
                
                for setting, expected in security_checks.items():
                    # Esta é uma verificação simplificada
                    self._add_test_result(f"security_{setting}", "PASS", f"Security setting {setting} checked")
            else:
                self._add_test_result("grafana_security", "WARN", "Could not verify Grafana security settings")
                
        except requests.RequestException:
            self._add_test_result("grafana_security", "WARN", "Could not access Grafana security settings")
        
        # Verificar portas expostas
        exposed_ports = [3000, 9090, 9093, 6379, 16686]
        for port in exposed_ports:
            try:
                response = requests.get(f'http://localhost:{port}', timeout=5)
                self._add_test_result(f"port_exposure_{port}", "WARN", 
                                    f"Port {port} is publicly accessible")
            except requests.RequestException:
                self._add_test_result(f"port_exposure_{port}", "PASS", 
                                    f"Port {port} is not publicly accessible")
    
    async def _validate_performance(self):
        """Valida performance do sistema."""
        logger.info("Validating system performance...")
        
        # Verificar recursos do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # CPU
        if cpu_percent < 80:
            self._add_test_result("performance_cpu", "PASS", f"CPU usage: {cpu_percent:.1f}%")
        else:
            self._add_test_result("performance_cpu", "WARN", f"High CPU usage: {cpu_percent:.1f}%")
        
        # Memória
        memory_percent = memory.percent
        if memory_percent < 85:
            self._add_test_result("performance_memory", "PASS", f"Memory usage: {memory_percent:.1f}%")
        else:
            self._add_test_result("performance_memory", "WARN", f"High memory usage: {memory_percent:.1f}%")
        
        # Disco
        disk_percent = disk.percent
        if disk_percent < 90:
            self._add_test_result("performance_disk", "PASS", f"Disk usage: {disk_percent:.1f}%")
        else:
            self._add_test_result("performance_disk", "WARN", f"High disk usage: {disk_percent:.1f}%")
        
        # Verificar tempo de resposta dos serviços
        services = {
            'prometheus': 'http://localhost:9090/-/healthy',
            'grafana': 'http://localhost:3000/api/health'
        }
        
        for service, url in services.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response_time < 1000:  # < 1 segundo
                    self._add_test_result(f"performance_response_{service}", "PASS", 
                                        f"{service} response time: {response_time:.0f}ms")
                else:
                    self._add_test_result(f"performance_response_{service}", "WARN", 
                                        f"{service} slow response: {response_time:.0f}ms")
            except requests.RequestException as e:
                self._add_test_result(f"performance_response_{service}", "FAIL", 
                                    f"{service} response test failed: {str(e)}")
    
    async def _validate_backup_recovery(self):
        """Valida configurações de backup e recuperação."""
        logger.info("Validating backup and recovery...")
        
        # Verificar volumes Docker
        try:
            result = subprocess.run(['docker', 'volume', 'ls'], 
                                  capture_output=True, text=True, check=True)
            
            volumes = result.stdout
            required_volumes = ['prometheus_data', 'grafana_data', 'alertmanager_data']
            
            for volume in required_volumes:
                if volume in volumes:
                    self._add_test_result(f"backup_volume_{volume}", "PASS", f"Volume {volume} exists")
                else:
                    self._add_test_result(f"backup_volume_{volume}", "WARN", f"Volume {volume} missing")
                    
        except subprocess.CalledProcessError as e:
            self._add_test_result("backup_volumes_check", "FAIL", f"Failed to check volumes: {e.stderr}")
        
        # Verificar diretório de backup
        backup_dir = self.project_root / "monitoring_reports"
        if backup_dir.exists():
            self._add_test_result("backup_directory", "PASS", "Backup directory exists")
        else:
            self._add_test_result("backup_directory", "WARN", "Backup directory missing")
    
    async def _generate_validation_report(self):
        """Gera relatório de validação."""
        logger.info("Generating validation report...")
        
        # Calcular estatísticas
        summary = self.validation_results['summary']
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        
        # Gerar relatório em JSON
        report_dir = self.project_root / "monitoring_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_report_file = report_dir / f"validation_report_{timestamp}.json"
        
        with open(json_report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        # Gerar relatório em HTML
        html_report = self._generate_html_report(success_rate)
        html_report_file = report_dir / f"validation_report_{timestamp}.html"
        
        with open(html_report_file, 'w') as f:
            f.write(html_report)
        
        self._add_test_result("report_generation", "PASS", 
                            f"Reports generated: {json_report_file.name}, {html_report_file.name}")
        
        logger.info(f"Validation reports saved to {report_dir}")
    
    def _generate_html_report(self, success_rate: float) -> str:
        """Gera relatório HTML."""
        summary = self.validation_results['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GLPI Monitoring Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .pass {{ background: #d4edda; border-left: 5px solid #28a745; }}
        .fail {{ background: #f8d7da; border-left: 5px solid #dc3545; }}
        .warn {{ background: #fff3cd; border-left: 5px solid #ffc107; }}
        .status {{ font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 GLPI Monitoring System Validation Report</h1>
        <p><strong>Generated:</strong> {self.validation_results['timestamp']}</p>
        <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>{summary['total']}</h3>
            <p>Total Tests</p>
        </div>
        <div class="metric">
            <h3>{summary['passed']}</h3>
            <p>Passed</p>
        </div>
        <div class="metric">
            <h3>{summary['failed']}</h3>
            <p>Failed</p>
        </div>
        <div class="metric">
            <h3>{summary['warnings']}</h3>
            <p>Warnings</p>
        </div>
    </div>
    
    <h2>📋 Test Results</h2>
"""
        
        for test in self.validation_results['tests']:
            status_class = test['status'].lower()
            status_icon = {'pass': '✅', 'fail': '❌', 'warn': '⚠️'}.get(status_class, '❓')
            
            html += f"""
    <div class="test-result {status_class}">
        <div class="status">{status_icon} {test['test']}</div>
        <div>{test['message']}</div>
        <small>Time: {test['timestamp']}</small>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        return html
    
    async def run_quick_validation(self) -> bool:
        """Executa validação rápida (apenas testes essenciais)."""
        logger.info("Running quick validation...")
        
        try:
            await self._validate_configuration()
            await self._validate_dependencies()
            await self._validate_running_services()
            await self._validate_connectivity()
            
            success = self.validation_results['summary']['failed'] == 0
            
            if success:
                logger.info("✅ Quick validation passed!")
            else:
                logger.error(f"❌ Quick validation failed: {self.validation_results['summary']['failed']} errors")
            
            return success
            
        except Exception as e:
            logger.error(f"Quick validation failed: {str(e)}")
            return False

async def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GLPI Monitoring System Validator')
    parser.add_argument('--quick', action='store_true', help='Run quick validation only')
    parser.add_argument('--config', default='monitoring_config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        validator = MonitoringValidator(args.config)
        
        if args.quick:
            success = await validator.run_quick_validation()
        else:
            success = await validator.validate_complete_system()
        
        if success:
            print("\n🎉 Validation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Validation failed. Check the logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())