#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configure Refactoring - Script para configurar fases da refatoração progressiva.

Este script permite configurar e alternar entre diferentes fases da refatoração
progressiva através de variáveis de ambiente e arquivos de configuração.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.application.services import RefactoringPhase


class RefactoringConfigurator:
    """Configurador para refatoração progressiva."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self.config = self._load_config()

    def _get_default_config_file(self) -> str:
        """Obtém caminho padrão do arquivo de configuração."""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "refactoring_config.json",
        )

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração existente ou cria padrão."""

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão."""

        return {
            "refactoring": {
                "phase": "legacy_only",
                "migration_percentage": 0.0,
                "endpoints_to_migrate": [],
                "enable_validation": False,
                "validation_sampling": 0.1,
                "enable_fallback": True,
                "fallback_timeout_ms": 5000,
                "log_performance_comparison": True,
                "log_data_differences": True,
            },
            "glpi": {
                "base_url": "https://glpi.example.com",
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 1.0,
                "session_renewal_threshold": 300,
            },
            "logging": {"level": "INFO", "format": "json", "correlation_sampling": 1.0},
            "monitoring": {
                "enable_metrics": True,
                "metrics_port": 9090,
                "health_check_interval": 30,
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0.0",
            },
        }

    def save_config(self) -> None:
        """Salva configuração no arquivo."""

        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        # Atualizar timestamp
        self.config["metadata"]["updated_at"] = datetime.now().isoformat()

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            print(f"Configuração salva em: {self.config_file}")

        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            raise

    def set_phase(self, phase: str) -> None:
        """Define fase da refatoração."""

        valid_phases = [p.value for p in RefactoringPhase]

        if phase not in valid_phases:
            raise ValueError(f"Fase inválida: {phase}. Válidas: {valid_phases}")

        self.config["refactoring"]["phase"] = phase
        print(f"Fase definida para: {phase}")

    def set_migration_percentage(self, percentage: float) -> None:
        """Define percentual de migração."""

        if not 0.0 <= percentage <= 1.0:
            raise ValueError("Percentual deve estar entre 0.0 e 1.0")

        self.config["refactoring"]["migration_percentage"] = percentage
        print(f"Percentual de migração definido para: {percentage * 100:.1f}%")

    def add_endpoint_to_migrate(self, endpoint: str) -> None:
        """Adiciona endpoint à lista de migração."""

        endpoints = self.config["refactoring"]["endpoints_to_migrate"]

        if endpoint not in endpoints:
            endpoints.append(endpoint)
            print(f"Endpoint adicionado à migração: {endpoint}")
        else:
            print(f"Endpoint já está na lista: {endpoint}")

    def remove_endpoint_from_migrate(self, endpoint: str) -> None:
        """Remove endpoint da lista de migração."""

        endpoints = self.config["refactoring"]["endpoints_to_migrate"]

        if endpoint in endpoints:
            endpoints.remove(endpoint)
            print(f"Endpoint removido da migração: {endpoint}")
        else:
            print(f"Endpoint não está na lista: {endpoint}")

    def enable_validation(self, enable: bool = True, sampling: float = 0.1) -> None:
        """Habilita/desabilita validação."""

        self.config["refactoring"]["enable_validation"] = enable
        self.config["refactoring"]["validation_sampling"] = sampling

        status = "habilitada" if enable else "desabilitada"
        print(f"Validação {status} com sampling de {sampling * 100:.1f}%")

    def set_glpi_config(self, **kwargs) -> None:
        """Define configurações do GLPI."""

        for key, value in kwargs.items():
            if key in self.config["glpi"]:
                self.config["glpi"][key] = value
                print(f"GLPI {key} definido para: {value}")
            else:
                print(f"Configuração GLPI desconhecida: {key}")

    def export_env_vars(self, output_file: Optional[str] = None) -> None:
        """Exporta configurações como variáveis de ambiente."""

        env_vars = {
            "REFACTORING_PHASE": self.config["refactoring"]["phase"],
            "MIGRATION_PERCENTAGE": str(self.config["refactoring"]["migration_percentage"]),
            "ENABLE_VALIDATION": str(self.config["refactoring"]["enable_validation"]).lower(),
            "VALIDATION_SAMPLING": str(self.config["refactoring"]["validation_sampling"]),
            "ENABLE_FALLBACK": str(self.config["refactoring"]["enable_fallback"]).lower(),
            "FALLBACK_TIMEOUT_MS": str(self.config["refactoring"]["fallback_timeout_ms"]),
            "GLPI_BASE_URL": self.config["glpi"]["base_url"],
            "GLPI_TIMEOUT": str(self.config["glpi"]["timeout"]),
            "GLPI_MAX_RETRIES": str(self.config["glpi"]["max_retries"]),
            "GLPI_RETRY_DELAY": str(self.config["glpi"]["retry_delay"]),
            "LOG_LEVEL": self.config["logging"]["level"],
            "LOG_FORMAT": self.config["logging"]["format"],
        }

        # Adicionar endpoints como string separada por vírgulas
        endpoints = self.config["refactoring"]["endpoints_to_migrate"]
        env_vars["ENDPOINTS_TO_MIGRATE"] = ",".join(endpoints)

        if output_file:
            # Salvar em arquivo .env
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("# Configurações de Refatoração Progressiva\n")
                f.write(f"# Gerado em: {datetime.now().isoformat()}\n\n")

                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

            print(f"Variáveis de ambiente exportadas para: {output_file}")
        else:
            # Imprimir no console
            print("\n# Variáveis de ambiente:")
            for key, value in env_vars.items():
                print(f"export {key}={value}")

    def show_status(self) -> None:
        """Mostra status atual da configuração."""

        print("\n=== Status da Refatoração Progressiva ===")
        print(f"Fase atual: {self.config['refactoring']['phase']}")
        print(f"Migração: {self.config['refactoring']['migration_percentage'] * 100:.1f}%")
        print(f"Validação: {'Habilitada' if self.config['refactoring']['enable_validation'] else 'Desabilitada'}")

        if self.config["refactoring"]["enable_validation"]:
            print(f"Sampling de validação: {self.config['refactoring']['validation_sampling'] * 100:.1f}%")

        endpoints = self.config["refactoring"]["endpoints_to_migrate"]
        if endpoints:
            print(f"Endpoints para migração: {', '.join(endpoints)}")
        else:
            print("Nenhum endpoint específico para migração")

        print(f"Fallback: {'Habilitado' if self.config['refactoring']['enable_fallback'] else 'Desabilitado'}")
        print(f"GLPI URL: {self.config['glpi']['base_url']}")
        print(f"Última atualização: {self.config['metadata']['updated_at']}")
        print("\n")

    def create_phase_plan(self, target_phase: str, steps: int = 5) -> None:
        """Cria plano de migração por fases."""

        current_phase = self.config["refactoring"]["phase"]

        print(f"\n=== Plano de Migração: {current_phase} → {target_phase} ===")

        if target_phase == "strangler_fig":
            percentages = [i / steps for i in range(1, steps + 1)]

            print("Fases sugeridas:")
            for i, pct in enumerate(percentages, 1):
                print(f"  {i}. Migrar {pct * 100:.1f}% do tráfego")
                print(f"     Comando: python configure_refactoring.py --phase strangler_fig --migration-percentage {pct}")

        elif target_phase == "validation":
            print("Fases sugeridas:")
            print("  1. Habilitar validação com 5% de sampling")
            print(
                "     Comando: python configure_refactoring.py --phase validation --enable-validation --validation-sampling 0.05"
            )
            print("  2. Aumentar sampling para 20%")
            print("     Comando: python configure_refactoring.py --validation-sampling 0.2")
            print("  3. Validação completa (100%)")
            print("     Comando: python configure_refactoring.py --validation-sampling 1.0")

        elif target_phase == "new_architecture":
            print("Fases sugeridas:")
            print("  1. Validar com nova arquitetura")
            print("     Comando: python configure_refactoring.py --phase validation")
            print("  2. Migrar endpoints específicos")
            print("     Comando: python configure_refactoring.py --phase strangler_fig --add-endpoint /api/metrics")
            print("  3. Migração completa")
            print("     Comando: python configure_refactoring.py --phase new_architecture")

        print("\n")


def main():
    """Função principal do script."""

    parser = argparse.ArgumentParser(
        description="Configurar refatoração progressiva",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Mostrar status atual
  python configure_refactoring.py --status
  
  # Definir fase para strangler fig com 10% de migração
  python configure_refactoring.py --phase strangler_fig --migration-percentage 0.1
  
  # Habilitar validação
  python configure_refactoring.py --enable-validation --validation-sampling 0.05
  
  # Adicionar endpoint para migração
  python configure_refactoring.py --add-endpoint /api/metrics
  
  # Exportar variáveis de ambiente
  python configure_refactoring.py --export-env .env
  
  # Criar plano de migração
  python configure_refactoring.py --create-plan new_architecture
""",
    )

    parser.add_argument("--config-file", help="Arquivo de configuração")
    parser.add_argument(
        "--phase",
        choices=["legacy_only", "strangler_fig", "new_architecture", "validation"],
        help="Fase da refatoração",
    )
    parser.add_argument("--migration-percentage", type=float, help="Percentual de migração (0.0 a 1.0)")
    parser.add_argument("--add-endpoint", help="Adicionar endpoint à migração")
    parser.add_argument("--remove-endpoint", help="Remover endpoint da migração")
    parser.add_argument("--enable-validation", action="store_true", help="Habilitar validação")
    parser.add_argument("--disable-validation", action="store_true", help="Desabilitar validação")
    parser.add_argument("--validation-sampling", type=float, help="Sampling de validação (0.0 a 1.0)")
    parser.add_argument("--glpi-url", help="URL base do GLPI")
    parser.add_argument("--glpi-timeout", type=int, help="Timeout do GLPI")
    parser.add_argument("--export-env", help="Exportar variáveis de ambiente para arquivo")
    parser.add_argument("--status", action="store_true", help="Mostrar status atual")
    parser.add_argument(
        "--create-plan",
        choices=["strangler_fig", "validation", "new_architecture"],
        help="Criar plano de migração",
    )
    parser.add_argument("--save", action="store_true", help="Salvar configurações")

    args = parser.parse_args()

    try:
        # Criar configurador
        configurator = RefactoringConfigurator(args.config_file)

        # Processar argumentos
        changes_made = False

        if args.phase:
            configurator.set_phase(args.phase)
            changes_made = True

        if args.migration_percentage is not None:
            configurator.set_migration_percentage(args.migration_percentage)
            changes_made = True

        if args.add_endpoint:
            configurator.add_endpoint_to_migrate(args.add_endpoint)
            changes_made = True

        if args.remove_endpoint:
            configurator.remove_endpoint_from_migrate(args.remove_endpoint)
            changes_made = True

        if args.enable_validation:
            sampling = args.validation_sampling or 0.1
            configurator.enable_validation(True, sampling)
            changes_made = True

        if args.disable_validation:
            configurator.enable_validation(False)
            changes_made = True

        if args.validation_sampling is not None and not args.enable_validation:
            configurator.config["refactoring"]["validation_sampling"] = args.validation_sampling
            print(f"Sampling de validação definido para: {args.validation_sampling * 100:.1f}%")
            changes_made = True

        if args.glpi_url or args.glpi_timeout:
            glpi_config = {}
            if args.glpi_url:
                glpi_config["base_url"] = args.glpi_url
            if args.glpi_timeout:
                glpi_config["timeout"] = args.glpi_timeout

            configurator.set_glpi_config(**glpi_config)
            changes_made = True

        # Salvar se houve mudanças ou se explicitamente solicitado
        if changes_made or args.save:
            configurator.save_config()

        # Exportar variáveis de ambiente
        if args.export_env:
            configurator.export_env_vars(args.export_env)

        # Mostrar status
        if args.status or not any(vars(args).values()):
            configurator.show_status()

        # Criar plano
        if args.create_plan:
            configurator.create_phase_plan(args.create_plan)

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
