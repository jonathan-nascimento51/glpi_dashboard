#!/usr/bin/env python3
"""
Sistema de Monitoramento Proativo - GLPI Dashboard

Este módulo implementa um sistema de monitoramento contínuo das métricas
com alertas automáticos para detectar inconsistências antes que se tornem
problemas críticos.

Autor: Sistema de Otimização GLPI Dashboard
Data: 2025-01-14
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import aiohttp
import psutil
from concurrent.futures import ThreadPoolExecutor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/monitoring.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Níveis de alerta do sistema"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class MetricStatus(Enum):
    """Status das métricas"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

@dataclass
class MetricThreshold:
    """Definição de limites para métricas"""
    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    expected_range: Optional[tuple] = None
    zero_tolerance: bool = False
    change_threshold: float = 0.2  # 20% de mudança
    consecutive_failures: int = 3

@dataclass
class Alert:
    """Estrutura de alerta"""
    id: str
    timestamp: datetime
    level: AlertLevel
    metric_name: str
    message: str
    current_value: Any
    expected_value: Any
    threshold: MetricThreshold
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

@dataclass
class MonitoringResult:
    """Resultado do monitoramento"""
    timestamp: datetime
    metric_name: str
    value: Any
    status: MetricStatus
    alerts: List[Alert]
    performance_ms: float
    metadata: Dict[str, Any]

class ProactiveMonitoringSystem:
    """Sistema de Monitoramento Proativo"""
    
    def __init__(self, config_file: str = "config_monitoring.py"):
        self.config = self._load_config(config_file)
        self.thresholds = self._load_thresholds()
        self.active_alerts: Dict[str, Alert] = {}
        self.metric_history: Dict[str, List[MonitoringResult]] = {}
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Criar diretórios necessários
        Path("logs").mkdir(exist_ok=True)
        Path("alerts").mkdir(exist_ok=True)
        Path("reports/monitoring").mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Carregar configurações do sistema"""
        try:
            # Configurações padrão
            default_config = {
                "monitoring_interval": 30,  # segundos
                "api_base_url": "http://localhost:8000",
                "frontend_url": "http://localhost:8050",
                "database_url": "postgresql://localhost:5432/glpi",
                "alert_channels": {
                    "email": False,
                    "slack": False,
                    "file": True
                },
                "retention_days": 30,
                "max_history_size": 1000
            }
            
            # Tentar carregar configurações personalizadas
            if Path(config_file).exists():
                with open(config_file, "r") as f:
                    custom_config = eval(f.read())
                    default_config.update(custom_config)
            
            return default_config
        except Exception as e:
            logger.warning(f"Erro ao carregar configurações: {e}. Usando padrões.")
            return {
                "monitoring_interval": 30,
                "api_base_url": "http://localhost:8000",
                "frontend_url": "http://localhost:8050",
                "alert_channels": {"file": True},
                "retention_days": 30
            }
    
    def _load_thresholds(self) -> Dict[str, MetricThreshold]:
        """Carregar limites das métricas"""
        return {
            "tickets_by_status": MetricThreshold(
                name="tickets_by_status",
                min_value=0,
                zero_tolerance=True,
                change_threshold=0.3
            ),
            "total_open_tickets": MetricThreshold(
                name="total_open_tickets",
                min_value=0,
                zero_tolerance=True,
                change_threshold=0.25
            ),
            "resolution_rate": MetricThreshold(
                name="resolution_rate",
                min_value=0.0,
                max_value=1.0,
                expected_range=(0.1, 0.9)
            ),
            "api_response_time": MetricThreshold(
                name="api_response_time",
                max_value=5000,  # 5 segundos
                change_threshold=0.5
            ),
            "database_connections": MetricThreshold(
                name="database_connections",
                max_value=100,
                change_threshold=0.4
            ),
            "memory_usage": MetricThreshold(
                name="memory_usage",
                max_value=0.85,  # 85%
                change_threshold=0.2
            ),
            "cpu_usage": MetricThreshold(
                name="cpu_usage",
                max_value=0.80,  # 80%
                change_threshold=0.3
            )
        }
    
    async def start_monitoring(self):
        """Iniciar monitoramento contínuo"""
        logger.info(" Iniciando Sistema de Monitoramento Proativo")
        self.is_running = True
        
        # Tarefas de monitoramento
        tasks = [
            self._monitor_api_metrics(),
            self._monitor_system_resources(),
            self._monitor_database_health(),
            self._monitor_frontend_health(),
            self._process_alerts(),
            self._cleanup_old_data()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
        finally:
            self.is_running = False
            logger.info(" Monitoramento interrompido")
    
    async def stop_monitoring(self):
        """Parar monitoramento"""
        logger.info(" Parando monitoramento...")
        self.is_running = False
    
    async def _monitor_api_metrics(self):
        """Monitorar métricas da API"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Endpoints críticos para monitorar
                endpoints = [
                    "/api/v1/tickets/summary",
                    "/api/v1/tickets/by-status",
                    "/api/v1/metrics/resolution-rate",
                    "/health",
                    "/metrics"
                ]
                
                for endpoint in endpoints:
                    await self._check_api_endpoint(endpoint)
                
                # Monitorar métricas específicas
                await self._check_tickets_metrics()
                await self._check_performance_metrics()
                
                execution_time = (time.time() - start_time) * 1000
                logger.debug(f"Ciclo de monitoramento API: {execution_time:.2f}ms")
                
            except Exception as e:
                logger.error(f"Erro no monitoramento da API: {e}")
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    "api_monitoring",
                    f"Falha no monitoramento da API: {e}",
                    None, None
                )
            
            await asyncio.sleep(self.config["monitoring_interval"])
    
    async def _check_api_endpoint(self, endpoint: str):
        """Verificar saúde de um endpoint específico"""
        url = f"{self.config["api_base_url"]}{endpoint}"
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # Verificar tempo de resposta
                    threshold = self.thresholds.get("api_response_time")
                    if threshold and response_time > threshold.max_value:
                        await self._create_alert(
                            AlertLevel.WARNING,
                            f"api_response_time_{endpoint}",
                            f"Endpoint {endpoint} lento: {response_time:.2f}ms",
                            response_time,
                            threshold.max_value
                        )
                    
                    # Verificar status HTTP
                    if response.status >= 400:
                        await self._create_alert(
                            AlertLevel.CRITICAL,
                            f"api_status_{endpoint}",
                            f"Endpoint {endpoint} retornou status {response.status}",
                            response.status,
                            200
                        )
                    
                    # Registrar resultado
                    result = MonitoringResult(
                        timestamp=datetime.now(),
                        metric_name=f"api_endpoint_{endpoint}",
                        value={
                            "status_code": response.status,
                            "response_time_ms": response_time
                        },
                        status=MetricStatus.HEALTHY if response.status < 400 else MetricStatus.CRITICAL,
                        alerts=[],
                        performance_ms=response_time,
                        metadata={"endpoint": endpoint, "url": url}
                    )
                    
                    self._store_metric_result(result)
                    
        except asyncio.TimeoutError:
            await self._create_alert(
                AlertLevel.CRITICAL,
                f"api_timeout_{endpoint}",
                f"Timeout no endpoint {endpoint}",
                "timeout",
                "< 10s"
            )
        except Exception as e:
            await self._create_alert(
                AlertLevel.CRITICAL,
                f"api_error_{endpoint}",
                f"Erro no endpoint {endpoint}: {e}",
                str(e),
                "success"
            )
    
    async def _check_tickets_metrics(self):
        """Verificar métricas específicas de tickets"""
        try:
            url = f"{self.config["api_base_url"]}/api/v1/tickets/summary"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Verificar tickets por status
                        tickets_by_status = data.get("tickets_by_status", {})
                        total_tickets = sum(tickets_by_status.values()) if tickets_by_status else 0
                        
                        # Alerta para dados zerados
                        if total_tickets == 0:
                            await self._create_alert(
                                AlertLevel.CRITICAL,
                                "tickets_zero_data",
                                "Todos os tickets estão retornando zero - possível problema na API GLPI",
                                0,
                                "> 0"
                            )
                        
                        # Verificar mudanças bruscas
                        await self._check_metric_changes("total_tickets", total_tickets)
                        
                        # Verificar cada status individualmente
                        for status, count in tickets_by_status.items():
                            await self._check_metric_changes(f"tickets_status_{status}", count)
                        
                        # Registrar resultado
                        result = MonitoringResult(
                            timestamp=datetime.now(),
                            metric_name="tickets_summary",
                            value=data,
                            status=MetricStatus.HEALTHY if total_tickets > 0 else MetricStatus.CRITICAL,
                            alerts=[],
                            performance_ms=0,
                            metadata={"total_tickets": total_tickets}
                        )
                        
                        self._store_metric_result(result)
                        
        except Exception as e:
            logger.error(f"Erro ao verificar métricas de tickets: {e}")
    
    async def _check_performance_metrics(self):
        """Verificar métricas de performance"""
        try:
            # Verificar tempo de resposta da API principal
            start_time = time.time()
            url = f"{self.config["api_base_url"]}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    await self._check_threshold("api_response_time", response_time)
                    
                    result = MonitoringResult(
                        timestamp=datetime.now(),
                        metric_name="api_performance",
                        value=response_time,
                        status=MetricStatus.HEALTHY if response_time < 5000 else MetricStatus.DEGRADED,
                        alerts=[],
                        performance_ms=response_time,
                        metadata={"endpoint": "/health"}
                    )
                    
                    self._store_metric_result(result)
                    
        except Exception as e:
            logger.error(f"Erro ao verificar métricas de performance: {e}")
    
    async def _monitor_system_resources(self):
        """Monitorar recursos do sistema"""
        while self.is_running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                await self._check_threshold("cpu_usage", cpu_percent / 100)
                
                # Memória
                memory = psutil.virtual_memory()
                await self._check_threshold("memory_usage", memory.percent / 100)
                
                # Disco
                disk = psutil.disk_usage("/")
                await self._check_threshold("disk_usage", disk.percent / 100)
                
                # Processos
                process_count = len(psutil.pids())
                
                # Registrar resultados
                system_metrics = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "process_count": process_count
                }
                
                result = MonitoringResult(
                    timestamp=datetime.now(),
                    metric_name="system_resources",
                    value=system_metrics,
                    status=MetricStatus.HEALTHY,
                    alerts=[],
                    performance_ms=0,
                    metadata=system_metrics
                )
                
                self._store_metric_result(result)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de recursos: {e}")
            
            await asyncio.sleep(self.config["monitoring_interval"])
    
    async def _monitor_database_health(self):
        """Monitorar saúde do banco de dados"""
        while self.is_running:
            try:
                # Verificar se o endpoint de health responde
                url = f"{self.config["api_base_url"]}/health"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            db_status = health_data.get("database", "unknown")
                            
                            if db_status != "healthy":
                                await self._create_alert(
                                    AlertLevel.CRITICAL,
                                    "database_health",
                                    f"Banco de dados não está saudável: {db_status}",
                                    db_status,
                                    "healthy"
                                )
                        else:
                            await self._create_alert(
                                AlertLevel.CRITICAL,
                                "database_connection",
                                "Não foi possível verificar saúde do banco",
                                "unreachable",
                                "reachable"
                            )
                            
            except Exception as e:
                logger.error(f"Erro no monitoramento do banco: {e}")
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    "database_monitoring",
                    f"Falha no monitoramento do banco: {e}",
                    str(e),
                    "success"
                )
            
            await asyncio.sleep(self.config["monitoring_interval"] * 2)  # Menos frequente
    
    async def _monitor_frontend_health(self):
        """Monitorar saúde do frontend"""
        while self.is_running:
            try:
                url = self.config["frontend_url"]
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            await self._create_alert(
                                AlertLevel.WARNING,
                                "frontend_health",
                                f"Frontend não está respondendo corretamente: {response.status}",
                                response.status,
                                200
                            )
                            
            except Exception as e:
                logger.error(f"Erro no monitoramento do frontend: {e}")
                await self._create_alert(
                    AlertLevel.WARNING,
                    "frontend_monitoring",
                    f"Falha no monitoramento do frontend: {e}",
                    str(e),
                    "success"
                )
            
            await asyncio.sleep(self.config["monitoring_interval"] * 3)  # Menos frequente
    
    async def _check_threshold(self, metric_name: str, value: float):
        """Verificar se métrica está dentro dos limites"""
        threshold = self.thresholds.get(metric_name)
        if not threshold:
            return
        
        alert_level = None
        message = None
        
        # Verificar valor mínimo
        if threshold.min_value is not None and value < threshold.min_value:
            alert_level = AlertLevel.WARNING
            message = f"{metric_name} abaixo do mínimo: {value} < {threshold.min_value}"
        
        # Verificar valor máximo
        if threshold.max_value is not None and value > threshold.max_value:
            alert_level = AlertLevel.CRITICAL if value > threshold.max_value * 1.2 else AlertLevel.WARNING
            message = f"{metric_name} acima do máximo: {value} > {threshold.max_value}"
        
        # Verificar tolerância zero
        if threshold.zero_tolerance and value == 0:
            alert_level = AlertLevel.CRITICAL
            message = f"{metric_name} está zerado quando deveria ter valor"
        
        # Verificar mudanças bruscas
        await self._check_metric_changes(metric_name, value)
        
        if alert_level and message:
            await self._create_alert(alert_level, metric_name, message, value, threshold.max_value or threshold.min_value)
    
    async def _check_metric_changes(self, metric_name: str, current_value: float):
        """Verificar mudanças bruscas nas métricas"""
        history = self.metric_history.get(metric_name, [])
        
        if len(history) < 3:  # Precisa de histórico mínimo
            return
        
        # Calcular média dos últimos valores
        recent_values = [r.value for r in history[-5:] if isinstance(r.value, (int, float))]
        
        if not recent_values:
            return
        
        avg_value = sum(recent_values) / len(recent_values)
        
        if avg_value == 0:
            return  # Evitar divisão por zero
        
        # Calcular mudança percentual
        change_percent = abs(current_value - avg_value) / avg_value
        
        threshold = self.thresholds.get(metric_name)
        if threshold and change_percent > threshold.change_threshold:
            await self._create_alert(
                AlertLevel.WARNING,
                f"{metric_name}_sudden_change",
                f"Mudança brusca em {metric_name}: {change_percent:.1%} (atual: {current_value}, média: {avg_value:.2f})",
                current_value,
                avg_value
            )
    
    async def _create_alert(self, level: AlertLevel, metric_name: str, message: str, current_value: Any, expected_value: Any):
        """Criar e processar alerta"""
        alert_id = f"{metric_name}_{int(time.time())}"
        
        # Evitar spam de alertas
        existing_alert_key = f"{metric_name}_{level.value}"
        if existing_alert_key in self.active_alerts:
            last_alert = self.active_alerts[existing_alert_key]
            if (datetime.now() - last_alert.timestamp).seconds < 300:  # 5 minutos
                return
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            level=level,
            metric_name=metric_name,
            message=message,
            current_value=current_value,
            expected_value=expected_value,
            threshold=self.thresholds.get(metric_name)
        )
        
        self.active_alerts[existing_alert_key] = alert
        
        # Log do alerta
        logger.warning(f" ALERTA {level.value}: {message}")
        
        # Salvar alerta em arquivo
        await self._save_alert(alert)
        
        # Enviar notificações
        await self._send_notifications(alert)
    
    async def _save_alert(self, alert: Alert):
        """Salvar alerta em arquivo"""
        try:
            alert_file = f"alerts/alert_{alert.timestamp.strftime("%Y%m%d")}.json"
            
            # Carregar alertas existentes
            alerts_data = []
            if Path(alert_file).exists():
                with open(alert_file, "r") as f:
                    alerts_data = json.load(f)
            
            # Adicionar novo alerta
            alert_dict = asdict(alert)
            alert_dict["timestamp"] = alert.timestamp.isoformat()
            if alert.resolution_timestamp:
                alert_dict["resolution_timestamp"] = alert.resolution_timestamp.isoformat()
            
            alerts_data.append(alert_dict)
            
            # Salvar
            with open(alert_file, "w") as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar alerta: {e}")
    
    async def _send_notifications(self, alert: Alert):
        """Enviar notificações do alerta"""
        try:
            channels = self.config.get("alert_channels", {})
            
            # Notificação por arquivo (sempre ativa)
            if channels.get("file", True):
                notification_file = f"alerts/notifications_{datetime.now().strftime("%Y%m%d")}.log"
                with open(notification_file, "a", encoding="utf-8") as f:
                    f.write(f"[{alert.timestamp}] {alert.level.value}: {alert.message}\n")
            
            # TODO: Implementar outras notificações (email, slack, etc.)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificações: {e}")
    
    def _store_metric_result(self, result: MonitoringResult):
        """Armazenar resultado de métrica no histórico"""
        metric_name = result.metric_name
        
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []
        
        self.metric_history[metric_name].append(result)
        
        # Limitar tamanho do histórico
        max_size = self.config.get("max_history_size", 1000)
        if len(self.metric_history[metric_name]) > max_size:
            self.metric_history[metric_name] = self.metric_history[metric_name][-max_size:]
    
    async def _process_alerts(self):
        """Processar e resolver alertas"""
        while self.is_running:
            try:
                current_time = datetime.now()
                resolved_alerts = []
                
                for alert_key, alert in self.active_alerts.items():
                    # Auto-resolver alertas antigos (implementar lógica específica)
                    if (current_time - alert.timestamp).seconds > 3600:  # 1 hora
                        alert.resolved = True
                        alert.resolution_timestamp = current_time
                        resolved_alerts.append(alert_key)
                        logger.info(f" Alerta auto-resolvido: {alert.message}")
                
                # Remover alertas resolvidos
                for alert_key in resolved_alerts:
                    del self.active_alerts[alert_key]
                    
            except Exception as e:
                logger.error(f"Erro no processamento de alertas: {e}")
            
            await asyncio.sleep(60)  # Processar a cada minuto
    
    async def _cleanup_old_data(self):
        """Limpar dados antigos"""
        while self.is_running:
            try:
                retention_days = self.config.get("retention_days", 30)
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # Limpar histórico de métricas
                for metric_name in self.metric_history:
                    self.metric_history[metric_name] = [
                        result for result in self.metric_history[metric_name]
                        if result.timestamp > cutoff_date
                    ]
                
                # Limpar arquivos de alerta antigos
                alerts_dir = Path("alerts")
                if alerts_dir.exists():
                    for alert_file in alerts_dir.glob("*.json"):
                        if alert_file.stat().st_mtime < cutoff_date.timestamp():
                            alert_file.unlink()
                            logger.info(f" Arquivo de alerta removido: {alert_file}")
                
            except Exception as e:
                logger.error(f"Erro na limpeza de dados: {e}")
            
            await asyncio.sleep(3600)  # Limpar a cada hora
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Obter status atual do monitoramento"""
        return {
            "is_running": self.is_running,
            "active_alerts_count": len(self.active_alerts),
            "active_alerts": [asdict(alert) for alert in self.active_alerts.values()],
            "metrics_monitored": list(self.metric_history.keys()),
            "last_check": datetime.now().isoformat(),
            "config": self.config
        }
    
    async def generate_monitoring_report(self) -> str:
        """Gerar relatório de monitoramento"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_status": await self.get_monitoring_status(),
                "metric_summary": {},
                "alert_summary": {
                    "total_alerts": len(self.active_alerts),
                    "by_level": {}
                }
            }
            
            # Resumo de métricas
            for metric_name, history in self.metric_history.items():
                if history:
                    latest = history[-1]
                    report_data["metric_summary"][metric_name] = {
                        "latest_value": latest.value,
                        "status": latest.status.value,
                        "last_update": latest.timestamp.isoformat(),
                        "history_count": len(history)
                    }
            
            # Resumo de alertas por nível
            for alert in self.active_alerts.values():
                level = alert.level.value
                if level not in report_data["alert_summary"]["by_level"]:
                    report_data["alert_summary"]["by_level"][level] = 0
                report_data["alert_summary"]["by_level"][level] += 1
            
            # Salvar relatório
            report_file = f"reports/monitoring/monitoring_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"
            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f" Relatório de monitoramento gerado: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return ""

# Função principal para execução standalone
async def main():
    """Função principal"""
    monitoring = ProactiveMonitoringSystem()
    
    try:
        await monitoring.start_monitoring()
    except KeyboardInterrupt:
        logger.info(" Interrompido pelo usuário")
        await monitoring.stop_monitoring()
    except Exception as e:
        logger.error(f"Erro no monitoramento: {e}")
        await monitoring.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
