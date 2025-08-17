#!/usr/bin/env python3
"""
Testes para validar a configuração dos service_levels e prevenir inconsistências futuras
"""

import pytest
from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config


class TestServiceLevelsConfig:
    """Testes para validar a configuração dos níveis de serviço"""
    
    def test_service_levels_have_unique_group_ids(self):
        """Testa se cada nível tem um group_id único"""
        service = GLPIService()
        
        # Verificar se service_levels está configurado
        assert hasattr(service, 'service_levels'), "service_levels não está configurado"
        assert service.service_levels, "service_levels está vazio"
        
        # Extrair todos os group_ids (valores do dicionário)
        group_ids = list(service.service_levels.values())
        
        # Verificar se todos os group_ids são únicos
        unique_group_ids = set(group_ids)
        assert len(group_ids) == len(unique_group_ids), (
            f"Group IDs duplicados encontrados: {group_ids}. "
            f"Cada nível deve ter um group_id único."
        )
    
    def test_service_levels_have_expected_structure(self):
        """Testa se os service_levels têm a estrutura esperada"""
        service = GLPIService()
        
        expected_levels = ['N1', 'N2', 'N3', 'N4']
        
        # Verificar se todos os níveis esperados estão presentes
        for level in expected_levels:
            assert level in service.service_levels, f"Nível {level} não encontrado"
            
            group_id = service.service_levels[level]
            
            # Verificar tipos
            assert isinstance(group_id, int), f"group_id do {level} deve ser int"
            
            # Verificar valores válidos
            assert group_id > 0, f"group_id do {level} deve ser positivo"
    
    def test_service_levels_group_ids_are_correct(self):
        """Testa se os group_ids estão configurados com os valores corretos"""
        service = GLPIService()
        
        expected_group_ids = {
            'N1': 89,
            'N2': 90,
            'N3': 91,
            'N4': 92
        }
        
        for level, expected_group_id in expected_group_ids.items():
            actual_group_id = service.service_levels[level]
            assert actual_group_id == expected_group_id, (
                f"Nível {level} tem group_id {actual_group_id}, "
                f"mas deveria ter {expected_group_id}"
            )
    
    def test_no_duplicate_group_ids_across_levels(self):
        """Testa especificamente que não há group_ids duplicados"""
        service = GLPIService()
        
        group_id_to_levels = {}
        
        for level, group_id in service.service_levels.items():
            if group_id in group_id_to_levels:
                pytest.fail(
                    f"Group ID {group_id} está sendo usado por múltiplos níveis: "
                    f"{group_id_to_levels[group_id]} e {level}. "
                    f"Cada nível deve ter um group_id único."
                )
            
            group_id_to_levels[group_id] = level
    
    def test_service_levels_names_are_correct(self):
        """Testa se os nomes dos níveis estão corretos"""
        service = GLPIService()
        
        expected_levels = ['N1', 'N2', 'N3', 'N4']
        
        # Verificar se as chaves do dicionário são os nomes corretos
        actual_levels = list(service.service_levels.keys())
        
        for expected_level in expected_levels:
            assert expected_level in actual_levels, (
                f"Nível '{expected_level}' não encontrado. "
                f"Níveis disponíveis: {actual_levels}"
            )
    
    def test_service_levels_consistency_with_tests(self):
        """Testa se a configuração de produção é consistente com os testes"""
        service = GLPIService()
        
        # Verificar se temos exatamente 4 níveis
        assert len(service.service_levels) == 4, (
            f"Esperado 4 níveis, mas encontrado {len(service.service_levels)}"
        )
        
        # Verificar se os group_ids são sequenciais (89, 90, 91, 92)
        group_ids = sorted(service.service_levels.values())
        expected_sequence = [89, 90, 91, 92]
        
        assert group_ids == expected_sequence, (
            f"Group IDs devem ser {expected_sequence}, mas encontrado {group_ids}"
        )