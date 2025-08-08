# -*- coding: utf-8 -*-
"""
Serviço para carregamento de lookups/catálogos GLPI
Integra com o módulo glpi_mapping para fornecer dados de catálogos ao dashboard
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class LookupLoader:
    """Carregador de lookups GLPI com cache inteligente"""
    
    def __init__(self, lookups_dir: Union[str, Path] = "./lookups"):
        self.lookups_dir = Path(lookups_dir)
        self.logger = logging.getLogger(__name__)
        
        # Cache com TTL
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutos
        
        # Metadados da última extração
        self._extraction_metadata = None
        self._metadata_timestamp = None
        
        self.logger.info(f"LookupLoader inicializado com diretório: {self.lookups_dir}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache é válido"""
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = time.time() - self._cache_timestamps[cache_key]
        return cache_age < self._cache_ttl
    
    def _load_json_file(self, file_path: Path) -> Optional[List[Dict]]:
        """Carrega arquivo JSON com tratamento de erros"""
        try:
            if not file_path.exists():
                self.logger.warning(f"Arquivo não encontrado: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"Arquivo carregado: {file_path} ({len(data)} itens)")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
            return None
    
    def load_catalog(self, catalog_name: str, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Carrega catálogo específico com cache"""
        cache_key = f"catalog_{catalog_name}"
        
        # Verificar cache
        if not force_reload and self._is_cache_valid(cache_key):
            self.logger.debug(f"Retornando {catalog_name} do cache")
            return self._cache.get(cache_key, [])
        
        # Carregar do arquivo
        file_path = self.lookups_dir / f"{catalog_name}.json"
        data = self._load_json_file(file_path)
        
        if data is not None:
            # Atualizar cache
            self._cache[cache_key] = data
            self._cache_timestamps[cache_key] = time.time()
            
            self.logger.info(f"Catálogo {catalog_name} carregado: {len(data)} itens")
            return data
        
        # Retornar cache antigo se disponível
        if cache_key in self._cache:
            self.logger.warning(f"Usando cache antigo para {catalog_name}")
            return self._cache[cache_key]
        
        self.logger.error(f"Não foi possível carregar catálogo: {catalog_name}")
        return []
    
    def get_lookup_dict(self, catalog_name: str, key_field: str = 'id', value_field: str = 'name') -> Dict[Any, Any]:
        """Retorna dicionário para lookups (id -> name por padrão)"""
        data = self.load_catalog(catalog_name)
        
        lookup_dict = {}
        for item in data:
            if key_field in item and value_field in item:
                lookup_dict[item[key_field]] = item[value_field]
        
        self.logger.debug(f"Lookup {catalog_name} criado: {len(lookup_dict)} entradas")
        return lookup_dict
    
    def get_hierarchical_lookup(self, catalog_name: str) -> Dict[str, Any]:
        """Retorna lookup hierárquico com níveis"""
        data = self.load_catalog(catalog_name)
        
        # Organizar por níveis
        hierarchy = {
            'items': {},
            'levels': {},
            'children': {},
            'parents': {}
        }
        
        for item in data:
            item_id = item.get('id')
            level = item.get('level')
            parent_id = item.get('parent_id')
            
            # Mapear item
            hierarchy['items'][item_id] = item
            
            # Mapear por nível
            if level is not None:
                if level not in hierarchy['levels']:
                    hierarchy['levels'][level] = []
                hierarchy['levels'][level].append(item_id)
            
            # Mapear relações pai-filho
            if parent_id:
                if parent_id not in hierarchy['children']:
                    hierarchy['children'][parent_id] = []
                hierarchy['children'][parent_id].append(item_id)
                hierarchy['parents'][item_id] = parent_id
        
        return hierarchy
    
    def get_extraction_metadata(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Obtém metadados da última extração"""
        if not force_reload and self._extraction_metadata and self._metadata_timestamp:
            # Cache válido por 1 minuto
            if time.time() - self._metadata_timestamp < 60:
                return self._extraction_metadata
        
        metadata_file = self.lookups_dir / 'extraction_metadata.json'
        metadata = self._load_json_file(metadata_file)
        
        if metadata:
            self._extraction_metadata = metadata
            self._metadata_timestamp = time.time()
            return metadata
        
        return None
    
    def is_data_fresh(self, max_age_hours: int = 24) -> bool:
        """Verifica se os dados estão atualizados"""
        metadata = self.get_extraction_metadata()
        if not metadata or 'extraction_date' not in metadata:
            return False
        
        try:
            extraction_date = datetime.fromisoformat(metadata['extraction_date'])
            age_hours = (datetime.now() - extraction_date).total_seconds() / 3600
            return age_hours <= max_age_hours
        except Exception as e:
            self.logger.error(f"Erro ao verificar idade dos dados: {e}")
            return False
    
    def get_available_catalogs(self) -> List[str]:
        """Lista catálogos disponíveis no diretório"""
        if not self.lookups_dir.exists():
            return []
        
        catalogs = []
        for file_path in self.lookups_dir.glob('*.json'):
            if file_path.name != 'extraction_metadata.json':
                catalog_name = file_path.stem
                if not catalog_name.endswith('_hierarchy'):
                    catalogs.append(catalog_name)
        
        return sorted(catalogs)
    
    def get_catalog_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obtém estatísticas dos catálogos"""
        stats = {}
        
        for catalog_name in self.get_available_catalogs():
            try:
                data = self.load_catalog(catalog_name)
                file_path = self.lookups_dir / f"{catalog_name}.json"
                
                stats[catalog_name] = {
                    'items_count': len(data),
                    'file_size': file_path.stat().st_size if file_path.exists() else 0,
                    'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() if file_path.exists() else None,
                    'has_hierarchy': (self.lookups_dir / f"{catalog_name}_hierarchy.json").exists()
                }
            except Exception as e:
                self.logger.error(f"Erro ao obter stats de {catalog_name}: {e}")
                stats[catalog_name] = {
                    'items_count': 0,
                    'file_size': 0,
                    'last_modified': None,
                    'has_hierarchy': False,
                    'error': str(e)
                }
        
        return stats
    
    def clear_cache(self, catalog_name: Optional[str] = None):
        """Limpa cache específico ou todo o cache"""
        if catalog_name:
            cache_key = f"catalog_{catalog_name}"
            self._cache.pop(cache_key, None)
            self._cache_timestamps.pop(cache_key, None)
            self.logger.info(f"Cache limpo para: {catalog_name}")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            self._extraction_metadata = None
            self._metadata_timestamp = None
            self.logger.info("Todo o cache foi limpo")
    
    def preload_catalogs(self, catalog_names: Optional[List[str]] = None):
        """Pré-carrega catálogos no cache"""
        if catalog_names is None:
            catalog_names = self.get_available_catalogs()
        
        self.logger.info(f"Pré-carregando {len(catalog_names)} catálogos...")
        
        for catalog_name in catalog_names:
            try:
                self.load_catalog(catalog_name, force_reload=True)
            except Exception as e:
                self.logger.error(f"Erro ao pré-carregar {catalog_name}: {e}")
        
        self.logger.info("Pré-carregamento concluído")
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de lookups"""
        health = {
            'status': 'healthy',
            'lookups_dir_exists': self.lookups_dir.exists(),
            'available_catalogs': len(self.get_available_catalogs()),
            'cache_entries': len(self._cache),
            'data_fresh': self.is_data_fresh(),
            'extraction_metadata': self.get_extraction_metadata() is not None,
            'issues': []
        }
        
        # Verificações de saúde
        if not health['lookups_dir_exists']:
            health['issues'].append(f"Diretório de lookups não existe: {self.lookups_dir}")
            health['status'] = 'unhealthy'
        
        if health['available_catalogs'] == 0:
            health['issues'].append("Nenhum catálogo disponível")
            health['status'] = 'degraded'
        
        if not health['data_fresh']:
            health['issues'].append("Dados podem estar desatualizados (>24h)")
            if health['status'] == 'healthy':
                health['status'] = 'degraded'
        
        if not health['extraction_metadata']:
            health['issues'].append("Metadados de extração não encontrados")
            if health['status'] == 'healthy':
                health['status'] = 'degraded'
        
        return health


# Instância global (singleton pattern)
_lookup_loader_instance = None


def get_lookup_loader(lookups_dir: Union[str, Path] = "./lookups") -> LookupLoader:
    """Obtém instância singleton do LookupLoader"""
    global _lookup_loader_instance
    
    if _lookup_loader_instance is None:
        _lookup_loader_instance = LookupLoader(lookups_dir)
    
    return _lookup_loader_instance


# Funções de conveniência
def load_catalog(catalog_name: str, **kwargs) -> List[Dict[str, Any]]:
    """Função de conveniência para carregar catálogo"""
    return get_lookup_loader().load_catalog(catalog_name, **kwargs)


def get_lookup_dict(catalog_name: str, **kwargs) -> Dict[Any, Any]:
    """Função de conveniência para obter lookup dict"""
    return get_lookup_loader().get_lookup_dict(catalog_name, **kwargs)


def clear_lookups_cache(catalog_name: Optional[str] = None):
    """Função de conveniência para limpar cache"""
    get_lookup_loader().clear_cache(catalog_name)