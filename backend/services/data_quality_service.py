"""Serviço de qualidade de dados para GLPI Dashboard.

Este módulo implementa validadores de consistência para detectar:
- Dados all-zero (todos os valores zerados)
- Picos anômalos nos dados
- Inconsistências temporais
- Dados faltantes ou corrompidos
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DataQualityLevel(Enum):
    """Níveis de qualidade dos dados."""

    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"


@dataclass
class DataQualityIssue:
    """Representa um problema de qualidade de dados."""

    type: str
    severity: DataQualityLevel
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class DataQualityReport:
    """Relatório de qualidade dos dados."""

    overall_quality: DataQualityLevel
    issues: List[DataQualityIssue]
    metrics: Dict[str, Any]
    timestamp: datetime
    all_zero_detected: bool = False
    anomalies_detected: bool = False

    @property
    def is_healthy(self) -> bool:
        """Retorna True se os dados estão saudáveis."""
        return self.overall_quality in [
            DataQualityLevel.EXCELLENT,
            DataQualityLevel.GOOD,
        ]

    @property
    def has_critical_issues(self) -> bool:
        """Retorna True se há problemas críticos."""
        return any(
            issue.severity in [DataQualityLevel.CRITICAL, DataQualityLevel.FAILED]
            for issue in self.issues
        )


class DataQualityService:
    """Serviço para validação de qualidade dos dados do GLPI."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._historical_data = []
        self._anomaly_threshold = 3.0  # Desvios padrão para detectar anomalias

    def validate_data_quality(self, data: Dict[str, Any]) -> DataQualityReport:
        """Valida a qualidade dos dados e retorna um relatório.

        Args:
            data: Dados a serem validados (ex: métricas de tickets)

        Returns:
            DataQualityReport: Relatório com problemas encontrados
        """
        self.logger.info("Iniciando validação de qualidade dos dados")

        issues = []
        metrics = {}

        # Validação 1: Detectar dados all-zero
        all_zero_issues = self._validate_all_zero(data)
        issues.extend(all_zero_issues)

        # Validação 2: Detectar picos anômalos
        anomaly_issues = self._validate_anomalies(data)
        issues.extend(anomaly_issues)

        # Validação 3: Validar consistência temporal
        temporal_issues = self._validate_temporal_consistency(data)
        issues.extend(temporal_issues)

        # Validação 4: Validar integridade dos dados
        integrity_issues = self._validate_data_integrity(data)
        issues.extend(integrity_issues)

        # Calcular métricas de qualidade
        metrics = self._calculate_quality_metrics(data, issues)

        # Determinar qualidade geral
        overall_quality = self._determine_overall_quality(issues)

        # Detectar flags específicos
        all_zero_detected = any(issue.type == "all_zero" for issue in issues)
        anomalies_detected = any(issue.type == "anomaly" for issue in issues)

        report = DataQualityReport(
            overall_quality=overall_quality,
            issues=issues,
            metrics=metrics,
            timestamp=datetime.now(),
            all_zero_detected=all_zero_detected,
            anomalies_detected=anomalies_detected,
        )

        self.logger.info(
            f"Validação concluída. Qualidade: {overall_quality.value}, "
            f"Problemas encontrados: {len(issues)}"
        )

        return report

    def _validate_all_zero(self, data: Dict[str, Any]) -> List[DataQualityIssue]:
        """Detecta se todos os valores numéricos estão zerados.

        Args:
            data: Dados a serem validados

        Returns:
            List[DataQualityIssue]: Lista de problemas encontrados
        """
        issues = []

        # Extrair valores numéricos dos dados
        numeric_values = self._extract_numeric_values(data)

        if not numeric_values:
            issues.append(
                DataQualityIssue(
                    type="no_data",
                    severity=DataQualityLevel.CRITICAL,
                    message="Nenhum dado numérico encontrado",
                )
            )
            return issues

        # Verificar se todos os valores são zero
        all_zero = all(value == 0 for value in numeric_values)

        if all_zero:
            issues.append(
                DataQualityIssue(
                    type="all_zero",
                    severity=DataQualityLevel.CRITICAL,
                    message=f"Todos os {len(numeric_values)} valores numéricos estão zerados",
                    value=numeric_values,
                )
            )
            self.logger.warning("Detectado problema all-zero nos dados")

        return issues

    def _validate_anomalies(self, data: Dict[str, Any]) -> List[DataQualityIssue]:
        """Detecta picos anômalos nos dados.

        Args:
            data: Dados a serem validados

        Returns:
            List[DataQualityIssue]: Lista de problemas encontrados
        """
        issues = []

        # Extrair valores numéricos
        numeric_values = self._extract_numeric_values(data)

        if len(numeric_values) < 3:
            return issues  # Não há dados suficientes para detectar anomalias

        try:
            mean_val = statistics.mean(numeric_values)
            stdev_val = statistics.stdev(numeric_values)

            if stdev_val == 0:
                return issues  # Todos os valores são iguais

            # Detectar valores que estão além do threshold de desvios padrão
            for i, value in enumerate(numeric_values):
                z_score = abs(value - mean_val) / stdev_val

                if z_score > self._anomaly_threshold:
                    severity = (
                        DataQualityLevel.WARNING
                        if z_score < 5.0
                        else DataQualityLevel.CRITICAL
                    )
                    issues.append(
                        DataQualityIssue(
                            type="anomaly",
                            severity=severity,
                            message=f"Valor anômalo detectado: {value} (z-score: {z_score:.2f})",
                            field=f"index_{i}",
                            value=value,
                        )
                    )

        except statistics.StatisticsError as e:
            self.logger.error(f"Erro ao calcular estatísticas: {e}")

        return issues

    def _validate_temporal_consistency(
        self, data: Dict[str, Any]
    ) -> List[DataQualityIssue]:
        """Valida consistência temporal dos dados.

        Args:
            data: Dados a serem validados

        Returns:
            List[DataQualityIssue]: Lista de problemas encontrados
        """
        issues = []

        # Verificar se há timestamps nos dados
        if "timestamp" in data or "data_inicio" in data:
            # Validar formato de data
            timestamp_fields = ["timestamp", "data_inicio", "data_fim", "last_update"]

            for field in timestamp_fields:
                if field in data:
                    try:
                        if isinstance(data[field], str):
                            # Tentar parsear diferentes formatos de data
                            datetime.fromisoformat(data[field].replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        issues.append(
                            DataQualityIssue(
                                type="invalid_timestamp",
                                severity=DataQualityLevel.WARNING,
                                message=f"Formato de timestamp inválido no campo {field}: {data[field]}",
                                field=field,
                                value=data[field],
                            )
                        )

        return issues

    def _validate_data_integrity(self, data: Dict[str, Any]) -> List[DataQualityIssue]:
        """Valida integridade geral dos dados.

        Args:
            data: Dados a serem validados

        Returns:
            List[DataQualityIssue]: Lista de problemas encontrados
        """
        issues = []

        # Verificar campos obrigatórios
        required_fields = ["total", "novos", "pendentes", "progresso", "resolvidos"]

        for field in required_fields:
            if field not in data:
                issues.append(
                    DataQualityIssue(
                        type="missing_field",
                        severity=DataQualityLevel.WARNING,
                        message=f"Campo obrigatório ausente: {field}",
                        field=field,
                    )
                )

        # Verificar consistência matemática (total deve ser soma das partes)
        if all(field in data for field in required_fields):
            try:
                calculated_total = (
                    data["novos"]
                    + data["pendentes"]
                    + data["progresso"]
                    + data["resolvidos"]
                )
                actual_total = data["total"]

                if calculated_total != actual_total:
                    issues.append(
                        DataQualityIssue(
                            type="inconsistent_totals",
                            severity=DataQualityLevel.WARNING,
                            message=f"Total inconsistente: calculado={calculated_total}, atual={actual_total}",
                            value={
                                "calculated": calculated_total,
                                "actual": actual_total,
                            },
                        )
                    )
            except (TypeError, KeyError) as e:
                issues.append(
                    DataQualityIssue(
                        type="calculation_error",
                        severity=DataQualityLevel.WARNING,
                        message=f"Erro ao validar totais: {e}",
                    )
                )

        return issues

    def _extract_numeric_values(self, data: Dict[str, Any]) -> List[float]:
        """Extrai todos os valores numéricos dos dados.

        Args:
            data: Dados a serem analisados

        Returns:
            List[float]: Lista de valores numéricos encontrados
        """
        numeric_values = []

        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    extract_recursive(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    extract_recursive(item, new_path)
            elif isinstance(obj, (int, float)):
                numeric_values.append(float(obj))

        extract_recursive(data)
        return numeric_values

    def _calculate_quality_metrics(
        self, data: Dict[str, Any], issues: List[DataQualityIssue]
    ) -> Dict[str, Any]:
        """Calcula métricas de qualidade dos dados.

        Args:
            data: Dados originais
            issues: Problemas encontrados

        Returns:
            Dict[str, Any]: Métricas calculadas
        """
        numeric_values = self._extract_numeric_values(data)

        metrics = {
            "total_fields": len(data),
            "numeric_fields": len(numeric_values),
            "total_issues": len(issues),
            "critical_issues": len(
                [i for i in issues if i.severity == DataQualityLevel.CRITICAL]
            ),
            "warning_issues": len(
                [i for i in issues if i.severity == DataQualityLevel.WARNING]
            ),
            "data_completeness": self._calculate_completeness(data),
            "numeric_summary": {
                "min": min(numeric_values) if numeric_values else None,
                "max": max(numeric_values) if numeric_values else None,
                "mean": statistics.mean(numeric_values) if numeric_values else None,
                "count": len(numeric_values),
            },
        }

        return metrics

    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calcula a completude dos dados (% de campos não nulos).

        Args:
            data: Dados a serem analisados

        Returns:
            float: Percentual de completude (0.0 a 1.0)
        """
        total_fields = 0
        non_null_fields = 0

        def count_recursive(obj):
            nonlocal total_fields, non_null_fields

            if isinstance(obj, dict):
                for value in obj.values():
                    count_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_recursive(item)
            else:
                total_fields += 1
                if obj is not None and obj != "":
                    non_null_fields += 1

        count_recursive(data)

        return non_null_fields / total_fields if total_fields > 0 else 0.0

    def _determine_overall_quality(
        self, issues: List[DataQualityIssue]
    ) -> DataQualityLevel:
        """Determina a qualidade geral baseada nos problemas encontrados.

        Args:
            issues: Lista de problemas encontrados

        Returns:
            DataQualityLevel: Nível de qualidade geral
        """
        if not issues:
            return DataQualityLevel.EXCELLENT

        # Contar problemas por severidade
        critical_count = len(
            [i for i in issues if i.severity == DataQualityLevel.CRITICAL]
        )
        warning_count = len(
            [i for i in issues if i.severity == DataQualityLevel.WARNING]
        )

        # Determinar qualidade baseada na severidade dos problemas
        if critical_count > 0:
            return DataQualityLevel.CRITICAL
        elif warning_count > 3:
            return DataQualityLevel.WARNING
        elif warning_count > 0:
            return DataQualityLevel.GOOD
        else:
            return DataQualityLevel.EXCELLENT

    def get_health_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna status de saúde dos dados para o endpoint /health/data.

        Args:
            data: Dados a serem validados

        Returns:
            Dict[str, Any]: Status de saúde formatado para API
        """
        report = self.validate_data_quality(data)

        return {
            "status": "ok" if report.is_healthy else "error",
            "quality_level": report.overall_quality.value,
            "all_zero": report.all_zero_detected,
            "anomalies": report.anomalies_detected,
            "issues_count": len(report.issues),
            "critical_issues": report.has_critical_issues,
            "timestamp": report.timestamp.isoformat(),
            "metrics": report.metrics,
            "issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "field": issue.field,
                }
                for issue in report.issues
            ],
        }
