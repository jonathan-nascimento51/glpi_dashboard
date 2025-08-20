#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progressive Refactoring Example - Exemplo prático de uso da refatoração progressiva.

Este exemplo demonstra como integrar a refatoração progressiva em uma aplicação
Flask existente, mostrando diferentes cenários de migração.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, request

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.application.controllers import RefactoringController, create_refactoring_blueprint, create_refactoring_controller
from core.application.services import (
    ProgressiveRefactoringService,
    RefactoringConfig,
    RefactoringPhase,
    create_progressive_refactoring_service,
)
from integration.progressive_refactoring_integration import ProgressiveRefactoringIntegration, setup_progressive_refactoring

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ExampleLegacyService:
    """Serviço legado simulado para demonstração."""

    def get_metrics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Simula obtenção de métricas do sistema legado."""

        logger.info("Obtendo métricas do sistema legado")

        # Simular processamento legado
        return {
            "total_tickets": 150,
            "new_tickets": 25,
            "pending_tickets": 45,
            "in_progress_tickets": 35,
            "resolved_tickets": 45,
            "levels": {"n1": 60, "n2": 40, "n3": 30, "n4": 20},
            "timestamp": "2024-01-15T10:30:00Z",
            "source": "legacy_system",
        }

    def get_technician_ranking(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Simula obtenção de ranking de técnicos do sistema legado."""

        logger.info("Obtendo ranking de técnicos do sistema legado")

        return {
            "technicians": [
                {
                    "name": "João Silva",
                    "resolved_tickets": 45,
                    "avg_resolution_time": 2.5,
                },
                {
                    "name": "Maria Santos",
                    "resolved_tickets": 38,
                    "avg_resolution_time": 3.1,
                },
                {
                    "name": "Pedro Costa",
                    "resolved_tickets": 32,
                    "avg_resolution_time": 2.8,
                },
            ],
            "period": "2024-01",
            "source": "legacy_system",
        }


def create_example_app() -> Flask:
    """Cria aplicação Flask de exemplo com refatoração progressiva."""

    app = Flask(__name__)

    # Configurar refatoração progressiva
    config = RefactoringConfig(
        phase=RefactoringPhase.STRANGLER_FIG,
        migration_percentage=0.2,  # 20% do tráfego para nova arquitetura
        endpoints_to_migrate=["/api/metrics"],
        enable_validation=True,
        validation_sampling=0.1,  # 10% de validação
        enable_fallback=True,
        fallback_timeout_ms=5000,
    )

    # Criar serviço legado
    legacy_service = ExampleLegacyService()

    # Configurar integração
    integration = ProgressiveRefactoringIntegration(
        glpi_config={"base_url": "https://glpi.example.com", "timeout": 30},
        refactoring_config=config,
        legacy_service=legacy_service,
    )

    # Inicializar integração
    integration.initialize(app)

    # Rotas legadas (serão interceptadas pela refatoração)
    @app.route("/api/metrics", methods=["GET"])
    def get_metrics():
        """Endpoint legado de métricas."""

        filters = request.args.to_dict()
        result = legacy_service.get_metrics(filters)

        return jsonify(result)

    @app.route("/api/technicians/ranking", methods=["GET"])
    def get_technician_ranking():
        """Endpoint legado de ranking de técnicos."""

        filters = request.args.to_dict()
        result = legacy_service.get_technician_ranking(filters)

        return jsonify(result)

    # Rotas de controle da refatoração
    @app.route("/admin/refactoring/status", methods=["GET"])
    def refactoring_status():
        """Status da refatoração progressiva."""

        return jsonify(
            {
                "phase": config.phase.value,
                "migration_percentage": config.migration_percentage,
                "endpoints_to_migrate": config.endpoints_to_migrate,
                "validation_enabled": config.enable_validation,
                "validation_sampling": config.validation_sampling,
                "fallback_enabled": config.enable_fallback,
            }
        )

    @app.route("/admin/refactoring/phase", methods=["POST"])
    def set_refactoring_phase():
        """Alterar fase da refatoração."""

        data = request.get_json()
        phase_name = data.get("phase")

        try:
            new_phase = RefactoringPhase(phase_name)
            config.phase = new_phase

            logger.info(f"Fase da refatoração alterada para: {new_phase.value}")

            return jsonify(
                {
                    "success": True,
                    "message": f"Fase alterada para: {new_phase.value}",
                    "current_phase": new_phase.value,
                }
            )

        except ValueError as e:
            return (
                jsonify({"success": False, "error": f"Fase inválida: {phase_name}"}),
                400,
            )

    @app.route("/admin/refactoring/migration-percentage", methods=["POST"])
    def set_migration_percentage():
        """Alterar percentual de migração."""

        data = request.get_json()
        percentage = data.get("percentage")

        if not isinstance(percentage, (int, float)) or not 0 <= percentage <= 1:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Percentual deve ser um número entre 0 e 1",
                    }
                ),
                400,
            )

        config.migration_percentage = percentage

        logger.info(f"Percentual de migração alterado para: {percentage * 100:.1f}%")

        return jsonify(
            {
                "success": True,
                "message": f"Percentual alterado para: {percentage * 100:.1f}%",
                "current_percentage": percentage,
            }
        )

    # Health check
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check da aplicação."""

        return jsonify(
            {
                "status": "healthy",
                "refactoring_phase": config.phase.value,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        )

    return app


def demonstrate_phase_transitions():
    """Demonstra transições entre fases da refatoração."""

    print("\n=== Demonstração de Transições de Fase ===")

    # Fase 1: Sistema Legado
    print("\n1. Fase Legado (Legacy Only)")
    print("   - Todo tráfego vai para o sistema legado")
    print("   - Nenhuma validação ou comparação")
    print("   - Risco mínimo, funcionalidade atual preservada")

    # Fase 2: Strangler Fig
    print("\n2. Fase Strangler Fig")
    print("   - Migração gradual do tráfego (5% → 10% → 25% → 50% → 100%)")
    print("   - Fallback automático em caso de erro")
    print("   - Monitoramento de performance e comparação")
    print("   - Endpoints específicos podem ser migrados primeiro")

    # Fase 3: Validação
    print("\n3. Fase Validação")
    print("   - Sistema legado continua servindo requisições")
    print("   - Nova arquitetura executa em paralelo (shadow mode)")
    print("   - Comparação de resultados com sampling configurável")
    print("   - Identificação de divergências sem impacto no usuário")

    # Fase 4: Nova Arquitetura
    print("\n4. Fase Nova Arquitetura")
    print("   - Todo tráfego vai para a nova arquitetura")
    print("   - Sistema legado pode ser mantido como fallback")
    print("   - Monitoramento contínuo de performance")

    print("\n=== Comandos de Exemplo ===")
    print("\n# Iniciar com validação (5% sampling)")
    print("curl -X POST http://localhost:5000/admin/refactoring/phase \\")
    print("  -H 'Content-Type: application/json' \\")
    print('  -d \'{"phase": "validation"}\'')

    print("\n# Migrar 10% do tráfego")
    print("curl -X POST http://localhost:5000/admin/refactoring/phase \\")
    print("  -H 'Content-Type: application/json' \\")
    print('  -d \'{"phase": "strangler_fig"}\'')

    print("curl -X POST http://localhost:5000/admin/refactoring/migration-percentage \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"percentage\": 0.1}'")

    print("\n# Verificar status")
    print("curl http://localhost:5000/admin/refactoring/status")


def demonstrate_monitoring():
    """Demonstra monitoramento e observabilidade."""

    print("\n=== Monitoramento e Observabilidade ===")

    print("\n1. Métricas de Performance:")
    print("   - Latência P50, P95, P99 (legado vs nova arquitetura)")
    print("   - Taxa de erro por endpoint")
    print("   - Throughput (requisições/segundo)")
    print("   - Taxa de fallback")

    print("\n2. Métricas de Negócio:")
    print("   - Divergências de dados entre sistemas")
    print("   - Cobertura de validação")
    print("   - Percentual de migração por endpoint")

    print("\n3. Logs Estruturados:")
    print("   - Correlation ID para rastreamento")
    print("   - Contexto de refatoração (fase, percentual)")
    print("   - Comparações de resultado (quando habilitadas)")

    print("\n4. Alertas:")
    print("   - P95 > 300ms")
    print("   - Taxa de erro > 1%")
    print("   - Divergências de dados > 5%")
    print("   - Fallback rate > 10%")


def main():
    """Função principal do exemplo."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Exemplo de refatoração progressiva",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--run-server", action="store_true", help="Executar servidor Flask de exemplo")
    parser.add_argument(
        "--demonstrate-phases",
        action="store_true",
        help="Demonstrar transições de fase",
    )
    parser.add_argument("--demonstrate-monitoring", action="store_true", help="Demonstrar monitoramento")
    parser.add_argument("--port", type=int, default=5000, help="Porta do servidor (padrão: 5000)")

    args = parser.parse_args()

    if args.run_server:
        print("Iniciando servidor Flask de exemplo...")
        print(f"Acesse: http://localhost:{args.port}")
        print("\nEndpoints disponíveis:")
        print("  GET  /api/metrics - Métricas (com refatoração)")
        print("  GET  /api/technicians/ranking - Ranking de técnicos")
        print("  GET  /admin/refactoring/status - Status da refatoração")
        print("  POST /admin/refactoring/phase - Alterar fase")
        print("  POST /admin/refactoring/migration-percentage - Alterar percentual")
        print("  GET  /health - Health check")
        print("\nPressione Ctrl+C para parar")

        app = create_example_app()
        app.run(host="0.0.0.0", port=args.port, debug=True)

    elif args.demonstrate_phases:
        demonstrate_phase_transitions()

    elif args.demonstrate_monitoring:
        demonstrate_monitoring()

    else:
        print("Exemplo de Refatoração Progressiva")
        print("\nUso:")
        print("  python progressive_refactoring_example.py --run-server")
        print("  python progressive_refactoring_example.py --demonstrate-phases")
        print("  python progressive_refactoring_example.py --demonstrate-monitoring")
        print("\nPara mais opções: python progressive_refactoring_example.py --help")


if __name__ == "__main__":
    main()
