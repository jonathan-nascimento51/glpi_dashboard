"""Testes para o sistema de observabilidade"""
import json
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask

from utils.alerting_system import AlertManager, AlertRule, AlertSeverity, MetricCollector
from utils.observability_middleware import ObservabilityMiddleware, setup_observability
from utils.prometheus_metrics import PrometheusMetrics
from utils.structured_logging import JSONFormatter, StructuredLogger, api_logger, glpi_logger


class TestPrometheusMetrics:
    """Testes para métricas Prometheus"""

    def setup_method(self):
        """Setup para cada teste"""
        self.metrics = PrometheusMetrics()

    def test_metrics_initialization(self):
        """Testa a inicialização das métricas"""
        assert self.metrics is not None
        assert hasattr(self.metrics, "enabled")

    def test_record_api_request(self):
        """Testa o registro de requisição de API"""
        self.metrics.record_api_request(endpoint="/test", method="GET", status_code=200, duration=0.1)
        # Verifica se a métrica foi registrada (mock necessário para teste real)

    def test_record_glpi_request(self):
        """Testa o registro de requisição GLPI"""
        self.metrics.record_glpi_request(endpoint="/tickets", status_code=200, duration=0.2)

    def test_update_tickets_metrics(self):
        """Testa a atualização de métricas de tickets"""
        tickets_data = {
            "n1": {"novo": 5, "pendente": 3},
            "n2": {"novo": 2, "resolvido": 8},
        }
        self.metrics.update_tickets_metrics(tickets_data)

    def test_record_error(self):
        """Testa o registro de erro"""
        self.metrics.record_error(error_type="connection_error", component="glpi_api")


class TestStructuredLogging:
    """Testes para logging estruturado"""

    def setup_method(self):
        """Setup para cada teste"""
        self.logger = StructuredLogger("test")

    def test_json_formatter(self):
        """Testa o formatador JSON"""
        formatter = JSONFormatter()

        # Criar LogRecord real em vez de Mock
        import logging

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "test_123"
        record.operation_context = {"operation": "test"}

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert log_data["logger"] == "test"
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["correlation_id"] == "test_123"

    def test_generate_correlation_id(self):
        """Testa a geração de correlation ID"""
        correlation_id = self.logger.generate_correlation_id()
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0

    def test_set_correlation_id(self):
        """Testa a definição de correlation ID"""
        test_id = "test_correlation_123"
        self.logger.set_correlation_id(test_id)
        assert self.logger.get_correlation_id() == test_id

    def test_set_operation_context(self):
        """Testa a definição de contexto de operação"""
        self.logger.set_operation_context("test_operation", user_id="123")
        # Verificar se o contexto foi definido (não há getter público)

    def test_log_operation_start(self):
        """Testa o log de início de operação"""
        with patch.object(self.logger.logger, "info") as mock_info:
            self.logger.log_operation_start(operation="test_op", param="value")
            mock_info.assert_called_once()

    def test_log_operation_step(self):
        """Testa o log de etapa de operação"""
        with patch.object(self.logger.logger, "info") as mock_info:
            self.logger.log_operation_step(step="validation", status="ok")
            mock_info.assert_called_once()

    def test_log_operation_end(self):
        """Testa o log de fim de operação"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.log_operation_end(operation="test_op", success=True, result_data="test_result")
            mock_log.assert_called_once()

    def test_log_error(self):
        """Testa o log de erro"""
        with patch.object(self.logger.logger, "error") as mock_error:
            try:
                raise ValueError("Test error")
            except Exception as e:
                self.logger.log_error_with_context("test_error", "Test error occurred", exception=e, operation="test")
            mock_error.assert_called_once()

    def test_log_warning_with_context(self):
        """Testa o log de warning com contexto"""
        with patch.object(self.logger.logger, "warning") as mock_warning:
            self.logger.log_warning_with_context("test_warning", "Test warning message", component="test")
            mock_warning.assert_called_once()


class TestAlertingSystem:
    """Testes para sistema de alertas"""

    def setup_method(self):
        """Setup para cada teste"""
        self.alert_manager = AlertManager()
        self.metric_collector = MetricCollector()

    def test_alert_rule_creation(self):
        """Testa a criação de regra de alerta"""
        rule = AlertRule(
            name="test_rule",
            description="Test alert",
            metric_name="test_metric",
            threshold=100,
            operator=">",
            severity=AlertSeverity.MEDIUM,
        )

        assert rule.name == "test_rule"
        assert rule.threshold == 100
        assert rule.severity == AlertSeverity.MEDIUM

    def test_metric_collector_record(self):
        """Testa o registro de métrica"""
        self.metric_collector.record_metric("test_metric", 50, {"label": "value"})

        metric = self.metric_collector.get_latest_metric("test_metric")
        assert metric is not None
        assert metric["value"] == 50

    def test_alert_evaluation(self):
        """Testa a avaliação de alertas"""
        # Adiciona regra com duration=0 para disparo imediato
        rule = AlertRule(
            name="high_value",
            description="Value too high",
            metric_name="test_metric",
            threshold=100,
            operator=">",
            severity=AlertSeverity.MEDIUM,
            duration=0,  # Disparo imediato
        )
        self.alert_manager.add_rule(rule)

        # Registra métrica que deve disparar alerta
        self.alert_manager.record_metric("test_metric", 150)

        # Verifica se alerta foi criado
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) > 0
        assert active_alerts[0].rule_name == "high_value"

    def test_alert_resolution(self):
        """Testa a resolução de alertas"""
        # Cria alerta com duration=0 para disparo imediato
        rule = AlertRule(
            name="high_value",
            description="Value too high",
            metric_name="test_metric",
            threshold=100,
            operator=">",
            severity=AlertSeverity.MEDIUM,
            duration=0,  # Disparo imediato
        )
        self.alert_manager.add_rule(rule)
        self.alert_manager.record_metric("test_metric", 150)

        # Verifica alerta ativo
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 1

        # Registra métrica que resolve o alerta
        self.alert_manager.record_metric("test_metric", 50)

        # Verifica se alerta foi resolvido
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 0


class TestObservabilityMiddleware:
    """Testes para middleware de observabilidade"""

    def setup_method(self):
        """Setup para cada teste"""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True

        # Mock das dependências
        with patch("backend.utils.observability_middleware.prometheus_metrics"), patch(
            "backend.utils.observability_middleware.api_logger"
        ), patch("backend.utils.observability_middleware.alert_manager"):
            self.middleware = ObservabilityMiddleware(self.app)

    def test_middleware_initialization(self):
        """Testa a inicialização do middleware"""
        assert self.middleware.app == self.app

    def test_health_endpoint(self):
        """Testa o endpoint de health check"""
        with self.app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data

    def test_metrics_endpoint(self):
        """Testa o endpoint de métricas"""
        with patch("backend.utils.observability_middleware.prometheus_metrics") as mock_prometheus:
            mock_prometheus.get_metrics_text.return_value = "# HELP test_metric Test metric\n"

            with self.app.test_client() as client:
                response = client.get("/metrics")
                assert response.status_code == 200
                assert response.content_type == "text/plain; charset=utf-8"

    def test_alerts_endpoint(self):
        """Testa o endpoint de alertas"""
        with self.app.test_client() as client:
            response = client.get("/alerts")
            assert response.status_code == 200

            data = json.loads(response.data)
            assert "active_alerts" in data
            assert "alert_history" in data


class TestIntegration:
    """Testes de integração do sistema de observabilidade"""

    def test_full_observability_setup(self):
        """Testa a configuração completa de observabilidade"""
        app = Flask(__name__)
        app.config["TESTING"] = True

        # Mock das dependências externas
        with patch("backend.utils.observability_middleware.prometheus_metrics") as mock_prometheus, patch(
            "backend.utils.observability_middleware.api_logger"
        ), patch("backend.utils.observability_middleware.alert_manager") as mock_alert_manager:
            # Configurar mocks
            mock_prometheus.enabled = True
            mock_prometheus.get_metrics_text.return_value = "# HELP test_metric Test metric\n"
            mock_alert_manager.rules = []
            mock_alert_manager.get_active_alerts.return_value = []
            mock_alert_manager.get_alert_history.return_value = []
            mock_alert_manager.get_alert_summary.return_value = {
                "total": 0,
                "active": 0,
            }

            setup_observability(app)

            # Verifica se os endpoints foram registrados
            with app.test_client() as client:
                # Health check
                response = client.get("/health")
                assert response.status_code == 200

                # Métricas
                response = client.get("/metrics")
                assert response.status_code == 200

                # Alertas
                response = client.get("/alerts")
                assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])
