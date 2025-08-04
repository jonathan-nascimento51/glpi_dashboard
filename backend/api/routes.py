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
def get_metrics():
    """Endpoint para obter métricas do dashboard do GLPI"""
    try:
        logger.info("Buscando métricas do GLPI...")
        
        # Busca métricas reais do GLPI
        metrics_data = glpi_service.get_dashboard_metrics() 
        
        if not metrics_data:
            logger.warning("Não foi possível obter métricas do GLPI, usando dados de fallback.")
            fallback_data = DEFAULT_METRICS.copy()
            fallback_data["error"] = "Não foi possível conectar ou obter dados do GLPI."
            return jsonify({
                "success": True, # A API funcionou, mas a fonte de dados falhou
                "data": fallback_data
            })

        logger.info(f"Métricas obtidas com sucesso.")
        return jsonify({"success": True, "data": metrics_data})
        
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar métricas: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor.",
            "data": DEFAULT_METRICS
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
        logger.error(f"Erro ao verificar status: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor."
        }), 500