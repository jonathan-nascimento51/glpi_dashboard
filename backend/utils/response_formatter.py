from typing import Any, Dict, List, Optional
from datetime import datetime
import time


class ResponseFormatter:
    """Utilitário para formatação unificada das respostas da API"""

    @staticmethod
    def format_dashboard_response(
        raw_metrics: Dict,
        filters: Optional[Dict] = None,
        start_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Formata resposta das métricas do dashboard de forma unificada"""
        try:
            # Calcular tempo de execução se fornecido
            execution_time = None
            if start_time:
                execution_time = (time.time() - start_time) * 1000

            # Processar dados dos níveis
            niveis_data = {}

            # Se há estrutura by_level (com filtros)
            if raw_metrics and "by_level" in raw_metrics:
                for level_name, level_data in raw_metrics["by_level"].items():
                    level_key = level_name.lower()
                    niveis_data[level_key] = {
                        "novos": level_data.get("Novo", 0),
                        "pendentes": level_data.get("Pendente", 0),
                        "progresso": (
                            level_data.get("Processando (atribuído)", 0)
                            + level_data.get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            level_data.get("Solucionado", 0)
                            + level_data.get("Fechado", 0)
                        ),
                    }

            # Se há estrutura niveis (sem filtros)
            elif raw_metrics and "niveis" in raw_metrics:
                for level_name, level_data in raw_metrics["niveis"].items():
                    niveis_data[level_name] = level_data

            # Garantir que todos os níveis existam
            for level in ["n1", "n2", "n3", "n4"]:
                if level not in niveis_data:
                    niveis_data[level] = {
                        "novos": 0,
                        "pendentes": 0,
                        "progresso": 0,
                        "resolvidos": 0,
                        "total": 0,
                    }
                else:
                    # Calcular total para cada nível
                    level_data = niveis_data[level]
                    level_data["total"] = (
                        level_data.get("novos", 0)
                        + level_data.get("pendentes", 0)
                        + level_data.get("progresso", 0)
                        + level_data.get("resolvidos", 0)
                    )

            # Extrair totais gerais
            if raw_metrics and "general" in raw_metrics:
                # Com filtros - usar dados gerais
                general = raw_metrics["general"]
                novos = general.get("Novo", 0)
                pendentes = general.get("Pendente", 0)
                progresso = general.get("Processando (atribuído)", 0) + general.get(
                    "Processando (planejado)", 0
                )
                resolvidos = general.get("Solucionado", 0) + general.get("Fechado", 0)
            else:
                # Sem filtros - calcular dos níveis
                novos = sum(level.get("novos", 0) for level in niveis_data.values())
                pendentes = sum(
                    level.get("pendentes", 0) for level in niveis_data.values()
                )
                progresso = sum(
                    level.get("progresso", 0) for level in niveis_data.values()
                )
                resolvidos = sum(
                    level.get("resolvidos", 0) for level in niveis_data.values()
                )

            total = novos + pendentes + progresso + resolvidos

            # Adicionar totais gerais aos níveis
            niveis_data["geral"] = {
                "novos": novos,
                "pendentes": pendentes,
                "progresso": progresso,
                "resolvidos": resolvidos,
                "total": total,
            }

            # Criar resposta
            response = {
                "success": True,
                "data": {
                    "niveis": niveis_data,
                    "tendencias": {
                        "novos_hoje": 0,
                        "resolvidos_hoje": 0,
                        "pendencias_ontem": 0,
                        "variacao_pendentes": 0,
                    },
                },
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            if execution_time:
                response["tempo_execucao"] = execution_time

            if filters:
                response["data"]["filtros_aplicados"] = filters

            return response

        except Exception as e:
            return ResponseFormatter.format_error_response(
                message="Erro ao formatar métricas do dashboard", errors=[str(e)]
            )

    @staticmethod
    def format_error_response(
        message: str, errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Formata resposta de erro de forma unificada"""
        return {
            "success": False,
            "message": message,
            "errors": errors or [],
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    @staticmethod
    def format_success_response(
        data: Any, message: str = "Operação realizada com sucesso"
    ) -> Dict[str, Any]:
        """Formata resposta de sucesso de forma unificada"""
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
