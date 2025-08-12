# -*- coding: utf-8 -*-
"""Use case para metricas consolidadas por nivel com deteccao de anomalias"""

from datetime import datetime
from typing import Dict, List, Any
import statistics
from dataclasses import dataclass

from schemas.metrics_levels import (
    MetricsLevelsQueryParams,
    MetricsLevelsResponse,
    MetricsByLevel,
    AggregatedMetrics,
    ServiceLevel,
    StatusFilter,
)
from utils.structured_logger import create_glpi_logger


@dataclass
class MetricsLevelsUseCase:
    """Use case para processamento de metricas por nivel de servico"""

    def __init__(self):
        self.logger = create_glpi_logger("INFO")

    async def get_metrics_by_level(
        self, params: MetricsLevelsQueryParams
    ) -> MetricsLevelsResponse:
        """Obtem metricas consolidadas por nivel de servico"""
        try:
            self.logger.info("Iniciando processamento de metricas por nivel")

            # Simular dados para demonstracao
            metrics_data = self._generate_sample_metrics(params)

            # Detectar anomalias se threshold fornecido
            if params.include_anomalies:
                metrics_data = self._detect_anomalies(
                    metrics_data, params.zscore_threshold
                )

            # Calcular metricas agregadas
            aggregated = self._calculate_aggregated_metrics(metrics_data)

            response = MetricsLevelsResponse(
                metrics_by_level=metrics_data,
                aggregated_metrics=aggregated,
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "query_params": params.dict(),
                    "total_levels_processed": len(metrics_data),
                },
                period_analyzed={
                    "start_date": params.start_date.isoformat()
                    if params.start_date
                    else None,
                    "end_date": params.end_date.isoformat()
                    if params.end_date
                    else None,
                    "days_analyzed": 30,  # default
                },
            )

            self.logger.info(
                f"Processamento concluido: {len(metrics_data)} niveis processados"
            )
            return response

        except Exception as e:
            self.logger.error(f"Erro ao processar metricas por nivel: {str(e)}")
            raise

    def _generate_sample_metrics(
        self, params: MetricsLevelsQueryParams
    ) -> List[MetricsByLevel]:
        """Gera dados de exemplo para demonstracao"""
        sample_data = [
            MetricsByLevel(
                level=ServiceLevel.N1,
                total_tickets=150,
                open_tickets=45,
                closed_tickets=95,
                pending_tickets=10,
                avg_resolution_time_hours=2.5,
                sla_compliance_rate=0.92,
                is_anomaly=False,
            ),
            MetricsByLevel(
                level=ServiceLevel.N2,
                total_tickets=89,
                open_tickets=23,
                closed_tickets=60,
                pending_tickets=6,
                avg_resolution_time_hours=4.2,
                sla_compliance_rate=0.88,
                is_anomaly=False,
            ),
            MetricsByLevel(
                level=ServiceLevel.N3,
                total_tickets=34,
                open_tickets=12,
                closed_tickets=20,
                pending_tickets=2,
                avg_resolution_time_hours=8.7,
                sla_compliance_rate=0.85,
                is_anomaly=False,
            ),
            MetricsByLevel(
                level=ServiceLevel.N4,
                total_tickets=12,
                open_tickets=5,
                closed_tickets=6,
                pending_tickets=1,
                avg_resolution_time_hours=15.3,
                sla_compliance_rate=0.75,
                is_anomaly=False,
            ),
        ]

        # Filtrar por status se especificado
        if params.status and params.status != StatusFilter.ALL:
            # Aplicar filtro de status (implementacao simplificada)
            pass

        return sample_data

    def _detect_anomalies(
        self, metrics: List[MetricsByLevel], threshold: float
    ) -> List[MetricsByLevel]:
        """Detecta anomalias usando Z-score"""
        if len(metrics) < 2:
            return metrics

        # Calcular Z-score para tempo de resolucao
        resolution_times = [m.avg_resolution_time_hours for m in metrics]
        mean_time = statistics.mean(resolution_times)
        std_time = (
            statistics.stdev(resolution_times) if len(resolution_times) > 1 else 0
        )

        for metric in metrics:
            if std_time > 0:
                z_score = abs((metric.avg_resolution_time_hours - mean_time) / std_time)
                metric.is_anomaly = z_score > threshold
                metric.anomaly_score = z_score

        return metrics

    def _calculate_aggregated_metrics(
        self, metrics: List[MetricsByLevel]
    ) -> AggregatedMetrics:
        """Calcula metricas agregadas"""
        total_tickets = sum(m.total_tickets for m in metrics)

        avg_resolution = (
            statistics.mean([m.avg_resolution_time_hours for m in metrics])
            if metrics
            else 0
        )
        avg_sla = (
            statistics.mean([m.sla_compliance_rate for m in metrics]) if metrics else 0
        )

        anomalies_count = sum(1 for m in metrics if m.is_anomaly)

        # Determinar tendencia (simplificado)
        performance_trend = "stable"
        if avg_sla > 0.9:
            performance_trend = "improving"
        elif avg_sla < 0.8:
            performance_trend = "declining"

        return AggregatedMetrics(
            total_tickets_all_levels=total_tickets,
            avg_resolution_time_all_levels=round(avg_resolution, 2),
            overall_sla_compliance=round(avg_sla, 3),
            anomalies_detected=anomalies_count,
            performance_trend=performance_trend,
        )

    async def health_check(self) -> Dict[str, Any]:
        """Verifica a saude do servico"""
        try:
            # Teste basico de funcionamento
            test_params = MetricsLevelsQueryParams()
            await self.get_metrics_by_level(test_params)

            return {
                "status": "healthy",
                "service": "metrics-levels",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Health check falhou: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "metrics-levels",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
