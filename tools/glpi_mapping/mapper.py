# -*- coding: utf-8 -*-
"""
Módulo principal para mapeamento de catálogos GLPI
Extrai e mapeia dados de catálogos, lookups e estruturas do GLPI
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import requests
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class GLPIConfig(BaseModel):
    """Configuração para conexão com GLPI"""
    base_url: str = Field(default_factory=lambda: os.getenv('GLPI_BASE_URL', ''), description="URL base do GLPI")
    app_token: str = Field(default_factory=lambda: os.getenv('GLPI_APP_TOKEN', ''), description="Token da aplicação")
    user_token: str = Field(default_factory=lambda: os.getenv('GLPI_USER_TOKEN', ''), description="Token do usuário")
    timeout: int = Field(default_factory=lambda: int(os.getenv('GLPI_REQUEST_TIMEOUT', '30')), description="Timeout para requisições")
    max_retries: int = Field(default_factory=lambda: int(os.getenv('GLPI_MAX_RETRIES', '3')), description="Máximo de tentativas")
    
    def model_post_init(self, __context) -> None:
        """Validação pós-inicialização"""
        if not self.base_url:
            raise ValueError("GLPI_BASE_URL é obrigatório")
        if not self.app_token:
            raise ValueError("GLPI_APP_TOKEN é obrigatório")
        if not self.user_token:
            raise ValueError("GLPI_USER_TOKEN é obrigatório")


class CatalogItem(BaseModel):
    """Modelo para item de catálogo GLPI"""
    id: int
    name: str
    level: Optional[int] = None
    parent_id: Optional[Union[int, str]] = None  # Pode ser int ou string
    category: Optional[str] = None
    status: Optional[Union[str, int]] = None  # Pode ser string ou int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('parent_id', mode='before')
    @classmethod
    def validate_parent_id(cls, v):
        if v is None or v == '' or v == 0:
            return None
        if isinstance(v, str):
            # Tentar converter para int, se falhar, manter como string
            try:
                return int(v)
            except (ValueError, TypeError):
                return None  # Ignorar parent_ids inválidos
        return v
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return 'active'
        return str(v)


class GLPIMapper:
    """Classe principal para mapeamento de catálogos GLPI"""
    
    def __init__(self, config: GLPIConfig):
        self.config = config
        self.session_token: Optional[str] = None
        self.token_created_at: Optional[float] = None
        self.session_timeout = 3600  # 1 hora
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        
        # Mapeamentos de catálogos
        self.catalog_mappings = {
            'users': {
                'endpoint': 'User',
                'name_field': 'name',
                'description': 'Usuários do sistema GLPI'
            },
            'groups': {
                'endpoint': 'Group',
                'name_field': 'name',
                'description': 'Grupos de usuários'
            },
            'categories': {
                'endpoint': 'ITILCategory',
                'name_field': 'name',
                'description': 'Categorias de chamados ITIL'
            },
            'tickets': {
                'endpoint': 'Ticket',
                'name_field': 'name',
                'description': 'Chamados do sistema'
            }
        }
    
    def _is_token_expired(self) -> bool:
        """Verifica se o token está expirado"""
        if not self.token_created_at:
            return True
        return (time.time() - self.token_created_at) >= self.session_timeout
    
    def authenticate(self) -> bool:
        """Autentica na API do GLPI (método público)"""
        return self._authenticate()
    
    def _authenticate(self) -> bool:
        """Autentica na API do GLPI"""
        if self.session_token and not self._is_token_expired():
            return True
        
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.config.app_token,
            "Authorization": f"user_token {self.config.user_token}"
        }
        
        try:
            self.console.print("[yellow]Autenticando na API do GLPI...[/yellow]")
            response = requests.get(
                f"{self.config.base_url}initSession",
                headers=headers,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data["session_token"]
            self.token_created_at = time.time()
            
            self.console.print("[green]✓ Autenticação bem-sucedida![/green]")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Erro na autenticação: {e}")
            self.console.print(f"[red]✗ Erro na autenticação: {e}[/red]")
            return False
    
    def close_session(self) -> bool:
        """Encerra a sessão GLPI"""
        if not self.session_token:
            return True
        
        headers = {
            "Session-Token": self.session_token,
            "App-Token": self.config.app_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.config.base_url}killSession",
                headers=headers,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            self.session_token = None
            self.token_created_at = None
            self.console.print("[green]✓ Sessão encerrada[/green]")
            return True
            
        except requests.RequestException as e:
            self.logger.warning(f"Erro ao encerrar sessão: {e}")
            return False
    
    def get_session_info(self) -> Optional[Dict]:
        """Obtém informações da sessão atual"""
        if not self.session_token:
            return None
        
        headers = self._get_headers()
        
        try:
            response = requests.get(
                f"{self.config.base_url}getFullSession",
                headers=headers,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            self.logger.warning(f"Erro ao obter informações da sessão: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições autenticadas"""
        return {
            "Session-Token": self.session_token,
            "App-Token": self.config.app_token,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Faz requisição autenticada para a API"""
        if not self._authenticate():
            return None
        
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params or {},
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    self.logger.error(f"Falha após {self.config.max_retries} tentativas")
                    return None
    
    def extract_catalog(self, catalog_name: str, limit: int = 1000) -> List[CatalogItem]:
        """Extrai catálogo específico do GLPI"""
        if catalog_name not in self.catalog_mappings:
            raise ValueError(f"Catálogo '{catalog_name}' não suportado")
        
        mapping = self.catalog_mappings[catalog_name]
        endpoint = mapping['endpoint']
        
        self.console.print(f"[blue]Extraindo catálogo: {catalog_name}[/blue]")
        
        params = {
            'range': f'0-{limit-1}',
            'expand_dropdowns': True,
            'get_hateoas': False
        }
        
        data = self._make_request(endpoint, params)
        if not data:
            return []
        
        # Verificar se data é uma lista ou dict
        if isinstance(data, dict):
            # Se for dict, pode ter uma chave com os dados ou ser um único item
            if 'data' in data:
                data = data['data']
            elif len(data) == 1 and isinstance(list(data.values())[0], list):
                data = list(data.values())[0]
            else:
                data = [data]  # Tratar como item único
        
        if not isinstance(data, list):
            self.logger.error(f"Formato de dados inesperado: {type(data)}")
            return []
        
        items = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Processando {catalog_name}...", total=len(data))
            
            for item_data in data:
                try:
                    if not isinstance(item_data, dict):
                        self.logger.warning(f"Item não é um dicionário: {type(item_data)}")
                        continue
                    
                    item = CatalogItem(
                        id=item_data.get('id', 0),
                        name=item_data.get('name', '') or item_data.get('realname', '') or item_data.get('firstname', ''),
                        level=item_data.get('level'),
                        parent_id=item_data.get('parent_id') or item_data.get(f'{endpoint.lower()}s_id') or item_data.get('itilcategories_id'),
                        category=catalog_name,
                        status=item_data.get('status', 'active'),
                        metadata={
                            k: v for k, v in item_data.items() 
                            if k not in ['id', 'name', 'level', 'parent_id', 'status', 'realname', 'firstname']
                        }
                    )
                    items.append(item)
                except Exception as e:
                    self.logger.warning(f"Erro ao processar item {item_data.get('id', 'N/A') if isinstance(item_data, dict) else 'N/A'}: {e}")
                
                progress.advance(task)
        
        self.console.print(f"[green]✓ {len(items)} itens extraídos de {catalog_name}[/green]")
        return items
    
    def extract_all_catalogs(self, output_dir: Path, detect_levels: bool = True) -> Dict[str, int]:
        """Extrai todos os catálogos suportados"""
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}
        
        self.console.print("[bold blue]Iniciando extração de todos os catálogos...[/bold blue]")
        
        for catalog_name in self.catalog_mappings.keys():
            try:
                items = self.extract_catalog(catalog_name)
                
                # Salvar como JSON
                output_file = output_dir / f"{catalog_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(
                        [item.model_dump() for item in items],
                        f,
                        indent=2,
                        ensure_ascii=False
                    )
                
                # Salvar como CSV para compatibilidade
                csv_file = output_dir / f"{catalog_name}.csv"
                self._save_as_csv(items, csv_file)
                
                results[catalog_name] = len(items)
                
            except Exception as e:
                self.logger.error(f"Erro ao extrair catálogo {catalog_name}: {e}")
                self.console.print(f"[red]✗ Erro em {catalog_name}: {e}[/red]")
                results[catalog_name] = 0
        
        # Salvar metadados da extração
        metadata = {
            'extraction_date': datetime.now().isoformat(),
            'glpi_url': self.config.base_url,
            'catalogs': results,
            'total_items': sum(results.values())
        }
        
        metadata_file = output_dir / 'extraction_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"[bold green]✓ Extração concluída! Total: {sum(results.values())} itens[/bold green]")
        return results
    
    def _save_as_csv(self, items: List[CatalogItem], output_file: Path):
        """Salva itens como CSV"""
        import csv
        
        if not items:
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            headers = ['id', 'name', 'level', 'parent_id', 'category', 'status']
            writer.writerow(headers)
            
            # Data
            for item in items:
                writer.writerow([
                    item.id,
                    item.name,
                    item.level or '',
                    item.parent_id or '',
                    item.category or '',
                    item.status or ''
                ])
    
    def detect_hierarchy_levels(self, catalog_name: str) -> Dict[str, Any]:
        """Detecta níveis hierárquicos em um catálogo"""
        items = self.extract_catalog(catalog_name)
        
        # Análise de hierarquia
        hierarchy = {}
        max_level = 0
        
        for item in items:
            if item.level is not None:
                max_level = max(max_level, item.level)
                if item.level not in hierarchy:
                    hierarchy[item.level] = []
                hierarchy[item.level].append({
                    'id': item.id,
                    'name': item.name,
                    'parent_id': item.parent_id
                })
        
        return {
            'catalog': catalog_name,
            'max_level': max_level,
            'hierarchy': hierarchy,
            'total_items': len(items)
        }
    
    def cleanup_session(self):
        """Limpa a sessão GLPI"""
        if self.session_token:
            try:
                headers = self._get_headers()
                requests.get(
                    f"{self.config.base_url}/killSession",
                    headers=headers,
                    timeout=self.config.timeout
                )
                self.console.print("[green]✓ Sessão GLPI encerrada[/green]")
            except Exception as e:
                self.logger.warning(f"Erro ao encerrar sessão: {e}")
            finally:
                self.session_token = None
                self.token_created_at = None