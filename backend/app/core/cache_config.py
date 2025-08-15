"""Configuracao avancada de cache com fallback inteligente e metricas"""
import os
import time
import logging
from typing import Dict, Any, Optional, Union
from functools import wraps
from flask_caching import Cache
import redis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)

class CacheMetrics:
    """Coleta metricas de performance do cache"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.total_time = 0.0
        self.operations = 0
    
    def record_hit(self, duration: float = 0.0):
        self.hits += 1
        self.total_time += duration
        self.operations += 1
    
    def record_miss(self, duration: float = 0.0):
        self.misses += 1
        self.total_time += duration
        self.operations += 1
    
    def record_error(self, duration: float = 0.0):
        self.errors += 1
        self.total_time += duration
        self.operations += 1
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        return (self.total_time / self.operations) if self.operations > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'hits': self.hits,
            'misses': self.misses,
            'errors': self.errors,
            'hit_rate_percent': round(self.hit_rate, 2),
            'avg_response_time_ms': round(self.avg_response_time * 1000, 2),
            'total_operations': self.operations
        }

class SmartCacheManager:
    """Gerenciador inteligente de cache com fallback automatico"""
    
    def __init__(self, app=None):
        self.cache = Cache()
        self.redis_client = None
        self.cache_type = 'SimpleCache'  # Default fallback
        self.metrics = CacheMetrics()
        self.redis_available = False
        self.last_redis_check = 0
        self.redis_check_interval = 30  # Verificar Redis a cada 30 segundos
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o cache com a aplicacao Flask"""
        self._configure_cache(app)
        self.cache.init_app(app)
        
        # Registrar metricas no contexto da aplicacao
        app.cache_metrics = self.metrics
        app.cache_manager = self
    
    def _configure_cache(self, app):
        """Configura o cache com fallback inteligente"""
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        
        # Tentar configurar Redis
        if self._test_redis_connection(redis_url):
            self._configure_redis_cache(app, redis_url)
        else:
            self._configure_simple_cache(app)
    
    def _test_redis_connection(self, redis_url: str) -> bool:
        """Testa conexao com Redis"""
        try:
            client = redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
            client.ping()
            self.redis_client = client
            self.redis_available = True
            self.last_redis_check = time.time()
            logger.info(f"✓ Redis conectado com sucesso: {redis_url}")
            return True
        except (ConnectionError, TimeoutError, Exception) as e:
            self.redis_available = False
            logger.warning(f"⚠ Redis nao disponivel ({e}), usando SimpleCache")
            return False
    
    def _configure_redis_cache(self, app, redis_url: str):
        """Configura cache Redis"""
        self.cache_type = 'RedisCache'
        cache_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': redis_url,
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'CACHE_KEY_PREFIX': app.config.get('CACHE_KEY_PREFIX', 'glpi_dashboard:'),
            'CACHE_OPTIONS': {
                'socket_timeout': 2,
                'socket_connect_timeout': 2,
                'retry_on_timeout': True,
                'health_check_interval': 30
            }
        }
        app.config.update(cache_config)
        logger.info("Cache configurado: Redis com fallback automatico")
    
    def _configure_simple_cache(self, app):
        """Configura cache SimpleCache otimizado"""
        self.cache_type = 'SimpleCache'
        cache_config = {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'CACHE_THRESHOLD': 1000,  # Maximo de 1000 chaves em memoria
        }
        app.config.update(cache_config)
        logger.info("Cache configurado: SimpleCache (fallback)")
    
    def _check_redis_health(self):
        """Verifica saude do Redis periodicamente"""
        current_time = time.time()
        if current_time - self.last_redis_check > self.redis_check_interval:
            if self.redis_client:
                try:
                    self.redis_client.ping()
                    self.redis_available = True
                except Exception:
                    self.redis_available = False
                    logger.warning("Redis connection lost, using fallback")
            self.last_redis_check = current_time
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Retorna informacoes sobre o cache"""
        self._check_redis_health()
        
        info = {
            'type': self.cache_type,
            'redis_available': self.redis_available,
            'metrics': self.metrics.get_stats()
        }
        
        if self.redis_client and self.redis_available:
            try:
                redis_info = self.redis_client.info()
                info['redis_info'] = {
                    'used_memory_human': redis_info.get('used_memory_human', 'N/A'),
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0)
                }
            except Exception as e:
                logger.warning(f"Erro ao obter info do Redis: {e}")
        
        return info

def cache_with_metrics(timeout: int = 300, key_prefix: str = ''):
    """Decorator para cache com metricas automaticas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import current_app
            
            cache_manager = getattr(current_app, 'cache_manager', None)
            if not cache_manager:
                return func(*args, **kwargs)
            
            # Gerar chave do cache
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            start_time = time.time()
            
            try:
                # Tentar obter do cache
                cached_result = cache_manager.cache.get(cache_key)
                duration = time.time() - start_time
                
                if cached_result is not None:
                    cache_manager.metrics.record_hit(duration)
                    return cached_result
                
                # Cache miss - executar funcao
                result = func(*args, **kwargs)
                
                # Armazenar no cache
                cache_manager.cache.set(cache_key, result, timeout=timeout)
                cache_manager.metrics.record_miss(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                cache_manager.metrics.record_error(duration)
                logger.error(f"Erro no cache para {func.__name__}: {e}")
                # Executar funcao sem cache em caso de erro
                return func(*args, **kwargs)
        
        # Preserva metadados da funcao original
        wrapper.__name__ = func.__name__
        wrapper.__qualname__ = func.__qualname__
        return wrapper
    return decorator

# Instancia global do gerenciador de cache
cache_manager = SmartCacheManager()

# Funcao de conveniencia para configurar cache
def configure_cache(app) -> SmartCacheManager:
    """Configura o cache para a aplicacao"""
    cache_manager.init_app(app)
    return cache_manager

# Decorators de conveniencia
def cache_short(func):
    """Decorator para cache de curta duracao (1 minuto)"""
    return cache_with_metrics(timeout=60, key_prefix='short:')(func)

def cache_medium(func):
    """Decorator para cache de media duracao (5 minutos)"""
    return cache_with_metrics(timeout=300, key_prefix='medium:')(func)

def cache_long(func):
    """Decorator para cache de longa duracao (30 minutos)"""
    return cache_with_metrics(timeout=1800, key_prefix='long:')(func)
