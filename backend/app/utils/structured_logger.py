# -*- coding: utf-8 -*-
"""
M�dulo de logging estruturado para o GLPI Dashboard.
Implementa logging em formato JSON com timestamp, n�vel, nome do logger e mensagem.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback


class JSONFormatter(logging.Formatter):
    """
    Formatador personalizado para logs em formato JSON.
    """
    
    def __init__(self, include_extra_fields: bool = True):
        super().__init__()
        self.include_extra_fields = include_extra_fields
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log em JSON.
        
        Args:
            record: Registro de log do Python logging
            
        Returns:
            String JSON formatada
        """
        # Campos b�sicos obrigat�rios
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage()
        }
        
        # Adicionar informa��es de contexto se dispon�veis
        if hasattr(record, 'module'):
            log_entry["module"] = record.module
            
        if hasattr(record, 'funcName'):
            log_entry["function"] = record.funcName
            
        if hasattr(record, 'lineno'):
            log_entry["line_number"] = record.lineno
            
        # Adicionar informa��es de exce��o se houver
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # Adicionar campos extras personalizados
        if self.include_extra_fields:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated', 
                              'thread', 'threadName', 'processName', 'process',
                              'exc_info', 'exc_text', 'stack_info', 'getMessage']:
                    try:
                        # Tentar serializar o valor para JSON
                        json.dumps(value)
                        extra_fields[key] = value
                    except (TypeError, ValueError):
                        # Se n�o for serializ�vel, converter para string
                        extra_fields[key] = str(value)
                        
            if extra_fields:
                log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class StructuredLogger:
    """
    Logger estruturado para o GLPI Dashboard.
    Fornece m�todos convenientes para logging com contexto adicional.
    """
    
    def __init__(self, name: str, level: str = "INFO"):
        """
        Inicializa o logger estruturado.
        
        Args:
            name: Nome do logger
            level: N�vel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Evitar duplica��o de handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
            
        # Evitar propaga��o para o logger raiz
        self.logger.propagate = False
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """
        Registra uma mensagem com contexto adicional.
        
        Args:
            level: N�vel do log
            message: Mensagem do log
            **kwargs: Campos adicionais para o contexto
        """
        extra = kwargs.copy()
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Registra mensagem de debug."""
        self._log_with_context("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Registra mensagem informativa."""
        self._log_with_context("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Registra mensagem de aviso."""
        self._log_with_context("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Registra mensagem de erro."""
        self._log_with_context("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Registra mensagem cr�tica."""
        self._log_with_context("CRITICAL", message, **kwargs)


def log_api_call(logger: StructuredLogger):
    """
    Decorador para logar chamadas de API com par�metros e tempo de execu��o.
    
    Args:
        logger: Inst�ncia do StructuredLogger
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            
            # Preparar par�metros para log (remover dados sens�veis)
            safe_args = []
            for arg in args[1:]:  # Pular self
                if isinstance(arg, str) and len(arg) > 100:
                    safe_args.append(f"{arg[:100]}...")
                else:
                    safe_args.append(arg)
            
            safe_kwargs = {}
            for key, value in kwargs.items():
                if key.lower() in ['password', 'token', 'secret', 'key']:
                    safe_kwargs[key] = "***REDACTED***"
                elif isinstance(value, str) and len(value) > 100:
                    safe_kwargs[key] = f"{value[:100]}..."
                else:
                    safe_kwargs[key] = value
            
            logger.info(
                f"Iniciando chamada de API: {function_name}",
                api_function=function_name,
                parameters={
                    "args": safe_args,
                    "kwargs": safe_kwargs
                },
                event_type="api_call_start"
            )
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Chamada de API conclu�da: {function_name}",
                    api_function=function_name,
                    execution_time_seconds=round(execution_time, 4),
                    success=True,
                    event_type="api_call_success"
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Erro na chamada de API: {function_name}",
                    api_function=function_name,
                    execution_time_seconds=round(execution_time, 4),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    success=False,
                    event_type="api_call_error",
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator


def log_performance(logger: StructuredLogger, threshold_seconds: float = 1.0):
    """
    Decorador para logar performance de fun��es.
    
    Args:
        logger: Inst�ncia do StructuredLogger
        threshold_seconds: Limite em segundos para considerar como lento
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    logger.warning(
                        f"Fun��o lenta detectada: {function_name}",
                        function=function_name,
                        execution_time_seconds=round(execution_time, 4),
                        threshold_seconds=threshold_seconds,
                        event_type="slow_function"
                    )
                else:
                    logger.debug(
                        f"Performance da fun��o: {function_name}",
                        function=function_name,
                        execution_time_seconds=round(execution_time, 4),
                        event_type="function_performance"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Erro na fun��o: {function_name}",
                    function=function_name,
                    execution_time_seconds=round(execution_time, 4),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    event_type="function_error",
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator


def log_api_response(logger: StructuredLogger, response_data: Any, 
                    status_code: Optional[int] = None, 
                    response_time: Optional[float] = None):
    """
    Loga resposta de API de forma estruturada.
    
    Args:
        logger: Inst�ncia do StructuredLogger
        response_data: Dados da resposta
        status_code: C�digo de status HTTP
        response_time: Tempo de resposta em segundos
    """
    # Preparar dados da resposta para log (limitar tamanho)
    if isinstance(response_data, (dict, list)):
        response_str = json.dumps(response_data, default=str)
        if len(response_str) > 1000:
            safe_response = f"{response_str[:1000]}..."
        else:
            safe_response = response_data
    else:
        safe_response = str(response_data)[:1000]
    
    log_data = {
        "response_data": safe_response,
        "event_type": "api_response"
    }
    
    if status_code is not None:
        log_data["status_code"] = status_code
        
    if response_time is not None:
        log_data["response_time_seconds"] = round(response_time, 4)
    
    if status_code and status_code >= 400:
        logger.error("Resposta de API com erro", **log_data)
    else:
        logger.info("Resposta de API recebida", **log_data)


def create_glpi_logger(level: str = "INFO") -> StructuredLogger:
    """
    Cria um logger estruturado espec�fico para o servi�o GLPI.
    
    Args:
        level: N�vel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Inst�ncia configurada do StructuredLogger
    """
    return StructuredLogger("glpi_service", level)
