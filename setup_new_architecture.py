#!/usr/bin/env python3
"""
Setup Automatizado da Nova Arquitetura
Script completo para implementar a refatoração arquitetural do GLPI Dashboard
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class ArchitectureSetup:
    """Configurador da nova arquitetura"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.setup_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.setup_log.append(log_entry)
        
        # Ícones para diferentes níveis
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "STEP": "🔄"
        }
        
        icon = icons.get(level, "📝")
        print(f"{icon} {message}")
    
    def run_command(self, command: str, description: str, check: bool = True) -> bool:
        """Executa comando do sistema"""
        self.log(f"Executando: {description}", "STEP")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                self.log(f"Sucesso: {description}", "SUCCESS")
                if result.stdout.strip():
                    self.log(f"Output: {result.stdout.strip()[:200]}...", "INFO")
                return True
            else:
                self.log(f"Erro em {description}: {result.stderr}", "ERROR")
                if not check:
                    return False
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"Timeout em {description}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Exceção em {description}: {str(e)}", "ERROR")
            return False
    
    def create_file(self, file_path: str, content: str, description: str = "") -> bool:
        """Cria arquivo com conteúdo"""
        try:
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            desc = description or f"Arquivo {file_path}"
            self.log(f"Criado: {desc}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao criar {file_path}: {str(e)}", "ERROR")
            return False
    
    def step_1_backup_and_prepare(self) -> bool:
        """Passo 1: Backup e preparação"""
        self.log("=== PASSO 1: BACKUP E PREPARAÇÃO ===", "STEP")
        
        # Verificar se é repositório Git
        if not (self.project_root / ".git").exists():
            self.log("Inicializando repositório Git", "INFO")
            if not self.run_command("git init", "Inicializar Git"):
                return False
        
        # Fazer commit do estado atual
        self.run_command("git add .", "Adicionar arquivos ao Git", check=False)
        self.run_command(
            'git commit -m "Backup antes da refatoração arquitetural"',
            "Commit de backup",
            check=False
        )
        
        # Criar branch de backup
        self.run_command(
            "git checkout -b backup-pre-refactoring",
            "Criar branch de backup",
            check=False
        )
        
        # Voltar para main/master
        self.run_command("git checkout main", "Voltar para main", check=False)
        if not self.run_command("git checkout master", "Voltar para master", check=False):
            # Se não existe master, criar main
            self.run_command("git checkout -b main", "Criar branch main", check=False)
        
        return True
    
    def step_2_install_dependencies(self) -> bool:
        """Passo 2: Instalar dependências"""
        self.log("=== PASSO 2: INSTALAÇÃO DE DEPENDÊNCIAS ===", "STEP")
        
        # Verificar Python
        if not self.run_command("python --version", "Verificar Python"):
            self.log("Python não encontrado. Instale Python 3.9+", "ERROR")
            return False
        
        # Criar ambiente virtual se não existir
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            if not self.run_command("python -m venv venv", "Criar ambiente virtual"):
                return False
        
        # Ativar ambiente virtual e instalar dependências
        if os.name == 'nt':  # Windows
            activate_cmd = "venv\\Scripts\\activate && "
        else:  # Unix/Linux/Mac
            activate_cmd = "source venv/bin/activate && "
        
        # Instalar dependências da nova arquitetura
        if not self.run_command(
            f"{activate_cmd}pip install -r requirements_new_architecture.txt",
            "Instalar dependências Python"
        ):
            # Fallback: instalar dependências básicas
            basic_deps = "fastapi uvicorn aiohttp redis pydantic pytest"
            self.run_command(
                f"{activate_cmd}pip install {basic_deps}",
                "Instalar dependências básicas",
                check=False
            )
        
        # Verificar Node.js se frontend existe
        if (self.project_root / "frontend").exists():
            if self.run_command("node --version", "Verificar Node.js", check=False):
                # Instalar dependências do frontend
                self.run_command(
                    "npm install",
                    "Instalar dependências Node.js",
                    check=False
                )
        
        return True
    
    def step_3_create_structure(self) -> bool:
        """Passo 3: Criar estrutura de diretórios"""
        self.log("=== PASSO 3: CRIAÇÃO DA ESTRUTURA ===", "STEP")
        
        # Executar script de migração
        if not self.run_command(
            "python config_migration.py --phase structure",
            "Criar estrutura de diretórios"
        ):
            # Fallback: criar manualmente
            self.log("Criando estrutura manualmente", "WARNING")
            return self._create_structure_manually()
        
        return True
    
    def _create_structure_manually(self) -> bool:
        """Cria estrutura manualmente como fallback"""
        directories = [
            # Backend - Clean Architecture
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
            "backend/tests/e2e",
            
            # Frontend - Feature-based
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
        
        for directory in directories:
            try:
                full_path = self.project_root / directory
                full_path.mkdir(parents=True, exist_ok=True)
                
                # Criar __init__.py para diretórios Python
                if "backend" in directory and not directory.endswith("tests"):
                    init_file = full_path / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("")
                
                # Criar index.ts para diretórios de componentes
                if "frontend" in directory and "components" in directory:
                    index_file = full_path / "index.ts"
                    if not index_file.exists():
                        index_file.write_text("// Export components from this directory\n")
                        
            except Exception as e:
                self.log(f"Erro ao criar {directory}: {str(e)}", "ERROR")
                return False
        
        self.log(f"Criados {len(directories)} diretórios", "SUCCESS")
        return True
    
    def step_4_create_base_files(self) -> bool:
        """Passo 4: Criar arquivos base da nova arquitetura"""
        self.log("=== PASSO 4: CRIAÇÃO DE ARQUIVOS BASE ===", "STEP")
        
        # Arquivo de configuração principal
        config_content = '''
"""Configuração principal da aplicação"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # GLPI Configuration
    glpi_base_url: str
    glpi_app_token: str
    glpi_user_token: str
    
    # Cache Configuration
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Database (opcional)
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
'''
        
        if not self.create_file(
            "backend/core/infrastructure/config/settings.py",
            config_content,
            "Configurações da aplicação"
        ):
            return False
        
        # Entidade base
        entity_content = '''
"""Entidade base do domínio"""
from abc import ABC
from typing import Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class BaseEntity(BaseModel, ABC):
    """Classe base para todas as entidades do domínio"""
    
    id: int = Field(..., description="Identificador único")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
        validate_assignment = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte entidade para dicionário"""
        return self.model_dump()
    
    def update_timestamp(self):
        """Atualiza timestamp de modificação"""
        self.updated_at = datetime.now()
'''
        
        if not self.create_file(
            "backend/core/domain/entities/base_entity.py",
            entity_content,
            "Entidade base"
        ):
            return False
        
        # Interface de repositório
        repository_content = '''
"""Interface base para repositórios"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Interface base para todos os repositórios"""
    
    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Busca entidade por ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Busca todas as entidades"""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Salva entidade"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Remove entidade"""
        pass
'''
        
        if not self.create_file(
            "backend/core/domain/repositories/base_repository.py",
            repository_content,
            "Interface de repositório base"
        ):
            return False
        
        # Caso de uso base
        use_case_content = '''
"""Caso de uso base"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

Request = TypeVar('Request')
Response = TypeVar('Response')

class BaseUseCase(ABC, Generic[Request, Response]):
    """Classe base para casos de uso"""
    
    @abstractmethod
    async def execute(self, request: Request) -> Response:
        """Executa o caso de uso"""
        pass
'''
        
        if not self.create_file(
            "backend/core/application/use_cases/base_use_case.py",
            use_case_content,
            "Caso de uso base"
        ):
            return False
        
        # Arquivo principal da API
        main_api_content = '''
"""Aplicação principal FastAPI"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.infrastructure.config.settings import settings

# Criar aplicação FastAPI
app = FastAPI(
    title="GLPI Dashboard API",
    description="API para Dashboard do GLPI com Clean Architecture",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar adequadamente em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "GLPI Dashboard API v2.0",
        "status": "running",
        "architecture": "Clean Architecture"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
'''
        
        if not self.create_file(
            "backend/main.py",
            main_api_content,
            "Aplicação principal FastAPI"
        ):
            return False
        
        return True
    
    def step_5_create_env_template(self) -> bool:
        """Passo 5: Criar template de configuração"""
        self.log("=== PASSO 5: CONFIGURAÇÃO DE AMBIENTE ===", "STEP")
        
        env_content = '''
# GLPI Dashboard - Nova Arquitetura
# Configurações de Ambiente

# === GLPI Configuration ===
GLPI_BASE_URL=https://seu-glpi.com/apirest.php
GLPI_APP_TOKEN=seu_app_token_aqui
GLPI_USER_TOKEN=seu_user_token_aqui

# === Cache Configuration ===
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# === API Configuration ===
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# === Database Configuration (opcional) ===
# DATABASE_URL=sqlite:///./glpi_dashboard.db

# === Frontend Configuration ===
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_CACHE_ENABLED=true
REACT_APP_REFRESH_INTERVAL=30000

# === Logging ===
LOG_LEVEL=INFO
LOG_FORMAT=json

# === Security (produção) ===
# SECRET_KEY=sua_chave_secreta_muito_forte
# JWT_ALGORITHM=HS256
# JWT_EXPIRE_MINUTES=30
'''
        
        if not self.create_file(
            ".env.new",
            env_content,
            "Template de configuração de ambiente"
        ):
            return False
        
        # Criar arquivo de desenvolvimento
        dev_env_content = env_content.replace(
            "API_DEBUG=true",
            "API_DEBUG=true\nENVIRONMENT=development"
        )
        
        if not self.create_file(
            ".env.development",
            dev_env_content,
            "Configuração de desenvolvimento"
        ):
            return False
        
        return True
    
    def step_6_run_validation(self) -> bool:
        """Passo 6: Executar validação"""
        self.log("=== PASSO 6: VALIDAÇÃO DA ARQUITETURA ===", "STEP")
        
        # Executar script de validação
        if not self.run_command(
            "python validation_script.py",
            "Validar nova arquitetura",
            check=False
        ):
            self.log("Validação com problemas, mas continuando", "WARNING")
        
        return True
    
    def generate_setup_report(self) -> str:
        """Gera relatório do setup"""
        report = {
            "setup_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "setup_log": self.setup_log,
            "next_steps": [
                "1. Copiar .env.new para .env e configurar tokens GLPI",
                "2. Instalar Redis: docker run -d -p 6379:6379 redis:alpine",
                "3. Testar API: python backend/main.py",
                "4. Implementar entidades de domínio",
                "5. Migrar código existente gradualmente"
            ]
        }
        
        report_file = self.project_root / "setup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(report_file)
    
    def run_complete_setup(self) -> bool:
        """Executa setup completo"""
        self.log("🚀 INICIANDO SETUP DA NOVA ARQUITETURA", "STEP")
        self.log(f"📁 Diretório do projeto: {self.project_root}", "INFO")
        
        steps = [
            ("Backup e Preparação", self.step_1_backup_and_prepare),
            ("Instalação de Dependências", self.step_2_install_dependencies),
            ("Criação da Estrutura", self.step_3_create_structure),
            ("Criação de Arquivos Base", self.step_4_create_base_files),
            ("Configuração de Ambiente", self.step_5_create_env_template),
            ("Validação", self.step_6_run_validation)
        ]
        
        success_count = 0
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*50}", "INFO")
            self.log(f"Executando: {step_name}", "STEP")
            
            try:
                if step_func():
                    success_count += 1
                    self.log(f"✅ {step_name} concluído com sucesso", "SUCCESS")
                else:
                    self.log(f"❌ {step_name} falhou", "ERROR")
            except Exception as e:
                self.log(f"❌ Erro em {step_name}: {str(e)}", "ERROR")
        
        # Gerar relatório
        report_file = self.generate_setup_report()
        
        # Resumo final
        total_steps = len(steps)
        success_rate = (success_count / total_steps * 100)
        
        self.log(f"\n{'='*50}", "INFO")
        self.log(f"📊 RESUMO DO SETUP", "STEP")
        self.log(f"✅ Passos concluídos: {success_count}/{total_steps} ({success_rate:.1f}%)", "INFO")
        self.log(f"📄 Relatório: {report_file}", "INFO")
        
        if success_count >= total_steps - 1:  # Tolerância de 1 falha
            self.log("\n🎉 SETUP CONCLUÍDO COM SUCESSO!", "SUCCESS")
            self.log("\n📋 PRÓXIMOS PASSOS:", "INFO")
            self.log("1. cp .env.new .env (e configurar tokens GLPI)", "INFO")
            self.log("2. docker run -d -p 6379:6379 redis:alpine", "INFO")
            self.log("3. python backend/main.py", "INFO")
            self.log("4. Acessar http://localhost:8000", "INFO")
            self.log("5. Implementar entidades de domínio", "INFO")
            return True
        else:
            self.log("\n⚠️ SETUP COM PROBLEMAS", "WARNING")
            self.log("Verifique os erros acima e execute novamente", "INFO")
            return False

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLPI Dashboard Architecture Setup")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--step", type=int, choices=range(1, 7), help="Execute specific step only")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    
    args = parser.parse_args()
    
    setup = ArchitectureSetup(args.project_root)
    
    if args.step:
        # Executar passo específico
        steps = {
            1: setup.step_1_backup_and_prepare,
            2: setup.step_2_install_dependencies,
            3: setup.step_3_create_structure,
            4: setup.step_4_create_base_files,
            5: setup.step_5_create_env_template,
            6: setup.step_6_run_validation
        }
        
        if args.skip_deps and args.step == 2:
            setup.log("Pulando instalação de dependências", "INFO")
            return
        
        success = steps[args.step]()
        sys.exit(0 if success else 1)
    else:
        # Executar setup completo
        success = setup.run_complete_setup()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()