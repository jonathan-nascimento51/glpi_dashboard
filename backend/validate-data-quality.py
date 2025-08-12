#!/usr/bin/env python3
"""
Script de Validação de Qualidade de Dados

Este script:
1. Sobe os serviços (backend/frontend)
2. Aguarda readiness via healthcheck
3. Testa endpoint /api/v1/health/data
4. Captura screenshots do dashboard
5. Gera relatório de validação
6. Falha se detectar dados all-zero
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    import httpx
except ImportError:
    print(" httpx não encontrado. Instale com: pip install httpx")
    sys.exit(1)

try:
    from playwright.async_api import async_playwright
except ImportError:
    print(" playwright não encontrado. Instale com: pip install playwright")
    sys.exit(1)

# Configurações
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
ARTIFACTS_DIR = Path("../artifacts/validation")
TIMEOUT_SERVICES = 60  # segundos
TIMEOUT_HEALTH = 30  # segundos


class DataQualityValidator:
    def __init__(self):
        self.artifacts_dir = ARTIFACTS_DIR
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report = {
            "timestamp": self.timestamp,
            "status": "running",
            "services": {},
            "health_data": {},
            "screenshots": [],
            "errors": [],
            "summary": {},
        }

    async def check_service_health(self, url: str, service_name: str) -> bool:
        """Verifica se um serviço está respondendo"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                is_healthy = response.status_code == 200

                self.report["services"][service_name] = {
                    "url": url,
                    "status_code": response.status_code,
                    "healthy": is_healthy,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }

                return is_healthy
        except Exception as e:
            self.report["services"][service_name] = {
                "url": url,
                "healthy": False,
                "error": str(e),
            }
            return False

    async def wait_for_services(self) -> bool:
        """Aguarda todos os serviços ficarem prontos"""
        print(" Aguardando serviços ficarem prontos...")

        start_time = time.time()
        while time.time() - start_time < TIMEOUT_SERVICES:
            # Verificar API
            api_health = await self.check_service_health(f"{API_BASE}/", "api")

            # Verificar Frontend
            frontend_health = await self.check_service_health(FRONTEND_BASE, "frontend")

            if api_health and frontend_health:
                print(" Todos os serviços estão prontos")
                return True

            print(
                f" Aguardando... API: {"" if api_health else ""} Frontend: {"" if frontend_health else ""}"
            )
            await asyncio.sleep(2)

        print(" Timeout aguardando serviços")
        return False

    async def test_data_health_endpoint(self) -> Dict[str, Any]:
        """Testa o endpoint de health/data"""
        print(" Testando endpoint /api/v1/health/data...")

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_HEALTH) as client:
                response = await client.get(f"{API_BASE}/api/v1/health/data")

                if response.status_code != 200:
                    raise Exception(f"Status code: {response.status_code}")

                health_data = response.json()
                self.report["health_data"] = health_data

                # Salvar dados brutos
                health_file = self.artifacts_dir / f"health_data_{self.timestamp}.json"
                with open(health_file, "w", encoding="utf-8") as f:
                    json.dump(health_data, f, indent=2, ensure_ascii=False)

                print(
                    f" Health endpoint OK - Qualidade: {health_data.get("quality_level", "unknown")}"
                )
                return health_data

        except Exception as e:
            error_msg = f"Erro ao testar health endpoint: {e}"
            print(f" {error_msg}")
            self.report["errors"].append(error_msg)
            raise

    def generate_simple_report(self) -> str:
        """Gera relatório simplificado sem screenshot"""
        health_data = self.report.get("health_data", {})

        # Análise de qualidade
        all_zero_detected = health_data.get("all_zero", False)
        critical_issues = health_data.get("critical_issues", False)
        quality_level = health_data.get("quality_level", "unknown")

        # Determinar status final
        if all_zero_detected or critical_issues:
            final_status = "FAILED"
            status_emoji = ""
        elif quality_level in ["poor", "critical"]:
            final_status = "WARNING"
            status_emoji = ""
        else:
            final_status = "PASSED"
            status_emoji = ""

        summary = {
            "final_status": final_status,
            "status_emoji": status_emoji,
            "all_zero_detected": all_zero_detected,
            "critical_issues": critical_issues,
            "quality_level": quality_level,
        }

        self.report["summary"] = summary

        report_path = self.artifacts_dir / f"validation_report_{self.timestamp}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        # Relatório em texto
        text_report = f"""
{summary["status_emoji"]} RELATÓRIO DE VALIDAÇÃO DE QUALIDADE DE DADOS
{"="*60}

Timestamp: {self.timestamp}
Status Final: {summary["final_status"]}

 ANÁLISE DE QUALIDADE:
- All-Zero Detectado: {"Sim" if summary["all_zero_detected"] else "Não"}
- Issues Críticos: {"Sim" if summary["critical_issues"] else "Não"}
- Nível de Qualidade: {summary["quality_level"]}

 ARTEFATOS GERADOS:
- Relatório JSON: {report_path}
- Health Data: {self.artifacts_dir}/health_data_{self.timestamp}.json

{"="*60}
"""

        text_report_path = (
            self.artifacts_dir / f"validation_report_{self.timestamp}.txt"
        )
        with open(text_report_path, "w", encoding="utf-8") as f:
            f.write(text_report)

        print(text_report)

        return str(report_path)


async def main():
    """Função principal"""
    print(" Iniciando validação de qualidade de dados...")

    validator = DataQualityValidator()

    try:
        # 1. Aguardar serviços
        if not await validator.wait_for_services():
            print(" Falha ao aguardar serviços - abortando")
            sys.exit(1)

        # 2. Testar endpoint de health
        health_data = await validator.test_data_health_endpoint()

        # 3. Gerar relatório
        report_path = validator.generate_simple_report()

        # 4. Verificar se deve falhar
        summary = validator.report["summary"]
        if summary["final_status"] == "FAILED":
            print(f"\n VALIDAÇÃO FALHOU: {summary["status_emoji"]}")
            if summary["all_zero_detected"]:
                print(" ALERTA: Dados all-zero detectados!")
            sys.exit(1)
        elif summary["final_status"] == "WARNING":
            print(f"\n VALIDAÇÃO COM AVISOS: {summary["status_emoji"]}")
            sys.exit(2)
        else:
            print(f"\n VALIDAÇÃO PASSOU: {summary["status_emoji"]}")
            sys.exit(0)

    except Exception as e:
        error_msg = f"Erro durante validação: {e}"
        print(f" {error_msg}")
        validator.report["errors"].append(error_msg)
        validator.report["status"] = "error"
        validator.generate_simple_report()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
