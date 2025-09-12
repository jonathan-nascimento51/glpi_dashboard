import logging
import time
from datetime import datetime

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config.settings import active_config
from schemas.dashboard import DashboardMetrics
from services.api_service import APIService
from services.glpi_service import GLPIService
from core.application.services.refactoring_integration import get_refactoring_integration_service
from utils.date_decorators import standard_date_validation
from utils.performance import cache_with_filters, monitor_performance, performance_monitor
from utils.prometheus_metrics import monitor_api_endpoint
from utils.response_formatter import ResponseFormatter

# Importar cache do app principal
try:
    from app import cache
except ImportError:
    # Fallback caso não consiga importar
    cache = None

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Inicializa serviços
api_service = APIService()
glpi_service = GLPIService()  # Legacy service - kept for fallback

# Function to get new service lazily
def get_new_glpi_service():
    """Get the new architecture service via refactoring integration."""
    return get_refactoring_integration_service().get_service()

# Obtém logger configurado
logger = logging.getLogger("api")

# Estrutura de dados padrão para métricas em caso de falha ou ausência de dados
DEFAULT_METRICS = {
    "novos": 0,
    "pendentes": 0,
    "progresso": 0,
    "resolvidos": 0,
    "total": 0,
    "niveis": {
        "n1": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
        "n2": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
        "n3": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
        "n4": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0},
    },
    "tendencias": {"novos": "0", "pendentes": "0", "progresso": "0", "resolvidos": "0"},
}


# Cache para métricas do GLPI (evita chamadas frequentes) - Cache por 180 segundos (3 minutos) para melhor performance
_metrics_cache = {"data": None, "timestamp": 0, "ttl": 180, "filters_hash": None}
# Cache para ranking de técnicos (evita chamadas frequentes)
_ranking_cache = {"data": None, "timestamp": 0, "ttl": 60, "filters_hash": None}  # Cache por 60 segundos

@api_bp.route("/metrics/v2")
@monitor_api_endpoint("get_metrics_v2")
@monitor_performance  
def get_metrics_v2():
    """New architecture metrics endpoint for testing and validation."""
    try:
        correlation_id = f"metrics_v2_{int(time.time())}"
        
        # Extract parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Use new architecture
        if start_date or end_date:
            metrics_data = get_new_glpi_service().get_dashboard_metrics_with_date_filter(
                start_date=start_date,
                end_date=end_date,
                correlation_id=correlation_id
            )
        else:
            metrics_data = get_new_glpi_service().get_dashboard_metrics(
                correlation_id=correlation_id
            )
        
        # Add architecture info for debugging
        metrics_data["_architecture"] = "new_v2"
        metrics_data["_facade"] = "MetricsFacade"
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Error in new metrics endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "_architecture": "new_v2"
        }), 500


@api_bp.route("/metrics")
@monitor_api_endpoint("get_metrics")
@monitor_performance
@cache_with_filters(timeout=300)
@standard_date_validation(support_predefined=True, log_usage=True)
def get_metrics(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter métricas do dashboard do GLPI com filtros avançados de forma robusta"""
    # Gerar correlation_id para rastreabilidade
    from utils.observability import ObservabilityLogger
    import hashlib
    import json

    correlation_id = ObservabilityLogger.generate_correlation_id()
    observability_logger = ObservabilityLogger("metrics_api")

    start_time = time.time()
    
    # Verificar cache baseado nos filtros
    filters_str = json.dumps({
        "start_date": validated_start_date.isoformat() if validated_start_date else None,
        "end_date": validated_end_date.isoformat() if validated_end_date else None,
        "filters": validated_filters or {}
    }, sort_keys=True)
    filters_hash = hashlib.md5(filters_str.encode()).hexdigest()
    
    current_time = time.time()
    if (_metrics_cache["data"] is not None and 
        current_time - _metrics_cache["timestamp"] < _metrics_cache["ttl"] and
        _metrics_cache["filters_hash"] == filters_hash):
        
        cached_data = _metrics_cache["data"].copy()
        if isinstance(cached_data, dict):
            cached_data["cached"] = True
            cached_data["correlation_id"] = correlation_id
        
        response_time = (time.time() - start_time) * 1000
        logger.info(f"[{correlation_id}] Métricas retornadas do cache em {response_time:.2f}ms")
        return jsonify(cached_data)

    try:
        # Usar datas já validadas pelo decorador
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter outros parâmetros de filtro
        filter_type = filters.get("filter_type", "creation")  # creation, modification, current_status
        status = filters.get("status")  # novo, pendente, progresso, resolvido
        priority = filters.get("priority")  # 1-5
        level = filters.get("level")  # n1, n2, n3, n4
        technician = filters.get("technician")  # ID do técnico
        category = filters.get("category")  # ID da categoria

        # Log início da operação com correlation_id
        observability_logger.log_pipeline_start(
            correlation_id=correlation_id,
            operation="get_metrics",
            filters=filters,
            endpoint="/api/metrics",
            method="GET",
        )

        logger.info(
            f"[{correlation_id}] Buscando métricas do GLPI com filtros: data={start_date} até {end_date}, status={status}, prioridade={priority}, nível={level}"
        )

        # Usar método com filtros se parâmetros fornecidos, senão usar método padrão
        if start_date or end_date:
            # Para filtros de data, usar o método específico baseado no filter_type
            if filter_type == "modification":
                observability_logger.log_pipeline_step(
                    correlation_id=correlation_id,
                    step="calling_get_dashboard_metrics_with_modification_date_filter",
                    data={
                        "method": "get_dashboard_metrics_with_modification_date_filter",
                        "filters": filters,
                    },
                )
                metrics_data = glpi_service.get_dashboard_metrics_with_modification_date_filter(
                    start_date=start_date,
                    end_date=end_date,
                    correlation_id=correlation_id,
                )
            else:  # filter_type == 'creation' (padrão)
                observability_logger.log_pipeline_step(
                    correlation_id=correlation_id,
                    step="calling_get_dashboard_metrics_with_date_filter",
                    data={
                        "method": "get_dashboard_metrics_with_date_filter",
                        "filters": filters,
                    },
                )
                metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(
                    start_date=start_date,
                    end_date=end_date,
                    correlation_id=correlation_id,
                )
        elif any([status, priority, level, technician, category]):
            # Para outros filtros, usar o método geral
            observability_logger.log_pipeline_step(
                correlation_id=correlation_id,
                step="calling_get_dashboard_metrics_with_filters",
                data={
                    "method": "get_dashboard_metrics_with_filters",
                    "filters": filters,
                },
            )
            metrics_data = glpi_service.get_dashboard_metrics_with_filters(
                start_date=start_date,
                end_date=end_date,
                status=status,
                priority=priority,
                level=level,
                technician=technician,
                category=category,
                correlation_id=correlation_id,
            )
        else:
            observability_logger.log_pipeline_step(
                correlation_id=correlation_id,
                step="calling_get_dashboard_metrics",
                data={"method": "get_dashboard_metrics", "filters": filters},
            )
            metrics_data = glpi_service.get_dashboard_metrics(correlation_id=correlation_id)

        # Verificar se houve erro no serviço
        if isinstance(metrics_data, dict) and metrics_data.get("success") is False:
            return jsonify(metrics_data), 500

        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ou obter dados do GLPI", ["Erro de conexão"]
            )
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000

        # Log fim da operação
        observability_logger.log_pipeline_end(
            correlation_id=correlation_id,
            operation="get_metrics",
            result_count=1 if metrics_data else 0,
            duration_ms=response_time,
        )

        logger.info(f"[{correlation_id}] Métricas obtidas com sucesso em {response_time:.2f}ms")

        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"[{correlation_id}] Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms")

        # Validar dados com Pydantic (opcional, para garantir estrutura)
        try:
            if "data" in metrics_data:
                DashboardMetrics(**metrics_data["data"])
        except ValidationError as ve:
            logger.warning(f"[{correlation_id}] Dados não seguem o schema esperado: {ve}")

        # Adicionar correlation_id à resposta se metrics_data for um dict
        if isinstance(metrics_data, dict) and "data" in metrics_data:
            metrics_data["correlation_id"] = correlation_id
            metrics_data["cached"] = False
        
        # Salvar no cache para próximas requisições
        _metrics_cache["data"] = metrics_data.copy() if isinstance(metrics_data, dict) else metrics_data
        _metrics_cache["timestamp"] = current_time
        _metrics_cache["filters_hash"] = filters_hash

        return jsonify(metrics_data)

    except Exception as e:
        logger.error(f"[{correlation_id}] Erro inesperado ao buscar métricas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno no servidor: {str(e)}",
            [str(e)],
            correlation_id=correlation_id,
        )
        return jsonify(error_response), 500


@api_bp.route("/metrics/filtered")
@monitor_api_endpoint("get_filtered_metrics")
@monitor_performance
@cache_with_filters(timeout=300)
@standard_date_validation(support_predefined=True, log_usage=True)
def get_filtered_metrics(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter métricas filtradas do dashboard do GLPI com validação"""
    # Gerar correlation_id específico para esta rota
    from utils.observability import ObservabilityLogger

    correlation_id = ObservabilityLogger.generate_correlation_id()
    observability_logger = ObservabilityLogger("metrics_api")

    # Log da chamada para a rota filtered
    observability_logger.log_pipeline_step(
        correlation_id=correlation_id,
        step="filtered_metrics_endpoint_call",
        data={"endpoint": "/api/metrics/filtered", "method": "GET"},
    )

    start_time = time.time()

    try:
        # Usar datas já validadas pelo decorador
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter outros parâmetros de filtro
        status = filters.get("status")  # novo, pendente, progresso, resolvido
        priority = filters.get("priority")  # 1-5
        level = filters.get("level")  # n1, n2, n3, n4
        technician = filters.get("technician")  # ID do técnico
        category = filters.get("category")  # ID da categoria

        # Log início da operação com correlation_id
        observability_logger.log_pipeline_start(
            correlation_id=correlation_id,
            operation="get_filtered_metrics",
            filters=filters,
            endpoint="/api/metrics/filtered",
            method="GET",
        )

        logger.info(
            f"[{correlation_id}] Buscando métricas filtradas do GLPI: data={start_date} até {end_date}, status={status}, prioridade={priority}, nível={level}"
        )

        # Usar método com filtros
        observability_logger.log_pipeline_step(
            correlation_id=correlation_id,
            step="calling_get_dashboard_metrics_with_filters",
            data={"method": "get_dashboard_metrics_with_filters", "filters": filters},
        )
        metrics_data = glpi_service.get_dashboard_metrics_with_filters(
            start_date=start_date,
            end_date=end_date,
            status=status,
            priority=priority,
            level=level,
            technician=technician,
            category=category,
            correlation_id=correlation_id,
        )

        # Verificar se houve erro no serviço
        if isinstance(metrics_data, dict) and metrics_data.get("success") is False:
            return jsonify(metrics_data), 500

        if not metrics_data:
            logger.warning("Não foi possível obter métricas filtradas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ou obter dados do GLPI", ["Erro de conexão"]
            )
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000

        # Log fim da operação
        observability_logger.log_pipeline_end(
            correlation_id=correlation_id,
            operation="get_filtered_metrics",
            result_count=1 if metrics_data else 0,
            duration_ms=response_time,
        )

        logger.info(f"[{correlation_id}] Métricas filtradas obtidas com sucesso em {response_time:.2f}ms")

        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"[{correlation_id}] Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms")

        # Validar dados com Pydantic (opcional, para garantir estrutura)
        try:
            if "data" in metrics_data:
                DashboardMetrics(**metrics_data["data"])
        except ValidationError as ve:
            logger.warning(f"[{correlation_id}] Dados não seguem o schema esperado: {ve}")

        # Adicionar correlation_id à resposta se metrics_data for um dict
        if isinstance(metrics_data, dict) and "data" in metrics_data:
            metrics_data["correlation_id"] = correlation_id

        return jsonify(metrics_data)

    except Exception as e:
        logger.error(
            f"[{correlation_id}] Erro inesperado ao buscar métricas filtradas: {e}",
            exc_info=True,
        )
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno no servidor: {str(e)}",
            [str(e)],
            correlation_id=correlation_id,
        )
        return jsonify(error_response), 500


@api_bp.route("/test")
def test_endpoint():
    """Endpoint de teste simples"""
    print("\n=== ENDPOINT DE TESTE CHAMADO ===")
    logger.info("Endpoint de teste chamado")
    return jsonify({"message": "Teste funcionando", "success": True})


@api_bp.route("/metrics/simple")
def get_metrics_simple():
    """Endpoint de métricas simplificado para teste"""
    print("\n=== ENDPOINT MÉTRICAS SIMPLES CHAMADO ===")
    logger.info("Endpoint de métricas simples chamado")

    # Dados de teste fixos
    test_data = {
        "novos": 15,
        "pendentes": 8,
        "progresso": 12,
        "resolvidos": 45,
        "total": 80,
        "niveis": {
            "n1": {"novos": 5, "pendentes": 2, "progresso": 3, "resolvidos": 10},
            "n2": {"novos": 4, "pendentes": 3, "progresso": 4, "resolvidos": 15},
            "n3": {"novos": 3, "pendentes": 2, "progresso": 3, "resolvidos": 12},
            "n4": {"novos": 3, "pendentes": 1, "progresso": 2, "resolvidos": 8},
        },
        "tendencias": {
            "novos": "+5%",
            "pendentes": "-2%",
            "progresso": "+3%",
            "resolvidos": "+8%",
        },
    }

    print(f"Retornando dados de teste: {test_data}")
    return jsonify({"success": True, "data": test_data})


@api_bp.route("/technicians")
@monitor_api_endpoint("get_technicians")
@monitor_performance
@cache_with_filters(timeout=300)
def get_technicians():
    """Endpoint para obter lista de técnicos com filtros"""
    from utils.observability import ObservabilityLogger
    
    start_time = time.time()
    obs_logger = ObservabilityLogger("get_technicians")
    correlation_id = obs_logger.generate_correlation_id()
    
    try:
        # Obter parâmetros de filtro
        entity_id = request.args.get("entity_id")
        limit = request.args.get("limit", 100)
        
        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 500))
        except (ValueError, TypeError):
            limit = 100
        
        # Validar entity_id
        if entity_id:
            try:
                entity_id = int(entity_id)
            except (ValueError, TypeError):
                entity_id = None
        
        # Buscar técnicos usando método correto
        technician_ids, technician_names = glpi_service._get_all_technician_ids_and_names(entity_id=entity_id)
        
        # Converter para formato de lista de dicionários
        technicians = []
        for tech_id in technician_ids:
            tech_name = technician_names.get(tech_id, f"Técnico {tech_id}")
            technicians.append({
                "id": tech_id,
                "name": tech_name
            })
        
        # Limitar resultados
        if len(technicians) > limit:
            technicians = technicians[:limit]
        
        # Formatar resposta
        response_data = {
            "success": True,
            "technicians": technicians,
            "total_count": len(technicians),
            "filters_applied": {
                "entity_id": entity_id,
                "limit": limit
            },
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "correlation_id": correlation_id,
            "cached": False
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erro ao buscar técnicos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno do servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500


@api_bp.route("/technicians/ranking")
@monitor_api_endpoint("get_technician_ranking")
@monitor_performance
@cache_with_filters(timeout=300)
@standard_date_validation(support_predefined=True, log_usage=True)
def get_technician_ranking(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter ranking de técnicos com filtros avançados de forma robusta"""
    print("[ENDPOINT DEBUG] Requisição recebida no endpoint /technicians/ranking")
    from datetime import datetime

    from utils.observability import ObservabilityLogger

    start_time = time.time()
    obs_logger = ObservabilityLogger("technician_ranking")
    correlation_id = obs_logger.generate_correlation_id()

    try:
        # Usar datas já validadas pelo decorador
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter outros parâmetros de filtro
        level = filters.get("level")
        limit = filters.get("limit", 100)  # Aumentado para 100 por padrão
        entity_id = filters.get("entity_id")  # Novo parâmetro para filtrar por entidade

        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 200))  # Entre 1 e 200 (aumentado o máximo)
        except (ValueError, TypeError):
            limit = 100  # Padrão aumentado para 100

        # Verificar cache
        current_time = time.time()
        filters_hash = hash(str(sorted(filters.items())) + str(start_date) + str(end_date) + str(limit) + str(entity_id))
        
        if (
            _ranking_cache["data"] is not None
            and current_time - _ranking_cache["timestamp"] < _ranking_cache["ttl"]
            and _ranking_cache["filters_hash"] == filters_hash
        ):
            print("[CACHE HIT] Retornando dados do cache para ranking de técnicos")
            cached_data = _ranking_cache["data"].copy()
            cached_data["cached"] = True
            cached_data["correlation_id"] = correlation_id
            return jsonify(cached_data)

        # Log início do pipeline
        obs_logger.log_pipeline_start(
            correlation_id,
            "technician_ranking",
            start_date=start_date,
            end_date=end_date,
            level=level,
            limit=limit,
            entity_id=entity_id,
        )

        # Log janela temporal
        obs_logger.log_pipeline_step(
            correlation_id,
            "temporal_window_validation",
            {
                "start_date": start_date,
                "end_date": end_date,
                "window_days": (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
                if start_date and end_date
                else None,
            },
        )

        logger.debug(
            f"[{correlation_id}] Buscando ranking de técnicos: dates={start_date}-{end_date}, level={level}, limit={limit}"
        )

        # Log parâmetros enviados ao GLPI
        glpi_params = {
            "start_date": start_date,
            "end_date": end_date,
            "level": level,
            "limit": limit,
            "entity_id": entity_id,
            "has_filters": any([start_date, end_date, level, entity_id]),
        }
        obs_logger.log_pipeline_step(correlation_id, "glpi_parameters", glpi_params)

        # Buscar ranking com ou sem filtros
        print(f"[ROUTES DEBUG] Chamando get_technician_ranking_with_filters com start_date={start_date}, end_date={end_date}, entity_id={entity_id}")
        if any([start_date, end_date, level, entity_id]):
            ranking_data = glpi_service.get_technician_ranking_with_filters(
                start_date=start_date,
                end_date=end_date,
                level=level,
                limit=limit,
                correlation_id=correlation_id,
                entity_id=entity_id,
            )
        else:
            ranking_data = glpi_service.get_technician_ranking(limit=limit)

        # Log contagem após consulta GLPI
        obs_logger.log_pipeline_step(
            correlation_id,
            "glpi_query_result",
            {
                "raw_count": len(ranking_data) if ranking_data else 0,
                "is_null": ranking_data is None,
            },
        )

        # Verificar resultado
        if ranking_data is None:
            logger.error("Falha na comunicação com o GLPI")
            error_response = ResponseFormatter.format_error_response("Não foi possível conectar ao GLPI", ["Erro de conexão"])
            return jsonify(error_response), 503

        if not ranking_data:
            obs_logger.log_pipeline_step(
                correlation_id,
                "empty_result",
                {"message": "Nenhum técnico encontrado com os filtros aplicados"},
            )
            logger.info(f"[{correlation_id}] Nenhum técnico encontrado com os filtros aplicados")
            return jsonify(
                {
                    "success": True,
                    "data": [],
                    "message": "Nenhum técnico encontrado com os filtros aplicados",
                    "correlation_id": correlation_id,
                    "filters_applied": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "level": level,
                        "limit": limit,
                        "entity_id": entity_id,
                    },
                }
            )

        # Log contagem após normalização/agregação
        obs_logger.log_pipeline_step(
            correlation_id,
            "data_normalization",
            {
                "final_count": len(ranking_data),
                "sample_data": ranking_data[:3] if len(ranking_data) > 0 else [],
            },
        )

        # Verificações de anomalias
        obs_logger.check_technician_cardinality(correlation_id, len(ranking_data))
        obs_logger.check_technician_names(correlation_id, ranking_data)
        obs_logger.check_zero_totals(
            correlation_id,
            ranking_data,
            {
                "start_date": start_date,
                "end_date": end_date,
                "level": level,
                "limit": limit,
            },
        )

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        obs_logger.log_pipeline_end(correlation_id, "technician_ranking", len(ranking_data), response_time)
        logger.info(f"[{correlation_id}] Ranking obtido: {len(ranking_data)} técnicos em {response_time:.2f}ms")

        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            obs_logger.emit_warning(
                correlation_id,
                "SLOW_RESPONSE",
                f"Resposta lenta: {response_time:.2f}ms (limite: {target_p95}ms)",
                response_time_ms=response_time,
                target_p95=target_p95,
            )
            logger.warning(f"[{correlation_id}] Resposta lenta: {response_time:.2f}ms")

        # Preparar dados de resposta
        response_data = {
            "success": True,
            "data": ranking_data,
            "response_time_ms": round(response_time, 2),
            "correlation_id": correlation_id,
            "cached": False,
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "level": level,
                "limit": limit,
                "entity_id": entity_id,
            },
        }
        
        # Salvar no cache
        _ranking_cache["data"] = response_data.copy()
        _ranking_cache["timestamp"] = current_time
        _ranking_cache["filters_hash"] = filters_hash
        
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ranking de técnicos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno do servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500


@api_bp.route("/tickets/new")
@monitor_api_endpoint("get_new_tickets")
@monitor_performance
@cache_with_filters(timeout=180)  # Cache menor para tickets novos
@standard_date_validation(support_predefined=True, log_usage=True)
def get_new_tickets(validated_start_date=None, validated_end_date=None, validated_filters=None):
    """Endpoint para obter tickets novos com filtros avançados de forma robusta"""
    start_time = time.time()

    try:
        # Usar datas já validadas pelo decorador
        start_date = validated_start_date
        end_date = validated_end_date
        filters = validated_filters or {}

        # Obter outros parâmetros de filtro
        limit = filters.get("limit", 5) or 5
        priority = filters.get("priority")
        category = filters.get("category")
        technician = filters.get("technician")

        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 50))  # Entre 1 e 50
        except (ValueError, TypeError):
            limit = 5

        logger.debug(
            f"Buscando {limit} tickets novos com filtros: priority={priority}, technician={technician}, dates={start_date}-{end_date}"
        )

        # Buscar tickets novos com ou sem filtros
        if any([priority, category, technician, start_date, end_date]):
            new_tickets = glpi_service.get_new_tickets_with_filters(
                limit=limit,
                priority=priority,
                category=category,
                technician=technician,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            new_tickets = glpi_service.get_new_tickets(limit)

        # Verificar resultado
        if new_tickets is None:
            logger.error("Falha na comunicação com o GLPI")
            error_response = ResponseFormatter.format_error_response("Não foi possível conectar ao GLPI", ["Erro de conexão"])
            return jsonify(error_response), 503

        if not new_tickets:
            logger.info("Nenhum ticket novo encontrado com os filtros aplicados")
            return jsonify(
                {
                    "success": True,
                    "data": [],
                    "message": "Nenhum ticket novo encontrado com os filtros aplicados",
                    "filters_applied": {
                        "limit": limit,
                        "priority": priority,
                        "category": category,
                        "technician": technician,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                }
            )

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Tickets novos obtidos: {len(new_tickets)} tickets em {response_time:.2f}ms")

        # Obter configuração de performance de forma segura
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except Exception:
            target_p95 = 300  # valor padrão

        if response_time > target_p95:
            logger.warning(f"Resposta lenta: {response_time:.2f}ms")

        return jsonify(
            {
                "success": True,
                "data": new_tickets,
                "response_time_ms": round(response_time, 2),
                "filters_applied": {
                    "limit": limit,
                    "priority": priority,
                    "category": category,
                    "technician": technician,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
        )

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar tickets novos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno do servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500


@api_bp.route("/alerts")
@monitor_performance
def get_alerts():
    """Endpoint para obter alertas do sistema de forma robusta"""
    start_time = time.time()

    try:
        logger.debug("Verificando alertas do sistema")

        # Alertas básicos do sistema
        alerts_data = []
        current_time = datetime.now().isoformat() + "Z"

        # Verifica status do GLPI para alertas dinâmicos
        try:
            glpi_status = glpi_service.get_system_status()

            if glpi_status and glpi_status.get("status") == "online":
                # Sistema funcionando normalmente
                alerts_data.append(
                    {
                        "id": "system_001",
                        "type": "info",
                        "severity": "low",
                        "title": "Sistema Operacional",
                        "message": "Dashboard funcionando normalmente",
                        "timestamp": current_time,
                        "acknowledged": False,
                    }
                )
            else:
                # Problema de conexão com GLPI
                message = glpi_status.get("message", "Conexão indisponível") if glpi_status else "Falha na verificação"
                alerts_data.append(
                    {
                        "id": "glpi_connection",
                        "type": "error",
                        "severity": "high",
                        "title": "Conexão GLPI",
                        "message": f"Status do GLPI: {message}",
                        "timestamp": current_time,
                        "acknowledged": False,
                    }
                )

        except Exception as glpi_error:
            logger.warning(f"Erro ao verificar status do GLPI: {glpi_error}")
            alerts_data.append(
                {
                    "id": "glpi_error",
                    "type": "warning",
                    "severity": "medium",
                    "title": "Verificação GLPI",
                    "message": "Não foi possível verificar o status do GLPI",
                    "timestamp": current_time,
                    "acknowledged": False,
                }
            )

        # Verificar performance do sistema
        try:
            stats = performance_monitor.get_stats()
            avg_response_time = stats.get("avg_response_time", 0)

            try:
                config_obj = active_config()
                target_p95 = config_obj.PERFORMANCE_TARGET_P95
            except:
                target_p95 = 300
            if avg_response_time > target_p95:
                alerts_data.append(
                    {
                        "id": "performance_warning",
                        "type": "warning",
                        "severity": "medium",
                        "title": "Performance",
                        "message": f"Tempo de resposta médio elevado: {avg_response_time:.2f}ms",
                        "timestamp": current_time,
                        "acknowledged": False,
                    }
                )
        except Exception as perf_error:
            logger.debug(f"Erro ao verificar performance: {perf_error}")

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.debug(f"Alertas obtidos: {len(alerts_data)} alertas em {response_time:.2f}ms")

        return jsonify(
            {
                "success": True,
                "data": alerts_data,
                "response_time_ms": round(response_time, 2),
                "total_alerts": len(alerts_data),
            }
        )

    except Exception as e:
        logger.error(f"Erro inesperado ao buscar alertas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno do servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500


@api_bp.route("/performance/stats")
def get_performance_stats():
    """Endpoint para obter estatísticas de performance do sistema"""
    try:
        stats = performance_monitor.get_stats()

        # Adiciona informações do cache
        cache_info = {
            "cache_type": "Redis" if hasattr(cache, "cache") and "Redis" in str(type(cache.cache)) else "Simple",
            "cache_timeout": getattr(cache, "config", {}).get("CACHE_DEFAULT_TIMEOUT", 300)
            if hasattr(cache, "config")
            else 300,
        }

        return jsonify(
            {
                "success": True,
                "data": {
                    **stats,
                    **cache_info,
                    "target_p95_ms": getattr(active_config(), "PERFORMANCE_TARGET_P95", 300),
                },
            }
        )

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de performance: {str(e)}")
        return (
            jsonify({"success": False, "error": f"Erro interno do servidor: {str(e)}"}),
            500,
        )


# Cache para status do GLPI (evita chamadas frequentes)
_status_cache = {"data": None, "timestamp": 0, "ttl": 30}  # Cache por 30 segundos
# Cache completo da resposta para máxima performance
_response_cache = {"data": None, "timestamp": 0, "ttl": 30}

@api_bp.route("/status")
def get_status():
    """Endpoint para verificar status do sistema - versão otimizada"""
    start_time = time.time()

    try:
        current_time_unix = time.time()
        
        # Verificar cache completo da resposta primeiro (máxima performance)
        response_cache_valid = (
            _response_cache["data"] is not None and 
            (current_time_unix - _response_cache["timestamp"]) < _response_cache["ttl"]
        )
        
        if response_cache_valid:
            cached_response = _response_cache["data"].copy()
            # Atualizar apenas o response_time para refletir a performance atual
            response_time = (time.time() - start_time) * 1000
            cached_response["response_time_ms"] = round(response_time, 2)
            return jsonify(cached_response)

        # Verificar cache do status do GLPI
        cache_valid = (
            _status_cache["data"] is not None and 
            (current_time_unix - _status_cache["timestamp"]) < _status_cache["ttl"]
        )

        if cache_valid:
            glpi_info = _status_cache["data"]
        else:
            # Verificação simplificada do GLPI (sem autenticação completa)
            try:
                import requests
                glpi_start = time.time()
                # Normalizar URL para evitar duplicação de /apirest.php
                glpi_base_url = active_config.GLPI_URL.rstrip('/')
                if glpi_base_url.endswith('/apirest.php'):
                    glpi_base_url = glpi_base_url.rsplit('/apirest.php', 1)[0]
                response = requests.get(f"{glpi_base_url}/apirest.php", timeout=1)
                glpi_response_time = (time.time() - glpi_start) * 1000
                
                if response.status_code == 200:
                    glpi_info = {
                        "status": "online",
                        "message": "GLPI acessível",
                        "response_time": round(glpi_response_time, 2),
                    }
                else:
                    glpi_info = {
                        "status": "error",
                        "message": f"GLPI respondeu com status {response.status_code}",
                        "response_time": round(glpi_response_time, 2),
                    }
                    
            except Exception as glpi_error:
                glpi_info = {
                    "status": "offline",
                    "message": f"GLPI inacessível: {str(glpi_error)}",
                    "response_time": 0,
                }
                
            # Atualizar cache
            _status_cache["data"] = glpi_info
            _status_cache["timestamp"] = current_time_unix

        # Dados do status do sistema (otimizado)
        current_time = datetime.now().isoformat()
        status_data = {
            "api": "online",
            "glpi": glpi_info["status"],
            "glpi_message": glpi_info["message"],
            "glpi_response_time": glpi_info["response_time"],
            "last_update": current_time,
            "version": "1.0.0",
            "uptime": "Sistema operacional",
            "cached": cache_valid,
        }

        # Determinar status geral do sistema
        overall_status = "healthy" if glpi_info["status"] == "online" else "degraded"

        response_time = (time.time() - start_time) * 1000

        response_data = {
            "success": True,
            "data": status_data,
            "overall_status": overall_status,
            "response_time_ms": round(response_time, 2),
        }
        
        # Cache da resposta completa para máxima performance
        _response_cache["data"] = response_data
        _response_cache["timestamp"] = current_time_unix
        
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Erro inesperado ao verificar status: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno do servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500


@api_bp.route("/filter-types")
def get_filter_types():
    """Endpoint para obter os tipos de filtro de data disponíveis"""
    try:
        filter_types = {
            "creation": {
                "name": "Data de Criação",
                "description": "Filtra tickets criados no período especificado",
                "default": True,
            },
            "modification": {
                "name": "Data de Modificação",
                "description": "Filtra tickets modificados no período (inclui mudanças de status)",
                "default": False,
            },
            "current_status": {
                "name": "Status Atual",
                "description": "Mostra snapshot atual dos tickets (sem filtro de data)",
                "default": False,
            },
        }

        return jsonify(
            {
                "success": True,
                "data": filter_types,
                "message": "Tipos de filtro obtidos com sucesso",
            }
        )

    except Exception as e:
        logger.error(f"Erro ao obter tipos de filtro: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno no servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500


@api_bp.route("/health")
def health_check():
    """Endpoint de health check básico"""
    try:
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "GLPI Dashboard API",
            }
        )
    except Exception as e:
        logger.error(f"Erro no health check: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
            ),
            500,
        )


@api_bp.route("/health/glpi")
def glpi_health_check():
    """Endpoint de health check da conexão GLPI"""
    try:
        # Testa autenticação GLPI
        auth_result = glpi_service._authenticate_with_retry()

        if auth_result:
            return jsonify(
                {
                    "glpi_connection": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Conexão GLPI funcionando corretamente",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "glpi_connection": "unhealthy",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Falha na autenticação GLPI",
                    }
                ),
                503,
            )

    except Exception as e:
        logger.error(f"Erro no health check GLPI: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "glpi_connection": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
            ),
            503,
        )


@api_bp.route("/docs", methods=["GET"])
def swagger_ui():
    """Serve Swagger UI for API documentation"""
    import os
    
    # Caminho para o arquivo HTML do Swagger UI
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs", "api")
    
    swagger_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GLPI Dashboard API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
        <style>
            html {
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }
            *, *:before, *:after {
                box-sizing: inherit;
            }
            body {
                margin:0;
                background: #fafafa;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/api/openapi.yaml',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                });
            };
        </script>
    </body>
    </html>
    """
    
    from flask import Response
    return Response(swagger_html, mimetype='text/html')


@api_bp.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    """Serve OpenAPI specification file"""
    import os
    from flask import Response
    
    # Caminho para o arquivo openapi.yaml
    openapi_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "docs", 
        "api", 
        "openapi.yaml"
    )
    
    if os.path.exists(openapi_path):
        with open(openapi_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='application/x-yaml')
    else:
        return jsonify({"error": "OpenAPI specification not found"}), 404
