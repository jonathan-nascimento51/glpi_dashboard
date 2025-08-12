# -*- coding: utf-8 -*-
"""Exception handlers com payloads úteis para debugging e UX"""

import traceback
from typing import Dict, Any, Optional, Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from .logger import get_logger, request_id_var

logger = get_logger(__name__)

class APIError(Exception):
    """Exceção base para erros de API"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"API_{status_code}"
        self.details = details or {}
        self.user_message = user_message or self._get_user_friendly_message()
        super().__init__(self.message)
        
    def _get_user_friendly_message(self) -> str:
        """Retorna mensagem amigável baseada no status code"""
        messages = {
            400: "Dados inválidos fornecidos",
            401: "Acesso não autorizado",
            403: "Acesso negado",
            404: "Recurso não encontrado",
            409: "Conflito com estado atual",
            422: "Dados não processáveis",
            429: "Muitas requisições. Tente novamente em alguns minutos",
            500: "Erro interno do servidor",
            502: "Serviço temporariamente indisponível",
            503: "Serviço em manutenção"
        }
        return messages.get(self.status_code, "Erro inesperado")

class BusinessError(APIError):
    """Erro de regra de negócio"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="BUSINESS_RULE_VIOLATION",
            details=details,
            user_message=message
        )

class ExternalServiceError(APIError):
    """Erro de serviço externo (GLPI, etc.)"""
    
    def __init__(
        self,
        service: str,
        message: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{service}: {message}",
            status_code=status_code,
            error_code=f"{service.upper()}_ERROR",
            details={"service": service, **(details or {})},
            user_message="Serviço temporariamente indisponível"
        )

class ValidationError(APIError):
    """Erro de validação de dados"""
    
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(
            message=f"Validation error on field '{field}': {message}",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": value, "message": message},
            user_message=f"Campo '{field}': {message}"
        )

def create_error_response(
    request: Request,
    error: Union[Exception, APIError],
    status_code: int = 500,
    include_traceback: bool = False
) -> JSONResponse:
    """Cria resposta de erro padronizada"""
    
    request_id = request_id_var.get() or "unknown"
    
    # Determinar tipo de erro e extrair informações
    if isinstance(error, APIError):
        error_data = {
            "error": {
                "code": error.error_code,
                "message": error.user_message,
                "details": error.details,
                "request_id": request_id
            }
        }
        status_code = error.status_code
        
        # Log do erro
        logger.error(
            f"API Error: {error.message}",
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details,
            path=request.url.path,
            method=request.method
        )
        
    else:
        # Erro genérico
        error_data = {
            "error": {
                "code": f"HTTP_{status_code}",
                "message": "Erro interno do servidor",
                "details": {"type": type(error).__name__},
                "request_id": request_id
            }
        }
        
        # Log do erro com stack trace
        logger.error(
            f"Unhandled error: {str(error)}",
            error_type=type(error).__name__,
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
    
    # Adicionar traceback em desenvolvimento
    if include_traceback and not isinstance(error, APIError):
        error_data["error"]["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handler para APIError"""
    return create_error_response(request, exc)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler para HTTPException do FastAPI"""
    api_error = APIError(
        message=exc.detail,
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}"
    )
    return create_error_response(request, api_error)

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler para HTTPException do Starlette"""
    api_error = APIError(
        message=exc.detail,
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}"
    )
    return create_error_response(request, api_error)

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler para erros de validação do Pydantic"""
    
    # Extrair detalhes dos erros de validação
    validation_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    api_error = APIError(
        message="Validation failed",
        status_code=422,
        error_code="VALIDATION_ERROR",
        details={"validation_errors": validation_errors},
        user_message="Dados fornecidos são inválidos"
    )
    
    return create_error_response(request, api_error)

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler geral para exceções não tratadas"""
    return create_error_response(
        request, 
        exc, 
        status_code=500,
        include_traceback=True  # Em produção, definir como False
    )

def setup_exception_handlers(app):
    """Configura todos os exception handlers na aplicação FastAPI"""
    
    # Handlers específicos
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Handler geral (deve ser o último)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configurados")
