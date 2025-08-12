from typing import Any, Dict, Optional, Callable, Type
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError
import logging
import time
import json
from datetime import datetime

from models.validation import MetricsData, TechnicianRanking, SystemStatus, ApiResponse


class ValidationMiddleware:
    """Middleware para validação de dados da API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_stats = {
            "total_requests": 0,
            "validation_errors": 0,
            "validation_successes": 0,
            "fallback_used": 0,
        }

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Intercepta requisições e aplica validação"""
        start_time = time.time()
        self.validation_stats["total_requests"] += 1

        try:
            response = await call_next(request)

            # Validar resposta se for JSON
            if self._should_validate_response(request, response):
                validated_response = await self._validate_response(request, response)
                if validated_response:
                    return validated_response

            return response

        except Exception as e:
            self.logger.error(f"Erro no middleware de validação: {str(e)}")
            return await self._create_error_response(
                "Erro interno do servidor", status_code=500
            )
        finally:
            duration = time.time() - start_time
            self.logger.info(
                f"Validação concluída em {duration:.3f}s para {request.url.path}"
            )

    def _should_validate_response(self, request: Request, response: Response) -> bool:
        """Determina se a resposta deve ser validada"""
        # Validar apenas respostas JSON de endpoints específicos
        api_endpoints = ["/api/metrics", "/api/ranking", "/api/status", "/api/tickets"]

        return (
            response.status_code == 200
            and any(request.url.path.startswith(endpoint) for endpoint in api_endpoints)
            and response.headers.get("content-type", "").startswith("application/json")
        )

    async def _validate_response(
        self, request: Request, response: Response
    ) -> Optional[Response]:
        """Valida o conteúdo da resposta"""
        try:
            # Ler o corpo da resposta
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            if not body:
                return None

            # Parse JSON
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.logger.warning("Resposta não é JSON válido")
                return None

            # Validar baseado no endpoint
            validated_data = self._validate_by_endpoint(request.url.path, data)

            if validated_data is not None:
                # Criar nova resposta com dados validados
                return JSONResponse(
                    content=validated_data,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            return None

        except Exception as e:
            self.logger.error(f"Erro na validação da resposta: {str(e)}")
            return None

    def _validate_by_endpoint(self, path: str, data: Any) -> Optional[Dict[str, Any]]:
        """Valida dados baseado no endpoint"""
        try:
            if "/metrics" in path:
                return self._validate_metrics_data(data)
            elif "/ranking" in path:
                return self._validate_ranking_data(data)
            elif "/status" in path:
                return self._validate_status_data(data)
            else:
                return None

        except Exception as e:
            self.logger.error(f"Erro na validação por endpoint {path}: {str(e)}")
            self.validation_stats["validation_errors"] += 1
            return self._get_fallback_data(path)

    def _validate_metrics_data(self, data: Any) -> Dict[str, Any]:
        """Valida dados de métricas"""
        try:
            # Extrair dados de métricas
            metrics_data = data.get("data", data)

            # Validar com Pydantic
            validated = MetricsData(**metrics_data)

            self.validation_stats["validation_successes"] += 1
            self.logger.info("Dados de métricas validados com sucesso")

            return {
                "success": True,
                "message": "Dados validados",
                "data": validated.dict(),
                "timestamp": datetime.now().isoformat(),
            }

        except PydanticValidationError as e:
            self.logger.warning(f"Erro de validação em métricas: {e}")
            self.validation_stats["validation_errors"] += 1
            return self._get_fallback_metrics()

    def _validate_ranking_data(self, data: Any) -> Dict[str, Any]:
        """Valida dados de ranking"""
        try:
            ranking_data = data.get("data", data)

            if isinstance(ranking_data, list):
                validated_items = []
                for item in ranking_data:
                    try:
                        validated = TechnicianRanking(**item)
                        validated_items.append(validated.dict())
                    except PydanticValidationError:
                        # Pular itens inválidos
                        continue

                self.validation_stats["validation_successes"] += 1
                return {
                    "success": True,
                    "message": "Ranking validado",
                    "data": validated_items,
                    "timestamp": datetime.now().isoformat(),
                }

            return self._get_fallback_ranking()

        except Exception as e:
            self.logger.warning(f"Erro de validação em ranking: {e}")
            self.validation_stats["validation_errors"] += 1
            return self._get_fallback_ranking()

    def _validate_status_data(self, data: Any) -> Dict[str, Any]:
        """Valida dados de status do sistema"""
        try:
            status_data = data.get("data", data)
            validated = SystemStatus(**status_data)

            self.validation_stats["validation_successes"] += 1
            return {
                "success": True,
                "message": "Status validado",
                "data": validated.dict(),
                "timestamp": datetime.now().isoformat(),
            }

        except PydanticValidationError as e:
            self.logger.warning(f"Erro de validação em status: {e}")
            self.validation_stats["validation_errors"] += 1
            return self._get_fallback_status()

    def _get_fallback_data(self, path: str) -> Dict[str, Any]:
        """Retorna dados de fallback baseado no endpoint"""
        self.validation_stats["fallback_used"] += 1

        if "/metrics" in path:
            return self._get_fallback_metrics()
        elif "/ranking" in path:
            return self._get_fallback_ranking()
        elif "/status" in path:
            return self._get_fallback_status()
        else:
            return {
                "success": False,
                "message": "Dados não disponíveis",
                "data": None,
                "timestamp": datetime.now().isoformat(),
            }

    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Dados de fallback para métricas"""
        return {
            "success": True,
            "message": "Dados de fallback - métricas indisponíveis",
            "data": {
                "niveis": {
                    "N1": {
                        "total": 0,
                        "resolvidos": 0,
                        "pendentes": 0,
                        "tempo_medio": 1.0,
                    },
                    "N2": {
                        "total": 0,
                        "resolvidos": 0,
                        "pendentes": 0,
                        "tempo_medio": 1.0,
                    },
                    "N3": {
                        "total": 0,
                        "resolvidos": 0,
                        "pendentes": 0,
                        "tempo_medio": 1.0,
                    },
                },
                "total_tickets": 0,
                "tickets_resolvidos": 0,
                "tickets_pendentes": 0,
                "tempo_medio_resolucao": 1.0,
                "satisfacao_cliente": 0.0,
            },
            "timestamp": datetime.now().isoformat(),
        }

    def _get_fallback_ranking(self) -> Dict[str, Any]:
        """Dados de fallback para ranking"""
        return {
            "success": True,
            "message": "Dados de fallback - ranking indisponível",
            "data": [],
            "timestamp": datetime.now().isoformat(),
        }

    def _get_fallback_status(self) -> Dict[str, Any]:
        """Dados de fallback para status"""
        return {
            "success": True,
            "message": "Dados de fallback - status indisponível",
            "data": {
                "api_status": "degraded",
                "database_status": "degraded",
                "glpi_connection": "degraded",
                "response_time": 1000.0,
                "uptime": 0.0,
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def _create_error_response(
        self, message: str, status_code: int = 400
    ) -> JSONResponse:
        """Cria resposta de erro padronizada"""
        error_response = ApiResponse(success=False, message=message, errors=[message])

        return JSONResponse(content=error_response.dict(), status_code=status_code)

    def get_validation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        total = self.validation_stats["total_requests"]
        if total == 0:
            return self.validation_stats

        return {
            **self.validation_stats,
            "success_rate": self.validation_stats["validation_successes"] / total * 100,
            "error_rate": self.validation_stats["validation_errors"] / total * 100,
            "fallback_rate": self.validation_stats["fallback_used"] / total * 100,
        }


def create_validation_middleware() -> ValidationMiddleware:
    """Factory para criar middleware de validação"""
    return ValidationMiddleware()


# Decorador para validação de endpoints
def validate_response(model_class: Type[BaseModel]):
    """Decorador para validar respostas de endpoints"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # Validar resultado
                if isinstance(result, dict) and "data" in result:
                    validated_data = model_class(**result["data"])
                    result["data"] = validated_data.dict()

                return result

            except PydanticValidationError as e:
                logging.error(f"Erro de validação em {func.__name__}: {e}")
                raise HTTPException(
                    status_code=422,
                    detail={
                        "message": "Erro de validação",
                        "errors": [str(error) for error in e.errors()],
                    },
                )
            except Exception as e:
                logging.error(f"Erro em {func.__name__}: {e}")
                raise HTTPException(
                    status_code=500, detail={"message": "Erro interno do servidor"}
                )

        return wrapper

    return decorator
