from flask import Blueprint, jsonify, request
from backend.services.api_service import APIService
from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config
import logging
from datetime import datetime

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

# Função para gerar chave de cache personalizada
def make_cache_key():
    """Gera chave de cache baseada nos parâmetros de data da requisição"""
    start = request.args.get('start_date', 'default')
    end = request.args.get('end_date', 'default')
    return f'metrics-{start}-{end}'

@api_bp.route('/metrics')
@cache.cached(timeout=300, make_cache_key=make_cache_key) if cache else lambda f: f
def get_metrics():
    """Endpoint para obter métricas do dashboard do GLPI com suporte a filtro de data"""
    try:
        # Obter parâmetros de data da query string (opcionais)
        start_date = request.args.get('start_date')  # Formato: YYYY-MM-DD
        end_date = request.args.get('end_date')      # Formato: YYYY-MM-DD
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de data_inicio inválido. Use YYYY-MM-DD",
                    "data": DEFAULT_METRICS
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de data_fim inválido. Use YYYY-MM-DD",
                    "data": DEFAULT_METRICS
                }), 400
        
        # Validar que data_inicio não seja posterior a data_fim
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                return jsonify({
                    "success": False,
                    "error": "Data de início não pode ser posterior à data de fim",
                    "data": DEFAULT_METRICS
                }), 400
        
        logger.info(f"Buscando métricas do GLPI com filtro de data: {start_date} até {end_date}")
        
        # Usar método com filtro de data se parâmetros fornecidos, senão usar método padrão
        if start_date or end_date:
            metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(start_date, end_date)
        else:
            metrics_data = glpi_service.get_dashboard_metrics()
        
        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI, usando dados de fallback.")
            fallback_data = DEFAULT_METRICS.copy()
            fallback_data["error"] = "Não foi possível conectar ou obter dados do GLPI."
            if start_date or end_date:
                fallback_data["filtro_data"] = {
                    "data_inicio": start_date,
                    "data_fim": end_date
                }
            return jsonify({
                "success": True, # A API funcionou, mas a fonte de dados falhou
                "data": fallback_data
            })

        logger.info(f"Métricas obtidas com sucesso.")
        return jsonify({"success": True, "data": metrics_data})
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar métricas: {e}", exc_info=True)
        fallback_data = DEFAULT_METRICS.copy()
        if request.args.get('start_date') or request.args.get('end_date'):
            fallback_data["filtro_data"] = {
                "data_inicio": request.args.get('start_date'),
                "data_fim": request.args.get('end_date')
            }
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor.",
            "data": fallback_data
        }), 500

@api_bp.route('/metrics/filtered')
def get_metrics_with_date_filter():
    """Endpoint para obter métricas do dashboard do GLPI com filtro de data"""
    try:
        # Obter parâmetros de data da query string
        start_date = request.args.get('start_date')  # Formato: YYYY-MM-DD
        end_date = request.args.get('end_date')      # Formato: YYYY-MM-DD
        
        # Validar formato das datas se fornecidas
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de data_inicio inválido. Use YYYY-MM-DD",
                    "data": DEFAULT_METRICS
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de data_fim inválido. Use YYYY-MM-DD",
                    "data": DEFAULT_METRICS
                }), 400
        
        # Validar que data_inicio não seja posterior a data_fim
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                return jsonify({
                    "success": False,
                    "error": "Data de início não pode ser posterior à data de fim",
                    "data": DEFAULT_METRICS
                }), 400
        
        logger.info(f"Buscando métricas do GLPI com filtro de data: {start_date} até {end_date}")
        
        # Busca métricas reais do GLPI com filtro de data
        metrics_data = glpi_service.get_dashboard_metrics_with_date_filter(start_date, end_date)
        
        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI com filtro, usando dados de fallback.")
            fallback_data = DEFAULT_METRICS.copy()
            fallback_data["error"] = "Não foi possível conectar ou obter dados do GLPI."
            fallback_data["filtro_data"] = {
                "data_inicio": start_date,
                "data_fim": end_date
            }
            return jsonify({
                "success": True,  # A API funcionou, mas a fonte de dados falhou
                "data": fallback_data
            })

        logger.info(f"Métricas com filtro obtidas com sucesso.")
        return jsonify({
            "success": True,
            "data": metrics_data
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar métricas com filtro: {e}")
        fallback_data = DEFAULT_METRICS.copy()
        fallback_data["filtro_data"] = {
            "data_inicio": request.args.get('start_date'),
            "data_fim": request.args.get('end_date')
        }
        return jsonify({
            "success": False,
            "error": str(e),
            "data": fallback_data
        }), 500

@api_bp.route('/test')
def test_endpoint():
    """Endpoint de teste simples"""
    print("\n=== ENDPOINT DE TESTE CHAMADO ===")
    logger.info("Endpoint de teste chamado")
    return jsonify({"message": "Teste funcionando", "success": True})

@api_bp.route('/technicians/ranking')
def get_technician_ranking():
    """Endpoint para obter ranking de técnicos por total de chamados"""
    print("=== REQUISIÇÃO RECEBIDA: /technicians/ranking ===")
    logger.info("=== REQUISIÇÃO RECEBIDA: /technicians/ranking ===")
    
    try:
        print("Iniciando busca de ranking de técnicos...")
        logger.info("Buscando ranking de técnicos do GLPI...")
        
        # Busca ranking real do GLPI
        print("Chamando glpi_service.get_technician_ranking()...")
        ranking_data = glpi_service.get_technician_ranking()
        print(f"Resultado: {len(ranking_data) if ranking_data else 0} técnicos")
        
        if not ranking_data:
            print("AVISO: Nenhum dado de técnico retornado pelo GLPI")
            logger.warning("Nenhum dado de técnico retornado pelo GLPI")
            return jsonify({
                "success": True,
                "data": [],
                "message": "Não foi possível obter dados de técnicos do GLPI."
            })

        print(f"SUCESSO: {len(ranking_data)} técnicos encontrados")
        logger.info(f"Ranking de técnicos obtido com sucesso: {len(ranking_data)} técnicos encontrados.")
        return jsonify({"success": True, "data": ranking_data})
        
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de técnicos: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}"
        }), 500

@api_bp.route('/tickets/new')
def get_new_tickets():
    """Endpoint para obter tickets com status 'novo'"""
    logger.info("=== REQUISIÇÃO RECEBIDA: /tickets/new ===")
    
    try:
        # Obter parâmetro de limite (padrão: 5)
        limit = request.args.get('limit', 5, type=int)
        limit = min(limit, 20)  # Máximo de 20 tickets
        
        logger.info(f"Buscando {limit} tickets novos do GLPI...")
        
        # Busca tickets novos do GLPI
        new_tickets = glpi_service.get_new_tickets(limit)
        
        if not new_tickets:
            logger.warning("Nenhum ticket novo encontrado")
            return jsonify({
                "success": True,
                "data": [],
                "message": "Nenhum ticket novo encontrado."
            })

        logger.info(f"Tickets novos obtidos com sucesso: {len(new_tickets)} tickets encontrados.")
        return jsonify({"success": True, "data": new_tickets})
        
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
        
        # Alertas básicos do sistema - pode ser expandido futuramente
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
        
        # Verifica status do GLPI para alertas dinâmicos
        glpi_status = glpi_service.get_system_status()
        
        if glpi_status["status"] != "online":
            alerts_data.append({
                "id": "glpi_connection",
                "type": "warning",
                "severity": "medium",
                "title": "Conexão GLPI",
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

@api_bp.route('/status')
def get_status():
    """Endpoint para verificar status do sistema e conexão com GLPI"""
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