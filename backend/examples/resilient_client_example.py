#!/usr/bin/env python3
"""
Exemplo prático de uso do Cliente GLPI Resiliente

Este exemplo demonstra como usar o cliente resiliente para:
1. Buscar tickets com filtros e paginação
2. Obter métricas agregadas por período
3. Monitorar métricas de resiliência
4. Tratar erros de forma robusta
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from adapters.glpi.resilient_client import create_glpi_client, GLPIClientConfig
from adapters.glpi.pagination import (
    TicketFilters,
    PaginationParams,
    TicketStatus,
    TicketPriority,
    DateRange,
    SortParams,
    SortOrder,
)
from usecases.aggregated_metrics import AggregatedMetricsUseCase, MetricPeriod
from utils.metrics import get_metrics

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GLPIExample:
    """Exemplo de uso do cliente GLPI resiliente"""

    def __init__(self):
        # Configuração do cliente (usando dados mock para desenvolvimento)
        self.client = create_glpi_client(
            base_url="http://localhost:8000/mock/glpi",  # Mock para desenvolvimento
            app_token="mock_app_token",
            user_token="mock_user_token",
            config=GLPIClientConfig(request_timeout=30, session_timeout=3600),
        )

        self.metrics_usecase = AggregatedMetricsUseCase(self.client)

    async def example_1_basic_ticket_search(self) -> List[Dict[str, Any]]:
        """
        Exemplo 1: Busca básica de tickets com filtros
        """
        logger.info("=== Exemplo 1: Busca básica de tickets ===")

        try:
            # Definir filtros para tickets dos últimos 7 dias
            filters = TicketFilters(
                status=[TicketStatus.NEW, TicketStatus.ASSIGNED, TicketStatus.PLANNED],
                priority=[TicketPriority.HIGH, TicketPriority.CRITICAL],
                date_range=DateRange(
                    start=datetime.now() - timedelta(days=7), end=datetime.now()
                ),
            )

            # Configurar paginação
            pagination = PaginationParams(page=1, page_size=20)

            # Configurar ordenação
            sort = SortParams(field="date_creation", order=SortOrder.DESC)

            # Buscar tickets
            response = await self.client.get_tickets(
                filters=filters, pagination=pagination, sort=sort
            )

            logger.info(f"Encontrados {len(response.data)} tickets")
            logger.info(
                f"Total: {response.total}, Página: {response.page}/{response.total_pages}"
            )

            # Exibir alguns tickets
            for ticket in response.data[:3]:
                logger.info(
                    f"Ticket #{ticket.get('id')}: {ticket.get('name')} - Status: {ticket.get('status')}"
                )

            return response.data

        except Exception as e:
            logger.error(f"Erro ao buscar tickets: {e}")
            return []

    async def example_2_paginated_search(self) -> List[Dict[str, Any]]:
        """
        Exemplo 2: Busca paginada completa
        """
        logger.info("=== Exemplo 2: Busca paginada completa ===")

        all_tickets = []
        page = 1
        page_size = 50

        try:
            while True:
                # Buscar página atual
                pagination = PaginationParams(page=page, page_size=page_size)

                response = await self.client.get_tickets(pagination=pagination)

                if not response.data:
                    break

                all_tickets.extend(response.data)
                logger.info(f"Página {page}: {len(response.data)} tickets")

                # Verificar se há mais páginas
                if page >= response.total_pages:
                    break

                page += 1

                # Evitar sobrecarga (em produção, remover este delay)
                await asyncio.sleep(0.1)

            logger.info(f"Total de tickets coletados: {len(all_tickets)}")
            return all_tickets

        except Exception as e:
            logger.error(f"Erro na busca paginada: {e}")
            return all_tickets

    async def example_3_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Exemplo 3: Métricas agregadas por período
        """
        logger.info("=== Exemplo 3: Métricas agregadas ===")

        try:
            today = datetime.now().date()

            # Métricas diárias (N1)
            daily_metrics = await self.metrics_usecase.get_daily_metrics(date=today)
            logger.info(f"Métricas diárias: {daily_metrics.total_tickets} tickets")

            # Métricas semanais (N2)
            week_start = today - timedelta(days=today.weekday())
            weekly_metrics = await self.metrics_usecase.get_weekly_metrics(
                week_start=week_start
            )
            logger.info(f"Métricas semanais: {weekly_metrics.total_tickets} tickets")

            # Métricas mensais (N3)
            month_start = today.replace(day=1)
            monthly_metrics = await self.metrics_usecase.get_monthly_metrics(
                month=month_start
            )
            logger.info(f"Métricas mensais: {monthly_metrics.total_tickets} tickets")

            # Comparativo (N4)
            comparative = await self.metrics_usecase.get_comparative_metrics(
                current_period=MetricPeriod.WEEKLY, periods_back=4
            )
            logger.info(f"Tendência semanal: {comparative.trend}")

            return {
                "daily": daily_metrics.dict(),
                "weekly": weekly_metrics.dict(),
                "monthly": monthly_metrics.dict(),
                "comparative": comparative.dict(),
            }

        except Exception as e:
            logger.error(f"Erro ao obter métricas agregadas: {e}")
            return {}

    async def example_4_resilience_monitoring(self) -> Dict[str, Any]:
        """
        Exemplo 4: Monitoramento de resiliência
        """
        logger.info("=== Exemplo 4: Monitoramento de resiliência ===")

        try:
            # Obter métricas do sistema
            metrics = get_metrics()
            summary = metrics.get_summary()

            logger.info("=== Métricas de Resiliência ===")
            logger.info(f"Total de requisições: {summary.get('total_requests', 0)}")
            logger.info(f"Taxa de sucesso: {summary.get('success_rate', 0):.2%}")
            logger.info(f"Latência média: {summary.get('avg_latency', 0):.3f}s")
            logger.info(
                f"Circuit breaker: {summary.get('circuit_breaker_state', 'unknown')}"
            )
            logger.info(f"Sessões ativas: {summary.get('active_sessions', 0)}")
            logger.info(f"Total de retries: {summary.get('total_retries', 0)}")

            # Verificar saúde do sistema
            health_status = "healthy"

            if summary.get("success_rate", 1) < 0.95:
                health_status = "degraded"
                logger.warning("Taxa de sucesso baixa detectada")

            if summary.get("circuit_breaker_state") == "open":
                health_status = "unhealthy"
                logger.error("Circuit breaker aberto")

            if summary.get("avg_latency", 0) > 5.0:
                health_status = "degraded"
                logger.warning("Latência alta detectada")

            logger.info(f"Status geral: {health_status}")

            return {"metrics": summary, "health_status": health_status}

        except Exception as e:
            logger.error(f"Erro ao monitorar resiliência: {e}")
            return {"health_status": "error"}

    async def example_5_error_handling(self) -> Dict[str, Any]:
        """
        Exemplo 5: Tratamento robusto de erros
        """
        logger.info("=== Exemplo 5: Tratamento de erros ===")

        results = {"successful_operations": 0, "failed_operations": 0, "errors": []}

        # Simular várias operações com possíveis falhas
        operations = [
            ("buscar_tickets_novos", self._search_new_tickets),
            ("buscar_tickets_criticos", self._search_critical_tickets),
            ("obter_metricas_diarias", self._get_daily_metrics),
            ("buscar_tickets_invalidos", self._search_invalid_tickets),  # Deve falhar
        ]

        for operation_name, operation_func in operations:
            try:
                logger.info(f"Executando: {operation_name}")
                result = await operation_func()

                if result:
                    results["successful_operations"] += 1
                    logger.info(f"✓ {operation_name} executada com sucesso")
                else:
                    results["failed_operations"] += 1
                    logger.warning(f"⚠ {operation_name} retornou resultado vazio")

            except Exception as e:
                results["failed_operations"] += 1
                error_info = {
                    "operation": operation_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
                results["errors"].append(error_info)
                logger.error(f"✗ {operation_name} falhou: {e}")

        logger.info(
            f"Resumo: {results['successful_operations']} sucessos, {results['failed_operations']} falhas"
        )
        return results

    # Métodos auxiliares para o exemplo 5
    async def _search_new_tickets(self) -> List[Dict[str, Any]]:
        filters = TicketFilters(status=[TicketStatus.NEW])
        response = await self.client.get_tickets(filters=filters)
        return response.data

    async def _search_critical_tickets(self) -> List[Dict[str, Any]]:
        filters = TicketFilters(priority=[TicketPriority.CRITICAL])
        response = await self.client.get_tickets(filters=filters)
        return response.data

    async def _get_daily_metrics(self) -> Dict[str, Any]:
        metrics = await self.metrics_usecase.get_daily_metrics(datetime.now().date())
        return metrics.dict()

    async def _search_invalid_tickets(self) -> List[Dict[str, Any]]:
        # Esta operação deve falhar propositalmente
        raise ValueError("Filtro inválido simulado")

    async def run_all_examples(self):
        """
        Executa todos os exemplos em sequência
        """
        logger.info("🚀 Iniciando exemplos do Cliente GLPI Resiliente")

        try:
            # Exemplo 1: Busca básica
            await self.example_1_basic_ticket_search()
            await asyncio.sleep(1)

            # Exemplo 2: Busca paginada
            await self.example_2_paginated_search()
            await asyncio.sleep(1)

            # Exemplo 3: Métricas agregadas
            await self.example_3_aggregated_metrics()
            await asyncio.sleep(1)

            # Exemplo 4: Monitoramento
            await self.example_4_resilience_monitoring()
            await asyncio.sleep(1)

            # Exemplo 5: Tratamento de erros
            await self.example_5_error_handling()

            logger.info("✅ Todos os exemplos executados com sucesso")

        except Exception as e:
            logger.error(f"❌ Erro durante execução dos exemplos: {e}")

        finally:
            # Fechar cliente
            await self.client.close()
            logger.info("🔒 Cliente GLPI fechado")


async def main():
    """
    Função principal para executar os exemplos
    """
    example = GLPIExample()
    await example.run_all_examples()


if __name__ == "__main__":
    # Executar exemplos
    asyncio.run(main())
