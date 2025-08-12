from typing import Any, Dict
from fastapi import HTTPException
from usecases.get_dashboard_metrics import GetDashboardMetricsUseCase
from adapters.glpi.glpi_adapter import GLPIAdapter
from adapters.cache.memory_cache_adapter import InMemoryCacheAdapter
from adapters.clock.system_clock_adapter import SystemClockAdapter
from utils.response_formatter import ResponseFormatter

class DashboardController:
    """Controlador para endpoints do dashboard"""

    def __init__(self):
        # Inicializa adaptadores existentes no projeto
        self.glpi_adapter = GLPIAdapter()
        self.cache_adapter = InMemoryCacheAdapter()
        self.clock_adapter = SystemClockAdapter()

        # Inicializa casos de uso
        self.get_dashboard_metrics_usecase = GetDashboardMetricsUseCase(
            glpi_repository=self.glpi_adapter,
            cache_repository=self.cache_adapter,
            clock=self.clock_adapter,
        )

    async def get_kpis(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Endpoint para buscar KPIs do dashboard"""
        try:
            metrics = await self.get_dashboard_metrics_usecase.execute(force_refresh)

            # Converte entidade para formato esperado pelo frontend atual
            response_data = {
                "niveis": {
                    nivel: {
                        "novos": data.novos,
                        "progresso": data.progresso,
                        "pendentes": data.pendentes,
                        "resolvidos": data.resolvidos,
                        "total": data.total,
                    }
                    for nivel, data in metrics.niveis.items()
                },
                "technician_ranking": [
                    {
                        "name": tech.name,
                        "resolved_tickets": tech.resolved_tickets,
                        "avg_resolution_time": tech.avg_resolution_time,
                        "satisfaction_score": tech.satisfaction_score,
                    }
                    for tech in metrics.technician_ranking
                ],
                "tendencias": {
                    trend_name: [
                        {
                            "date": data.date.isoformat(),
                            "value": data.value,
                            "label": data.label,
                        }
                        for data in trend_data
                    ]
                    for trend_name, trend_data in metrics.trends.items()
                },
                "system_status": metrics.system_status,
                "last_updated": metrics.last_updated.isoformat(),
                "total_tickets": metrics.get_total_tickets(),
                "resolution_rate": metrics.get_resolution_rate(),
            }

            return ResponseFormatter.format_success_response(
                data=response_data, message="KPIs obtidos com sucesso"
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar KPIs: {str(e)}")
