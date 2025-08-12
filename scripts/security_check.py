#!/usr/bin/env python3
"""
Script de Validação de Segurança Local
Executa todas as verificações de segurança antes do commit
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any


class SecurityValidator:
    """Classe para executar validações de segurança."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_path = self.project_root / "backend"
        self.reports_dir = self.project_root / "security_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_command(self, cmd: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Executa um comando e retorna o resultado."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def check_dependencies(self) -> bool:
        """Verifica se as dependências necessárias estão instaladas."""
        print(" Verificando dependências...")
        
        dependencies = [
            "bandit", "safety", "semgrep", "gitleaks", "pre-commit"
        ]
        
        missing = []
        for dep in dependencies:
            result = self.run_command(["which", dep] if os.name != "nt" else ["where", dep])
            if not result["success"]:
                missing.append(dep)
        
        if missing:
            print(f" Dependências faltando: {', '.join(missing)}")
            print(" Instale com: pip install bandit safety semgrep pre-commit")
            print(" GitLeaks: https://github.com/zricethezav/gitleaks#installation")
            return False
        
        print(" Todas as dependências estão instaladas")
        return True
    
    def run_bandit(self) -> bool:
        """Executa análise de segurança com Bandit."""
        print(" Executando Bandit (SAST)...")
        
        cmd = [
            "bandit", "-r", str(self.backend_path),
            "-f", "json",
            "-o", str(self.reports_dir / "bandit_report.json"),
            "-c", "bandit.yaml"
        ]
        
        result = self.run_command(cmd)
        
        if result["success"]:
            print(" Bandit: Nenhum problema de segurança encontrado")
            return True
        else:
            print(f"  Bandit: Problemas encontrados")
            print(result["stdout"])
            return False
    
    def run_safety(self) -> bool:
        """Executa verificação de vulnerabilidades com Safety."""
        print("  Executando Safety (vulnerabilidades de dependências)...")
        
        # Instalar dependências primeiro
        install_result = self.run_command(
            ["pip", "install", "-r", "requirements.txt"],
            cwd=self.backend_path
        )
        
        if not install_result["success"]:
            print(" Erro ao instalar dependências")
            return False
        
        cmd = [
            "safety", "check",
            "--json",
            "--output", str(self.reports_dir / "safety_report.json")
        ]
        
        result = self.run_command(cmd)
        
        if result["success"]:
            print(" Safety: Nenhuma vulnerabilidade conhecida encontrada")
            return True
        else:
            print(f"  Safety: Vulnerabilidades encontradas")
            print(result["stdout"])
            return False
    
    def run_semgrep(self) -> bool:
        """Executa análise de segurança com Semgrep."""
        print(" Executando Semgrep (SAST)...")
        
        cmd = [
            "semgrep", "--config=auto",
            str(self.backend_path),
            "--json",
            "--output", str(self.reports_dir / "semgrep_report.json")
        ]
        
        result = self.run_command(cmd)
        
        if result["success"]:
            print(" Semgrep: Análise concluída")
            return True
        else:
            print(f"  Semgrep: Problemas encontrados")
            print(result["stdout"])
            return False
    
    def run_gitleaks(self) -> bool:
        """Executa detecção de segredos com GitLeaks."""
        print(" Executando GitLeaks (detecção de segredos)...")
        
        cmd = [
            "gitleaks", "detect",
            "--config", ".gitleaks.toml",
            "--report-format", "json",
            "--report-path", str(self.reports_dir / "gitleaks_report.json"),
            "--verbose"
        ]
        
        result = self.run_command(cmd)
        
        if result["success"]:
            print(" GitLeaks: Nenhum segredo encontrado")
            return True
        else:
            print(f"  GitLeaks: Possíveis segredos detectados")
            print(result["stderr"])
            return False
    
    def run_pre_commit(self) -> bool:
        """Executa hooks do pre-commit."""
        print(" Executando pre-commit hooks...")
        
        # Instalar hooks se necessário
        install_result = self.run_command(["pre-commit", "install"])
        if not install_result["success"]:
            print(" Erro ao instalar pre-commit hooks")
            return False
        
        # Executar hooks
        result = self.run_command(["pre-commit", "run", "--all-files"])
        
        if result["success"]:
            print(" Pre-commit: Todos os hooks passaram")
            return True
        else:
            print(f"  Pre-commit: Alguns hooks falharam")
            print(result["stdout"])
            return False
    
    def generate_summary_report(self) -> None:
        """Gera um relatório resumo de todas as verificações."""
        print(" Gerando relatório resumo...")
        
        summary = {
            "timestamp": subprocess.run(
                ["date", "+%Y-%m-%d %H:%M:%S"],
                capture_output=True,
                text=True
            ).stdout.strip(),
            "reports": []
        }
        
        # Verificar cada relatório
        report_files = {
            "bandit": "bandit_report.json",
            "safety": "safety_report.json",
            "semgrep": "semgrep_report.json",
            "gitleaks": "gitleaks_report.json"
        }
        
        for tool, filename in report_files.items():
            filepath = self.reports_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    if tool == "bandit":
                        issues = len(data.get("results", []))
                    elif tool == "safety":
                        issues = len(data) if isinstance(data, list) else 0
                    elif tool == "semgrep":
                        issues = len(data.get("results", []))
                    elif tool == "gitleaks":
                        issues = len(data) if isinstance(data, list) else 0
                    else:
                        issues = 0
                    
                    summary["reports"].append({
                        "tool": tool,
                        "issues_found": issues,
                        "report_file": str(filepath)
                    })
                except Exception as e:
                    summary["reports"].append({
                        "tool": tool,
                        "error": str(e),
                        "report_file": str(filepath)
                    })
        
        # Salvar resumo
        summary_file = self.reports_dir / "security_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f" Relatório resumo salvo em: {summary_file}")
        
        # Exibir resumo
        print("\n" + "="*50)
        print(" RESUMO DA VALIDAÇÃO DE SEGURANÇA")
        print("="*50)
        
        total_issues = 0
        for report in summary["reports"]:
            if "issues_found" in report:
                issues = report["issues_found"]
                total_issues += issues
                status = "" if issues == 0 else ""
                print(f"{status} {report['tool'].upper()}: {issues} problemas")
            else:
                print(f" {report['tool'].upper()}: Erro na análise")
        
        print(f"\n Total de problemas encontrados: {total_issues}")
        print(f" Relatórios detalhados em: {self.reports_dir}")
        
        return total_issues == 0
    
    def run_all_checks(self) -> bool:
        """Executa todas as verificações de segurança."""
        print(" Iniciando validação de segurança completa...\n")
        
        if not self.check_dependencies():
            return False
        
        checks = [
            ("Bandit", self.run_bandit),
            ("Safety", self.run_safety),
            ("Semgrep", self.run_semgrep),
            ("GitLeaks", self.run_gitleaks),
            ("Pre-commit", self.run_pre_commit)
        ]
        
        results = []
        for name, check_func in checks:
            print(f"\n{'='*20} {name} {'='*20}")
            try:
                result = check_func()
                results.append(result)
            except Exception as e:
                print(f" Erro ao executar {name}: {e}")
                results.append(False)
        
        print(f"\n{'='*50}")
        
        # Gerar relatório resumo
        summary_ok = self.generate_summary_report()
        
        # Resultado final
        all_passed = all(results)
        if all_passed and summary_ok:
            print("\n Todas as verificações de segurança passaram!")
            return True
        else:
            print("\n  Algumas verificações falharam. Verifique os relatórios.")
            return False


def main():
    """Função principal."""
    validator = SecurityValidator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Modo rápido - apenas GitLeaks e Bandit
        print(" Modo rápido - executando verificações essenciais...")
        success = (validator.check_dependencies() and 
                  validator.run_gitleaks() and 
                  validator.run_bandit())
    else:
        # Modo completo
        success = validator.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
