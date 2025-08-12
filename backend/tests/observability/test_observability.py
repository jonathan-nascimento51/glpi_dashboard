# -*- coding: utf-8 -*-
"""Tests for observability module."""

import pytest
import json
import logging
from unittest.mock import Mock, patch
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.datastructures import URL
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from observability.exceptions import (
    APIError,
    BusinessError,
    ExternalServiceError,
    ValidationError,
    http_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    setup_exception_handlers,
)
from observability.middleware import MetricsMiddleware
from observability.logger import (
    JSONFormatter,
    StructuredLogger,
    setup_logging,
    get_logger,
    set_request_context,
    generate_request_id,
    clear_request_context,
    request_id_var,
    user_id_var,
)


class TestMetricsMiddleware:
    """Test cases for MetricsMiddleware."""

    def test_middleware_initialization(self):
        """Test middleware initialization."""
        middleware = MetricsMiddleware(Mock())
        assert middleware.app is not None
        assert middleware.exclude_paths == [
            "/metrics",
            "/health",
            "/docs",
            "/openapi.json",
        ]

    def test_middleware_initialization_with_exclude_paths(self):
        """Test middleware initialization with exclude paths."""
        exclude_paths = ["/custom", "/test"]
        middleware = MetricsMiddleware(Mock(), exclude_paths=exclude_paths)
        assert middleware.exclude_paths == exclude_paths

    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        """Test metrics collection for successful requests."""
        app = Mock()
        middleware = MetricsMiddleware(app)

        # Create a proper mock request
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock(spec=URL)
        request.url.path = "/test"
        request.headers = {"content-length": "0"}

        # Create response
        response = JSONResponse({"status": "ok"})
        response.status_code = 200
        response.body = b'{"status": "ok"}'

        async def call_next(req):
            return response

        with patch("observability.middleware.REQUEST_COUNT") as mock_counter, patch(
            "observability.middleware.REQUEST_DURATION"
        ) as mock_duration, patch(
            "observability.middleware.REQUEST_SIZE"
        ) as mock_req_size, patch(
            "observability.middleware.RESPONSE_SIZE"
        ) as mock_resp_size, patch("observability.middleware.logger"):
            result = await middleware.dispatch(request, call_next)

            # Verify REQUEST_COUNT was called
            mock_counter.labels.assert_called_once_with(
                method="GET", endpoint="/test", status_code="200"
            )
            mock_counter.labels().inc.assert_called_once()

            # Verify other metrics were called
            mock_duration.labels.assert_called_once()
            mock_req_size.labels.assert_called_once()
            mock_resp_size.labels.assert_called_once()

            assert result == response

    @pytest.mark.asyncio
    async def test_error_metrics_collection(self):
        """Test metrics collection for error responses."""
        app = Mock()
        middleware = MetricsMiddleware(app)

        # Create a proper mock request
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = Mock(spec=URL)
        request.url.path = "/error"
        request.headers = {"content-length": "10"}

        async def call_next(req):
            raise Exception("Test error")

        with patch("observability.middleware.REQUEST_COUNT") as mock_counter, patch(
            "observability.middleware.REQUEST_DURATION"
        ) as mock_duration, patch("observability.middleware.logger"):
            with pytest.raises(Exception, match="Test error"):
                await middleware.dispatch(request, call_next)

            # Verify that REQUEST_COUNT was called for the error case
            mock_counter.labels.assert_called_with(
                method="POST", endpoint="/error", status_code="500"
            )
            mock_counter.labels().inc.assert_called()

            # Verify REQUEST_DURATION was also called
            mock_duration.labels.assert_called()

    @pytest.mark.asyncio
    async def test_excluded_path_no_metrics(self):
        """Test that excluded paths don't generate metrics."""
        app = Mock()
        middleware = MetricsMiddleware(app, exclude_paths=["/health"])

        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock(spec=URL)
        request.url.path = "/health"
        request.headers = {}

        response = JSONResponse({"status": "healthy"})
        response.status_code = 200
        response.body = b'{"status": "healthy"}'

        async def call_next(req):
            return response

        with patch("observability.middleware.REQUEST_COUNT") as mock_counter:
            result = await middleware.dispatch(request, call_next)

            # Verify no metrics were recorded
            mock_counter.labels.assert_not_called()
            assert result == response


class TestJSONFormatter:
    """Test cases for JSONFormatter."""

    def test_format_basic_log(self):
        """Test basic log formatting."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "path"
        assert log_data["line"] == 42
        assert "timestamp" in log_data

    def test_format_with_request_context(self):
        """Test formatting with request context."""
        formatter = JSONFormatter()

        # Set request context
        set_request_context("test-request-id", "test-user-id")

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["request_id"] == "test-request-id"
        assert log_data["user_id"] == "test-user-id"

        # Clean up
        clear_request_context()

    def test_format_with_exception(self):
        """Test formatting with exception information."""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/test/path.py",
            lineno=42,
            msg="Test error",
            args=(),
            exc_info=exc_info,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "exception" in log_data
        assert "ValueError" in log_data["exception"]

    def test_format_with_extra_fields(self):
        """Test formatting with extra fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.custom_field = "custom_value"
        record.another_field = 123

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "extra" in log_data
        assert log_data["extra"]["custom_field"] == "custom_value"
        assert log_data["extra"]["another_field"] == 123


class TestStructuredLogger:
    """Test cases for StructuredLogger."""

    def setup_method(self):
        """Setup for each test."""
        self.logger = StructuredLogger("test_logger")

    @patch("observability.logger.logging.getLogger")
    def test_debug_log(self, mock_get_logger):
        """Test debug logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.debug("Debug message", extra_field="value")

        mock_logger.log.assert_called_once_with(
            logging.DEBUG, "Debug message", extra={"extra_field": "value"}
        )

    @patch("observability.logger.logging.getLogger")
    def test_info_log(self, mock_get_logger):
        """Test info logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.info("Info message", extra_field="value")

        mock_logger.log.assert_called_once_with(
            logging.INFO, "Info message", extra={"extra_field": "value"}
        )

    @patch("observability.logger.logging.getLogger")
    def test_warning_log(self, mock_get_logger):
        """Test warning logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.warning("Warning message")

        mock_logger.log.assert_called_once_with(
            logging.WARNING, "Warning message", extra={}
        )

    @patch("observability.logger.logging.getLogger")
    def test_error_log(self, mock_get_logger):
        """Test error logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.error("Error message")

        mock_logger.log.assert_called_once_with(
            logging.ERROR, "Error message", extra={}
        )

    @patch("observability.logger.logging.getLogger")
    def test_critical_log(self, mock_get_logger):
        """Test critical logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.critical("Critical message")

        mock_logger.log.assert_called_once_with(
            logging.CRITICAL, "Critical message", extra={}
        )

    @patch("observability.logger.logging.getLogger")
    def test_log_with_duration_performance(self, mock_get_logger):
        """Test logging with performance metrics."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.info("Performance test", duration=123.45)

        expected_extra = {"performance": {"duration_ms": 123.45}}
        mock_logger.log.assert_called_once_with(
            logging.INFO, "Performance test", extra=expected_extra
        )

    @patch("observability.logger.logging.getLogger")
    def test_api_request_log(self, mock_get_logger):
        """Test API request logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/api/test"
        mock_request.query_params = {"param1": "value1"}
        mock_request.headers = {"user-agent": "test-agent"}

        logger = StructuredLogger("test")
        logger.api_request(mock_request, custom_field="value")

        expected_extra = {
            "method": "GET",
            "path": "/api/test",
            "query_params": {"param1": "value1"},
            "user_agent": "test-agent",
            "custom_field": "value",
        }
        mock_logger.log.assert_called_once_with(
            logging.INFO, "GET /api/test", extra=expected_extra
        )

    @patch("observability.logger.logging.getLogger")
    def test_api_response_log(self, mock_get_logger):
        """Test API response logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.url = Mock()
        mock_request.url.path = "/api/create"

        logger = StructuredLogger("test")
        logger.api_response(mock_request, 201, 45.67, custom_field="value")

        expected_extra = {
            "method": "POST",
            "path": "/api/create",
            "status_code": 201,
            "duration": 45.67,
            "custom_field": "value",
            "performance": {"duration_ms": 45.67},
        }
        mock_logger.log.assert_called_once_with(
            logging.INFO, "POST /api/create - 201", extra=expected_extra
        )

    @patch("observability.logger.logging.getLogger")
    def test_business_event_log(self, mock_get_logger):
        """Test business event logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.business_event("user_created", user_id="123", email="test@example.com")

        expected_extra = {
            "event_type": "user_created",
            "category": "business",
            "user_id": "123",
            "email": "test@example.com",
        }
        mock_logger.log.assert_called_once_with(
            logging.INFO, "Business event: user_created", extra=expected_extra
        )

    @patch("observability.logger.logging.getLogger")
    def test_security_event_log(self, mock_get_logger):
        """Test security event logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger("test")
        logger.security_event("failed_login", ip="192.168.1.1", user="admin")

        expected_extra = {
            "event_type": "failed_login",
            "category": "security",
            "ip": "192.168.1.1",
            "user": "admin",
        }
        mock_logger.log.assert_called_once_with(
            logging.WARNING, "Security event: failed_login", extra=expected_extra
        )


class TestLoggingFunctions:
    """Test cases for logging configuration functions."""

    @patch("observability.logger.logging")
    def test_setup_logging_with_json(self, mock_logging):
        """Test logging setup with JSON formatting."""
        mock_root_logger = Mock()
        mock_logging.getLogger.return_value = mock_root_logger
        mock_logging.INFO = logging.INFO
        mock_logging.StreamHandler.return_value = Mock()

        setup_logging("INFO", True)

        mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_root_logger.handlers.clear.assert_called_once()
        mock_root_logger.addHandler.assert_called_once()

    @patch("observability.logger.logging")
    def test_setup_logging_without_json(self, mock_logging):
        """Test logging setup without JSON formatting."""
        mock_root_logger = Mock()
        mock_logging.getLogger.return_value = mock_root_logger
        mock_logging.DEBUG = logging.DEBUG
        mock_handler = Mock()
        mock_logging.StreamHandler.return_value = mock_handler
        mock_logging.Formatter.return_value = Mock()

        setup_logging("DEBUG", False)

        mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)
        mock_handler.setFormatter.assert_called_once()

    def test_get_logger(self):
        """Test getting structured logger."""
        logger = get_logger("test_logger")
        assert isinstance(logger, StructuredLogger)

    def test_set_and_clear_request_context(self):
        """Test setting and clearing request context."""
        # Test setting context
        set_request_context("test-request-id", "test-user-id")
        assert request_id_var.get() == "test-request-id"
        assert user_id_var.get() == "test-user-id"

        # Test clearing context
        clear_request_context()
        assert request_id_var.get() == ""
        assert user_id_var.get() == ""

    def test_set_request_context_without_user_id(self):
        """Test setting context without user_id."""
        set_request_context("test-request-id")
        assert request_id_var.get() == "test-request-id"
        # user_id should remain unchanged

    def test_generate_request_id(self):
        """Test request ID generation."""
        request_id = generate_request_id()
        assert isinstance(request_id, str)
        assert len(request_id) > 0

        # Test uniqueness
        request_id2 = generate_request_id()
        assert request_id != request_id2


class TestExceptionHandlers:
    """Testes para os handlers de exceção"""

    @pytest.mark.asyncio
    async def test_http_exception_handler(self):
        """Testa o handler de HTTPException"""
        request = Mock(spec=Request)
        exc = HTTPException(status_code=404, detail="Not found")

        response = await http_exception_handler(request, exc)

        assert response.status_code == 404
        response_data = json.loads(response.body)
        assert response_data["error"]["message"] == "Not found"
        assert response_data["error"]["error_code"] == "HTTP_ERROR"

    @pytest.mark.asyncio
    async def test_starlette_http_exception_handler(self):
        """Testa o handler de StarletteHTTPException"""
        request = Mock(spec=Request)
        exc = StarletteHTTPException(status_code=500, detail="Internal error")

        response = await starlette_http_exception_handler(request, exc)

        assert response.status_code == 500
        response_data = json.loads(response.body)
        assert response_data["error"]["message"] == "Internal error"
        assert response_data["error"]["error_code"] == "HTTP_ERROR"

    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """Testa o handler de ValidationError do Pydantic"""
        from pydantic import ValidationError as PydanticValidationError

        request = Mock(spec=Request)

        # Create a mock validation error
        exc = Mock(spec=PydanticValidationError)
        exc.errors.return_value = [
            {
                "loc": ("field1",),
                "msg": "field required",
                "type": "value_error.missing",
            },
            {"loc": ("field2",), "msg": "invalid format", "type": "value_error.format"},
        ]

        response = await validation_exception_handler(request, exc)

        assert response.status_code == 422
        response_data = json.loads(response.body)
        assert response_data["error"]["message"] == "Validation failed"
        assert response_data["error"]["error_code"] == "VALIDATION_ERROR"
        assert "validation_errors" in response_data["error"]["details"]

    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Testa o handler de exceção geral"""
        request = Mock(spec=Request)
        exc = Exception("Unexpected error")

        with patch("observability.exceptions.logger") as mock_logger:
            response = await general_exception_handler(request, exc)

        assert response.status_code == 500
        response_data = json.loads(response.body)
        assert response_data["error"]["message"] == "Internal server error"
        assert response_data["error"]["error_code"] == "INTERNAL_ERROR"
        mock_logger.error.assert_called_once()

    @patch("observability.exceptions.FastAPI")
    def test_setup_exception_handlers(self, mock_fastapi):
        """Testa a configuração dos handlers de exceção"""
        mock_app = Mock()
        mock_fastapi.return_value = mock_app

        setup_exception_handlers(mock_app)

        # Verifica se os handlers foram adicionados
        assert mock_app.add_exception_handler.call_count == 4

        # Verifica os tipos de exceção registrados
        call_args = [
            call[0][0] for call in mock_app.add_exception_handler.call_args_list
        ]
        assert HTTPException in call_args
        assert StarletteHTTPException in call_args
        assert Exception in call_args


class TestExceptionClasses:
    """Test cases for custom exception classes."""

    def test_api_error_creation(self):
        """Test APIError creation and attributes."""
        error = APIError(
            message="Test API error", status_code=400, error_code="TEST_ERROR"
        )
        assert error.message == "Test API error"
        assert error.status_code == 400
        assert error.error_code == "TEST_ERROR"
        assert str(error) == "Test API error"

    def test_business_error_creation(self):
        """Test BusinessError creation and attributes."""
        error = BusinessError(
            message="Business rule violation", details={"rule": "TEST_RULE"}
        )
        assert error.message == "Business rule violation"
        assert error.details["rule"] == "TEST_RULE"
        assert error.status_code == 422
        assert error.user_message == "Business rule violation"

    def test_external_service_error_creation(self):
        """Test ExternalServiceError creation and attributes."""
        error = ExternalServiceError(
            service="GLPI", message="Connection timeout", status_code=503
        )
        assert error.details["service"] == "GLPI"
        assert "Connection timeout" in error.message
        assert error.status_code == 503
        assert "temporariamente" in error.user_message

    def test_validation_error_creation(self):
        """Test ValidationError creation and attributes."""
        error = ValidationError(field="email", message="Invalid email format")
        assert error.details["field"] == "email"
        assert "Invalid email format" in error.message
        assert error.status_code == 400
        assert "email" in error.user_message

    def test_api_error_with_details(self):
        """Test APIError with additional details."""
        details = {"field": "username", "constraint": "unique"}
        error = APIError(
            message="Validation failed",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )
        assert error.details["field"] == "username"
        assert error.details["constraint"] == "unique"
        assert error.error_code == "VALIDATION_ERROR"

    def test_business_error_inheritance(self):
        """Test BusinessError inherits from APIError."""
        error = BusinessError(message="Test", details={"rule": "TEST"})
        assert isinstance(error, APIError)
        assert "rule" in error.details

    def test_external_service_error_inheritance(self):
        """Test ExternalServiceError inherits from APIError."""
        error = ExternalServiceError(service="TEST", message="Test")
        assert isinstance(error, APIError)
        assert "service" in error.details

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from APIError."""
        error = ValidationError(field="test", message="Test")
        assert isinstance(error, APIError)
        assert "field" in error.details
