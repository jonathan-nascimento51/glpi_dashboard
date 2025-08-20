#!/usr/bin/env python3
"""
Script de Validação da Nova Arquitetura
Verifica se a migração foi bem-sucedida e a nova arquitetura está funcionando
"""

import os
import sys
import json
import asyncio
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    name: str
    success: bool
    message: str
    details: Optional[Dict] = None
    execution_time: float = 0.0

class ArchitectureValidator:
    """Validador da nova arquitetura"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.results: List[ValidationResult] = []
        
    def log_result(self, result: ValidationResult):
        """Registra resultado da validação"""
        self.results.append(result)
        status_icon = "✅" if result.success else "❌"
        print(f"{status_icon} {result.name}: {result.message} ({result.execution_time:.2f}s)")
        
        if result.details:
            for key, value in result.details.items():
                print(f"   📊 {key}: {value}")
    
    def validate_directory_structure(self) -> ValidationResult:
        """Valida se a nova estrutura de diretórios foi criada"""
        start_time = time.time()
        
        required_dirs = [
            "backend/core/domain/entities",
            "backend/core/domain/value_objects",
            "backend/core/domain/services", 
            "backend/core/domain/repositories",
            "backend/core/application/dto",
            "backend/core/application/use_cases",
            "backend/core/application/interfaces",
            "backend/core/infrastructure/external/glpi",
            "backend/core/infrastructure/repositories",
            "backend/core/infrastructure/services",
            "backend/api/v1/endpoints",
            "frontend/src/features/dashboard",
            "frontend/src/features/metrics",
            "frontend/src/features/ranking",
            "frontend/src/shared/components",
            "frontend/src/store"
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)
        
        success = len(missing_dirs) == 0
        message = f"Structure validation: {len(existing_dirs)}/{len(required_dirs)} directories"
        
        details = {
            "existing_directories": len(existing_dirs),
            "missing_directories": len(missing_dirs),
            "missing_list": missing_dirs[:5] if missing_dirs else []
        }
        
        return ValidationResult(
            name="Directory Structure",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def validate_python_imports(self) -> ValidationResult:
        """Valida se os imports Python estão funcionando"""
        start_time = time.time()
        
        test_imports = [
            ("fastapi", "FastAPI framework"),
            ("pydantic", "Data validation"),
            ("aiohttp", "Async HTTP client"),
            ("redis", "Cache service"),
            ("pytest", "Testing framework")
        ]
        
        successful_imports = []
        failed_imports = []
        
        for module_name, description in test_imports:
            try:
                __import__(module_name)
                successful_imports.append((module_name, description))
            except ImportError:
                failed_imports.append((module_name, description))
        
        success = len(failed_imports) == 0
        message = f"Python imports: {len(successful_imports)}/{len(test_imports)} modules"
        
        details = {
            "successful_imports": [name for name, _ in successful_imports],
            "failed_imports": [name for name, _ in failed_imports]
        }
        
        return ValidationResult(
            name="Python Dependencies",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def validate_existing_code_compatibility(self) -> ValidationResult:
        """Valida se o código existente ainda funciona"""
        start_time = time.time()
        
        critical_files = [
            "backend/glpi_service.py",
            "backend/api_service.py",
            "frontend/src/App.tsx"
        ]
        
        working_files = []
        broken_files = []
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    if file_path.endswith('.py'):
                        # Tentar importar módulo Python
                        module_path = file_path.replace('/', '.').replace('.py', '')
                        spec = __import__(module_path.replace('backend.', ''), fromlist=[''])
                        working_files.append(file_path)
                    else:
                        # Para arquivos TypeScript, apenas verificar se existem
                        working_files.append(file_path)
                except Exception as e:
                    broken_files.append((file_path, str(e)))
            else:
                broken_files.append((file_path, "File not found"))
        
        success = len(broken_files) == 0
        message = f"Code compatibility: {len(working_files)}/{len(critical_files)} files"
        
        details = {
            "working_files": working_files,
            "broken_files": [f"{file}: {error}" for file, error in broken_files]
        }
        
        return ValidationResult(
            name="Code Compatibility",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def validate_configuration_files(self) -> ValidationResult:
        """Valida arquivos de configuração"""
        start_time = time.time()
        
        config_files = [
            (".env.example", "Environment template"),
            ("requirements.txt", "Python dependencies"),
            ("frontend/package.json", "Node.js dependencies"),
            ("README.md", "Documentation"),
            (".gitignore", "Git ignore rules")
        ]
        
        existing_configs = []
        missing_configs = []
        
        for file_path, description in config_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_configs.append((file_path, description))
            else:
                missing_configs.append((file_path, description))
        
        success = len(missing_configs) <= 1  # Tolerância para 1 arquivo faltando
        message = f"Configuration files: {len(existing_configs)}/{len(config_files)} present"
        
        details = {
            "existing_configs": [file for file, _ in existing_configs],
            "missing_configs": [file for file, _ in missing_configs]
        }
        
        return ValidationResult(
            name="Configuration Files",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def validate_test_structure(self) -> ValidationResult:
        """Valida estrutura de testes"""
        start_time = time.time()
        
        test_dirs = [
            "backend/tests/unit",
            "backend/tests/integration",
            "frontend/src/__tests__"
        ]
        
        existing_test_dirs = []
        missing_test_dirs = []
        
        for test_dir in test_dirs:
            full_path = self.project_root / test_dir
            if full_path.exists() and full_path.is_dir():
                existing_test_dirs.append(test_dir)
            else:
                missing_test_dirs.append(test_dir)
        
        # Contar arquivos de teste existentes
        test_files_count = 0
        for test_dir in existing_test_dirs:
            test_path = self.project_root / test_dir
            test_files_count += len(list(test_path.rglob("test_*.py"))) + len(list(test_path.rglob("*.test.ts")))
        
        success = len(existing_test_dirs) >= 2  # Pelo menos 2 diretórios de teste
        message = f"Test structure: {len(existing_test_dirs)} directories, {test_files_count} test files"
        
        details = {
            "test_directories": existing_test_dirs,
            "test_files_count": test_files_count,
            "missing_directories": missing_test_dirs
        }
        
        return ValidationResult(
            name="Test Structure",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def validate_git_status(self) -> ValidationResult:
        """Valida status do Git"""
        start_time = time.time()
        
        try:
            # Verificar se é um repositório Git
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                modified_count = len([f for f in modified_files if f])
                
                # Verificar se há backup branch
                branch_result = subprocess.run(
                    ["git", "branch", "--list", "backup-pre-refactoring"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                has_backup_branch = bool(branch_result.stdout.strip())
                
                success = True  # Git status sempre é informativo
                message = f"Git status: {modified_count} modified files"
                
                details = {
                    "modified_files_count": modified_count,
                    "has_backup_branch": has_backup_branch,
                    "git_clean": modified_count == 0
                }
            else:
                success = False
                message = "Not a Git repository or Git error"
                details = {"error": result.stderr}
                
        except Exception as e:
            success = False
            message = f"Git validation failed: {str(e)}"
            details = {"error": str(e)}
        
        return ValidationResult(
            name="Git Status",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def run_basic_tests(self) -> ValidationResult:
        """Executa testes básicos se disponíveis"""
        start_time = time.time()
        
        test_commands = [
            ("python -c 'import sys; print(f\"Python {sys.version}\")'', "Python version"),
            ("python -c 'import backend; print(\"Backend module OK\")'', "Backend import"),
        ]
        
        successful_tests = []
        failed_tests = []
        
        for command, description in test_commands:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    successful_tests.append((description, result.stdout.strip()))
                else:
                    failed_tests.append((description, result.stderr.strip()))
                    
            except Exception as e:
                failed_tests.append((description, str(e)))
        
        success = len(failed_tests) == 0
        message = f"Basic tests: {len(successful_tests)}/{len(test_commands)} passed"
        
        details = {
            "successful_tests": [desc for desc, _ in successful_tests],
            "failed_tests": [f"{desc}: {error}" for desc, error in failed_tests]
        }
        
        return ValidationResult(
            name="Basic Tests",
            success=success,
            message=message,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def generate_validation_report(self) -> str:
        """Gera relatório de validação"""
        total_validations = len(self.results)
        successful_validations = len([r for r in self.results if r.success])
        total_time = sum(r.execution_time for r in self.results)
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_validations": total_validations,
                "successful_validations": successful_validations,
                "failed_validations": total_validations - successful_validations,
                "success_rate": (successful_validations / total_validations * 100) if total_validations > 0 else 0,
                "total_execution_time": total_time
            },
            "validations": [
                {
                    "name": r.name,
                    "success": r.success,
                    "message": r.message,
                    "details": r.details,
                    "execution_time": r.execution_time
                }
                for r in self.results
            ]
        }
        
        report_file = self.project_root / "validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(report_file)
    
    def run_all_validations(self) -> bool:
        """Executa todas as validações"""
        print("🔍 Iniciando validação da nova arquitetura...\n")
        
        validations = [
            self.validate_directory_structure,
            self.validate_python_imports,
            self.validate_existing_code_compatibility,
            self.validate_configuration_files,
            self.validate_test_structure,
            self.validate_git_status,
            self.run_basic_tests
        ]
        
        for validation_func in validations:
            try:
                result = validation_func()
                self.log_result(result)
            except Exception as e:
                error_result = ValidationResult(
                    name=validation_func.__name__,
                    success=False,
                    message=f"Validation error: {str(e)}",
                    execution_time=0.0
                )
                self.log_result(error_result)
        
        # Gerar relatório
        report_file = self.generate_validation_report()
        
        # Resumo final
        successful_count = len([r for r in self.results if r.success])
        total_count = len(self.results)
        success_rate = (successful_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n📊 Resumo da Validação:")
        print(f"   ✅ Sucessos: {successful_count}/{total_count} ({success_rate:.1f}%)")
        print(f"   📄 Relatório: {report_file}")
        
        if success_rate >= 80:
            print("\n🎉 Validação bem-sucedida! A nova arquitetura está pronta.")
            print("\n📋 Próximos passos:")
            print("   1. Implementar entidades de domínio")
            print("   2. Criar casos de uso")
            print("   3. Migrar código existente gradualmente")
            print("   4. Executar testes de integração")
            return True
        else:
            print("\n⚠️  Validação com problemas. Verifique os erros acima.")
            print("\n🔧 Ações recomendadas:")
            print("   1. Instalar dependências faltantes")
            print("   2. Corrigir estrutura de diretórios")
            print("   3. Verificar configurações")
            print("   4. Executar novamente a validação")
            return False

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLPI Dashboard Architecture Validator")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report-only", action="store_true", help="Generate report without running validations")
    
    args = parser.parse_args()
    
    validator = ArchitectureValidator(args.project_root)
    
    if args.report_only:
        # Apenas gerar relatório se já existir
        report_file = validator.project_root / "validation_report.json"
        if report_file.exists():
            print(f"📄 Relatório existente: {report_file}")
        else:
            print("❌ Nenhum relatório encontrado. Execute a validação primeiro.")
        return
    
    # Executar validações
    success = validator.run_all_validations()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()