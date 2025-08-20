#!/usr/bin/env python3
"""
Script de Auditoria do Dashboard GLPI
Realiza testes exaustivos para identificar inconsistências nas métricas
"""

import json
import logging
import time
from datetime import datetime, timedelta

import requests

from backend.config.settings import active_config
from backend.services.glpi_service import GLPIService

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DashboardAuditor:
    def __init__(self):
        self.base_url = "http://localhost:5000/api"
        self.glpi_service = GLPIService()
        self.results = {}

    def test_api_endpoints(self):
        """Testa todos os endpoints da API relacionados às métricas"""
        print("\n=== TESTE DOS ENDPOINTS DA API ===")

        endpoints = [
            "/metrics",
            "/metrics/simple",
            "/metrics/filtered",
            "/status",
            "/test",
        ]

        for endpoint in endpoints:
            print(f"\n🔍 Testando endpoint: {endpoint}")
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                print(f"  Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"  Sucesso: {data.get('success', 'N/A')}")

                    if endpoint == "/metrics":
                        self.analyze_metrics_response(data)
                    elif endpoint == "/metrics/simple":
                        self.analyze_simple_metrics(data)

                else:
                    print(f"  ❌ Erro: {response.text}")

            except Exception as e:
                print(f"  ❌ Exceção: {e}")

    def analyze_metrics_response(self, data):
        """Analisa a resposta do endpoint /metrics"""
        print("\n📊 ANÁLISE DA RESPOSTA /metrics:")

        if not data.get("success"):
            print(f"  ❌ API retornou success=False: {data.get('message', 'Sem mensagem')}")
            return

        metrics = data.get("data", {})

        # Verificar métricas gerais
        geral = metrics.get("niveis", {}).get("geral", {})
        print(f"  📈 Métricas Gerais:")
        print(f"    - Novos: {geral.get('novos', 0)}")
        print(f"    - Em Progresso: {geral.get('progresso', 0)}")
        print(f"    - Pendentes: {geral.get('pendentes', 0)}")
        print(f"    - Resolvidos: {geral.get('resolvidos', 0)}")
        print(f"    - Total: {geral.get('total', 0)}")

        # Verificar se todos são zero
        if all(geral.get(key, 0) == 0 for key in ["novos", "progresso", "pendentes", "resolvidos"]):
            print("  ⚠️ PROBLEMA: Todas as métricas gerais estão zeradas!")

        # Verificar métricas por nível
        niveis = metrics.get("niveis", {})
        for nivel in ["n1", "n2", "n3", "n4"]:
            nivel_data = niveis.get(nivel, {})
            total_nivel = sum(nivel_data.get(key, 0) for key in ["novos", "progresso", "pendentes", "resolvidos"])
            print(f"  📊 {nivel.upper()}: Total = {total_nivel}")

        self.results["api_metrics"] = metrics

    def analyze_simple_metrics(self, data):
        """Analisa a resposta do endpoint /metrics/simple"""
        print("\n📊 ANÁLISE DA RESPOSTA /metrics/simple:")

        if data.get("success"):
            simple_data = data.get("data", {})
            print(f"  📈 Dados de Teste:")
            print(f"    - Novos: {simple_data.get('novos', 0)}")
            print(f"    - Em Progresso: {simple_data.get('progresso', 0)}")
            print(f"    - Pendentes: {simple_data.get('pendentes', 0)}")
            print(f"    - Resolvidos: {simple_data.get('resolvidos', 0)}")
            print(f"    - Total: {simple_data.get('total', 0)}")
        else:
            print("  ❌ Endpoint de teste simples falhou")

    def test_glpi_service_direct(self):
        """Testa o GLPIService diretamente"""
        print("\n=== TESTE DIRETO DO GLPI SERVICE ===")

        try:
            # Autenticar
            print("🔐 Autenticando no GLPI...")
            if self.glpi_service.authenticate():
                print("  ✅ Autenticação bem-sucedida")
            else:
                print("  ❌ Falha na autenticação")
                return

            # Testar método principal de métricas
            print("\n📊 Testando get_dashboard_metrics()...")
            metrics = self.glpi_service.get_dashboard_metrics()

            if metrics:
                print("  ✅ Métricas obtidas com sucesso")
                self.analyze_direct_metrics(metrics)
            else:
                print("  ❌ Nenhuma métrica retornada")

            # Testar contagem direta de tickets
            print("\n🎫 Testando contagem direta de tickets...")
            self.test_direct_ticket_counts()

        except Exception as e:
            print(f"  ❌ Erro no teste direto: {e}")
            logger.exception("Erro detalhado:")

    def analyze_direct_metrics(self, metrics):
        """Analisa métricas obtidas diretamente do serviço"""
        print("\n📈 ANÁLISE DAS MÉTRICAS DIRETAS:")

        if isinstance(metrics, dict):
            if "data" in metrics:
                data = metrics["data"]
            else:
                data = metrics

            # Verificar estrutura
            if "niveis" in data:
                niveis = data["niveis"]
                geral = niveis.get("geral", {})

                print(f"  📊 Métricas Gerais (Diretas):")
                print(f"    - Novos: {geral.get('novos', 0)}")
                print(f"    - Em Progresso: {geral.get('progresso', 0)}")
                print(f"    - Pendentes: {geral.get('pendentes', 0)}")
                print(f"    - Resolvidos: {geral.get('resolvidos', 0)}")
                print(f"    - Total: {geral.get('total', 0)}")

                # Comparar com resultados da API
                if "api_metrics" in self.results:
                    self.compare_metrics(self.results["api_metrics"], data)

            self.results["direct_metrics"] = data

    def test_direct_ticket_counts(self):
        """Testa contagem direta de tickets por status"""
        print("\n🔢 CONTAGEM DIRETA DE TICKETS:")

        try:
            # Buscar todos os tickets sem filtro
            print("  📋 Buscando todos os tickets...")
            all_tickets = self.glpi_service.search_items("Ticket", {"range": "0-50", "criteria": []})  # Limitar para teste

            if all_tickets:
                print(f"    ✅ {len(all_tickets)} tickets encontrados (amostra)")

                # Contar por status
                status_counts = {}
                for ticket in all_tickets:
                    status = ticket.get("12", "Desconhecido")  # Campo 12 = status
                    status_counts[status] = status_counts.get(status, 0) + 1

                print("    📊 Contagem por Status:")
                for status, count in status_counts.items():
                    print(f"      - {status}: {count}")

                self.results["direct_ticket_counts"] = status_counts

            else:
                print("    ❌ Nenhum ticket encontrado")

        except Exception as e:
            print(f"    ❌ Erro na contagem direta: {e}")

    def test_technician_ranking(self):
        """Testa o ranking de técnicos"""
        print("\n=== TESTE DO RANKING DE TÉCNICOS ===")

        try:
            # Testar endpoint de ranking
            print("🏆 Testando endpoint /ranking...")
            response = requests.get(f"{self.base_url}/ranking", timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Status: {response.status_code}")

                if data.get("success"):
                    ranking = data.get("data", [])
                    print(f"  📊 {len(ranking)} técnicos no ranking")

                    # Analisar top 5
                    for i, tech in enumerate(ranking[:5]):
                        print(f"    {i+1}. {tech.get('name', 'N/A')}: {tech.get('total', 0)} tickets")

                    # Verificar se os números estão muito baixos
                    if ranking:
                        max_tickets = max(tech.get("total", 0) for tech in ranking)
                        if max_tickets < 100:  # Threshold arbitrário
                            print(f"  ⚠️ PROBLEMA: Maior número de tickets é apenas {max_tickets}")

                else:
                    print(f"  ❌ API retornou success=False: {data.get('message')}")
            else:
                print(f"  ❌ Erro HTTP: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Erro no teste de ranking: {e}")

    def compare_metrics(self, api_data, direct_data):
        """Compara métricas da API com métricas diretas"""
        print("\n🔍 COMPARAÇÃO API vs DIRETO:")

        api_geral = api_data.get("niveis", {}).get("geral", {})
        direct_geral = direct_data.get("niveis", {}).get("geral", {})

        for metric in ["novos", "progresso", "pendentes", "resolvidos", "total"]:
            api_val = api_geral.get(metric, 0)
            direct_val = direct_geral.get(metric, 0)

            if api_val == direct_val:
                print(f"  ✅ {metric}: {api_val} (iguais)")
            else:
                print(f"  ⚠️ {metric}: API={api_val}, Direto={direct_val} (DIFERENTE)")

    def generate_summary_report(self):
        """Gera relatório resumo da auditoria"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO RESUMO DA AUDITORIA")
        print("=" * 60)

        # Problemas identificados
        problems = []

        # Verificar métricas zeradas
        if "api_metrics" in self.results:
            geral = self.results["api_metrics"].get("niveis", {}).get("geral", {})
            if all(geral.get(key, 0) == 0 for key in ["novos", "progresso", "pendentes", "resolvidos"]):
                problems.append("❌ Métricas gerais do dashboard estão todas zeradas")

        # Verificar inconsistências
        if "api_metrics" in self.results and "direct_metrics" in self.results:
            api_geral = self.results["api_metrics"].get("niveis", {}).get("geral", {})
            direct_geral = self.results["direct_metrics"].get("niveis", {}).get("geral", {})

            for metric in ["novos", "progresso", "pendentes", "resolvidos"]:
                if api_geral.get(metric, 0) != direct_geral.get(metric, 0):
                    problems.append(f"⚠️ Inconsistência em {metric}: API vs Direto")

        # Exibir problemas
        if problems:
            print("\n🚨 PROBLEMAS IDENTIFICADOS:")
            for problem in problems:
                print(f"  {problem}")
        else:
            print("\n✅ Nenhum problema crítico identificado")

        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if problems:
            print("  1. Verificar logs do backend para erros de conexão com GLPI")
            print("  2. Validar configurações de autenticação")
            print("  3. Testar queries SQL diretamente no banco GLPI")
            print("  4. Verificar cache da aplicação")
            print("  5. Analisar filtros de data aplicados")
        else:
            print("  1. Sistema aparenta estar funcionando corretamente")
            print("  2. Continuar monitoramento regular")


if __name__ == "__main__":
    print("🔍 Iniciando Auditoria do Dashboard GLPI")
    print(f"⏰ Timestamp: {datetime.now()}")

    auditor = DashboardAuditor()

    # Executar todos os testes
    auditor.test_api_endpoints()
    auditor.test_glpi_service_direct()
    auditor.test_technician_ranking()

    # Gerar relatório final
    auditor.generate_summary_report()

    print("\n🏁 Auditoria concluída!")
