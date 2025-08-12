from typing import Any, Optional
import time
from domain.interfaces.repositories import CacheRepositoryInterface

class InMemoryCacheAdapter(CacheRepositoryInterface):
    """Adaptador de cache em memória"""
    
    def __init__(self):
        self._cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        try:
            if key in self._cache:
                cache_entry = self._cache[key]
                current_time = time.time()
                
                # Verifica se não expirou
                if cache_entry["expires_at"] > current_time:
                    return cache_entry["value"]
                else:
                    # Remove entrada expirada
                    del self._cache[key]
            
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Define valor no cache"""
        try:
            current_time = time.time()
            expires_at = current_time + ttl
            
            self._cache[key] = {
                "value": value,
                "created_at": current_time,
                "expires_at": expires_at
            }
            
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            if key in self._cache:
                del self._cache[key]
            return True
        except Exception:
            return False
    
    async def clear(self) -> bool:
        """Limpa todo o cache"""
        try:
            self._cache.clear()
            return True
        except Exception:
            return False
