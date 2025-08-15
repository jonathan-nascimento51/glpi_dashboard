#!/usr/bin/env python3
"""
Script para reorganizar a estrutura de diretórios do projeto GLPI Dashboard
Implementa uma estrutura limpa e consistente seguindo boas práticas.
"""

import os
import shutil
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StructureReorganizer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.changes_made = []
        
    def log_change(self, action: str, source: str = None, target: str = None):
        """Registra mudanças realizadas"""
        if source and target:
            message = f"{action}: {source} -> {target}"
        elif source:
            message = f"{action}: {source}"
        else:
            message = action
            
        logger.info(message)
        self.changes_made.append(message)
    
    def create_directory_if_not_exists(self, path: Path):
        """Cria diretório se náo existir"""
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.log_change("CREATED_DIR", str(path))
            return True
        return False
    
    def move_file_safely(self, source: Path, target: Path):
        """Move arquivo de forma segura, criando diretórios necessários"""
        if not source.exists():
            logger.warning(f"Source file does not exist: {source}")
            return False
            
        # Criar diretório de destino se necessário
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Se o arquivo de destino já existe, fazer backup
        if target.exists():
            backup_path = target.with_suffix(target.suffix + '.backup')
            shutil.move(str(target), str(backup_path))
            self.log_change("BACKUP", str(target), str(backup_path))
        
        # Mover arquivo
        shutil.move(str(source), str(target))
        self.log_change("MOVED", str(source), str(target))
        return True
    
    def remove_empty_directories(self):
        """Remove diretórios vazios"""
        empty_dirs = []
        
        # Encontrar diretórios vazios
        for root, dirs, files in os.walk(self.backend_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if dir_path.exists() and not any(dir_path.iterdir()):
                    empty_dirs.append(dir_path)
        
        # Remover diretórios vazios
        for empty_dir in empty_dirs:
            try:
                empty_dir.rmdir()
                self.log_change("REMOVED_EMPTY_DIR", str(empty_dir))
            except OSError as e:
                logger.warning(f"Could not remove {empty_dir}: {e}")
    
    def reorganize_backend_structure(self):
        """Reorganiza a estrutura do backend"""
        logger.info("=== Iniciando reorganizaçáo da estrutura do backend ===")
        
        # 1. Criar estrutura principal se náo existir
        main_dirs = [
            self.backend_dir / "app",
            self.backend_dir / "app" / "api",
            self.backend_dir / "app" / "core",
            self.backend_dir / "app" / "models",
            self.backend_dir / "app" / "services",
            self.backend_dir / "app" / "schemas",
            self.backend_dir / "app" / "utils",
        ]
        
        for dir_path in main_dirs:
            self.create_directory_if_not_exists(dir_path)
        
        # 2. Mover arquivos de configuraçáo para app/core
        config_moves = [
            (self.backend_dir / "config" / "settings.py", self.backend_dir / "app" / "core" / "config.py"),
            (self.backend_dir / "config" / "logging_config.py", self.backend_dir / "app" / "core" / "logging.py"),
        ]
        
        for source, target in config_moves:
            if source.exists():
                self.move_file_safely(source, target)
        
        # 3. Mover serviços para app/services
        services_dir = self.backend_dir / "services"
        app_services_dir = self.backend_dir / "app" / "services"
        
        if services_dir.exists():
            for service_file in services_dir.glob("*.py"):
                if service_file.name != "__init__.py":
                    target = app_services_dir / service_file.name
                    self.move_file_safely(service_file, target)
        
        # 4. Mover schemas para app/schemas
        schemas_dir = self.backend_dir / "schemas"
        app_schemas_dir = self.backend_dir / "app" / "schemas"
        
        if schemas_dir.exists():
            for schema_file in schemas_dir.glob("*.py"):
                if schema_file.name != "__init__.py":
                    target = app_schemas_dir / schema_file.name
                    self.move_file_safely(schema_file, target)
        
        # 5. Mover utils para app/utils
        utils_dir = self.backend_dir / "utils"
        app_utils_dir = self.backend_dir / "app" / "utils"
        
        if utils_dir.exists():
            for util_file in utils_dir.glob("*.py"):
                if util_file.name != "__init__.py":
                    target = app_utils_dir / util_file.name
                    self.move_file_safely(util_file, target)
        
        # 6. Mover rotas da API para app/api
        api_dir = self.backend_dir / "api"
        app_api_dir = self.backend_dir / "app" / "api"
        
        if api_dir.exists():
            for api_file in api_dir.glob("*.py"):
                if api_file.name != "__init__.py":
                    target = app_api_dir / api_file.name
                    self.move_file_safely(api_file, target)
            
            # Mover subdiretórios da API
            for subdir in api_dir.iterdir():
                if subdir.is_dir() and subdir.name != "__pycache__":
                    target = app_api_dir / subdir.name
                    if not target.exists():
                        shutil.move(str(subdir), str(target))
                        self.log_change("MOVED_DIR", str(subdir), str(target))
        
        # 7. Criar arquivos __init__.py necessários
        init_files = [
            self.backend_dir / "app" / "__init__.py",
            self.backend_dir / "app" / "api" / "__init__.py",
            self.backend_dir / "app" / "core" / "__init__.py",
            self.backend_dir / "app" / "models" / "__init__.py",
            self.backend_dir / "app" / "services" / "__init__.py",
            self.backend_dir / "app" / "schemas" / "__init__.py",
            self.backend_dir / "app" / "utils" / "__init__.py",
        ]
        
        for init_file in init_files:
            if not init_file.exists():
                init_file.write_text("")
                self.log_change("CREATED", str(init_file))
        
        # 8. Criar main.py no backend se náo existir
        main_py = self.backend_dir / "main.py"
        if not main_py.exists():
            main_content = '''#!/usr/bin/env python3
"""
Ponto de entrada principal para o backend do GLPI Dashboard
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"Iniciando servidor em http://{host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
'''
            main_py.write_text(main_content, encoding='utf-8')
            self.log_change("CREATED", str(main_py))
    
    def cleanup_old_structure(self):
        """Remove diretórios antigos vazios após reorganizaçáo"""
        logger.info("=== Limpando estrutura antiga ===")
        
        # Diretórios que podem ser removidos se estiverem vazios
        old_dirs = [
            self.backend_dir / "config",
            self.backend_dir / "services",
            self.backend_dir / "schemas",
            self.backend_dir / "utils",
            self.backend_dir / "api",
            self.backend_dir / "routes",
            self.backend_dir / "models",
        ]
        
        for old_dir in old_dirs:
            if old_dir.exists() and not any(old_dir.iterdir()):
                try:
                    old_dir.rmdir()
                    self.log_change("REMOVED_EMPTY_DIR", str(old_dir))
                except OSError as e:
                    logger.warning(f"Could not remove {old_dir}: {e}")
    
    def generate_report(self):
        """Gera relatório das mudanças realizadas"""
        logger.info("=== RELATÓRIO DE REORGANIZAÇáO ===")
        logger.info(f"Total de mudanças: {len(self.changes_made)}")
        
        for change in self.changes_made:
            logger.info(f"  - {change}")
        
        # Salvar relatório em arquivo
        report_file = self.project_root / "reorganization_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RELATORIO DE REORGANIZACAO DA ESTRUTURA\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de mudancas: {len(self.changes_made)}\n\n")
            
            for change in self.changes_made:
                f.write(f"- {change}\n")
        
        logger.info(f"Relatório salvo em: {report_file}")
    
    def run(self):
        """Executa a reorganizaçáo completa"""
        try:
            logger.info("Iniciando reorganizacao da estrutura do projeto")
            
            # Executar reorganizaçáo
            self.reorganize_backend_structure()
            self.cleanup_old_structure()
            self.remove_empty_directories()
            
            # Gerar relatório
            self.generate_report()
            
            logger.info("Reorganizacao concluida com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante reorganizacao: {e}")
            return False

if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    # Diretório do projeto
    project_root = Path(__file__).parent
    
    # Criar reorganizador
    reorganizer = StructureReorganizer(str(project_root))
    
    # Executar reorganizaçáo
    success = reorganizer.run()
    
    if success:
        print("\nReorganizacao concluida com sucesso!")
        print("Verifique o arquivo 'reorganization_report.txt' para detalhes")
    else:
        print("\nFalha na reorganizacao. Verifique os logs acima.")
        sys.exit(1)
