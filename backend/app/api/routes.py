from flask import Blueprint, jsonify, request
from ..services.api_service import APIService
from ..services.glpi_service import GLPIService
from ..core.config import active_config
from ..core.cache_config import (
    cache_short, cache_medium, cache_long,
    cache_manager
)
from ..utils.performance import (
    monitor_performance, 
    performance_monitor,
    extract_filter_params
)
from ..utils.response_formatter import ResponseFormatter
from ..schemas.dashboard import DashboardMetrics, ApiError
from pydantic import ValidationError
import logging
from datetime import datetime
import time

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicializa servicos
api_service = APIService()
glpi_service = GLPIService()

# Obtem logger configurado
logger = logging.getLogger('api')

# Estrutura de dados padrao para metricas em caso de falha ou ausencia de dados
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
        "n4": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0}
    },
    "tendencias": {"novos": "0", "pendentes": "0", "progresso": "0", "resolvidos": "0"}
}

@api_bp.route('/metrics')
@monitor_performance
@cache_medium
def get_metrics():
    """Endpoint para obter metricas do dashboard do GLPI com suporte a filtros avancados e validacao"""
    start_time = time.time()
    
    try:
        # Obter todos os parametros de filtro
        filters = extract_filter_params()
        start_date = filters.get('start_date')  # Formato: YYYY-MM-DD
        end_date = filters.get('end_date')      # Formato: YYYY-MM-DD
        status = filters.get('status')          # novo, pendente, progresso, resolvido
        priority = filters.get('priority')      # 1-5
        level = filters.get('level')            # n1, n2, n3, n4
        technician = filters.get('technician')  # ID do tecnico
        category = filters.get('category')      # ID da categoria
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_inicio invalido. Use YYYY-MM-DD", ["Formato de data invalido"])
                return jsonify(error_response), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_fim invalido. Use YYYY-MM-DD", ["Formato de data invalido"])
                return jsonify(error_response), 400
        
        # Validar que data_inicio nao seja posterior a data_fim
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                error_response = ResponseFormatter.format_error_response("Data de inicio nao pode ser posterior a data de fim", ["Intervalo de data invalido"])
                return jsonify(error_response), 400
        
        logger.info(f"Buscando metricas do GLPI com filtros: data={start_date} ate {end_date}, status={status}, prioridade={priority}, nivel={level}")
        
        # Usar metodo com filtros se parametros fornecidos, senao usar metodo padrao
        if start_date or end_date:
            # Para filtros de data, usar o metodo especifico
            metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(
                start_date=start_date,
                end_date=end_date
            )
        elif any([status, priority, level, technician, category]):
            # Para outros filtros, usar o metodo geral
            metrics_data = glpi_service.get_dashboard_metrics_with_filters(
                start_date=start_date,
                end_date=end_date,
                status=status,
                priority=priority,
                level=level,
                technician=technician,
                category=category
            )
        else:
            metrics_data = glpi_service.get_dashboard_metrics()
        
        # Verificar se houve erro no servico
        if isinstance(metrics_data, dict) and metrics_data.get('success') is False:
            return jsonify(metrics_data), 500
        
        if not metrics_data:
            logger.warning("Nao foi possivel obter metricas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response("Nao foi possivel conectar ou obter dados do GLPI", ["Erro de conexao"])
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Metricas obtidas com sucesso em {response_time:.2f}ms")
        
        if response_time > active_config.PERFORMANCE_TARGET_P95:
            logger.warning(f"Resposta lenta detectada: {response_time:.2f}ms > {active_config.PERFORMANCE_TARGET_P95}ms")
        
        # Validar dados com Pydantic (opcional, para garantir estrutura)
        try:
            if 'data' in metrics_data:
                DashboardMetrics(**metrics_data['data'])
        except ValidationError as ve:
            logger.warning(f"Dados nao seguem o schema esperado: {ve}")
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar metricas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno no servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500

@api_bp.route('/metrics/filtered')
@monitor_performance
@cache_medium
def get_filtered_metrics():
    """Endpoint para obter metricas filtradas do dashboard do GLPI com validacao"""
    start_time = time.time()
    
    try:
        # Obter todos os parametros de filtro
        filters = extract_filter_params()
        start_date = filters.get('start_date')  # Formato: YYYY-MM-DD
        end_date = filters.get('end_date')      # Formato: YYYY-MM-DD
        status = filters.get('status')          # novo, pendente, progresso, resolvido
        priority = filters.get('priority')      # 1-5
        level = filters.get('level')            # n1, n2, n3, n4
        technician = filters.get('technician')  # ID do tecnico
        category = filters.get('category')      # ID da categoria
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_inicio invalido. Use YYYY-MM-DD", ["Formato de data invalido"])
                return jsonify(error_response), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_fim invalido. Use YYYY-MM-DD", ["Formato de data invalido"])
                return jsonify(error_response), 400
        
        # Validar que data_inicio nao seja posterior a data_fim
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                error_response = ResponseFormatter.format_error_response("Data de inicio nao pode ser posterior a data de fim", ["Intervalo de data invalido"])
                return jsonify(error_response), 400
        
        logger.info(f"Buscando metricas filtradas do GLPI: data={start_date} ate {end_date}, status={status}, prioridade={priority}, nivel={level}")
        
        # Usar metodo com filtros
        metrics_data = glpi_service.get_dashboard_metrics_with_filters(
            start_date=start_date,
            end_date=end_date,
            status=status,
            priority=priority,
            level=level,
            technician=technician,
            category=category
        )
        
        # Verificar se houve erro no servico
        if isinstance(metrics_data, dict) and metrics_data.get('success') is False:
            return jsonify(metrics_data), 500
        
        if not metrics_data:
            logger.warning("Nao foi possivel obter metricas filtradas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response("Nao foi possivel conectar ou obter dados do GLPI", ["Erro de conexao"])
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Metricas filtradas obtidas com sucesso em {response_time:.2f}ms")
        
        if response_time > active_config.PERFORMANCE_TARGET_P95:
            logger.warning(f"Resposta lenta detectada: {response_time:.2f}ms > {active_config.PERFORMANCE_TARGET_P95}ms")
        
        # Validar dados com Pydantic (opcional, para garantir estrutura)
        try:
            if 'data' in metrics_data:
                DashboardMetrics(**metrics_data['data'])
        except ValidationError as ve:
            logger.warning(f"Dados nao seguem o schema esperado: {ve}")
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar metricas filtradas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno no servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500

@api_bp.route('/test')
def test_endpoint():
    """Endpoint de teste simples"""
    print("\n=== ENDPOINT DE TESTE CHAMADO ===")
    logger.info("Endpoint de teste chamado")
    return jsonify({"message": "Teste funcionando", "success": True})

@api_bp.route('/metrics/simple')
def get_metrics_simple():
    """Endpoint de metricas simplificado para teste"""
    print("\n=== ENDPOINT MeTRICAS SIMPLES CHAMADO ===")
    logger.info("Endpoint de metricas simples chamado")
    
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
            "n4": {"novos": 3, "pendentes": 1, "progresso": 2, "resolvidos": 8}
        },
        "tendencias": {
            "novos": "+5%",
            "pendentes": "-2%",
            "progresso": "+3%",
            "resolvidos": "+8%"
        }
    }
    
    print(f"Retornando dados de teste: {test_data}")
    return jsonify({"success": True, "data": test_data})

@api_bp.route('/technicians/ranking')
@monitor_performance
@cache_medium
def get_technician_ranking():
    """Endpoint para obter ranking de tecnicos com filtros avancados"""
    start_time = time.time()
    logger.info("=== REQUISIcaO RECEBIDA: /technicians/ranking ===")
    
    try:
        # Obter parametros de filtro
        filters = extract_filter_params()
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        level = filters.get('level')
        limit = filters.get('limit', 10)  # Padrao: top 10
        
        logger.info(f"Buscando ranking de tecnicos com filtros: data={start_date} ate {end_date}, nivel={level}, limite={limit}")
        
        # Busca ranking com filtros se fornecidos
        if any([start_date, end_date, level]):
            ranking_data = glpi_service.get_technician_ranking_with_filters(
                start_date=start_date,
                end_date=end_date,
                level=level,
                limit=limit
            )
        else:
            ranking_data = glpi_service.get_technician_ranking(limit=limit)
        
        if not ranking_data:
            print("AVISO: Nenhum dado de tecnico retornado pelo GLPI")
            logger.warning("Nenhum dado de tecnico retornado pelo GLPI")
            return jsonify({
                "success": True,
                "data": [],
                "message": "Nao foi possivel obter dados de tecnicos do GLPI."
            })

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Ranking de tecnicos obtido com sucesso: {len(ranking_data)} tecnicos em {response_time:.2f}ms")
        
        if response_time > active_config.PERFORMANCE_TARGET_P95:
            logger.warning(f"Resposta lenta detectada: {response_time:.2f}ms > {active_config.PERFORMANCE_TARGET_P95}ms")
        
        return jsonify({"success": True, "data": ranking_data, "response_time_ms": round(response_time, 2)})
        
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de tecnicos: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}"
        }), 500

@api_bp.route('/tickets/new')
@monitor_performance
@cache_short
def get_new_tickets():
    """Endpoint para obter tickets novos com filtros avancados"""
    start_time = time.time()
    logger.info("=== REQUISIcaO RECEBIDA: /tickets/new ===")
    
    try:
        # Obter parametros de filtro
        filters = extract_filter_params()
        limit = filters.get('limit', 5) or 5
        limit = min(limit, 20)  # Maximo de 20 tickets
        priority = filters.get('priority')
        category = filters.get('category')
        technician = filters.get('technician')
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        logger.info(f"Buscando {limit} tickets novos com filtros: prioridade={priority}, categoria={category}, tecnico={technician}")
        
        # Busca tickets novos com filtros
        if any([priority, category, technician, start_date, end_date]):
            new_tickets = glpi_service.get_new_tickets_with_filters(
                limit=limit,
                priority=priority,
                category=category,
                technician=technician,
                start_date=start_date,
                end_date=end_date
            )
        else:
            new_tickets = glpi_service.get_new_tickets(limit)
        
        if not new_tickets:
            logger.warning("Nenhum ticket novo encontrado")
            return jsonify({
                "success": True,
                "data": [],
                "message": "Nenhum ticket novo encontrado."
            })

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Tickets novos obtidos com sucesso: {len(new_tickets)} tickets em {response_time:.2f}ms")
        
        if response_time > active_config.PERFORMANCE_TARGET_P95:
            logger.warning(f"Resposta lenta detectada: {response_time:.2f}ms > {active_config.PERFORMANCE_TARGET_P95}ms")
        
        return jsonify({"success": True, "data": new_tickets, "response_time_ms": round(response_time, 2)})
        
    except Exception as e:
        logger.error(f"Erro ao buscar tickets novos: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}"
        }), 500

@api_bp.route('/alerts')
def get_alerts():
    """Endpoint para obter alertas do sistema"""
    try:
        logger.info("Buscando alertas do sistema...")
        
        # Alertas basicos do sistema - pode ser expandido futuramente
        alerts_data = [
            {
                "id": "system_001",
                "type": "info",
                "severity": "low",
                "title": "Sistema Operacional",
                "message": "Dashboard funcionando normalmente",
                "timestamp": "2024-01-15T10:30:00Z",
                "acknowledged": False
            }
        ]
        
        # Verifica status do GLPI para alertas dinamicos
        glpi_status = glpi_service.get_system_status()
        
        if glpi_status["status"] != "online":
            alerts_data.append({
                "id": "glpi_connection",
                "type": "warning",
                "severity": "medium",
                "title": "Conexao GLPI",
                "message": f"Status do GLPI: {glpi_status['message']}",
                "timestamp": "2024-01-15T10:30:00Z",
                "acknowledged": False
            })
        
        logger.info(f"Alertas obtidos: {len(alerts_data)} alertas encontrados.")
        return jsonify({"success": True, "data": alerts_data})
        
    except Exception as e:
        logger.error(f"Erro ao buscar alertas: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}",
            "data": []
        }), 500

@api_bp.route('/performance/stats')
def get_performance_stats():
    """Endpoint para obter estatisticas de performance do sistema"""
    try:
        stats = performance_monitor.get_stats()
        
        # Adiciona informacoes do cache
        cache_info = {
            'cache_type': 'Redis' if hasattr(cache, 'cache') and 'Redis' in str(type(cache.cache)) else 'Simple',
            'cache_timeout': getattr(cache, 'config', {}).get('CACHE_DEFAULT_TIMEOUT', 300) if hasattr(cache, 'config') else 300
        }
        
        return jsonify({
            "success": True,
            "data": {
                **stats,
                **cache_info,
                "target_p95_ms": active_config.PERFORMANCE_TARGET_P95
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatisticas de performance: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}"
        }), 500

@api_bp.route('/cache/metrics')
def get_cache_metrics():
    """Endpoint para obter metricas detalhadas do cache"""
    try:
        if cache_manager:
            cache_info = cache_manager.get_cache_info()
            return jsonify({
                'success': True,
                'data': cache_info,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Cache manager not available',
                'timestamp': datetime.now().isoformat()
            }), 503
    except Exception as e:
        logger.error(f"Erro ao obter metricas do cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/status')
def get_status():
    """Endpoint para verificar status do sistema e conexao com GLPI"""
    try:
        logger.info("Verificando status do sistema...")
        
        # Verifica status do GLPI
        glpi_status = glpi_service.get_system_status()
        
        status_data = {
            "api": "online",
            "glpi": glpi_status["status"],
            "glpi_message": glpi_status["message"],
            "glpi_response_time": glpi_status["response_time"],
            "last_update": "2024-01-15 10:30:00",
            "version": "1.0.0"
        }
        
        logger.info(f"Status verificado: API={status_data['api']}, GLPI={status_data['glpi']}")
        return jsonify({"success": True, "data": status_data})
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}"
        }), 500

