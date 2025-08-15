#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validaçáo Completa do Sistema GLPI Dashboard

Este script executa uma auditoria completa do sistema para identificar
problemas na apresentaçáo de dados no dashboard.
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Adicionar o diretório do backend ao path
project_root = Path(__file__).parent.parent.parent  # scripts/validation -> scripts -> root
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.services.glpi_service import GLPIService
    from app.core.config import active_config
except ImportError as e:
    print(f"❌ Erro ao importar módulos do backend: {e}")
    sys.exit(1)

class SystemValidator:
    """Validador completo do sistema GLPI Dashboard"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "recommendations": []
        }
        self.glpi_service = None
        
    def log_test(self, test_name: str, status: str, message: str, details: Any = None):
        """Registra resultado de um teste"""
        self.results["tests"][test_name] = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["summary"]["total_tests"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {message}")
        elif status == "WARN":
            self.results["summary"]["warnings"] += 1
            print(f"⚠️  {test_name}: {message}")
            
        if details:
            print(f"   Detalhes: {details}")
    
    def test_environment_config(self):
        """Testa configurações de ambiente"""
        print("\n🔧 Testando Configurações de Ambiente...")
        
        # Verificar variáveis essenciais
        required_vars = {
            "GLPI_URL": active_config.GLPI_URL,
            "GLPI_USER_TOKEN": active_config.GLPI_USER_TOKEN,
            "GLPI_APP_TOKEN": active_config.GLPI_APP_TOKEN
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                self.log_test(
                    f"config_{var_name.lower()}",
                    "FAIL",
                    f"Variável {var_name} náo configurada"
                )
                self.results["recommendations"].append(
                    f"Configure a variável {var_name} no arquivo .env"
                )
            else:
                # Mascarar tokens para segurança
                display_value = var_value
                if "TOKEN" in var_name:
                    display_value = f"{var_value[:8]}...{var_value[-4:]}"
                    
                self.log_test(
                    f"config_{var_name.lower()}",
                    "PASS",
                    f"Variável {var_name} configurada",
                    display_value
                )
    
    def test_glpi_connectivity(self):
        """Testa conectividade com a API do GLPI"""
        print("\n🌐 Testando Conectividade GLPI...")
        
        try:
            # Testar URL básica
            response = requests.get(active_config.GLPI_URL, timeout=10)
            if response.status_code == 200:
                self.log_test(
                    "glpi_url_reachable",
                    "PASS",
                    "URL do GLPI acessível",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "glpi_url_reachable",
                    "WARN",
                    f"URL do GLPI retornou status {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "glpi_url_reachable",
                "FAIL",
                "Náo foi possível acessar a URL do GLPI",
                str(e)
            )
            self.results["recommendations"].append(
                "Verifique se o servidor GLPI está acessível e a URL está correta"
            )
    
    def test_glpi_authentication(self):
        """Testa autenticaçáo com a API do GLPI"""
        print("\n🔐 Testando Autenticaçáo GLPI...")
        
        try:
            self.glpi_service = GLPIService()
            auth_success = self.glpi_service._authenticate_with_retry()
            
            if auth_success:
                self.log_test(
                    "glpi_authentication",
                    "PASS",
                    "Autenticaçáo GLPI bem-sucedida",
                    f"Token: {self.glpi_service.session_token[:8]}..."
                )
            else:
                self.log_test(
                    "glpi_authentication",
                    "FAIL",
                    "Falha na autenticaçáo GLPI"
                )
                self.results["recommendations"].append(
                    "Verifique se os tokens GLPI_USER_TOKEN e GLPI_APP_TOKEN estáo corretos"
                )
        except Exception as e:
            self.log_test(
                "glpi_authentication",
                "FAIL",
                "Erro durante autenticaçáo GLPI",
                str(e)
            )
    
    def test_field_discovery(self):
        """Testa descoberta de IDs de campos"""
        print("\n🔍 Testando Descoberta de Campos...")
        
        if not self.glpi_service:
            self.log_test(
                "field_discovery",
                "FAIL",
                "Serviço GLPI náo inicializado"
            )
            return
            
        try:
            field_discovery = self.glpi_service.discover_field_ids()
            
            if field_discovery:
                self.log_test(
                    "field_discovery",
                    "PASS",
                    "IDs de campos descobertos com sucesso",
                    self.glpi_service.field_ids
                )
            else:
                self.log_test(
                    "field_discovery",
                    "FAIL",
                    "Falha na descoberta de IDs de campos"
                )
        except Exception as e:
            self.log_test(
                "field_discovery",
                "FAIL",
                "Erro durante descoberta de campos",
                str(e)
            )
    
    def test_data_retrieval(self):
        """Testa recuperaçáo de dados do GLPI"""
        print("\n📊 Testando Recuperaçáo de Dados...")
        
        if not self.glpi_service:
            self.log_test(
                "data_retrieval",
                "FAIL",
                "Serviço GLPI náo inicializado"
            )
            return
        
        # Testar métricas gerais
        try:
            general_metrics = self.glpi_service.get_general_metrics()
            
            if general_metrics:
                total_tickets = sum(general_metrics.values())
                self.log_test(
                    "general_metrics",
                    "PASS",
                    f"Métricas gerais obtidas - Total: {total_tickets} tickets",
                    general_metrics
                )
                
                # Verificar se há dados reais
                if total_tickets == 0:
                    self.log_test(
                        "general_metrics_data",
                        "WARN",
                        "Nenhum ticket encontrado nas métricas gerais"
                    )
                    self.results["recommendations"].append(
                        "Verifique se existem tickets no sistema GLPI"
                    )
                else:
                    self.log_test(
                        "general_metrics_data",
                        "PASS",
                        f"Dados reais encontrados: {total_tickets} tickets"
                    )
            else:
                self.log_test(
                    "general_metrics",
                    "FAIL",
                    "Falha ao obter métricas gerais"
                )
        except Exception as e:
            self.log_test(
                "general_metrics",
                "FAIL",
                "Erro ao obter métricas gerais",
                str(e)
            )
        
        # Testar métricas por nível
        try:
            level_metrics = self.glpi_service.get_metrics_by_level()
            
            if level_metrics:
                self.log_test(
                    "level_metrics",
                    "PASS",
                    "Métricas por nível obtidas",
                    {level: sum(data.values()) for level, data in level_metrics.items()}
                )
                
                # Verificar se há dados por nível
                total_by_level = sum(sum(data.values()) for data in level_metrics.values())
                if total_by_level == 0:
                    self.log_test(
                        "level_metrics_data",
                        "WARN",
                        "Nenhum ticket encontrado nos grupos N1-N4"
                    )
                    self.results["recommendations"].append(
                        "Verifique se os IDs dos grupos N1-N4 estáo corretos no código"
                    )
                else:
                    self.log_test(
                        "level_metrics_data",
                        "PASS",
                        f"Dados por nível encontrados: {total_by_level} tickets"
                    )
            else:
                self.log_test(
                    "level_metrics",
                    "FAIL",
                    "Falha ao obter métricas por nível"
                )
        except Exception as e:
            self.log_test(
                "level_metrics",
                "FAIL",
                "Erro ao obter métricas por nível",
                str(e)
            )
    
    def test_dashboard_metrics(self):
        """Testa métricas completas do dashboard"""
        print("\n📈 Testando Métricas do Dashboard...")
        
        if not self.glpi_service:
            self.log_test(
                "dashboard_metrics",
                "FAIL",
                "Serviço GLPI náo inicializado"
            )
            return
        
        try:
            dashboard_data = self.glpi_service.get_dashboard_metrics()
            
            if dashboard_data and dashboard_data.get("success"):
                data = dashboard_data.get("data", {})
                total = data.get("total", 0)
                
                self.log_test(
                    "dashboard_metrics",
                    "PASS",
                    f"Métricas do dashboard obtidas - Total: {total} tickets",
                    {
                        "novos": data.get("novos", 0),
                        "progresso": data.get("progresso", 0),
                        "pendentes": data.get("pendentes", 0),
                        "resolvidos": data.get("resolvidos", 0),
                        "total": total
                    }
                )
                
                # Verificar estrutura de níveis
                niveis = data.get("niveis", {})
                if niveis:
                    self.log_test(
                        "dashboard_levels_structure",
                        "PASS",
                        "Estrutura de níveis presente",
                        list(niveis.keys())
                    )
                else:
                    self.log_test(
                        "dashboard_levels_structure",
                        "WARN",
                        "Estrutura de níveis ausente"
                    )
                
                # Verificar se há dados zerados
                if total == 0:
                    self.log_test(
                        "dashboard_data_validation",
                        "WARN",
                        "Dashboard retornando dados zerados"
                    )
                    self.results["recommendations"].append(
                        "Investigar por que o dashboard está retornando dados zerados"
                    )
                else:
                    self.log_test(
                        "dashboard_data_validation",
                        "PASS",
                        "Dashboard retornando dados válidos"
                    )
            else:
                self.log_test(
                    "dashboard_metrics",
                    "FAIL",
                    "Falha ao obter métricas do dashboard",
                    dashboard_data
                )
        except Exception as e:
            self.log_test(
                "dashboard_metrics",
                "FAIL",
                "Erro ao obter métricas do dashboard",
                str(e)
            )
    
    def test_backend_api(self):
        """Testa API do backend"""
        print("\n🔌 Testando API do Backend...")
        
        backend_url = "http://localhost:8000"
        
        # Testar health check
        try:
            response = requests.get(f"{backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test(
                    "backend_health",
                    "PASS",
                    "Backend health check OK",
                    response.json()
                )
            else:
                self.log_test(
                    "backend_health",
                    "FAIL",
                    f"Backend health check falhou: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "backend_health",
                "FAIL",
                "Erro ao acessar backend health check",
                str(e)
            )
            self.results["recommendations"].append(
                "Verifique se o backend está rodando na porta 8000"
            )
        
        # Testar endpoint de métricas
        try:
            response = requests.get(f"{backend_url}/api/metrics", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "backend_metrics_endpoint",
                    "PASS",
                    "Endpoint de métricas funcionando",
                    {
                        "success": data.get("success"),
                        "data_keys": list(data.get("data", {}).keys()) if data.get("data") else []
                    }
                )
                
                # Verificar estrutura da resposta
                if data.get("success") and data.get("data"):
                    metrics_data = data["data"]
                    total = metrics_data.get("total", 0)
                    
                    if total > 0:
                        self.log_test(
                            "backend_metrics_data",
                            "PASS",
                            f"API retornando dados válidos: {total} tickets"
                        )
                    else:
                        self.log_test(
                            "backend_metrics_data",
                            "WARN",
                            "API retornando dados zerados"
                        )
                else:
                    self.log_test(
                        "backend_metrics_data",
                        "FAIL",
                        "Estrutura de resposta da API inválida"
                    )
            else:
                self.log_test(
                    "backend_metrics_endpoint",
                    "FAIL",
                    f"Endpoint de métricas falhou: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "backend_metrics_endpoint",
                "FAIL",
                "Erro ao acessar endpoint de métricas",
                str(e)
            )
    
    def test_frontend_connectivity(self):
        """Testa conectividade do frontend"""
        print("\n🌐 Testando Frontend...")
        
        frontend_url = "http://localhost:3002"
        
        try:
            response = requests.get(frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_test(
                    "frontend_accessibility",
                    "PASS",
                    "Frontend acessível",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "frontend_accessibility",
                    "WARN",
                    f"Frontend retornou status {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "frontend_accessibility",
                "FAIL",
                "Erro ao acessar frontend",
                str(e)
            )
            self.results["recommendations"].append(
                "Verifique se o frontend está rodando na porta 3002"
            )
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados dos testes"""
        print("\n💡 Gerando Recomendações...")
        
        failed_tests = [name for name, result in self.results["tests"].items() 
                       if result["status"] == "FAIL"]
        
        if failed_tests:
            self.results["recommendations"].append(
                f"Corrigir {len(failed_tests)} testes que falharam: {', '.join(failed_tests)}"
            )
        
        warning_tests = [name for name, result in self.results["tests"].items() 
                        if result["status"] == "WARN"]
        
        if warning_tests:
            self.results["recommendations"].append(
                f"Investigar {len(warning_tests)} avisos: {', '.join(warning_tests)}"
            )
        
        # Recomendações específicas baseadas nos padrões de falha
        if any("glpi" in test for test in failed_tests):
            self.results["recommendations"].append(
                "Verificar configuraçáo e conectividade com o servidor GLPI"
            )
        
        if any("backend" in test for test in failed_tests):
            self.results["recommendations"].append(
                "Verificar se o backend está rodando e configurado corretamente"
            )
        
        if any("data" in test for test in warning_tests):
            self.results["recommendations"].append(
                "Verificar se há dados reais no sistema GLPI para exibiçáo"
            )
    
    def save_results(self):
        """Salva resultados em arquivo JSON"""
        artifacts_dir = project_root / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = artifacts_dir / f"system_validation_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Resultados salvos em: {results_file}")
        return results_file
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        print("\n" + "="*60)
        print("📋 RESUMO DA AUDITORIA")
        print("="*60)
        
        summary = self.results["summary"]
        print(f"Total de testes: {summary['total_tests']}")
        print(f"✅ Passou: {summary['passed']}")
        print(f"❌ Falhou: {summary['failed']}")
        print(f"⚠️  Avisos: {summary['warnings']}")
        
        success_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if self.results["recommendations"]:
            print("\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        # Status geral
        if summary['failed'] == 0:
            if summary['warnings'] == 0:
                print("\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
            else:
                print("\n✅ SISTEMA FUNCIONANDO COM ALGUNS AVISOS")
        else:
            print("\n🚨 SISTEMA COM PROBLEMAS QUE PRECISAM SER CORRIGIDOS")
    
    def run_full_audit(self):
        """Executa auditoria completa do sistema"""
        print("🔍 INICIANDO AUDITORIA COMPLETA DO SISTEMA GLPI DASHBOARD")
        print("="*60)
        
        # Executar todos os testes
        self.test_environment_config()
        self.test_glpi_connectivity()
        self.test_glpi_authentication()
        self.test_field_discovery()
        self.test_data_retrieval()
        self.test_dashboard_metrics()
        self.test_backend_api()
        self.test_frontend_connectivity()
        
        # Gerar recomendações
        self.generate_recommendations()
        
        # Salvar resultados
        results_file = self.save_results()
        
        # Imprimir resumo
        self.print_summary()
        
        return self.results

def main():
    """Funçáo principal"""
    validator = SystemValidator()
    results = validator.run_full_audit()
    
    # Retornar código de saída baseado nos resultados
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    elif results["summary"]["warnings"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

