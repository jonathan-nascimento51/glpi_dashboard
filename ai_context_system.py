#!/usr/bin/env python3`n# -*- coding: utf-8 -*-
"""
Sistema de Treinamento e Otimização do AI Context

Este módulo implementa um sistema para alimentar continuamente o contexto da IA
com informações atualizadas do projeto, incluindo configuração de MCPs especializados.

Autor: GLPI Dashboard Team
Versão: 1.0.0
Data: 2024
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import aiofiles
    import yaml
except ImportError:
    print("Dependências necessárias: pip install aiofiles pyyaml")
    
from dataclasses import dataclass, field
from enum import Enum

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Tipos de contexto para alimentar a IA."""
    ARCHITECTURE = "architecture"
    CODE_PATTERNS = "code_patterns"
    DEPENDENCIES = "dependencies"
    METRICS = "metrics"
    TROUBLESHOOTING = "troubleshooting"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"


class Priority(Enum):
    """Prioridades para atualização de contexto."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ContextItem:
    """Item de contexto para a IA."""
    id: str
    type: ContextType
    title: str
    content: str
    priority: Priority
    tags: Set[str] = field(default_factory=set)
    last_updated: datetime = field(default_factory=datetime.now)
    source_file: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPConfig:
    """Configuração de MCP especializado."""
    name: str
    type: str
    description: str
    config_path: str
    enabled: bool = True
    auto_update: bool = True
    update_interval: int = 3600  # segundos
    last_update: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ContextMetrics:
    """Métricas do sistema de contexto."""
    total_items: int = 0
    items_by_type: Dict[str, int] = field(default_factory=dict)
    items_by_priority: Dict[str, int] = field(default_factory=dict)
    last_update: Optional[datetime] = None
    update_frequency: float = 0.0  # updates per hour
    storage_size: int = 0  # bytes
    processing_time: float = 0.0  # seconds


class AIContextSystem:
    """Sistema principal de treinamento e otimização do AI Context."""

    def __init__(self, config_path: str = "config_ai_context.py"):
        """Inicializa o sistema de contexto da IA.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.project_root = Path.cwd()
        self.context_storage = self.project_root / "ai_context_storage"
        self.mcp_configs: Dict[str, MCPConfig] = {}
        self.context_items: Dict[str, ContextItem] = {}
        self.metrics = ContextMetrics()
        self.running = False
        
        # Criar diretório de armazenamento
        self.context_storage.mkdir(exist_ok=True)
        
        # Carregar configurações
        self._load_config()
        
        logger.info(f"AI Context System inicializado em {self.project_root}")

    def _load_config(self) -> None:
        """Carrega configurações do sistema."""
        try:
            if os.path.exists(self.config_path):
                # Importar configurações do Python
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", self.config_path)
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                
                # Carregar MCPs configurados
                if hasattr(config, "MCP_CONFIGS"):
                    for mcp_data in config.MCP_CONFIGS:
                        mcp = MCPConfig(**mcp_data)
                        self.mcp_configs[mcp.name] = mcp
                        
                logger.info(f"Configurações carregadas: {len(self.mcp_configs)} MCPs")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """Cria configuração padrão."""
        default_mcps = [
            MCPConfig(
                name="filesystem",
                type="core",
                description="Acesso ao sistema de arquivos",
                config_path="mcp/filesystem.json"
            ),
            MCPConfig(
                name="git",
                type="version_control",
                description="Integração com Git",
                config_path="mcp/git.json"
            ),
            MCPConfig(
                name="knowledge_graph",
                type="knowledge",
                description="Grafo de conhecimento persistente",
                config_path="mcp/knowledge_graph.json"
            )
        ]
        
        for mcp in default_mcps:
            self.mcp_configs[mcp.name] = mcp

    async def start_monitoring(self) -> None:
        """Inicia o monitoramento contínuo do contexto."""
        if self.running:
            logger.warning("Sistema já está em execução")
            return
            
        self.running = True
        logger.info("Iniciando monitoramento do AI Context")
        
        try:
            # Carregar contexto existente
            await self._load_existing_context()
            
            # Iniciar loops de monitoramento
            tasks = [
                asyncio.create_task(self._monitor_project_changes()),
                asyncio.create_task(self._update_context_periodically()),
                asyncio.create_task(self._monitor_mcps()),
                asyncio.create_task(self._generate_metrics())
            ]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
        finally:
            self.running = False

    async def stop_monitoring(self) -> None:
        """Para o monitoramento."""
        self.running = False
        logger.info("Parando monitoramento do AI Context")

    async def get_context_summary(self) -> Dict[str, Any]:
        """Obtém resumo do contexto atual."""
        return {
            "total_items": len(self.context_items),
            "items_by_type": {t.value: sum(1 for item in self.context_items.values() if item.type == t) 
                             for t in ContextType},
            "items_by_priority": {p.value: sum(1 for item in self.context_items.values() if item.priority == p) 
                                 for p in Priority},
            "mcps_configured": len(self.mcp_configs),
            "mcps_enabled": sum(1 for mcp in self.mcp_configs.values() if mcp.enabled),
            "storage_path": str(self.context_storage),
            "last_update": max((item.last_updated for item in self.context_items.values()), 
                              default=datetime.now()).isoformat()
        }

    async def _load_existing_context(self) -> None:
        """Carrega contexto existente do armazenamento."""
        try:
            context_file = self.context_storage / "context_items.json"
            if context_file.exists():
                with open(context_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                for item_data in data:
                    item = ContextItem(
                        id=item_data["id"],
                        type=ContextType(item_data["type"]),
                        title=item_data["title"],
                        content=item_data["content"],
                        priority=Priority(item_data["priority"]),
                        tags=set(item_data.get("tags", [])),
                        last_updated=datetime.fromisoformat(item_data["last_updated"]),
                        source_file=item_data.get("source_file"),
                        dependencies=set(item_data.get("dependencies", [])),
                        metadata=item_data.get("metadata", {})
                    )
                    self.context_items[item.id] = item
                    
                logger.info(f"Carregados {len(self.context_items)} itens de contexto")
        except Exception as e:
            logger.error(f"Erro ao carregar contexto existente: {e}")

    async def _monitor_project_changes(self) -> None:
        """Monitora mudanças no projeto."""
        last_check = datetime.now()
        
        while self.running:
            try:
                # Verificar arquivos modificados
                modified_files = await self._get_modified_files(last_check)
                
                for file_path in modified_files:
                    await self._process_file_change(file_path)
                
                last_check = datetime.now()
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de mudanças: {e}")
                await asyncio.sleep(60)

    async def _get_modified_files(self, since: datetime) -> List[str]:
        """Obtém lista de arquivos modificados desde uma data."""
        try:
            # Usar git para encontrar arquivos modificados
            cmd = [
                "git", "diff", "--name-only", 
                f"--since={since.isoformat()}"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.split("\n") if f.strip()]
            else:
                logger.warning(f"Git diff falhou: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter arquivos modificados: {e}")
            return []

    async def _process_file_change(self, file_path: str) -> None:
        """Processa mudança em um arquivo."""
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                # Arquivo foi deletado
                await self._handle_file_deletion(file_path)
                return
            
            # Determinar tipo de contexto baseado no arquivo
            context_type = self._determine_context_type(file_path)
            
            if context_type:
                await self._extract_context_from_file(full_path, context_type)
                
        except Exception as e:
            logger.error(f"Erro ao processar mudança em {file_path}: {e}")

    def _determine_context_type(self, file_path: str) -> Optional[ContextType]:
        """Determina o tipo de contexto baseado no caminho do arquivo."""
        path_lower = file_path.lower()
        
        if any(x in path_lower for x in ["architecture", "design", "arch"]):
            return ContextType.ARCHITECTURE
        elif any(x in path_lower for x in ["test", "spec"]):
            return ContextType.TESTING
        elif any(x in path_lower for x in ["config", "settings", ".env"]):
            return ContextType.CONFIGURATION
        elif any(x in path_lower for x in ["readme", "doc", "guide"]):
            return ContextType.DOCUMENTATION
        elif any(x in path_lower for x in ["metric", "monitor", "observ"]):
            return ContextType.METRICS
        elif any(x in path_lower for x in ["security", "auth", "permission"]):
            return ContextType.SECURITY
        elif any(x in path_lower for x in ["performance", "perf", "benchmark"]):
            return ContextType.PERFORMANCE
        elif any(x in path_lower for x in ["troubleshoot", "debug", "error"]):
            return ContextType.TROUBLESHOOTING
        elif file_path.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
            return ContextType.CODE_PATTERNS
        elif file_path.endswith((".json", ".yaml", ".yml", ".toml")):
            return ContextType.DEPENDENCIES
        
        return None

    async def _extract_context_from_file(self, file_path: Path, context_type: ContextType) -> None:
        """Extrai contexto de um arquivo."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Gerar ID único para o item
            item_id = f"{context_type.value}_{file_path.name}_{hash(str(file_path))}"
            
            # Extrair informações específicas baseadas no tipo
            extracted_info = await self._analyze_content(content, context_type, file_path)
            
            # Criar item de contexto
            context_item = ContextItem(
                id=item_id,
                type=context_type,
                title=extracted_info.get("title", file_path.name),
                content=extracted_info.get("summary", content[:1000]),
                priority=extracted_info.get("priority", Priority.MEDIUM),
                tags=extracted_info.get("tags", set()),
                source_file=str(file_path),
                dependencies=extracted_info.get("dependencies", set()),
                metadata={
                    "file_size": len(content),
                    "file_type": file_path.suffix,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Armazenar item
            self.context_items[item_id] = context_item
            
            logger.info(f"Contexto extraído de {file_path.name}: {context_type.value}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair contexto de {file_path}: {e}")

    async def _analyze_content(self, content: str, context_type: ContextType, file_path: Path) -> Dict[str, Any]:
        """Analisa conteúdo para extrair informações relevantes."""
        analysis = {
            "title": file_path.name,
            "summary": content[:500],
            "priority": Priority.MEDIUM,
            "tags": set(),
            "dependencies": set()
        }
        
        try:
            if context_type == ContextType.CODE_PATTERNS:
                analysis.update(await self._analyze_code_patterns(content, file_path))
            elif context_type == ContextType.ARCHITECTURE:
                analysis.update(await self._analyze_architecture(content))
            elif context_type == ContextType.CONFIGURATION:
                analysis.update(await self._analyze_configuration(content))
            elif context_type == ContextType.DEPENDENCIES:
                analysis.update(await self._analyze_dependencies(content, file_path))
            elif context_type == ContextType.DOCUMENTATION:
                analysis.update(await self._analyze_documentation(content))
                
        except Exception as e:
            logger.error(f"Erro na análise de conteúdo: {e}")
        
        return analysis

    async def _analyze_code_patterns(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analisa padrões de código."""
        patterns = {
            "tags": set(),
            "dependencies": set(),
            "priority": Priority.MEDIUM
        }
        
        # Detectar imports/requires
        import_lines = [line for line in content.split("\n") if 
                       line.strip().startswith(("import ", "from ", "require(", "const "))]
        
        for line in import_lines:
            # Extrair dependências
            if "import" in line or "require" in line:
                patterns["dependencies"].add(line.strip())
        
        # Detectar padrões específicos
        if "async def" in content or "await " in content:
            patterns["tags"].add("async")
        if "class " in content:
            patterns["tags"].add("oop")
        if "test_" in file_path.name or "spec" in file_path.name:
            patterns["tags"].add("testing")
            patterns["priority"] = Priority.HIGH
        
        return patterns

    async def _analyze_architecture(self, content: str) -> Dict[str, Any]:
        """Analisa documentação de arquitetura."""
        return {
            "priority": Priority.HIGH,
            "tags": {"architecture", "design"},
            "summary": content[:1000]
        }

    async def _analyze_configuration(self, content: str) -> Dict[str, Any]:
        """Analisa arquivos de configuração."""
        return {
            "priority": Priority.HIGH,
            "tags": {"configuration", "settings"},
            "summary": content[:500]
        }

    async def _analyze_dependencies(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analisa arquivos de dependências."""
        deps = set()
        
        try:
            if file_path.suffix == ".json":
                data = json.loads(content)
                if "dependencies" in data:
                    deps.update(data["dependencies"].keys())
                if "devDependencies" in data:
                    deps.update(data["devDependencies"].keys())
        except Exception as e:
            logger.error(f"Erro ao analisar dependências: {e}")
        
        return {
            "dependencies": deps,
            "priority": Priority.HIGH,
            "tags": {"dependencies", "packages"}
        }

    async def _analyze_documentation(self, content: str) -> Dict[str, Any]:
        """Analisa documentação."""
        # Extrair títulos
        lines = content.split("\n")
        titles = [line.strip("# ") for line in lines if line.startswith("#")]
        
        return {
            "title": titles[0] if titles else "Documentation",
            "priority": Priority.HIGH,
            "tags": {"documentation", "guide"},
            "summary": content[:1000]
        }

    async def _handle_file_deletion(self, file_path: str) -> None:
        """Lida com a exclusão de arquivos."""
        # Remover itens de contexto relacionados ao arquivo deletado
        items_to_remove = [
            item_id for item_id, item in self.context_items.items()
            if item.source_file and file_path in item.source_file
        ]
        
        for item_id in items_to_remove:
            del self.context_items[item_id]
            logger.info(f"Removido contexto para arquivo deletado: {file_path}")

    async def _update_context_periodically(self) -> None:
        """Atualiza contexto periodicamente."""
        while self.running:
            try:
                await self._save_context_to_storage()
                await self._cleanup_old_context()
                await self._optimize_context_storage()
                
                await asyncio.sleep(300)  # A cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro na atualização periódica: {e}")
                await asyncio.sleep(60)

    async def _save_context_to_storage(self) -> None:
        """Salva contexto no armazenamento."""
        try:
            context_file = self.context_storage / "context_items.json"
            
            # Converter itens para formato serializável
            serializable_items = []
            for item in self.context_items.values():
                serializable_items.append({
                    "id": item.id,
                    "type": item.type.value,
                    "title": item.title,
                    "content": item.content,
                    "priority": item.priority.value,
                    "tags": list(item.tags),
                    "last_updated": item.last_updated.isoformat(),
                    "source_file": item.source_file,
                    "dependencies": list(item.dependencies),
                    "metadata": item.metadata
                })
            
            with open(context_file, "w", encoding="utf-8") as f:
                json.dump(serializable_items, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Contexto salvo: {len(serializable_items)} itens")
            
        except Exception as e:
            logger.error(f"Erro ao salvar contexto: {e}")

    async def _cleanup_old_context(self) -> None:
        """Remove contexto antigo ou irrelevante."""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        items_to_remove = [
            item_id for item_id, item in self.context_items.items()
            if item.last_updated < cutoff_date and item.priority == Priority.LOW
        ]
        
        for item_id in items_to_remove:
            del self.context_items[item_id]
        
        if items_to_remove:
            logger.info(f"Removidos {len(items_to_remove)} itens de contexto antigos")

    async def _optimize_context_storage(self) -> None:
        """Otimiza o armazenamento de contexto."""
        # Remover duplicatas
        seen_content = set()
        items_to_remove = []
        
        for item_id, item in self.context_items.items():
            content_hash = hash(item.content)
            if content_hash in seen_content:
                items_to_remove.append(item_id)
            else:
                seen_content.add(content_hash)
        
        for item_id in items_to_remove:
            del self.context_items[item_id]
        
        if items_to_remove:
            logger.info(f"Removidas {len(items_to_remove)} duplicatas de contexto")

    async def _monitor_mcps(self) -> None:
        """Monitora e atualiza MCPs."""
        while self.running:
            try:
                for mcp_name, mcp_config in self.mcp_configs.items():
                    if mcp_config.enabled and mcp_config.auto_update:
                        await self._update_mcp(mcp_config)
                
                await asyncio.sleep(3600)  # A cada hora
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de MCPs: {e}")
                await asyncio.sleep(300)

    async def _update_mcp(self, mcp_config: MCPConfig) -> None:
        """Atualiza um MCP específico."""
        try:
            # Verificar se precisa atualizar
            if (mcp_config.last_update and 
                datetime.now() - mcp_config.last_update < timedelta(seconds=mcp_config.update_interval)):
                return
            
            logger.info(f"Atualizando MCP: {mcp_config.name}")
            
            # Aqui seria implementada a lógica específica de cada MCP
            # Por exemplo, atualizar configurações, verificar conectividade, etc.
            
            mcp_config.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar MCP {mcp_config.name}: {e}")

    async def _generate_metrics(self) -> None:
        """Gera métricas do sistema."""
        while self.running:
            try:
                start_time = time.time()
                
                # Calcular métricas
                self.metrics.total_items = len(self.context_items)
                self.metrics.items_by_type = {}
                self.metrics.items_by_priority = {}
                
                for item in self.context_items.values():
                    # Por tipo
                    type_key = item.type.value
                    self.metrics.items_by_type[type_key] = self.metrics.items_by_type.get(type_key, 0) + 1
                    
                    # Por prioridade
                    priority_key = item.priority.value
                    self.metrics.items_by_priority[priority_key] = self.metrics.items_by_priority.get(priority_key, 0) + 1
                
                # Calcular tamanho de armazenamento
                storage_size = 0
                for file_path in self.context_storage.rglob("*"):
                    if file_path.is_file():
                        storage_size += file_path.stat().st_size
                
                self.metrics.storage_size = storage_size
                self.metrics.last_update = datetime.now()
                self.metrics.processing_time = time.time() - start_time
                
                # Salvar métricas
                await self._save_metrics()
                
                await asyncio.sleep(300)  # A cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro ao gerar métricas: {e}")
                await asyncio.sleep(60)

    async def _save_metrics(self) -> None:
        """Salva métricas no armazenamento."""
        try:
            metrics_file = self.context_storage / "metrics.json"
            
            metrics_data = {
                "total_items": self.metrics.total_items,
                "items_by_type": self.metrics.items_by_type,
                "items_by_priority": self.metrics.items_by_priority,
                "last_update": self.metrics.last_update.isoformat() if self.metrics.last_update else None,
                "update_frequency": self.metrics.update_frequency,
                "storage_size": self.metrics.storage_size,
                "processing_time": self.metrics.processing_time
            }
            
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")


# Funções utilitárias
async def main():
    """Função principal para execução standalone."""
    system = AIContextSystem()
    
    try:
        await system.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    finally:
        await system.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())

