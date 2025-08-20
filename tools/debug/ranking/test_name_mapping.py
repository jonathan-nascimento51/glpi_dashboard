#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificar o mapeamento de nomes para níveis.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_name_mapping():
    """Testa o mapeamento de nomes para níveis"""
    try:
        print("🚀 Iniciando teste de mapeamento de nomes...")
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar nomes específicos que deveriam ser encontrados
        test_cases = [
            # Casos que deveriam ser N4
            ("Técnico silvio-godinho", "N4"),
            ("silvio-godinho", "N4"),
            ("Técnico edson-joel", "N4"),
            ("edson-joel", "N4"),
            ("Técnico paulo-pedo", "N4"),
            ("paulo-pedo", "N4"),
            
            # Casos que deveriam ser N3
            ("Técnico gabriel-machado", "N3"),
            ("gabriel-machado", "N3"),
            ("Técnico jorge-swift", "N3"),
            ("jorge-swift", "N3"),
            
            # Casos que deveriam ser N2
            ("Técnico gabriel-conceicao", "N2"),
            ("gabriel-conceicao", "N2"),
            ("Técnico luciano-araujo", "N2"),
            ("luciano-araujo", "N2"),
            
            # Casos que não estão mapeados (deveriam ser N1)
            ("Técnico anderson-oliveira", "N1"),
            ("anderson-oliveira", "N1"),
        ]
        
        print("\n🔍 Testando mapeamento de nomes:")
        all_correct = True
        
        for test_name, expected_level in test_cases:
            actual_level = glpi_service._get_technician_level_by_name(test_name)
            status = "✅" if actual_level == expected_level else "❌"
            print(f"  {status} {test_name} -> {actual_level} (esperado: {expected_level})")
            
            if actual_level != expected_level:
                all_correct = False
        
        if all_correct:
            print("\n✅ Todos os testes de mapeamento passaram!")
        else:
            print("\n❌ Alguns testes de mapeamento falharam!")
            
        return all_correct
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de mapeamento de nomes...")
    success = test_name_mapping()
    
    if success:
        print("\n✅ Teste de mapeamento concluído com sucesso!")
    else:
        print("\n❌ Teste de mapeamento falhou!")
        sys.exit(1)