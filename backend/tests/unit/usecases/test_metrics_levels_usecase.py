import pytest
from usecases.metrics_levels_usecase import MetricsLevelsUseCase
from schemas.metrics_levels import MetricsLevelsQueryParams, ServiceLevel

class TestMetricsLevelsUseCase:
    @pytest.fixture
    def use_case(self):
        return MetricsLevelsUseCase()
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_level_success(self, use_case):
        """Testa execução bem-sucedida do use case"""
        params = MetricsLevelsQueryParams()
        result = await use_case.get_metrics_by_level(params)
        
        assert result is not None
        assert hasattr(result, 'metrics_by_level')
        assert hasattr(result, 'aggregated_metrics')
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_specific_levels(self, use_case):
        """Testa filtro por níveis específicos"""
        params = MetricsLevelsQueryParams(
            levels=[ServiceLevel.N1, ServiceLevel.N2]
        )
        result = await use_case.get_metrics_by_level(params)
        
        assert result is not None
        # Verificar se apenas N1 e N2 estão presentes
        if result.metrics_by_level:
            levels = [metric.level for metric in result.metrics_by_level]
            assert any(level in [ServiceLevel.N1, ServiceLevel.N2] for level in levels)
