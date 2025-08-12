# -*- coding: utf-8 -*-
"""Sistema de logging JSON estruturado com request_id e contexto"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from fastapi import Request

# Context variables para request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class JSONFormatter(logging.Formatter):
    """Formatter para logs em formato JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record em JSON estruturado"""
        
        # Dados base do log
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Adicionar request_id se disponível
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id
            
        # Adicionar user_id se disponível
        user_id = user_id_var.get()
        if user_id:
            log_data['user_id'] = user_id
            
        # Adicionar exception info se presente
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        # Adicionar campos extras do record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }:
                extra_fields[key] = value
                
        if extra_fields:
            log_data['extra'] = extra_fields
            
        return json.dumps(log_data, ensure_ascii=False, default=str)

class StructuredLogger:
    """Logger estruturado com contexto de request"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log com contexto adicional"""
        extra = kwargs.copy()
        
        # Adicionar métricas de performance se disponível
        if 'duration' in extra:
            extra['performance'] = {'duration_ms': extra.pop('duration')}
            
        self.logger.log(level, message, extra=extra)
        
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log de informação"""
        self._log_with_context(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log de warning"""
        self._log_with_context(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        """Log de erro"""
        self._log_with_context(logging.ERROR, message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        """Log crítico"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
        
    def api_request(self, request: Request, **kwargs):
        """Log específico para requests de API"""
        self.info(
            f"{request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            user_agent=request.headers.get('user-agent'),
            **kwargs
        )
        
    def api_response(self, request: Request, status_code: int, duration_ms: float, **kwargs):
        """Log específico para responses de API"""
        self.info(
            f"{request.method} {request.url.path} - {status_code}",
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration=duration_ms,
            **kwargs
        )
        
    def business_event(self, event_type: str, **kwargs):
        """Log para eventos de negócio"""
        self.info(
            f"Business event: {event_type}",
            event_type=event_type,
            category="business",
            **kwargs
        )
        
    def security_event(self, event_type: str, **kwargs):
        """Log para eventos de segurança"""
        self.warning(
            f"Security event: {event_type}",
            event_type=event_type,
            category="security",
            **kwargs
        )

def setup_logging(level: str = "INFO", enable_json: bool = True) -> None:
    """Configura o sistema de logging"""
    
    # Converter string level para logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar handler
    handler = logging.StreamHandler()
    
    if enable_json:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Configurar loggers específicos
    logging.getLogger("uvicorn.access").disabled = True  # Evitar logs duplicados
    
def get_logger(name: str) -> StructuredLogger:
    """Obtém um logger estruturado"""
    return StructuredLogger(name)

def set_request_context(request_id: str, user_id: Optional[str] = None) -> None:
    """Define o contexto da request atual"""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
        
def generate_request_id() -> str:
    """Gera um ID único para a request"""
    return str(uuid.uuid4())

def clear_request_context() -> None:
    """Limpa o contexto da request"""
    request_id_var.set('')
    user_id_var.set('')
