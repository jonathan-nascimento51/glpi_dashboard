#!/usr/bin/env python3
"""
Script de Atualização Automática da Documentação

Este script mantém a documentação viva e contextual sempre atualizada,
coletando informações do sistema e atualizando os arquivos de documentação.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class DocumentationUpdater:
    """Atualizador automático de documentação viva."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def get_system_info(self) -> Dict[str, Any]:
        """Coleta informações atuais do sistema."""
        info = {
            "timestamp": self.timestamp,
            "git_commit": self._get_git_commit(),
            "dependencies": self._get_dependencies(),
            "test_status": self._get_test_status(),
            "validation_results": self._get_validation_results(),
            "knowledge_graph_stats": self._get_knowledge_stats()
        }
        return info
    
    def _get_git_commit(self) -> str:
        """Obtém o commit atual do Git."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    def _get_dependencies(self) -> Dict[str, str]:
        """Analisa dependências do projeto."""
        deps = {}
        
        # Backend dependencies
        backend_pyproject = self.project_root / "backend" / "pyproject.toml"
        if backend_pyproject.exists():
            deps["backend"] = "pyproject.toml found"
        
        # Frontend dependencies
        frontend_package = self.project_root / "frontend" / "package.json"
        if frontend_package.exists():
            try:
                with open(frontend_package) as f:
                    package_data = json.load(f)
                    deps["frontend"] = f"React {package_data.get('dependencies', {}).get('react', 'unknown')}"
            except Exception:
                deps["frontend"] = "package.json found"
        
        return deps
    
    def _get_test_status(self) -> Dict[str, str]:
        """Verifica status dos testes."""
        status = {}
        
        # Backend tests
        backend_tests = self.project_root / "backend" / "tests"
        if backend_tests.exists():
            test_files = list(backend_tests.rglob("test_*.py"))
            status["backend_tests"] = f"{len(test_files)} arquivos de teste"
        
        # Frontend tests
        frontend_tests = self.project_root / "frontend" / "src" / "__tests__"
        if frontend_tests.exists():
            test_files = list(frontend_tests.rglob("*.test.*"))
            status["frontend_tests"] = f"{len(test_files)} arquivos de teste"
        
        return status
    
    def _get_validation_results(self) -> Dict[str, Any]:
        """Obtém resultados da última validação."""
        artifacts_dir = self.project_root / "artifacts"
        if not artifacts_dir.exists():
            return {"status": "no_artifacts"}
        
        # Busca o arquivo de validação mais recente
        validation_files = list(artifacts_dir.glob("system_validation_*.json"))
        if not validation_files:
            return {"status": "no_validation_files"}
        
        latest_file = max(validation_files, key=lambda f: f.stat().st_mtime)
        try:
            with open(latest_file) as f:
                data = json.load(f)
                return {
                    "status": "success" if data.get("overall_status") == "PASS" else "failure",
                    "timestamp": data.get("timestamp"),
                    "tests_passed": len([t for t in data.get("tests", []) if t.get("status") == "PASS"]),
                    "tests_failed": len([t for t in data.get("tests", []) if t.get("status") == "FAIL"])
                }
        except Exception:
            return {"status": "error_reading_validation"}
    
    def _get_knowledge_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do Knowledge Graph (simulado)."""
        # Em um cenário real, isso consultaria o MCP Knowledge Graph
        return {
            "entities": 11,
            "relations": 22,
            "last_update": self.timestamp
        }
    
    def update_architecture_doc(self) -> None:
        """Atualiza o arquivo ARCHITECTURE.md com informações atuais."""
        info = self.get_system_info()
        
        # Lê o template atual
        arch_file = self.project_root / "ARCHITECTURE.md"
        if not arch_file.exists():
            print("ARCHITECTURE.md não encontrado")
            return
        
        content = arch_file.read_text(encoding="utf-8")
        
        # Atualiza timestamp e informações dinâmicas
        updated_content = content.replace(
            "$(Get-Date -Format \"yyyy-MM-dd HH:mm:ss\")",
            self.timestamp
        )
        
        # Adiciona seção de status atual
        status_section = f"""

##  Status Atual do Sistema

**Última Atualização**: {self.timestamp}
**Commit**: {info['git_commit']}
**Validação**: {info['validation_results'].get('status', 'unknown')}

### Estatísticas
- **Knowledge Graph**: {info['knowledge_graph_stats']['entities']} entidades, {info['knowledge_graph_stats']['relations']} relações
- **Testes Backend**: {info['test_status'].get('backend_tests', 'N/A')}
- **Testes Frontend**: {info['test_status'].get('frontend_tests', 'N/A')}
- **Última Validação**: {info['validation_results'].get('timestamp', 'N/A')}

### Dependências Ativas
{chr(10).join([f"- **{k}**: {v}" for k, v in info['dependencies'].items()])}
"""
        
        # Insere antes das referências técnicas
        if "##  Referências Técnicas" in updated_content:
            updated_content = updated_content.replace(
                "##  Referências Técnicas",
                status_section + "\n##  Referências Técnicas"
            )
        
        arch_file.write_text(updated_content, encoding="utf-8")
        print(f" ARCHITECTURE.md atualizado em {self.timestamp}")
    
    def update_changelog(self) -> None:
        """Atualiza o CHANGELOG.md com informações recentes."""
        changelog_file = self.project_root / "CHANGELOG.md"
        if not changelog_file.exists():
            print("CHANGELOG.md não encontrado")
            return
        
        content = changelog_file.read_text(encoding="utf-8")
        
        # Adiciona entrada automática se houver mudanças significativas
        info = self.get_system_info()
        if info['validation_results'].get('status') == 'failure':
            new_entry = f"""
### {datetime.now().strftime('%Y-%m-%d')} - Atualização Automática

#### Detectado
- Falhas na validação do sistema
- Commit: {info['git_commit']}
- Testes falhando: {info['validation_results'].get('tests_failed', 0)}

#### Ação Requerida
- Investigar falhas de validação
- Executar troubleshooting
- Atualizar Knowledge Graph com lições aprendidas
"""
            
            # Insere após [Não Lançado]
            content = content.replace(
                "## [Não Lançado]",
                f"## [Não Lançado]{new_entry}"
            )
            
            changelog_file.write_text(content, encoding="utf-8")
            print(f" CHANGELOG.md atualizado com detecção automática")
    
    def generate_dependency_map(self) -> None:
        """Gera mapa visual de dependências."""
        deps_file = self.project_root / "docs" / "DEPENDENCY_MAP.md"
        deps_file.parent.mkdir(exist_ok=True)
        
        content = f"""
# Mapa de Dependências

> Gerado automaticamente em: {self.timestamp}

## Dependências Externas

```mermaid
graph TD
    A[GLPI Dashboard] --> B[GLPI REST API]
    A --> C[Redis Cache]
    A --> D[PostgreSQL]
    
    E[Backend FastAPI] --> B
    E --> C
    E --> D
    
    F[Frontend React] --> E
    F --> G[Vite Dev Server]
    
    H[Validation System] --> E
    H --> I[Knowledge Graph MCP]
    
    J[CI/CD] --> K[GitHub Actions]
    J --> L[Docker Compose]
```

## Dependências Internas

### Backend
- FastAPI (API framework)
- Pydantic (validação de dados)
- SQLAlchemy (ORM)
- Redis (cache)
- Pytest (testes)

### Frontend
- React (UI framework)
- TypeScript (tipagem)
- Vite (build tool)
- Tailwind CSS (styling)
- Vitest (testes)

### DevOps
- Docker & Docker Compose
- GitHub Actions
- Pre-commit hooks
- Ruff (linting)

## Pontos de Falha Críticos

1. **GLPI API**: Fonte única de dados
2. **Autenticação**: Tokens podem expirar
3. **Descoberta de Campos**: IDs dinâmicos
4. **Cache Redis**: Performance dependente

---

**Atualização**: Automática via `python scripts/update_docs.py`
"""
        
        deps_file.write_text(content, encoding="utf-8")
        print(f" Mapa de dependências gerado")
    
    def run_full_update(self) -> None:
        """Executa atualização completa da documentação."""
        print(f" Iniciando atualização da documentação - {self.timestamp}")
        
        try:
            self.update_architecture_doc()
            self.update_changelog()
            self.generate_dependency_map()
            
            print(f" Documentação atualizada com sucesso!")
            print(f" Timestamp: {self.timestamp}")
            
        except Exception as e:
            print(f" Erro na atualização: {e}")
            raise

if __name__ == "__main__":
    updater = DocumentationUpdater()
    updater.run_full_update()
