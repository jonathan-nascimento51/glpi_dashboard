from flask import Blueprint, jsonify
from backend.services.api_service import APIService
from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicializa serviços
api_service = APIService()
glpi_service = GLPIService()

# Obtém logger configurado
logger = logging.getLogger('api')

@api_bp.route('/metrics')
def get_metrics():
    """Endpoint para obter métricas do dashboard do GLPI"""
    try:
        logger.info("Buscando métricas do GLPI...")
        
        # Busca métricas reais do GLPI
        metrics_data = glpi_service.get_dashboard_metrics()
        
        if not metrics_data or metrics_data.get('total', 0) == 0:
            logger.warning("Nenhuma métrica encontrada no GLPI, usando dados de fallback")
            # Fallback para dados mockados em caso de erro
            metrics_data = {
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
                "tendencias": {"novos": "0", "pendentes": "0", "progresso": "0", "resolvidos": "0"},
                "detalhes": {},
                "error": "Não foi possível conectar ao GLPI"
            }
        
        # Adiciona tendências (pode ser implementado posteriormente)
        if "tendencias" not in metrics_data:
            metrics_data["tendencias"] = {
                "novos": "0",
                "pendentes": "0",
                "progresso": "0",
                "resolvidos": "0"
            }
        
        logger.info(f"Métricas obtidas: {metrics_data}")
        
        return jsonify({
            "success": True,
            "data": metrics_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": {
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
        
        logger.info(f"Status do sistema: {status_data}")
        
        return jsonify({
            "success": True,
            "data": status_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500