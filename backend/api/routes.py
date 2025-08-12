from flask import Blueprint, jsonify, request
from backend.services.api_service import APIService
from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config
from backend.utils.performance import (
    monitor_performance, 
    cache_with_filters, 
    performance_monitor,
    extract_filter_params
)
from backend.utils.response_formatter import ResponseFormatter
from backend.schemas.dashboard import DashboardMetrics, ApiError
from pydantic import ValidationError
import logging
from datetime import datetime
import time

# Importar cache do app principal
try:
    from app import cache
except ImportError:
    # Fallback caso não consiga importar
    cache = None

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicializa serviços
api_service = APIService()
glpi_service = GLPIService()

# Obtém logger configurado
logger = logging.getLogger('api')

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
        "n4": {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0}
    },
    "tendencias": {"novos": "0", "pendentes": "0", "progresso": "0", "resolvidos": "0"}
}

@api_bp.route('/metrics')
@monitor_performance
@cache_with_filters(timeout=300)
def get_metrics():
    """Endpoint para obter métricas do dashboard do GLPI com suporte a filtros avançados e validação"""
    start_time = time.time()
    
    try:
        # Obter todos os parâmetros de filtro
        filters = extract_filter_params()
        start_date = filters.get('start_date')  # Formato: YYYY-MM-DD
        end_date = filters.get('end_date')      # Formato: YYYY-MM-DD
        filter_type = filters.get('filter_type', 'creation')  # creation, modification, current_status
        status = filters.get('status')          # novo, pendente, progresso, resolvido
        priority = filters.get('priority')      # 1-5
        level = filters.get('level')            # n1, n2, n3, n4
        technician = filters.get('technician')  # ID do técnico
        category = filters.get('category')      # ID da categoria
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_inicio inválido. Use YYYY-MM-DD", ["Formato de data inválido"])
                return jsonify(error_response), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_fim inválido. Use YYYY-MM-DD", ["Formato de data inválido"])
                return jsonify(error_response), 400
        
        # Validar que data_inicio não seja posterior a data_fim
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                error_response = ResponseFormatter.format_error_response("Data de início não pode ser posterior à data de fim", ["Intervalo de data inválido"])
                return jsonify(error_response), 400
        
        logger.info(f"Buscando métricas do GLPI com filtros: data={start_date} até {end_date}, status={status}, prioridade={priority}, nível={level}")
        
        # Usar método com filtros se parâmetros fornecidos, senão usar método padrão
        if start_date or end_date:
            # Para filtros de data, usar o método específico baseado no filter_type
            if filter_type == 'modification':
                metrics_data = glpi_service.get_dashboard_metrics_with_modification_date_filter(
                    start_date=start_date,
                    end_date=end_date
                )
            else:  # filter_type == 'creation' (padrão)
                metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(
                    start_date=start_date,
                    end_date=end_date
                )
        elif any([status, priority, level, technician, category]):
            # Para outros filtros, usar o método geral
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
        
        # Verificar se houve erro no serviço
        if isinstance(metrics_data, dict) and metrics_data.get('success') is False:
            return jsonify(metrics_data), 500
        
        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response("Não foi possível conectar ou obter dados do GLPI", ["Erro de conexão"])
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Métricas obtidas com sucesso em {response_time:.2f}ms")
        
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms")
        
        # Validar dados com Pydantic (opcional, para garantir estrutura)
        try:
            if 'data' in metrics_data:
                DashboardMetrics(**metrics_data['data'])
        except ValidationError as ve:
            logger.warning(f"Dados não seguem o schema esperado: {ve}")
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar métricas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(f"Erro interno no servidor: {str(e)}", [str(e)])
        return jsonify(error_response), 500

@api_bp.route('/metrics/filtered')
@monitor_performance
@cache_with_filters(timeout=300)
def get_filtered_metrics():
    """Endpoint para obter métricas filtradas do dashboard do GLPI com validação"""
    start_time = time.time()
    
    try:
        # Obter todos os parâmetros de filtro
        filters = extract_filter_params()
        start_date = filters.get('start_date')  # Formato: YYYY-MM-DD
        end_date = filters.get('end_date')      # Formato: YYYY-MM-DD
        status = filters.get('status')          # novo, pendente, progresso, resolvido
        priority = filters.get('priority')      # 1-5
        level = filters.get('level')            # n1, n2, n3, n4
        technician = filters.get('technician')  # ID do técnico
        category = filters.get('category')      # ID da categoria
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_inicio inválido. Use YYYY-MM-DD", ["Formato de data inválido"])
                return jsonify(error_response), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response("Formato de data_fim inválido. Use YYYY-MM-DD", ["Formato de data inválido"])
                return jsonify(error_response), 400
        
        # Validar que data_inicio não seja posterior a data_fim
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                error_response = ResponseFormatter.format_error_response("Data de início não pode ser posterior à data de fim", ["Intervalo de data inválido"])
                return jsonify(error_response), 400
        
        logger.info(f"Buscando métricas filtradas do GLPI: data={start_date} até {end_date}, status={status}, prioridade={priority}, nível={level}")
        
        # Usar método com filtros
        metrics_data = glpi_service.get_dashboard_metrics_with_filters(
            start_date=start_date,
            end_date=end_date,
            status=status,
            priority=priority,
            level=level,
            technician=technician,
            category=category
        )
        
        # Verificar se houve erro no serviço
        if isinstance(metrics_data, dict) and metrics_data.get('success') is False:
            return jsonify(metrics_data), 500
        
        if not metrics_data:
            logger.warning("Não foi possível obter métricas filtradas do GLPI, usando dados de fallback.")
            error_response = ResponseFormatter.format_error_response("Não foi possível conectar ou obter dados do GLPI", ["Erro de conexão"])
            return jsonify(error_response), 503

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Métricas filtradas obtidas com sucesso em {response_time:.2f}ms")
        
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"Resposta lenta detectada: {response_time:.2f}ms > {target_p95}ms")
        
        # Validar dados com Pydantic (opcional, para garantir estrutura)
        try:
            if 'data' in metrics_data:
                DashboardMetrics(**metrics_data['data'])
        except ValidationError as ve:
            logger.warning(f"Dados não seguem o schema esperado: {ve}")
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar métricas filtradas: {e}", exc_info=True)
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
@cache_with_filters(timeout=300)
def get_technician_ranking():
    """Endpoint para obter ranking de técnicos com filtros avançados de forma robusta"""
    start_time = time.time()
    
    try:
        # Obter e validar parâmetros de filtro
        filters = extract_filter_params()
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        level = filters.get('level')
        limit = filters.get('limit', 10)
        
        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 50))  # Entre 1 e 50
        except (ValueError, TypeError):
            limit = 10
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response(
                    "Formato de start_date inválido. Use YYYY-MM-DD", 
                    ["Formato de data inválido"]
                )
                return jsonify(error_response), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response(
                    "Formato de end_date inválido. Use YYYY-MM-DD", 
                    ["Formato de data inválido"]
                )
                return jsonify(error_response), 400
        
        # Validar que start_date não seja posterior a end_date
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                error_response = ResponseFormatter.format_error_response(
                    "Data de início não pode ser posterior à data de fim", 
                    ["Intervalo de data inválido"]
                )
                return jsonify(error_response), 400
        
        logger.debug(f"Buscando ranking de técnicos: dates={start_date}-{end_date}, level={level}, limit={limit}")
        
        # Buscar ranking com ou sem filtros
        if any([start_date, end_date, level]):
            ranking_data = glpi_service.get_technician_ranking_with_filters(
                start_date=start_date,
                end_date=end_date,
                level=level,
                limit=limit
            )
        else:
            ranking_data = glpi_service.get_technician_ranking(limit=limit)
        
        # Verificar resultado
        if ranking_data is None:
            logger.error("Falha na comunicação com o GLPI")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ao GLPI", 
                ["Erro de conexão"]
            )
            return jsonify(error_response), 503
        
        if not ranking_data:
            logger.info("Nenhum técnico encontrado com os filtros aplicados")
            return jsonify({
                "success": True,
                "data": [],
                "message": "Nenhum técnico encontrado com os filtros aplicados",
                "filters_applied": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "level": level,
                    "limit": limit
                }
            })

        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.info(f"Ranking obtido: {len(ranking_data)} técnicos em {response_time:.2f}ms")
        
        try:
            config_obj = active_config()
            target_p95 = config_obj.PERFORMANCE_TARGET_P95
        except:
            target_p95 = 300
        if response_time > target_p95:
            logger.warning(f"Resposta lenta: {response_time:.2f}ms")
        
        return jsonify({
            "success": True, 
            "data": ranking_data, 
            "response_time_ms": round(response_time, 2),
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "level": level,
                "limit": limit
            }
        })
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar ranking de técnicos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", 
            [str(e)]
        )
        return jsonify(error_response), 500

@api_bp.route('/tickets/new')
@monitor_performance
@cache_with_filters(timeout=180)  # Cache menor para tickets novos
def get_new_tickets():
    """Endpoint para obter tickets novos com filtros avançados de forma robusta"""
    start_time = time.time()
    
    try:
        # Obter e validar parâmetros de filtro
        filters = extract_filter_params()
        limit = filters.get('limit', 5) or 5
        priority = filters.get('priority')
        category = filters.get('category')
        technician = filters.get('technician')
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        # Validar limite
        try:
            limit = int(limit)
            limit = max(1, min(limit, 50))  # Entre 1 e 50
        except (ValueError, TypeError):
            limit = 5
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response(
                    "Formato de start_date inválido. Use YYYY-MM-DD", 
                    ["Formato de data inválido"]
                )
                return jsonify(error_response), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                error_response = ResponseFormatter.format_error_response(
                    "Formato de end_date inválido. Use YYYY-MM-DD", 
                    ["Formato de data inválido"]
                )
                return jsonify(error_response), 400
        
        # Validar que start_date não seja posterior a end_date
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                error_response = ResponseFormatter.format_error_response(
                    "Data de início não pode ser posterior à data de fim", 
                    ["Intervalo de data inválido"]
                )
                return jsonify(error_response), 400
        
        logger.debug(f"Buscando {limit} tickets novos com filtros: priority={priority}, technician={technician}, dates={start_date}-{end_date}")
        
        # Buscar tickets novos com ou sem filtros
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
        
        # Verificar resultado
        if new_tickets is None:
            logger.error("Falha na comunicação com o GLPI")
            error_response = ResponseFormatter.format_error_response(
                "Não foi possível conectar ao GLPI", 
                ["Erro de conexão"]
            )
            return jsonify(error_response), 503
        
        if not new_tickets:
            logger.info("Nenhum ticket novo encontrado com os filtros aplicados")
            return jsonify({
                "success": True,
                "data": [],
                "message": "Nenhum ticket novo encontrado com os filtros aplicados",
                "filters_applied": {
                    "limit": limit,
                    "priority": priority,
                    "category": category,
                    "technician": technician,
                    "start_date": start_date,
                    "end_date": end_date
                }
            })

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
        
        return jsonify({
            "success": True, 
            "data": new_tickets, 
            "response_time_ms": round(response_time, 2),
            "filters_applied": {
                "limit": limit,
                "priority": priority,
                "category": category,
                "technician": technician,
                "start_date": start_date,
                "end_date": end_date
            }
        })
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar tickets novos: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", 
            [str(e)]
        )
        return jsonify(error_response), 500

@api_bp.route('/alerts')
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
                alerts_data.append({
                    "id": "system_001",
                    "type": "info",
                    "severity": "low",
                    "title": "Sistema Operacional",
                    "message": "Dashboard funcionando normalmente",
                    "timestamp": current_time,
                    "acknowledged": False
                })
            else:
                # Problema de conexão com GLPI
                message = glpi_status.get('message', 'Conexão indisponível') if glpi_status else 'Falha na verificação'
                alerts_data.append({
                    "id": "glpi_connection",
                    "type": "error",
                    "severity": "high",
                    "title": "Conexão GLPI",
                    "message": f"Status do GLPI: {message}",
                    "timestamp": current_time,
                    "acknowledged": False
                })
                
        except Exception as glpi_error:
            logger.warning(f"Erro ao verificar status do GLPI: {glpi_error}")
            alerts_data.append({
                "id": "glpi_error",
                "type": "warning",
                "severity": "medium",
                "title": "Verificação GLPI",
                "message": "Não foi possível verificar o status do GLPI",
                "timestamp": current_time,
                "acknowledged": False
            })
        
        # Verificar performance do sistema
        try:
            stats = performance_monitor.get_stats()
            avg_response_time = stats.get('avg_response_time', 0)
            
            try:
                config_obj = active_config()
                target_p95 = config_obj.PERFORMANCE_TARGET_P95
            except:
                target_p95 = 300
            if avg_response_time > target_p95:
                alerts_data.append({
                    "id": "performance_warning",
                    "type": "warning",
                    "severity": "medium",
                    "title": "Performance",
                    "message": f"Tempo de resposta médio elevado: {avg_response_time:.2f}ms",
                    "timestamp": current_time,
                    "acknowledged": False
                })
        except Exception as perf_error:
            logger.debug(f"Erro ao verificar performance: {perf_error}")
        
        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.debug(f"Alertas obtidos: {len(alerts_data)} alertas em {response_time:.2f}ms")
        
        return jsonify({
            "success": True, 
            "data": alerts_data,
            "response_time_ms": round(response_time, 2),
            "total_alerts": len(alerts_data)
        })
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar alertas: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", 
            [str(e)]
        )
        return jsonify(error_response), 500

@api_bp.route('/performance/stats')
def get_performance_stats():
    """Endpoint para obter estatísticas de performance do sistema"""
    try:
        stats = performance_monitor.get_stats()
        
        # Adiciona informações do cache
        cache_info = {
            'cache_type': 'Redis' if hasattr(cache, 'cache') and 'Redis' in str(type(cache.cache)) else 'Simple',
            'cache_timeout': getattr(cache, 'config', {}).get('CACHE_DEFAULT_TIMEOUT', 300) if hasattr(cache, 'config') else 300
        }
        
        return jsonify({
            "success": True,
            "data": {
                **stats,
                **cache_info,
                "target_p95_ms": getattr(active_config(), 'PERFORMANCE_TARGET_P95', 300)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de performance: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}"
        }), 500

@api_bp.route('/status')
@monitor_performance
def get_status():
    """Endpoint para verificar status do sistema e conexão com GLPI de forma robusta"""
    start_time = time.time()
    
    try:
        logger.debug("Verificando status do sistema")
        
        # Verifica status do GLPI com tratamento de erro
        try:
            glpi_status = glpi_service.get_system_status()
            
            if glpi_status:
                glpi_info = {
                    "status": glpi_status.get("status", "unknown"),
                    "message": glpi_status.get("message", "Status indisponível"),
                    "response_time": glpi_status.get("response_time", 0)
                }
            else:
                glpi_info = {
                    "status": "offline",
                    "message": "Falha na verificação do status",
                    "response_time": 0
                }
                
        except Exception as glpi_error:
            logger.warning(f"Erro ao verificar status do GLPI: {glpi_error}")
            glpi_info = {
                "status": "error",
                "message": f"Erro na verificação: {str(glpi_error)}",
                "response_time": 0
            }
        
        # Dados do status do sistema
        current_time = datetime.now().isoformat()
        status_data = {
            "api": "online",
            "glpi": glpi_info["status"],
            "glpi_message": glpi_info["message"],
            "glpi_response_time": glpi_info["response_time"],
            "last_update": current_time,
            "version": "1.0.0",
            "uptime": "Sistema operacional"
        }
        
        # Determinar status geral do sistema
        overall_status = "healthy" if glpi_info["status"] == "online" else "degraded"
        
        # Log de performance
        response_time = (time.time() - start_time) * 1000
        logger.debug(f"Status verificado: API={status_data['api']}, GLPI={status_data['glpi']} em {response_time:.2f}ms")
        
        return jsonify({
            "success": True, 
            "data": status_data,
            "overall_status": overall_status,
            "response_time_ms": round(response_time, 2)
        })
        
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar status: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno do servidor: {str(e)}", 
            [str(e)]
        )
        return jsonify(error_response), 500

@api_bp.route('/filter-types')
def get_filter_types():
    """Endpoint para obter os tipos de filtro de data disponíveis"""
    try:
        filter_types = {
            "creation": {
                "name": "Data de Criação",
                "description": "Filtra tickets criados no período especificado",
                "default": True
            },
            "modification": {
                "name": "Data de Modificação",
                "description": "Filtra tickets modificados no período (inclui mudanças de status)",
                "default": False
            },
            "current_status": {
                "name": "Status Atual",
                "description": "Mostra snapshot atual dos tickets (sem filtro de data)",
                "default": False
            }
        }
        
        return jsonify({
            "success": True,
            "data": filter_types,
            "message": "Tipos de filtro obtidos com sucesso"
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter tipos de filtro: {e}", exc_info=True)
        error_response = ResponseFormatter.format_error_response(
            f"Erro interno no servidor: {str(e)}", 
            [str(e)]
        )
        return jsonify(error_response), 500

@api_bp.route('/health')
def health_check():
    """Endpoint de health check básico"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "GLPI Dashboard API"
        })
    except Exception as e:
        logger.error(f"Erro no health check: {e}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

@api_bp.route('/health/glpi')
def glpi_health_check():
    """Endpoint de health check da conexão GLPI"""
    try:
        # Testa autenticação GLPI
        auth_result = glpi_service._authenticate_with_retry()
        
        if auth_result:
            return jsonify({
                "glpi_connection": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Conexão GLPI funcionando corretamente"
            })
        else:
            return jsonify({
                "glpi_connection": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Falha na autenticação GLPI"
            }), 503
            
    except Exception as e:
        logger.error(f"Erro no health check GLPI: {e}", exc_info=True)
        return jsonify({
            "glpi_connection": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 503