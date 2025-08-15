#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Validação Automática Aprimorado - GLPI Dashboard

Este script implementa validação automática robusta com:
- Testes de regressão
- Validação de integridade de dados
- Comparação de snapshots
- Alertas automáticos
- Relatórios detalhados
"""

import sys
import os
import json
import time
import requests
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Adicionar o diretório do backend ao path
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.services.glpi_service import GLPIService
    from app.core.config import active_config
except ImportError as e:
    print(f" Erro ao importar módulos do backend: {e}")
    sys.exit(1)

class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str
    details: Any = None
    timestamp: str = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ValidationSnapshot:
    timestamp: str
    total_tickets: int
    metrics_by_status: Dict[str, int]
    metrics_by_level: Dict[str, Dict[str, int]]
    system_health: Dict[str, Any]
    data_hash: str
    
class EnhancedSystemValidator:
    """Validador de sistema aprimorado com testes de regressão"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        self.results: List[TestResult] = []
        self.snapshots_dir = project_root / "artifacts" / "snapshots"
        self.reports_dir = project_root / "artifacts" / "reports"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.glpi_service = None
        self.config_override = config_override or {}
        self.baseline_snapshot: Optional[ValidationSnapshot] = None
        
    def log_test(self, name: str, status: TestStatus, message: str, 
                details: Any = None, execution_time: float = 0.0):
        """Registra resultado de um teste"""
        result = TestResult(
            name=name,
            status=status,
            message=message,
            details=details,
            execution_time=execution_time
        )
        self.results.append(result)
        
        # Log em tempo real
        status_icon = {
            TestStatus.PASS: "",
            TestStatus.FAIL: "", 
            TestStatus.WARN: "",
            TestStatus.SKIP: ""
        }
        
        print(f"{status_icon[status]} {name}: {message}")
        if details and status != TestStatus.PASS:
            print(f"   Details: {details}")
            
    def create_data_snapshot(self) -> Optional[ValidationSnapshot]:
        """Cria snapshot dos dados atuais do sistema"""
        if not self.glpi_service:
            return None
            
        try:
            # Coletar métricas
            general_metrics = self.glpi_service.get_general_metrics() or {}
            level_metrics = self.glpi_service.get_metrics_by_level() or {}
            dashboard_data = self.glpi_service.get_dashboard_metrics() or {}
            
            # Calcular totais
            total_tickets = sum(general_metrics.values())
            
            # Criar hash dos dados para detecção de mudanças
            data_str = json.dumps({
                "general": general_metrics,
                "levels": level_metrics,
                "dashboard": dashboard_data
            }, sort_keys=True)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()
            
            # Testar saúde do sistema
            system_health = self._test_system_health()
            
            snapshot = ValidationSnapshot(
                timestamp=datetime.now().isoformat(),
                total_tickets=total_tickets,
                metrics_by_status=general_metrics,
                metrics_by_level=level_metrics,
                system_health=system_health,
                data_hash=data_hash
            )
            
            return snapshot
            
        except Exception as e:
            self.log_test(
                "snapshot_creation",
                TestStatus.FAIL,
                "Erro ao criar snapshot",
                str(e)
            )
            return None
    
    def _test_system_health(self) -> Dict[str, Any]:
        """Testa saúde geral do sistema"""
        health = {
            "backend_responsive": False,
            "frontend_responsive": False,
            "glpi_connection": False,
            "response_times": {}
        }
        
        # Testar backend
        try:
            start_time = time.time()
            response = requests.get(
                f"http://localhost:8000/health",
                timeout=10
            )
            health["response_times"]["backend"] = time.time() - start_time
            health["backend_responsive"] = response.status_code == 200
        except:
            health["backend_responsive"] = False
            
        # Testar frontend
        try:
            start_time = time.time()
            response = requests.get(
                f"http://localhost:5173",
                timeout=10
            )
            health["response_times"]["frontend"] = time.time() - start_time
            health["frontend_responsive"] = response.status_code == 200
        except:
            health["frontend_responsive"] = False
            
        # Testar conexão GLPI
        if self.glpi_service:
            try:
                start_time = time.time()
                auth_success = self.glpi_service._authenticate_with_retry()
                health["response_times"]["glpi"] = time.time() - start_time
                health["glpi_connection"] = auth_success
            except:
                health["glpi_connection"] = False
                
        return health
    
    def load_baseline_snapshot(self) -> Optional[ValidationSnapshot]:
        """Carrega snapshot baseline mais recente"""
        snapshot_files = list(self.snapshots_dir.glob("baseline_*.json"))
        if not snapshot_files:
            return None
            
        # Pegar o mais recente
        latest_file = max(snapshot_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ValidationSnapshot(**data)
        except Exception as e:
            self.log_test(
                "baseline_load",
                TestStatus.WARN,
                f"Erro ao carregar baseline: {e}"
            )
            return None
    
    def save_snapshot(self, snapshot: ValidationSnapshot, is_baseline: bool = False):
        """Salva snapshot em arquivo"""
        prefix = "baseline" if is_baseline else "snapshot"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = self.snapshots_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(snapshot), f, indent=2, ensure_ascii=False)
            
            self.log_test(
                "snapshot_save",
                TestStatus.PASS,
                f"Snapshot salvo: {filename}"
            )
        except Exception as e:
            self.log_test(
                "snapshot_save",
                TestStatus.FAIL,
                f"Erro ao salvar snapshot: {e}"
            )
    
    def test_regression(self, current: ValidationSnapshot, baseline: ValidationSnapshot):
        """Testa regressão comparando snapshots"""
        print("\n Executando Testes de Regressão...")
        
        # Comparar total de tickets
        if current.total_tickets < baseline.total_tickets * 0.9:  # 10% de tolerância
            self.log_test(
                "regression_total_tickets",
                TestStatus.FAIL,
                f"Regressão detectada: tickets caíram de {baseline.total_tickets} para {current.total_tickets}"
            )
        elif current.total_tickets == 0 and baseline.total_tickets > 0:
            self.log_test(
                "regression_zero_data",
                TestStatus.FAIL,
                "Regressão crítica: dados zerados detectados"
            )
        else:
            self.log_test(
                "regression_total_tickets",
                TestStatus.PASS,
                f"Total de tickets estável: {current.total_tickets}"
            )
        
        # Comparar hash dos dados
        if current.data_hash != baseline.data_hash:
            self.log_test(
                "regression_data_consistency",
                TestStatus.WARN,
                "Dados mudaram desde o baseline",
                {
                    "baseline_hash": baseline.data_hash,
                    "current_hash": current.data_hash
                }
            )
        else:
            self.log_test(
                "regression_data_consistency",
                TestStatus.PASS,
                "Dados consistentes com baseline"
            )
        
        # Comparar saúde do sistema
        baseline_health = baseline.system_health
        current_health = current.system_health
        
        for component in ["backend_responsive", "frontend_responsive", "glpi_connection"]:
            if baseline_health.get(component) and not current_health.get(component):
                self.log_test(
                    f"regression_{component}",
                    TestStatus.FAIL,
                    f"Regressão detectada: {component} não está funcionando"
                )
            elif current_health.get(component):
                self.log_test(
                    f"regression_{component}",
                    TestStatus.PASS,
                    f"{component} funcionando corretamente"
                )
    
    def test_data_integrity(self):
        """Testa integridade dos dados"""
        print("\n Testando Integridade dos Dados...")
        
        if not self.glpi_service:
            self.log_test(
                "data_integrity",
                TestStatus.SKIP,
                "Serviço GLPI não disponível"
            )
            return
        
        try:
            # Testar consistência entre diferentes endpoints
            general_metrics = self.glpi_service.get_general_metrics() or {}
            dashboard_data = self.glpi_service.get_dashboard_metrics() or {}
            
            if dashboard_data.get("success"):
                dashboard_total = dashboard_data.get("data", {}).get("total", 0)
                general_total = sum(general_metrics.values())
                
                # Verificar consistência
                if abs(dashboard_total - general_total) > 5:  # Tolerância de 5 tickets
                    self.log_test(
                        "data_integrity_consistency",
                        TestStatus.FAIL,
                        f"Inconsistência entre endpoints: dashboard={dashboard_total}, general={general_total}"
                    )
                else:
                    self.log_test(
                        "data_integrity_consistency",
                        TestStatus.PASS,
                        "Dados consistentes entre endpoints"
                    )
            
            # Testar estrutura de dados
            required_fields = ["novos", "progresso", "pendentes", "resolvidos"]
            if dashboard_data.get("success"):
                data = dashboard_data.get("data", {})
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "data_integrity_structure",
                        TestStatus.FAIL,
                        f"Campos obrigatórios ausentes: {missing_fields}"
                    )
                else:
                    self.log_test(
                        "data_integrity_structure",
                        TestStatus.PASS,
                        "Estrutura de dados válida"
                    )
            
        except Exception as e:
            self.log_test(
                "data_integrity",
                TestStatus.FAIL,
                "Erro durante teste de integridade",
                str(e)
            )
    
    def test_performance_benchmarks(self):
        """Testa benchmarks de performance"""
        print("\n Testando Performance...")
        
        benchmarks = {
            "glpi_auth": 5.0,      # 5 segundos max
            "dashboard_metrics": 10.0,  # 10 segundos max
            "backend_health": 2.0   # 2 segundos max
        }
        
        # Testar autenticação GLPI
        if self.glpi_service:
            start_time = time.time()
            try:
                auth_success = self.glpi_service._authenticate_with_retry()
                auth_time = time.time() - start_time
                
                if auth_time > benchmarks["glpi_auth"]:
                    self.log_test(
                        "performance_glpi_auth",
                        TestStatus.WARN,
                        f"Autenticação GLPI lenta: {auth_time:.2f}s",
                        execution_time=auth_time
                    )
                else:
                    self.log_test(
                        "performance_glpi_auth",
                        TestStatus.PASS,
                        f"Autenticação GLPI rápida: {auth_time:.2f}s",
                        execution_time=auth_time
                    )
            except Exception as e:
                self.log_test(
                    "performance_glpi_auth",
                    TestStatus.FAIL,
                    "Erro durante teste de performance de auth",
                    str(e)
                )
        
        # Testar métricas do dashboard
        if self.glpi_service:
            start_time = time.time()
            try:
                dashboard_data = self.glpi_service.get_dashboard_metrics()
                metrics_time = time.time() - start_time
                
                if metrics_time > benchmarks["dashboard_metrics"]:
                    self.log_test(
                        "performance_dashboard_metrics",
                        TestStatus.WARN,
                        f"Métricas do dashboard lentas: {metrics_time:.2f}s",
                        execution_time=metrics_time
                    )
                else:
                    self.log_test(
                        "performance_dashboard_metrics",
                        TestStatus.PASS,
                        f"Métricas do dashboard rápidas: {metrics_time:.2f}s",
                        execution_time=metrics_time
                    )
            except Exception as e:
                self.log_test(
                    "performance_dashboard_metrics",
                    TestStatus.FAIL,
                    "Erro durante teste de performance de métricas",
                    str(e)
                )
    
    def generate_detailed_report(self) -> Dict[str, Any]:
        """Gera relatório detalhado dos testes"""
        summary = {
            "total_tests": len(self.results),
            "passed": len([r for r in self.results if r.status == TestStatus.PASS]),
            "failed": len([r for r in self.results if r.status == TestStatus.FAIL]),
            "warnings": len([r for r in self.results if r.status == TestStatus.WARN]),
            "skipped": len([r for r in self.results if r.status == TestStatus.SKIP])
        }
        
        # Calcular tempo total de execução
        total_execution_time = sum(r.execution_time for r in self.results)
        
        # Agrupar resultados por categoria
        categories = {
            "regression": [r for r in self.results if "regression" in r.name],
            "integrity": [r for r in self.results if "integrity" in r.name],
            "performance": [r for r in self.results if "performance" in r.name],
            "basic": [r for r in self.results if not any(cat in r.name for cat in ["regression", "integrity", "performance"])]
        }
        
        # Gerar recomendações
        recommendations = self._generate_smart_recommendations()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "total_execution_time": total_execution_time,
            "categories": {cat: [asdict(r) for r in results] for cat, results in categories.items()},
            "recommendations": recommendations,
            "baseline_comparison": self.baseline_snapshot is not None
        }
        
        return report
    
    def _generate_smart_recommendations(self) -> List[str]:
        """Gera recomendações inteligentes baseadas nos resultados"""
        recommendations = []
        
        failed_tests = [r for r in self.results if r.status == TestStatus.FAIL]
        warning_tests = [r for r in self.results if r.status == TestStatus.WARN]
        
        # Recomendações para falhas
        if any("regression" in t.name for t in failed_tests):
            recommendations.append(
                " CRÍTICO: Regressão detectada! Revisar mudanças recentes e considerar rollback."
            )
        
        if any("zero_data" in t.name for t in failed_tests):
            recommendations.append(
                " CRÍTICO: Dados zerados detectados! Verificar conexão GLPI e configurações."
            )
        
        if any("glpi" in t.name for t in failed_tests):
            recommendations.append(
                " Verificar configuração e conectividade com servidor GLPI."
            )
        
        if any("backend" in t.name for t in failed_tests):
            recommendations.append(
                " Verificar se o backend está rodando e configurado corretamente."
            )
        
        # Recomendações para warnings
        if any("performance" in t.name for t in warning_tests):
            recommendations.append(
                " Considerar otimizações de performance - alguns endpoints estão lentos."
            )
        
        if any("data" in t.name for t in warning_tests):
            recommendations.append(
                " Verificar qualidade dos dados - possíveis inconsistências detectadas."
            )
        
        # Recomendações gerais
        if len(failed_tests) == 0 and len(warning_tests) == 0:
            recommendations.append(
                " Sistema funcionando corretamente! Considerar criar novo baseline."
            )
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """Salva relatório em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n Relatório salvo: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f" Erro ao salvar relatório: {e}")
            return ""
    
    def run_enhanced_validation(self, create_baseline: bool = False) -> Dict[str, Any]:
        """Executa validação completa aprimorada"""
        print(" INICIANDO VALIDAÇÃO AUTOMÁTICA APRIMORADA")
        print("=" * 60)
        
        # Inicializar serviço GLPI
        try:
            self.glpi_service = GLPIService()
        except Exception as e:
            self.log_test(
                "glpi_service_init",
                TestStatus.FAIL,
                "Erro ao inicializar serviço GLPI",
                str(e)
            )
        
        # Carregar baseline se disponível
        if not create_baseline:
            self.baseline_snapshot = self.load_baseline_snapshot()
            if self.baseline_snapshot:
                print(f" Baseline carregado: {self.baseline_snapshot.timestamp}")
            else:
                print(" Nenhum baseline encontrado - executando validação básica")
        
        # Criar snapshot atual
        current_snapshot = self.create_data_snapshot()
        
        # Executar testes básicos
        self._run_basic_tests()
        
        # Executar testes de integridade
        self.test_data_integrity()
        
        # Executar testes de performance
        self.test_performance_benchmarks()
        
        # Executar testes de regressão se temos baseline
        if self.baseline_snapshot and current_snapshot:
            self.test_regression(current_snapshot, self.baseline_snapshot)
        
        # Salvar snapshot atual
        if current_snapshot:
            self.save_snapshot(current_snapshot, is_baseline=create_baseline)
        
        # Gerar e salvar relatório
        report = self.generate_detailed_report()
        self.save_report(report)
        
        # Imprimir resumo
        self._print_summary(report)
        
        return report
    
    def _run_basic_tests(self):
        """Executa testes básicos do sistema"""
        print("\n Executando Testes Básicos...")
        
        # Testar configurações
        required_vars = {
            "GLPI_URL": active_config.GLPI_URL,
            "GLPI_USER_TOKEN": active_config.GLPI_USER_TOKEN,
            "GLPI_APP_TOKEN": active_config.GLPI_APP_TOKEN
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                self.log_test(
                    f"config_{var_name.lower()}",
                    TestStatus.FAIL,
                    f"Variável {var_name} não configurada"
                )
            else:
                self.log_test(
                    f"config_{var_name.lower()}",
                    TestStatus.PASS,
                    f"Variável {var_name} configurada"
                )
        
        # Testar autenticação GLPI
        if self.glpi_service:
            try:
                auth_success = self.glpi_service._authenticate_with_retry()
                if auth_success:
                    self.log_test(
                        "glpi_authentication",
                        TestStatus.PASS,
                        "Autenticação GLPI bem-sucedida"
                    )
                else:
                    self.log_test(
                        "glpi_authentication",
                        TestStatus.FAIL,
                        "Falha na autenticação GLPI"
                    )
            except Exception as e:
                self.log_test(
                    "glpi_authentication",
                    TestStatus.FAIL,
                    "Erro durante autenticação GLPI",
                    str(e)
                )
    
    def _print_summary(self, report: Dict[str, Any]):
        """Imprime resumo dos resultados"""
        print("\n" + "=" * 60)
        print(" RESUMO DA VALIDAÇÃO")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"Total de testes: {summary['total_tests']}")
        print(f" Passou: {summary['passed']}")
        print(f" Falhou: {summary['failed']}")
        print(f" Avisos: {summary['warnings']}")
        print(f" Pulados: {summary['skipped']}")
        print(f" Tempo total: {report['total_execution_time']:.2f}s")
        
        if report["recommendations"]:
            print("\n RECOMENDAÇÕES:")
            for rec in report["recommendations"]:
                print(f"   {rec}")
        
        # Status geral
        if summary['failed'] > 0:
            print("\n STATUS: FALHAS DETECTADAS")
        elif summary['warnings'] > 0:
            print("\n STATUS: AVISOS ENCONTRADOS")
        else:
            print("\n STATUS: TODOS OS TESTES PASSARAM")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de Validação Automática Aprimorado")
    parser.add_argument("--baseline", action="store_true", help="Criar novo baseline")
    parser.add_argument("--config", help="Arquivo de configuração personalizada")
    
    args = parser.parse_args()
    
    config_override = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config_override = json.load(f)
    
    validator = EnhancedSystemValidator(config_override)
    report = validator.run_enhanced_validation(create_baseline=args.baseline)
    
    # Retornar código de saída baseado nos resultados
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    elif report["summary"]["warnings"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
