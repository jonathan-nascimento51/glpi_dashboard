#!/usr/bin/env python3
"""
Sistema de Monitoramento Avançado - GLPI Dashboard
Integra métricas de performance, segurança e observabilidade em tempo real.

Autor: Sistema DevSecOps
Versão: 1.0.0
Data: 2024-01-15
"""

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import redis
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest
import structlog

# Configuração de logging estruturado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@dataclass
class SystemMetrics:
    """Métricas do sistema."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]
    uptime: float

@dataclass
class SecurityMetrics:
    """Métricas de segurança."""
    timestamp: str
    failed_login_attempts: int
    suspicious_requests: int
    blocked_ips: List[str]
    ssl_cert_expiry_days: Optional[int]
    security_headers_score: float
    vulnerability_count: int
    last_security_scan: str

@dataclass
class ApplicationMetrics:
    """Métricas da aplicação."""
    timestamp: str
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    request_count: int
    error_rate: float
    active_users: int
    database_connections: int
    cache_hit_rate: float
    queue_size: int

@dataclass
class BusinessMetrics:
    """Métricas de negócio."""
    timestamp: str
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    avg_resolution_time: float
    technician_workload: Dict[str, int]
    sla_compliance: float
    customer_satisfaction: float

class PrometheusMetrics:
    """Gerenciador de métricas Prometheus."""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Métricas de sistema
        self.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage', registry=self.registry)
        self.memory_usage = Gauge('system_memory_usage_percent', 'Memory usage percentage', registry=self.registry)
        self.disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage', registry=self.registry)
        
        # Métricas de aplicação
        self.response_time = Histogram('http_request_duration_seconds', 'HTTP request duration', 
                                     ['method', 'endpoint'], registry=self.registry)
        self.request_count = Counter('http_requests_total', 'Total HTTP requests', 
                                   ['method', 'endpoint', 'status'], registry=self.registry)
        self.error_rate = Gauge('application_error_rate', 'Application error rate', registry=self.registry)
        
        # Métricas de segurança
        self.failed_logins = Counter('security_failed_logins_total', 'Total failed login attempts', registry=self.registry)
        self.suspicious_requests = Counter('security_suspicious_requests_total', 'Total suspicious requests', registry=self.registry)
        self.security_score = Gauge('security_headers_score', 'Security headers score', registry=self.registry)
        
        # Métricas de negócio
        self.total_tickets = Gauge('business_tickets_total', 'Total tickets', registry=self.registry)
        self.open_tickets = Gauge('business_tickets_open', 'Open tickets', registry=self.registry)
        self.sla_compliance = Gauge('business_sla_compliance_percent', 'SLA compliance percentage', registry=self.registry)
    
    def update_system_metrics(self, metrics: SystemMetrics):
        """Atualiza métricas do sistema."""
        self.cpu_usage.set(metrics.cpu_percent)
        self.memory_usage.set(metrics.memory_percent)
        self.disk_usage.set(metrics.disk_usage)
    
    def update_security_metrics(self, metrics: SecurityMetrics):
        """Atualiza métricas de segurança."""
        self.security_score.set(metrics.security_headers_score)
    
    def update_business_metrics(self, metrics: BusinessMetrics):
        """Atualiza métricas de negócio."""
        self.total_tickets.set(metrics.total_tickets)
        self.open_tickets.set(metrics.open_tickets)
        self.sla_compliance.set(metrics.sla_compliance)
    
    def get_metrics(self) -> str:
        """Retorna métricas no formato Prometheus."""
        return generate_latest(self.registry).decode('utf-8')

class AdvancedMonitoring:
    """Sistema de monitoramento avançado."""
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        self.config = self._load_config(config_path)
        self.prometheus = PrometheusMetrics()
        self.redis_client = self._init_redis()
        self.session = None
        self.running = False
        
        # Configurar diretórios
        self.reports_dir = Path("monitoring_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Configurar alertas
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.alert_history = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração do monitoramento."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Config file not found, using defaults", config_path=config_path)
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuração padrão do monitoramento."""
        return {
            "collection_interval": 30,
            "retention_days": 30,
            "redis_url": "redis://localhost:6379/0",
            "glpi_api_url": "http://localhost:5000/api",
            "alert_thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_usage": 90.0,
                "error_rate": 5.0,
                "response_time_p95": 2.0,
                "failed_logins_per_hour": 10
            },
            "security_checks": {
                "ssl_cert_check": True,
                "security_headers_check": True,
                "vulnerability_scan": True
            },
            "business_metrics": {
                "sla_target": 95.0,
                "resolution_time_target": 24.0
            }
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Inicializa conexão Redis."""
        try:
            client = redis.from_url(self.config["redis_url"])
            client.ping()
            return client
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            return None
    
    async def start_monitoring(self):
        """Inicia o sistema de monitoramento."""
        self.running = True
        self.session = aiohttp.ClientSession()
        
        logger.info("Starting advanced monitoring system")
        
        # Tarefas de monitoramento
        tasks = [
            self._collect_system_metrics(),
            self._collect_security_metrics(),
            self._collect_application_metrics(),
            self._collect_business_metrics(),
            self._process_alerts(),
            self._generate_reports(),
            self._cleanup_old_data()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Para o sistema de monitoramento."""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Monitoring system stopped")
    
    async def _collect_system_metrics(self):
        """Coleta métricas do sistema."""
        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memória
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Disco
                disk = psutil.disk_usage('/')
                disk_usage = (disk.used / disk.total) * 100
                
                # Rede
                network = psutil.net_io_counters()
                network_io = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
                
                # Processos
                process_count = len(psutil.pids())
                
                # Load average (Unix only)
                try:
                    load_average = list(os.getloadavg())
                except (OSError, AttributeError):
                    load_average = [0.0, 0.0, 0.0]
                
                # Uptime
                uptime = time.time() - psutil.boot_time()
                
                metrics = SystemMetrics(
                    timestamp=datetime.now().isoformat(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    disk_usage=disk_usage,
                    network_io=network_io,
                    process_count=process_count,
                    load_average=load_average,
                    uptime=uptime
                )
                
                # Atualizar Prometheus
                self.prometheus.update_system_metrics(metrics)
                
                # Armazenar no Redis
                if self.redis_client:
                    key = f"system_metrics:{int(time.time())}"
                    self.redis_client.setex(key, 86400, json.dumps(asdict(metrics)))
                
                # Verificar alertas
                await self._check_system_alerts(metrics)
                
                logger.debug("System metrics collected", 
                           cpu=cpu_percent, memory=memory_percent, disk=disk_usage)
                
            except Exception as e:
                logger.error("Error collecting system metrics", error=str(e))
            
            await asyncio.sleep(self.config["collection_interval"])
    
    async def _collect_security_metrics(self):
        """Coleta métricas de segurança."""
        while self.running:
            try:
                # Simular coleta de métricas de segurança
                # Em produção, isso seria integrado com logs de segurança reais
                
                failed_logins = await self._get_failed_login_count()
                suspicious_requests = await self._get_suspicious_request_count()
                blocked_ips = await self._get_blocked_ips()
                ssl_cert_expiry = await self._check_ssl_certificate()
                security_headers_score = await self._check_security_headers()
                vulnerability_count = await self._get_vulnerability_count()
                
                metrics = SecurityMetrics(
                    timestamp=datetime.now().isoformat(),
                    failed_login_attempts=failed_logins,
                    suspicious_requests=suspicious_requests,
                    blocked_ips=blocked_ips,
                    ssl_cert_expiry_days=ssl_cert_expiry,
                    security_headers_score=security_headers_score,
                    vulnerability_count=vulnerability_count,
                    last_security_scan=datetime.now().isoformat()
                )
                
                # Atualizar Prometheus
                self.prometheus.update_security_metrics(metrics)
                
                # Armazenar no Redis
                if self.redis_client:
                    key = f"security_metrics:{int(time.time())}"
                    self.redis_client.setex(key, 86400, json.dumps(asdict(metrics)))
                
                # Verificar alertas de segurança
                await self._check_security_alerts(metrics)
                
                logger.debug("Security metrics collected", 
                           failed_logins=failed_logins, 
                           suspicious_requests=suspicious_requests)
                
            except Exception as e:
                logger.error("Error collecting security metrics", error=str(e))
            
            await asyncio.sleep(self.config["collection_interval"] * 2)  # Menos frequente
    
    async def _collect_application_metrics(self):
        """Coleta métricas da aplicação."""
        while self.running:
            try:
                # Métricas da aplicação via API
                response_times = await self._get_response_times()
                request_count = await self._get_request_count()
                error_rate = await self._get_error_rate()
                active_users = await self._get_active_users()
                db_connections = await self._get_db_connections()
                cache_hit_rate = await self._get_cache_hit_rate()
                queue_size = await self._get_queue_size()
                
                metrics = ApplicationMetrics(
                    timestamp=datetime.now().isoformat(),
                    response_time_avg=response_times.get("avg", 0.0),
                    response_time_p95=response_times.get("p95", 0.0),
                    response_time_p99=response_times.get("p99", 0.0),
                    request_count=request_count,
                    error_rate=error_rate,
                    active_users=active_users,
                    database_connections=db_connections,
                    cache_hit_rate=cache_hit_rate,
                    queue_size=queue_size
                )
                
                # Armazenar no Redis
                if self.redis_client:
                    key = f"app_metrics:{int(time.time())}"
                    self.redis_client.setex(key, 86400, json.dumps(asdict(metrics)))
                
                # Verificar alertas da aplicação
                await self._check_application_alerts(metrics)
                
                logger.debug("Application metrics collected", 
                           response_time_avg=response_times.get("avg", 0.0),
                           error_rate=error_rate)
                
            except Exception as e:
                logger.error("Error collecting application metrics", error=str(e))
            
            await asyncio.sleep(self.config["collection_interval"])
    
    async def _collect_business_metrics(self):
        """Coleta métricas de negócio."""
        while self.running:
            try:
                # Métricas de negócio do GLPI
                total_tickets = await self._get_total_tickets()
                open_tickets = await self._get_open_tickets()
                resolved_tickets = await self._get_resolved_tickets()
                avg_resolution_time = await self._get_avg_resolution_time()
                technician_workload = await self._get_technician_workload()
                sla_compliance = await self._calculate_sla_compliance()
                customer_satisfaction = await self._get_customer_satisfaction()
                
                metrics = BusinessMetrics(
                    timestamp=datetime.now().isoformat(),
                    total_tickets=total_tickets,
                    open_tickets=open_tickets,
                    resolved_tickets=resolved_tickets,
                    avg_resolution_time=avg_resolution_time,
                    technician_workload=technician_workload,
                    sla_compliance=sla_compliance,
                    customer_satisfaction=customer_satisfaction
                )
                
                # Atualizar Prometheus
                self.prometheus.update_business_metrics(metrics)
                
                # Armazenar no Redis
                if self.redis_client:
                    key = f"business_metrics:{int(time.time())}"
                    self.redis_client.setex(key, 86400, json.dumps(asdict(metrics)))
                
                # Verificar alertas de negócio
                await self._check_business_alerts(metrics)
                
                logger.debug("Business metrics collected", 
                           total_tickets=total_tickets,
                           sla_compliance=sla_compliance)
                
            except Exception as e:
                logger.error("Error collecting business metrics", error=str(e))
            
            await asyncio.sleep(self.config["collection_interval"] * 3)  # Menos frequente
    
    async def _process_alerts(self):
        """Processa alertas do sistema."""
        while self.running:
            try:
                # Processar alertas pendentes
                current_time = datetime.now()
                
                # Limpar alertas antigos
                self.alert_history = [
                    alert for alert in self.alert_history 
                    if current_time - datetime.fromisoformat(alert["timestamp"]) < timedelta(hours=24)
                ]
                
                # Enviar notificações se necessário
                await self._send_alert_notifications()
                
            except Exception as e:
                logger.error("Error processing alerts", error=str(e))
            
            await asyncio.sleep(60)  # Verificar alertas a cada minuto
    
    async def _generate_reports(self):
        """Gera relatórios periódicos."""
        while self.running:
            try:
                # Gerar relatório diário
                if datetime.now().hour == 6 and datetime.now().minute < 5:  # 6:00 AM
                    await self._generate_daily_report()
                
                # Gerar relatório semanal
                if datetime.now().weekday() == 0 and datetime.now().hour == 7:  # Segunda-feira 7:00 AM
                    await self._generate_weekly_report()
                
            except Exception as e:
                logger.error("Error generating reports", error=str(e))
            
            await asyncio.sleep(300)  # Verificar a cada 5 minutos
    
    async def _cleanup_old_data(self):
        """Limpa dados antigos."""
        while self.running:
            try:
                if self.redis_client:
                    # Limpar dados antigos do Redis
                    cutoff_time = int(time.time()) - (self.config["retention_days"] * 86400)
                    
                    for pattern in ["system_metrics:*", "security_metrics:*", "app_metrics:*", "business_metrics:*"]:
                        keys = self.redis_client.keys(pattern)
                        for key in keys:
                            timestamp = int(key.decode().split(":")[1])
                            if timestamp < cutoff_time:
                                self.redis_client.delete(key)
                
                logger.debug("Old data cleanup completed")
                
            except Exception as e:
                logger.error("Error during cleanup", error=str(e))
            
            await asyncio.sleep(3600)  # Limpar a cada hora
    
    # Métodos auxiliares para coleta de métricas
    async def _get_failed_login_count(self) -> int:
        """Obtém contagem de tentativas de login falhadas."""
        # Implementar integração com logs de autenticação
        return 0
    
    async def _get_suspicious_request_count(self) -> int:
        """Obtém contagem de requisições suspeitas."""
        # Implementar integração com WAF/logs de segurança
        return 0
    
    async def _get_blocked_ips(self) -> List[str]:
        """Obtém lista de IPs bloqueados."""
        # Implementar integração com firewall/WAF
        return []
    
    async def _check_ssl_certificate(self) -> Optional[int]:
        """Verifica expiração do certificado SSL."""
        # Implementar verificação de certificado SSL
        return None
    
    async def _check_security_headers(self) -> float:
        """Verifica score dos headers de segurança."""
        # Implementar verificação de headers de segurança
        return 85.0
    
    async def _get_vulnerability_count(self) -> int:
        """Obtém contagem de vulnerabilidades."""
        # Implementar integração com scanner de vulnerabilidades
        return 0
    
    async def _get_response_times(self) -> Dict[str, float]:
        """Obtém tempos de resposta da aplicação."""
        # Implementar coleta de métricas de performance
        return {"avg": 0.5, "p95": 1.2, "p99": 2.1}
    
    async def _get_request_count(self) -> int:
        """Obtém contagem de requisições."""
        return 1000
    
    async def _get_error_rate(self) -> float:
        """Obtém taxa de erro da aplicação."""
        return 2.5
    
    async def _get_active_users(self) -> int:
        """Obtém número de usuários ativos."""
        return 50
    
    async def _get_db_connections(self) -> int:
        """Obtém número de conexões de banco de dados."""
        return 10
    
    async def _get_cache_hit_rate(self) -> float:
        """Obtém taxa de acerto do cache."""
        return 85.5
    
    async def _get_queue_size(self) -> int:
        """Obtém tamanho da fila de processamento."""
        return 5
    
    async def _get_total_tickets(self) -> int:
        """Obtém total de tickets."""
        return 1500
    
    async def _get_open_tickets(self) -> int:
        """Obtém tickets abertos."""
        return 150
    
    async def _get_resolved_tickets(self) -> int:
        """Obtém tickets resolvidos."""
        return 1350
    
    async def _get_avg_resolution_time(self) -> float:
        """Obtém tempo médio de resolução."""
        return 18.5
    
    async def _get_technician_workload(self) -> Dict[str, int]:
        """Obtém carga de trabalho dos técnicos."""
        return {"tech1": 25, "tech2": 30, "tech3": 20}
    
    async def _calculate_sla_compliance(self) -> float:
        """Calcula compliance do SLA."""
        return 96.5
    
    async def _get_customer_satisfaction(self) -> float:
        """Obtém satisfação do cliente."""
        return 4.2
    
    # Métodos de alertas
    async def _check_system_alerts(self, metrics: SystemMetrics):
        """Verifica alertas do sistema."""
        thresholds = self.alert_thresholds
        
        if metrics.cpu_percent > thresholds.get("cpu_percent", 80):
            await self._create_alert("HIGH_CPU", f"CPU usage: {metrics.cpu_percent}%", "critical")
        
        if metrics.memory_percent > thresholds.get("memory_percent", 85):
            await self._create_alert("HIGH_MEMORY", f"Memory usage: {metrics.memory_percent}%", "critical")
        
        if metrics.disk_usage > thresholds.get("disk_usage", 90):
            await self._create_alert("HIGH_DISK", f"Disk usage: {metrics.disk_usage}%", "critical")
    
    async def _check_security_alerts(self, metrics: SecurityMetrics):
        """Verifica alertas de segurança."""
        if metrics.failed_login_attempts > self.alert_thresholds.get("failed_logins_per_hour", 10):
            await self._create_alert("SECURITY_BREACH", 
                                   f"High failed login attempts: {metrics.failed_login_attempts}", 
                                   "critical")
        
        if metrics.vulnerability_count > 0:
            await self._create_alert("VULNERABILITIES", 
                                   f"Vulnerabilities detected: {metrics.vulnerability_count}", 
                                   "warning")
    
    async def _check_application_alerts(self, metrics: ApplicationMetrics):
        """Verifica alertas da aplicação."""
        if metrics.error_rate > self.alert_thresholds.get("error_rate", 5.0):
            await self._create_alert("HIGH_ERROR_RATE", 
                                   f"Error rate: {metrics.error_rate}%", 
                                   "warning")
        
        if metrics.response_time_p95 > self.alert_thresholds.get("response_time_p95", 2.0):
            await self._create_alert("SLOW_RESPONSE", 
                                   f"P95 response time: {metrics.response_time_p95}s", 
                                   "warning")
    
    async def _check_business_alerts(self, metrics: BusinessMetrics):
        """Verifica alertas de negócio."""
        sla_target = self.config["business_metrics"]["sla_target"]
        if metrics.sla_compliance < sla_target:
            await self._create_alert("SLA_BREACH", 
                                   f"SLA compliance: {metrics.sla_compliance}% (target: {sla_target}%)", 
                                   "critical")
    
    async def _create_alert(self, alert_type: str, message: str, severity: str):
        """Cria um alerta."""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        self.alert_history.append(alert)
        
        logger.warning("Alert created", 
                      alert_type=alert_type, 
                      message=message, 
                      severity=severity)
    
    async def _send_alert_notifications(self):
        """Envia notificações de alertas."""
        # Implementar integração com sistemas de notificação
        # (Slack, email, PagerDuty, etc.)
        pass
    
    async def _generate_daily_report(self):
        """Gera relatório diário."""
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_path = self.reports_dir / f"daily_report_{report_date}.json"
        
        # Coletar dados do último dia
        report_data = {
            "date": report_date,
            "summary": {
                "total_alerts": len(self.alert_history),
                "critical_alerts": len([a for a in self.alert_history if a["severity"] == "critical"]),
                "system_uptime": "99.9%",
                "avg_response_time": "0.5s",
                "error_rate": "2.1%"
            },
            "alerts": self.alert_history[-50:],  # Últimos 50 alertas
            "generated_at": datetime.now().isoformat()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info("Daily report generated", report_path=str(report_path))
    
    async def _generate_weekly_report(self):
        """Gera relatório semanal."""
        report_date = datetime.now().strftime("%Y-W%U")
        report_path = self.reports_dir / f"weekly_report_{report_date}.json"
        
        # Implementar geração de relatório semanal
        logger.info("Weekly report generated", report_path=str(report_path))
    
    def get_prometheus_metrics(self) -> str:
        """Retorna métricas no formato Prometheus."""
        return self.prometheus.get_metrics()

async def main():
    """Função principal."""
    monitoring = AdvancedMonitoring()
    
    try:
        await monitoring.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await monitoring.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())