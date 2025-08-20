#!/usr/bin/env python3
"""
Configuração para Migração Arquitetural
Script para configurar e validar a nova arquitetura do GLPI Dashboard
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MigrationConfig:
    """Configuração da migração"""
    project_root: Path
    backup_dir: Path
    new_structure_dir: Path
    preserve_files: List[str]
    critical_files: List[str]
    test_commands: List[str]
    validation_endpoints: List[str]

class MigrationManager:
    """Gerenciador da migração arquitetural"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.config = self._load_config()
        self.migration_log = []
        
    def _load_config(self) -> MigrationConfig:
        """Carrega configuração da migração"""
        return MigrationConfig(
            project_root=self.project_root,
            backup_dir=self.project_root / "backup_pre_migration",
            new_structure_dir=self.project_root / "new_architecture",
            preserve_files=[
                ".env",
                ".env.example", 
                "README.md",
                "requirements.txt",
                "package.json",
                ".gitignore",
                "RELATORIO_AUDITORIA_CONSISTENCIA.md",
                "TESTING_README.md"
            ],
            critical_files=[
                "backend/glpi_service.py",
                "backend/api_service.py", 
                "frontend/src/App.tsx",
                "frontend/src/hooks/useDashboard.ts"
            ],
            test_commands=[
                "python -m pytest backend/tests/ -v",
                "npm test -- --watchAll=false",
                "python -c 'import backend.glpi_service; print(\"Backend OK\")'",
                "npm run build"
            ],
            validation_endpoints=[
                "/api/dashboard/metrics",
                "/api/dashboard/ranking", 
                "/api/dashboard/status"
            ]
        )
    
    def log_action(self, action: str, status: str = "INFO", details: str = ""):
        """Registra ação no log"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.migration_log.append(log_entry)
        print(f"[{status}] {action}: {details}")
    
    def create_backup(self) -> bool:
        """Cria backup completo do projeto atual"""
        try:
            self.log_action("Creating backup", "INFO", f"Backup directory: {self.config.backup_dir}")
            
            if self.config.backup_dir.exists():
                shutil.rmtree(self.config.backup_dir)
            
            # Backup dos arquivos críticos
            self.config.backup_dir.mkdir(parents=True)
            
            for file_path in self.config.critical_files:
                source = self.project_root / file_path
                if source.exists():
                    dest = self.config.backup_dir / file_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    self.log_action("Backup file", "SUCCESS", str(file_path))
            
            # Backup de configurações
            for file_name in self.config.preserve_files:
                source = self.project_root / file_name
                if source.exists():
                    dest = self.config.backup_dir / file_name
                    shutil.copy2(source, dest)
                    self.log_action("Backup config", "SUCCESS", file_name)
            
            return True
            
        except Exception as e:
            self.log_action("Backup failed", "ERROR", str(e))
            return False
    
    def validate_current_state(self) -> Dict[str, bool]:
        """Valida estado atual do projeto"""
        validation_results = {}
        
        # Verificar arquivos críticos
        for file_path in self.config.critical_files:
            file_exists = (self.project_root / file_path).exists()
            validation_results[f"file_{file_path}"] = file_exists
            status = "SUCCESS" if file_exists else "WARNING"
            self.log_action("Validate file", status, file_path)
        
        # Verificar dependências Python
        try:
            import requests
            import fastapi
            validation_results["python_deps"] = True
            self.log_action("Python dependencies", "SUCCESS", "Core packages available")
        except ImportError as e:
            validation_results["python_deps"] = False
            self.log_action("Python dependencies", "WARNING", f"Missing: {e}")
        
        # Verificar Node.js dependencies
        package_json = self.project_root / "frontend" / "package.json"
        if package_json.exists():
            validation_results["node_config"] = True
            self.log_action("Node.js config", "SUCCESS", "package.json found")
        else:
            validation_results["node_config"] = False
            self.log_action("Node.js config", "WARNING", "package.json not found")
        
        return validation_results
    
    def create_new_structure(self) -> bool:
        """Cria nova estrutura de diretórios"""
        try:
            self.log_action("Creating new structure", "INFO", "Starting directory creation")
            
            # Estrutura do backend
            backend_dirs = [
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
                "backend/core/infrastructure/config",
                "backend/api/v1/endpoints",
                "backend/api/v1/dependencies",
                "backend/api/v1/middleware",
                "backend/tests/unit/domain",
                "backend/tests/unit/application", 
                "backend/tests/unit/infrastructure",
                "backend/tests/integration",
                "backend/tests/e2e"
            ]
            
            # Estrutura do frontend
            frontend_dirs = [
                "frontend/src/features/dashboard/components",
                "frontend/src/features/dashboard/hooks",
                "frontend/src/features/dashboard/services",
                "frontend/src/features/dashboard/types",
                "frontend/src/features/metrics/components",
                "frontend/src/features/metrics/hooks",
                "frontend/src/features/ranking/components",
                "frontend/src/features/ranking/hooks",
                "frontend/src/shared/components/ui",
                "frontend/src/shared/hooks",
                "frontend/src/shared/services",
                "frontend/src/shared/types",
                "frontend/src/shared/utils",
                "frontend/src/store/slices",
                "frontend/src/store/middleware"
            ]
            
            all_dirs = backend_dirs + frontend_dirs
            
            for dir_path in all_dirs:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                
                # Criar __init__.py para diretórios Python
                if "backend" in dir_path and not dir_path.endswith("tests"):
                    init_file = full_path / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("")
                
                # Criar index.ts para diretórios TypeScript
                if "frontend" in dir_path and "components" in dir_path:
                    index_file = full_path / "index.ts"
                    if not index_file.exists():
                        index_file.write_text("// Export components from this directory\n")
                
                self.log_action("Create directory", "SUCCESS", dir_path)
            
            return True
            
        except Exception as e:
            self.log_action("Structure creation failed", "ERROR", str(e))
            return False
    
    def generate_migration_report(self) -> str:
        """Gera relatório da migração"""
        report = {
            "migration_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "backup_location": str(self.config.backup_dir),
            "migration_log": self.migration_log,
            "summary": {
                "total_actions": len(self.migration_log),
                "successful_actions": len([log for log in self.migration_log if log["status"] == "SUCCESS"]),
                "warnings": len([log for log in self.migration_log if log["status"] == "WARNING"]),
                "errors": len([log for log in self.migration_log if log["status"] == "ERROR"])
            }
        }
        
        report_file = self.project_root / "migration_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_action("Generate report", "SUCCESS", str(report_file))
        return str(report_file)
    
    def run_migration(self, phase: str = "all") -> bool:
        """Executa migração completa ou por fase"""
        self.log_action("Starting migration", "INFO", f"Phase: {phase}")
        
        success = True
        
        if phase in ["all", "backup"]:
            if not self.create_backup():
                success = False
        
        if phase in ["all", "validate"]:
            validation_results = self.validate_current_state()
            if not all(validation_results.values()):
                self.log_action("Validation warnings", "WARNING", "Some validations failed")
        
        if phase in ["all", "structure"]:
            if not self.create_new_structure():
                success = False
        
        # Gerar relatório
        report_file = self.generate_migration_report()
        
        if success:
            self.log_action("Migration completed", "SUCCESS", f"Report: {report_file}")
        else:
            self.log_action("Migration failed", "ERROR", "Check logs for details")
        
        return success

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLPI Dashboard Migration Tool")
    parser.add_argument("--phase", choices=["all", "backup", "validate", "structure"], 
                       default="all", help="Migration phase to execute")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("📁 Project structure analysis:")
        
        project_root = Path(args.project_root or os.getcwd())
        
        # Mostrar estrutura atual
        print("\n📂 Current structure:")
        for item in project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                print(f"  📁 {item.name}/")
                for subitem in item.iterdir():
                    if subitem.is_file() and subitem.suffix in ['.py', '.ts', '.tsx', '.js']:
                        print(f"    📄 {subitem.name}")
        
        print("\n✅ Dry run completed - use without --dry-run to execute")
        return
    
    # Executar migração
    manager = MigrationManager(args.project_root)
    success = manager.run_migration(args.phase)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📋 Next steps:")
        print("  1. Review migration_report.json")
        print("  2. Install new dependencies: pip install fastapi uvicorn aiohttp redis pydantic")
        print("  3. Run validation script: python validation_script.py")
        print("  4. Start implementing domain entities")
    else:
        print("\n❌ Migration failed - check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    main()