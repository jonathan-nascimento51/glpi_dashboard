#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Comparador de Regressão para Métricas GLPI Dashboard

Este script compara JSONs de métricas para detectar divergências campo a campo,
identificando regressões em funcionalidades após mudanças no código.
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Adicionar diretório backend ao path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from utils.structured_logger import StructuredLogger


@dataclass
class ComparisonResult:
    """Resultado de uma comparação entre dois valores"""

    field_path: str
    expected_value: Any
    actual_value: Any
    match: bool
    difference_type: str
    tolerance_applied: bool = False


@dataclass
class RegressionReport:
    """Relatório completo de regressão"""

    test_name: str
    timestamp: datetime
    total_comparisons: int
    passed_comparisons: int
    failed_comparisons: int
    differences: List[ComparisonResult]
    success: bool
    execution_time: float


class MetricsRegressionComparator:
    """Comparador de regressão para métricas do dashboard GLPI"""

    def __init__(self, base_url: str = "http://localhost:5000/api", tolerance: float = 0.05):
        self.base_url = base_url
        self.tolerance = tolerance  # Tolerância para comparações numéricas (5%)
        self.logger = StructuredLogger("MetricsRegressionComparator")
        self.snapshots_dir = Path(__file__).parent / "snapshots"
        self.reports_dir = Path(__file__).parent / "reports"

        # Criar diretórios se não existirem
        self.snapshots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def capture_baseline_snapshot(self, endpoint: str, params: Dict = None, snapshot_name: str = None) -> str:
        """Captura um snapshot baseline da API para comparação futura"""
        try:
            self.logger.info(f"Capturando snapshot baseline para {endpoint}")

            # Fazer requisição à API
            response = requests.get(f"{self.base_url}{endpoint}", params=params or {}, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Gerar nome do snapshot se não fornecido
            if not snapshot_name:
                endpoint_clean = endpoint.replace("/", "_").replace("?", "_")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot_name = f"baseline_{endpoint_clean}_{timestamp}.json"

            # Salvar snapshot
            snapshot_path = self.snapshots_dir / snapshot_name
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "metadata": {
                            "endpoint": endpoint,
                            "params": params,
                            "timestamp": datetime.now().isoformat(),
                            "response_status": response.status_code,
                            "response_time": response.elapsed.total_seconds(),
                        },
                        "data": data,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            self.logger.info(f"Snapshot salvo: {snapshot_path}")
            return str(snapshot_path)

        except Exception as e:
            self.logger.error(f"Erro ao capturar snapshot: {e}")
            raise

    def load_snapshot(self, snapshot_path: str) -> Dict:
        """Carrega um snapshot salvo"""
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar snapshot {snapshot_path}: {e}")
            raise

    def compare_values(self, field_path: str, expected: Any, actual: Any) -> ComparisonResult:
        """Compara dois valores com tolerância para números"""
        tolerance_applied = False

        # Comparação exata para tipos diferentes
        if type(expected) != type(actual):
            return ComparisonResult(
                field_path=field_path,
                expected_value=expected,
                actual_value=actual,
                match=False,
                difference_type="type_mismatch",
            )

        # Comparação numérica com tolerância
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if expected == 0:
                match = actual == 0
            else:
                diff_percentage = abs(expected - actual) / abs(expected)
                match = diff_percentage <= self.tolerance
                tolerance_applied = True

            return ComparisonResult(
                field_path=field_path,
                expected_value=expected,
                actual_value=actual,
                match=match,
                difference_type="numeric" if not match else "none",
                tolerance_applied=tolerance_applied,
            )

        # Comparação exata para outros tipos
        match = expected == actual
        return ComparisonResult(
            field_path=field_path,
            expected_value=expected,
            actual_value=actual,
            match=match,
            difference_type="value_mismatch" if not match else "none",
        )

    def compare_structures(self, expected: Any, actual: Any, path: str = "") -> List[ComparisonResult]:
        """Compara estruturas de dados recursivamente"""
        results = []

        # Comparar tipos
        if type(expected) != type(actual):
            results.append(
                ComparisonResult(
                    field_path=path,
                    expected_value=type(expected).__name__,
                    actual_value=type(actual).__name__,
                    match=False,
                    difference_type="structure_type_mismatch",
                )
            )
            return results

        # Comparar dicionários
        if isinstance(expected, dict):
            # Verificar chaves ausentes ou extras
            expected_keys = set(expected.keys())
            actual_keys = set(actual.keys())

            missing_keys = expected_keys - actual_keys
            extra_keys = actual_keys - expected_keys

            for key in missing_keys:
                results.append(
                    ComparisonResult(
                        field_path=f"{path}.{key}" if path else key,
                        expected_value="<present>",
                        actual_value="<missing>",
                        match=False,
                        difference_type="missing_key",
                    )
                )

            for key in extra_keys:
                results.append(
                    ComparisonResult(
                        field_path=f"{path}.{key}" if path else key,
                        expected_value="<missing>",
                        actual_value="<present>",
                        match=False,
                        difference_type="extra_key",
                    )
                )

            # Comparar valores das chaves comuns
            common_keys = expected_keys & actual_keys
            for key in common_keys:
                new_path = f"{path}.{key}" if path else key
                results.extend(self.compare_structures(expected[key], actual[key], new_path))

        # Comparar listas
        elif isinstance(expected, list):
            if len(expected) != len(actual):
                results.append(
                    ComparisonResult(
                        field_path=f"{path}.length",
                        expected_value=len(expected),
                        actual_value=len(actual),
                        match=False,
                        difference_type="list_length_mismatch",
                    )
                )

            # Comparar elementos (até o menor tamanho)
            min_length = min(len(expected), len(actual))
            for i in range(min_length):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                results.extend(self.compare_structures(expected[i], actual[i], new_path))

        # Comparar valores primitivos
        else:
            results.append(self.compare_values(path, expected, actual))

        return results

    def run_regression_test(
        self,
        snapshot_path: str,
        endpoint: str,
        params: Dict = None,
        test_name: str = None,
    ) -> RegressionReport:
        """Executa um teste de regressão comparando com snapshot"""
        start_time = time.time()

        try:
            self.logger.info(f"Iniciando teste de regressão: {test_name or endpoint}")

            # Carregar snapshot baseline
            snapshot = self.load_snapshot(snapshot_path)
            expected_data = snapshot["data"]

            # Capturar dados atuais da API
            response = requests.get(f"{self.base_url}{endpoint}", params=params or {}, timeout=30)
            response.raise_for_status()
            actual_data = response.json()

            # Comparar estruturas
            differences = self.compare_structures(expected_data, actual_data)

            # Calcular estatísticas
            total_comparisons = len(differences)
            failed_comparisons = len([d for d in differences if not d.match])
            passed_comparisons = total_comparisons - failed_comparisons

            execution_time = time.time() - start_time

            # Criar relatório
            report = RegressionReport(
                test_name=test_name or f"regression_{endpoint.replace('/', '_')}",
                timestamp=datetime.now(),
                total_comparisons=total_comparisons,
                passed_comparisons=passed_comparisons,
                failed_comparisons=failed_comparisons,
                differences=differences,
                success=failed_comparisons == 0,
                execution_time=execution_time,
            )

            self.logger.info(f"Teste concluído: {passed_comparisons}/{total_comparisons} comparações passaram")
            return report

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erro no teste de regressão: {e}")

            return RegressionReport(
                test_name=test_name or f"regression_{endpoint.replace('/', '_')}",
                timestamp=datetime.now(),
                total_comparisons=0,
                passed_comparisons=0,
                failed_comparisons=1,
                differences=[
                    ComparisonResult(
                        field_path="test_execution",
                        expected_value="success",
                        actual_value=str(e),
                        match=False,
                        difference_type="execution_error",
                    )
                ],
                success=False,
                execution_time=execution_time,
            )

    def save_report(self, report: RegressionReport, filename: str = None) -> str:
        """Salva relatório de regressão"""
        if not filename:
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"regression_report_{report.test_name}_{timestamp}.json"

        report_path = self.reports_dir / filename

        # Converter relatório para dict serializável
        report_dict = {
            "test_name": report.test_name,
            "timestamp": report.timestamp.isoformat(),
            "summary": {
                "total_comparisons": report.total_comparisons,
                "passed_comparisons": report.passed_comparisons,
                "failed_comparisons": report.failed_comparisons,
                "success": report.success,
                "execution_time": report.execution_time,
            },
            "differences": [
                {
                    "field_path": diff.field_path,
                    "expected_value": diff.expected_value,
                    "actual_value": diff.actual_value,
                    "match": diff.match,
                    "difference_type": diff.difference_type,
                    "tolerance_applied": diff.tolerance_applied,
                }
                for diff in report.differences
                if not diff.match
            ],
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Relatório salvo: {report_path}")
        return str(report_path)

    def print_report_summary(self, report: RegressionReport):
        """Imprime resumo do relatório"""
        print(f"\n{'='*60}")
        print(f"RELATÓRIO DE REGRESSÃO: {report.test_name}")
        print(f"{'='*60}")
        print(f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tempo de execução: {report.execution_time:.2f}s")
        print(f"\n📊 RESUMO:")
        print(f"  Total de comparações: {report.total_comparisons}")
        print(f"  Comparações aprovadas: {report.passed_comparisons}")
        print(f"  Comparações falharam: {report.failed_comparisons}")
        print(f"  Resultado: {'✅ SUCESSO' if report.success else '❌ FALHA'}")

        if report.failed_comparisons > 0:
            print(f"\n🔍 DIFERENÇAS ENCONTRADAS:")
            for diff in report.differences:
                if not diff.match:
                    print(f"  • {diff.field_path}:")
                    print(f"    Esperado: {diff.expected_value}")
                    print(f"    Atual: {diff.actual_value}")
                    print(f"    Tipo: {diff.difference_type}")
                    if diff.tolerance_applied:
                        print(f"    Tolerância aplicada: {self.tolerance*100}%")
                    print()


def main():
    """Função principal para execução via linha de comando"""
    parser = argparse.ArgumentParser(description="Comparador de Regressão para Métricas GLPI")
    parser.add_argument(
        "--action",
        choices=["capture", "test", "batch"],
        required=True,
        help="Ação a executar: capture (capturar baseline), test (testar regressão), batch (testes em lote)",
    )
    parser.add_argument("--endpoint", help="Endpoint da API para testar")
    parser.add_argument("--snapshot", help="Caminho do snapshot para comparação")
    parser.add_argument("--name", help="Nome do teste")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.05,
        help="Tolerância para comparações numéricas (padrão: 0.05)",
    )
    parser.add_argument("--base-url", default="http://localhost:5000/api", help="URL base da API")

    args = parser.parse_args()

    comparator = MetricsRegressionComparator(base_url=args.base_url, tolerance=args.tolerance)

    if args.action == "capture":
        if not args.endpoint:
            print("❌ Endpoint é obrigatório para capturar snapshot")
            sys.exit(1)

        snapshot_path = comparator.capture_baseline_snapshot(args.endpoint, snapshot_name=args.name)
        print(f"✅ Snapshot capturado: {snapshot_path}")

    elif args.action == "test":
        if not args.endpoint or not args.snapshot:
            print("❌ Endpoint e snapshot são obrigatórios para teste de regressão")
            sys.exit(1)

        report = comparator.run_regression_test(args.snapshot, args.endpoint, test_name=args.name)
        comparator.print_report_summary(report)
        report_path = comparator.save_report(report)
        print(f"\n📄 Relatório salvo: {report_path}")

        sys.exit(0 if report.success else 1)

    elif args.action == "batch":
        # Executar testes em lote para endpoints principais
        endpoints = [
            {"endpoint": "/metrics", "name": "dashboard_metrics", "params": {}},
            {
                "endpoint": "/metrics/filtered",
                "name": "filtered_metrics",
                "params": {"status": "novo"},
            },
            {
                "endpoint": "/technicians/ranking",
                "name": "technician_ranking",
                "params": {"limit": 10},
            },
        ]

        all_success = True

        for endpoint_config in endpoints:
            print(f"\n🔄 Testando {endpoint_config['name']}...")

            # Procurar snapshot existente
            snapshot_pattern = f"baseline_{endpoint_config['name']}_*.json"
            snapshots = list(comparator.snapshots_dir.glob(snapshot_pattern))

            if not snapshots:
                print(f"⚠️  Nenhum snapshot encontrado para {endpoint_config['name']}. Capturando baseline...")
                snapshot_path = comparator.capture_baseline_snapshot(
                    endpoint_config["endpoint"],
                    endpoint_config["params"],
                    f"baseline_{endpoint_config['name']}.json",
                )
            else:
                # Usar o snapshot mais recente
                snapshot_path = str(max(snapshots, key=os.path.getctime))
                print(f"📁 Usando snapshot: {snapshot_path}")

            # Executar teste
            report = comparator.run_regression_test(
                snapshot_path,
                endpoint_config["endpoint"],
                endpoint_config["params"],
                endpoint_config["name"],
            )

            comparator.print_report_summary(report)
            comparator.save_report(report)

            if not report.success:
                all_success = False

        print(f"\n{'='*60}")
        print(f"RESULTADO GERAL: {'✅ TODOS OS TESTES PASSARAM' if all_success else '❌ ALGUNS TESTES FALHARAM'}")
        print(f"{'='*60}")

        sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
