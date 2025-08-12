from domain.entities.dashboard_metrics import DashboardMetrics
from domain.interfaces.repositories import GLPIRepositoryInterface, CacheRepositoryInterface, ClockInterface

class GetDashboardMetricsUseCase:
    """Caso de uso para buscar métricas do dashboard"""
    
    def __init__(
        self,
        glpi_repository: GLPIRepositoryInterface,
        cache_repository: CacheRepositoryInterface,
        clock: ClockInterface,
        cache_ttl: int = 300
    ):
        self._glpi_repository = glpi_repository
        self._cache_repository = cache_repository
        self._clock = clock
        self._cache_ttl = cache_ttl
    
    async def execute(self, force_refresh: bool = False) -> DashboardMetrics:
        """Executa o caso de uso para buscar métricas"""
        cache_key = "dashboard_metrics"
        
        # Tenta buscar do cache primeiro
        if not force_refresh:
            cached_metrics = await self._cache_repository.get(cache_key)
            if cached_metrics:
                return cached_metrics
        
        # Busca dados do GLPI
        metrics = await self._glpi_repository.get_dashboard_metrics()
        
        # Atualiza timestamp
        metrics.last_updated = self._clock.now()
        
        # Salva no cache
        await self._cache_repository.set(cache_key, metrics, self._cache_ttl)
        
        return metrics
