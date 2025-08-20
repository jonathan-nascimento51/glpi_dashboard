#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de execução de testes de regressão para o GLPI Dashboard

Este script automatiza a execução de testes de regressão usando o
MetricsRegressionComparator para detectar divergências nas métricas.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório do comparador ao path
sys.path.insert(0, str(Path(__file__).parent))

from metrics_regression_comparator import MetricsRegressionComparator


def setup_baseline_snapshots():
    """Configura snapshots baseline para todos os endpoints principais"""
    print("🔧 Configurando snapshots baseline...")

    comparator = MetricsRegressionComparator()

    # Endpoints principais para capturar
    endpoints = [
        {
            "endpoint": "/metrics",
            "name": "dashboard_metrics_baseline",
            "params": {},
            "description": "Métricas principais do dashboard",
        },
        {
            "endpoint": "/metrics",
            "name": "dashboard_metrics_with_dates",
            "params": {"start_date": "2024-01-01", "end_date": "2024-12-31"},
            "description": "Métricas com filtro de data",
        },
        {
            "endpoint": "/metrics/filtered",
            "name": "filtered_metrics_novo",
            "params": {"status": "novo"},
            "description": "Métricas filtradas por status novo",
        },
        {
            "endpoint": "/metrics/filtered",
            "name": "filtered_metrics_progresso",
            "params": {"status": "progresso"},
            "description": "Métricas filtradas por status em progresso",
        },
        {
            "endpoint": "/technicians/ranking",
            "name": "technician_ranking_default",
            "params": {"limit": 10},
            "description": "Ranking de técnicos padrão",
        },
        {
            "endpoint": "/technicians/ranking",
            "name": "technician_ranking_n1",
            "params": {"limit": 10, "level": "N1"},
            "description": "Ranking de técnicos N1",
        },
        {
            "endpoint": "/technicians/ranking",
            "name": "technician_ranking_n2",
            "params": {"limit": 10, "level": "N2"},
            "description": "Ranking de técnicos N2",
        },
        {
            "endpoint": "/technicians/ranking",
            "name": "technician_ranking_n3",
            "params": {"limit": 10, "level": "N3"},
            "description": "Ranking de técnicos N3",
        },
        {
            "endpoint": "/technicians/ranking",
            "name": "technician_ranking_n4",
            "params": {"limit": 10, "level": "N4"},
            "description": "Ranking de técnicos N4",
        },
        {
            "endpoint": "/tickets/new",
            "name": "new_tickets_default",
            "params": {"limit": 5},
            "description": "Tickets novos padrão",
        },
    ]

    captured_snapshots = []

    for endpoint_config in endpoints:
        try:
            print(f"\n📸 Capturando: {endpoint_config['description']}")
            print(f"   Endpoint: {endpoint_config['endpoint']}")
            print(f"   Parâmetros: {endpoint_config['params']}")

            snapshot_path = comparator.capture_baseline_snapshot(
                endpoint_config["endpoint"],
                endpoint_config["params"],
                f"{endpoint_config['name']}.json",
            )

            captured_snapshots.append(
                {
                    "name": endpoint_config["name"],
                    "path": snapshot_path,
                    "endpoint": endpoint_config["endpoint"],
                    "params": endpoint_config["params"],
                    "description": endpoint_config["description"],
                }
            )

            print(f"   ✅ Capturado: {snapshot_path}")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    # Salvar índice de snapshots
    index_path = comparator.snapshots_dir / "snapshots_index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at": datetime.now().isoformat(),
                "total_snapshots": len(captured_snapshots),
                "snapshots": captured_snapshots,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n✅ Configuração concluída: {len(captured_snapshots)} snapshots capturados")
    print(f"📄 Índice salvo: {index_path}")

    return captured_snapshots


def run_full_regression_suite():
    """Executa suite completa de testes de regressão"""
    print("🧪 Executando suite completa de testes de regressão...")

    comparator = MetricsRegressionComparator(tolerance=0.05)  # 5% de tolerância

    # Carregar índice de snapshots
    index_path = comparator.snapshots_dir / "snapshots_index.json"

    if not index_path.exists():
        print("❌ Índice de snapshots não encontrado. Execute setup_baseline_snapshots() primeiro.")
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    snapshots = index_data["snapshots"]

    print(f"📋 Encontrados {len(snapshots)} snapshots para testar")

    all_reports = []
    total_tests = len(snapshots)
    passed_tests = 0
    failed_tests = 0

    for i, snapshot_config in enumerate(snapshots, 1):
        print(f"\n[{i}/{total_tests}] 🔍 Testando: {snapshot_config['description']}")

        try:
            # Verificar se snapshot existe
            if not os.path.exists(snapshot_config["path"]):
                print(f"   ❌ Snapshot não encontrado: {snapshot_config['path']}")
                failed_tests += 1
                continue

            # Executar teste de regressão
            report = comparator.run_regression_test(
                snapshot_config["path"],
                snapshot_config["endpoint"],
                snapshot_config["params"],
                snapshot_config["name"],
            )

            all_reports.append(report)

            # Mostrar resultado resumido
            if report.success:
                print(f"   ✅ PASSOU: {report.passed_comparisons}/{report.total_comparisons} comparações")
                passed_tests += 1
            else:
                print(f"   ❌ FALHOU: {report.failed_comparisons}/{report.total_comparisons} diferenças encontradas")
                failed_tests += 1

                # Mostrar primeiras 3 diferenças
                failed_diffs = [d for d in report.differences if not d.match][:3]
                for diff in failed_diffs:
                    print(f"      • {diff.field_path}: {diff.expected_value} → {diff.actual_value}")

                if len(failed_diffs) < report.failed_comparisons:
                    remaining = report.failed_comparisons - len(failed_diffs)
                    print(f"      ... e mais {remaining} diferenças")

            print(f"   ⏱️  Tempo: {report.execution_time:.2f}s")

            # Salvar relatório individual
            comparator.save_report(report)

        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            failed_tests += 1

    # Gerar relatório consolidado
    generate_consolidated_report(all_reports, comparator)

    # Resumo final
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL DA SUITE DE REGRESSÃO")
    print(f"{'='*60}")
    print(f"Total de testes: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {failed_tests}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")

    if failed_tests == 0:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! Nenhuma regressão detectada.")
    else:
        print(f"\n⚠️  {failed_tests} TESTES FALHARAM. Regressões detectadas!")

    print(f"{'='*60}")

    return failed_tests == 0


def generate_consolidated_report(reports, comparator):
    """Gera relatório consolidado de todos os testes"""
    timestamp = datetime.now()

    # Calcular estatísticas gerais
    total_tests = len(reports)
    passed_tests = len([r for r in reports if r.success])
    failed_tests = total_tests - passed_tests
    total_comparisons = sum(r.total_comparisons for r in reports)
    total_differences = sum(r.failed_comparisons for r in reports)
    avg_execution_time = sum(r.execution_time for r in reports) / total_tests if total_tests > 0 else 0

    # Agrupar diferenças por tipo
    differences_by_type = {}
    for report in reports:
        for diff in report.differences:
            if not diff.match:
                diff_type = diff.difference_type
                if diff_type not in differences_by_type:
                    differences_by_type[diff_type] = []
                differences_by_type[diff_type].append(
                    {
                        "test": report.test_name,
                        "field": diff.field_path,
                        "expected": diff.expected_value,
                        "actual": diff.actual_value,
                    }
                )

    # Criar relatório consolidado
    consolidated_report = {
        "metadata": {
            "timestamp": timestamp.isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_comparisons": total_comparisons,
            "total_differences": total_differences,
            "avg_execution_time": avg_execution_time,
        },
        "test_results": [
            {
                "test_name": report.test_name,
                "success": report.success,
                "total_comparisons": report.total_comparisons,
                "failed_comparisons": report.failed_comparisons,
                "execution_time": report.execution_time,
            }
            for report in reports
        ],
        "differences_by_type": differences_by_type,
        "failed_tests_details": [
            {
                "test_name": report.test_name,
                "failed_comparisons": report.failed_comparisons,
                "differences": [
                    {
                        "field_path": diff.field_path,
                        "expected_value": diff.expected_value,
                        "actual_value": diff.actual_value,
                        "difference_type": diff.difference_type,
                    }
                    for diff in report.differences
                    if not diff.match
                ],
            }
            for report in reports
            if not report.success
        ],
    }

    # Salvar relatório consolidado
    report_filename = f"consolidated_regression_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    report_path = comparator.reports_dir / report_filename

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_report, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Relatório consolidado salvo: {report_path}")

    return str(report_path)


def quick_smoke_test():
    """Executa teste rápido de smoke nos endpoints principais"""
    print("💨 Executando teste rápido de smoke...")

    comparator = MetricsRegressionComparator(tolerance=0.1)  # Tolerância maior para smoke test

    # Endpoints críticos para smoke test
    critical_endpoints = [
        {"endpoint": "/metrics", "params": {}, "name": "smoke_dashboard_metrics"},
        {
            "endpoint": "/technicians/ranking",
            "params": {"limit": 5},
            "name": "smoke_technician_ranking",
        },
    ]

    all_passed = True

    for endpoint_config in critical_endpoints:
        print(f"\n🔍 Testando: {endpoint_config['name']}")

        try:
            # Capturar snapshot temporário
            temp_snapshot = comparator.capture_baseline_snapshot(
                endpoint_config["endpoint"],
                endpoint_config["params"],
                f"temp_{endpoint_config['name']}.json",
            )

            # Aguardar um pouco e testar novamente (deve ser idêntico)
            import time

            time.sleep(1)

            report = comparator.run_regression_test(
                temp_snapshot,
                endpoint_config["endpoint"],
                endpoint_config["params"],
                endpoint_config["name"],
            )

            if report.success:
                print(f"   ✅ PASSOU: Endpoint está estável")
            else:
                print(f"   ❌ FALHOU: Endpoint instável - {report.failed_comparisons} diferenças")
                all_passed = False

            # Limpar snapshot temporário
            os.remove(temp_snapshot)

        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            all_passed = False

    result = "✅ SMOKE TEST PASSOU" if all_passed else "❌ SMOKE TEST FALHOU"
    print(f"\n{result}")

    return all_passed


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Executar testes de regressão para GLPI Dashboard")
    parser.add_argument(
        "--action",
        choices=["setup", "test", "smoke", "full"],
        default="full",
        help="Ação a executar",
    )

    args = parser.parse_args()

    print(f"🚀 Iniciando testes de regressão - Ação: {args.action}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        if args.action == "setup":
            setup_baseline_snapshots()

        elif args.action == "smoke":
            success = quick_smoke_test()
            sys.exit(0 if success else 1)

        elif args.action == "test" or args.action == "full":
            # Verificar se snapshots existem
            comparator = MetricsRegressionComparator()
            index_path = comparator.snapshots_dir / "snapshots_index.json"

            if not index_path.exists():
                print("⚠️  Snapshots baseline não encontrados. Configurando...")
                setup_baseline_snapshots()

            success = run_full_regression_suite()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
