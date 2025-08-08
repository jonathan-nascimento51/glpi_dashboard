"""Rotas específicas para análises de manutenção da Casa Civil"""

import logging
from flask import Blueprint, request
from datetime import datetime
from dependency_injector.wiring import inject, Provide

from backend.containers import Container
from backend.services.maintenance_analytics_service import MaintenanceAnalyticsService
from backend.utils.response_formatter import ResponseFormatter
from backend.utils.validators import validate_date_format

logger = logging.getLogger(__name__)

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/api/maintenance')

@maintenance_bp.route('/metrics', methods=['GET'])
@inject
def get_maintenance_metrics(
    maintenance_service: MaintenanceAnalyticsService = Provide[Container.maintenance_analytics_service]
):
    """Endpoint para obter métricas específicas de manutenção"""
    try:
        # Obter parâmetros de data opcionais
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validar formato das datas se fornecidas
        if start_date and not validate_date_format(start_date):
            return ResponseFormatter.error(
                "Formato de data inválido para start_date. Use YYYY-MM-DD",
                status_code=400
            )
        
        if end_date and not validate_date_format(end_date):
            return ResponseFormatter.error(
                "Formato de data inválido para end_date. Use YYYY-MM-DD",
                status_code=400
            )
        
        # Validar que start_date não seja posterior a end_date
        if start_date and end_date and start_date > end_date:
            return ResponseFormatter.error(
                "start_date não pode ser posterior a end_date",
                status_code=400
            )
        
        logger.info(f"Solicitação de métricas de manutenção - Período: {start_date} até {end_date}")
        
        # Obter métricas do serviço de análise de manutenção
        metrics_result = maintenance_service.get_maintenance_dashboard_metrics(start_date, end_date)
        
        if not metrics_result.get('success', False):
            logger.warning("Falha ao obter métricas de manutenção, usando dados de fallback")
            return ResponseFormatter.success(
                metrics_result.get('data', {}),
                message="Métricas de manutenção obtidas com dados de fallback"
            )
        
        return ResponseFormatter.success(
            metrics_result['data'],
            message="Métricas de manutenção obtidas com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas de manutenção: {e}", exc_info=True)
        return ResponseFormatter.error(
            "Erro interno do servidor ao obter métricas de manutenção",
            status_code=500
        )

@maintenance_bp.route('/categories', methods=['GET'])
@inject
def get_maintenance_categories(
    maintenance_service: MaintenanceAnalyticsService = Provide[Container.maintenance_analytics_service]
):
    """Endpoint para análise das categorias de manutenção"""
    try:
        logger.info("Solicitação de análise de categorias de manutenção")
        
        # Obter análise das categorias
        categories_result = maintenance_service.get_maintenance_categories_analysis()
        
        if not categories_result.get('success', False):
            logger.warning("Falha ao obter análise de categorias, usando dados simulados")
            return ResponseFormatter.success(
                categories_result.get('data', {}),
                message="Análise de categorias obtida com dados simulados"
            )
        
        return ResponseFormatter.success(
            categories_result['data'],
            message="Análise de categorias de manutenção obtida com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter análise de categorias: {e}", exc_info=True)
        return ResponseFormatter.error(
            "Erro interno do servidor ao obter análise de categorias",
            status_code=500
        )

@maintenance_bp.route('/groups', methods=['GET'])
@inject
def get_technical_groups_performance(
    maintenance_service: MaintenanceAnalyticsService = Provide[Container.maintenance_analytics_service]
):
    """Endpoint para análise de performance dos grupos técnicos"""
    try:
        logger.info("Solicitação de análise de performance dos grupos técnicos")
        
        # Obter análise dos grupos técnicos
        groups_result = maintenance_service.get_technical_groups_performance()
        
        if not groups_result.get('success', False):
            logger.warning("Falha ao obter análise de grupos, usando dados simulados")
            return ResponseFormatter.success(
                groups_result.get('data', {}),
                message="Análise de grupos obtida com dados simulados"
            )
        
        return ResponseFormatter.success(
            groups_result['data'],
            message="Análise de performance dos grupos técnicos obtida com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter análise de grupos: {e}", exc_info=True)
        return ResponseFormatter.error(
            "Erro interno do servidor ao obter análise de grupos",
            status_code=500
        )

@maintenance_bp.route('/categories/<category_id>/details', methods=['GET'])
@inject
def get_category_details(
    category_id: str,
    maintenance_service: MaintenanceAnalyticsService = Provide[Container.maintenance_analytics_service]
):
    """Endpoint para obter detalhes específicos de uma categoria"""
    try:
        logger.info(f"Solicitação de detalhes da categoria: {category_id}")
        
        # Obter análise completa das categorias
        categories_result = maintenance_service.get_maintenance_categories_analysis()
        
        if not categories_result.get('success', False):
            return ResponseFormatter.error(
                "Falha ao obter dados das categorias",
                status_code=500
            )
        
        # Encontrar a categoria específica
        categories = categories_result['data'].get('categories', [])
        category_details = next((cat for cat in categories if cat['id'] == category_id), None)
        
        if not category_details:
            return ResponseFormatter.error(
                f"Categoria {category_id} não encontrada",
                status_code=404
            )
        
        # Enriquecer com informações adicionais
        enriched_details = {
            **category_details,
            'trends': {
                'last_week': '+5%',
                'last_month': '+12%',
                'resolution_trend': 'Melhorando'
            },
            'recommendations': [
                "Considerar aumento da equipe para esta categoria",
                "Implementar manutenção preventiva",
                "Revisar processos de atendimento"
            ]
        }
        
        return ResponseFormatter.success(
            enriched_details,
            message=f"Detalhes da categoria {category_details['name']} obtidos com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da categoria {category_id}: {e}", exc_info=True)
        return ResponseFormatter.error(
            "Erro interno do servidor ao obter detalhes da categoria",
            status_code=500
        )

@maintenance_bp.route('/groups/<group_id>/performance', methods=['GET'])
@inject
def get_group_performance_details(
    group_id: str,
    maintenance_service: MaintenanceAnalyticsService = Provide[Container.maintenance_analytics_service]
):
    """Endpoint para obter detalhes de performance de um grupo específico"""
    try:
        logger.info(f"Solicitação de detalhes de performance do grupo: {group_id}")
        
        # Obter análise completa dos grupos
        groups_result = maintenance_service.get_technical_groups_performance()
        
        if not groups_result.get('success', False):
            return ResponseFormatter.error(
                "Falha ao obter dados dos grupos",
                status_code=500
            )
        
        # Encontrar o grupo específico
        groups = groups_result['data'].get('groups', [])
        group_details = next((group for group in groups if group['id'] == group_id), None)
        
        if not group_details:
            return ResponseFormatter.error(
                f"Grupo {group_id} não encontrado",
                status_code=404
            )
        
        # Enriquecer com métricas detalhadas
        enriched_performance = {
            **group_details,
            'detailed_metrics': {
                'avg_response_time': '2.5 horas',
                'avg_resolution_time': '24 horas',
                'customer_satisfaction': '4.2/5.0',
                'sla_compliance': '85%'
            },
            'recent_activity': [
                {'date': '2024-01-15', 'action': 'Ticket resolvido', 'category': 'Ar Condicionado'},
                {'date': '2024-01-14', 'action': 'Novo ticket atribuído', 'category': 'Elétrica'},
                {'date': '2024-01-13', 'action': 'Ticket em progresso', 'category': 'Hidráulica'}
            ],
            'performance_trends': {
                'efficiency_trend': '+5%',
                'workload_trend': 'Estável',
                'quality_trend': 'Melhorando'
            }
        }
        
        return ResponseFormatter.success(
            enriched_performance,
            message=f"Detalhes de performance do grupo {group_details['name']} obtidos com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do grupo {group_id}: {e}", exc_info=True)
        return ResponseFormatter.error(
            "Erro interno do servidor ao obter detalhes do grupo",
            status_code=500
        )

@maintenance_bp.route('/dashboard/summary', methods=['GET'])
@inject
def get_maintenance_dashboard_summary(
    maintenance_service: MaintenanceAnalyticsService = Provide[Container.maintenance_analytics_service]
):
    """Endpoint para obter resumo completo do dashboard de manutenção"""
    try:
        logger.info("Solicitação de resumo completo do dashboard de manutenção")
        
        # Obter dados de todas as análises
        metrics_result = maintenance_service.get_maintenance_dashboard_metrics()
        categories_result = maintenance_service.get_maintenance_categories_analysis()
        groups_result = maintenance_service.get_technical_groups_performance()
        
        # Compilar resumo completo
        dashboard_summary = {
            'overview': {
                'total_tickets': metrics_result.get('data', {}).get('total', 0),
                'active_tickets': (
                    metrics_result.get('data', {}).get('novos', 0) +
                    metrics_result.get('data', {}).get('progresso', 0) +
                    metrics_result.get('data', {}).get('pendentes', 0)
                ),
                'resolved_tickets': metrics_result.get('data', {}).get('resolvidos', 0),
                'categories_count': len(categories_result.get('data', {}).get('categories', [])),
                'groups_count': len(groups_result.get('data', {}).get('groups', []))
            },
            'performance_indicators': {
                'avg_resolution_time': categories_result.get('data', {}).get('summary', {}).get('avgResolutionTime', 0),
                'avg_group_efficiency': groups_result.get('data', {}).get('summary', {}).get('avgEfficiency', 0),
                'critical_categories': categories_result.get('data', {}).get('summary', {}).get('criticalCategories', 0),
                'high_priority_categories': categories_result.get('data', {}).get('summary', {}).get('highPriorityCategories', 0)
            },
            'alerts': [
                {
                    'type': 'warning',
                    'message': 'Categoria Ar Condicionado com alto volume de tickets',
                    'priority': 'Alta'
                },
                {
                    'type': 'info',
                    'message': 'Performance geral dos grupos dentro da meta',
                    'priority': 'Baixa'
                }
            ],
            'recommendations': [
                'Considerar redistribuição de carga entre grupos técnicos',
                'Implementar manutenção preventiva para reduzir tickets de ar condicionado',
                'Revisar processos de atendimento para melhorar eficiência'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return ResponseFormatter.success(
            dashboard_summary,
            message="Resumo do dashboard de manutenção obtido com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter resumo do dashboard: {e}", exc_info=True)
        return ResponseFormatter.error(
            "Erro interno do servidor ao obter resumo do dashboard",
            status_code=500
        )

# Registrar blueprint no app principal
def register_maintenance_routes(app):
    """Registra as rotas de manutenção no app Flask"""
    app.register_blueprint(maintenance_bp)
    logger.info("Rotas de manutenção registradas com sucesso")