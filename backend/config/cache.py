# -*- coding: utf-8 -*-
"""
Configuração e inicialização do cache
Resolve dependências circulares extraindo cache de app.py
"""

import logging
import redis
from flask_caching import Cache
from typing import Optional

logger = logging.getLogger(__name__)

# Instância global do cache
cache: Optional[Cache] = None

def init_cache(app) -> Cache:
    """
    Inicializa o cache com a aplicação Flask
    
    Args:
        app: Instância da aplicação Flask
        
    Returns:
        Cache: Instância configurada do cache
    """
    global cache
    
    cache = Cache()
    
    # Configuração do cache baseada nas configurações da app
    cache_config = {
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'SimpleCache'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
        'CACHE_KEY_PREFIX': app.config.get('CACHE_KEY_PREFIX', 'glpi_dashboard_')
    }
    
    # Se Redis estiver configurado, tenta usar
    if app.config.get('CACHE_TYPE') == 'RedisCache':
        redis_url = app.config.get('CACHE_REDIS_URL')
        if redis_url:
            try:
                # Testa conexão Redis
                redis_client = redis.from_url(redis_url)
                redis_client.ping()
                cache_config.update({
                    'CACHE_REDIS_URL': redis_url
                })
                logger.info("Cache Redis configurado com sucesso")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis: {e}. Usando SimpleCache")
                cache_config['CACHE_TYPE'] = 'SimpleCache'
    
    cache.init_app(app, config=cache_config)
    logger.info(f"Cache inicializado: {cache_config['CACHE_TYPE']}")
    
    return cache

def get_cache() -> Optional[Cache]:
    """
    Retorna a instância do cache
    
    Returns:
        Cache: Instância do cache ou None se não inicializado
    """
    return cache