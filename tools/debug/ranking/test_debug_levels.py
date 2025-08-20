#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de debug para verificar se os níveis estão sendo determinados corretamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_debug_levels():
    """Testa a determinação de níveis com debug detalhado"""
    try:
        print("🚀 Iniciando teste de debug de níveis...")
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar alguns nomes específicos
        test_names = [
            "Técnico jorge-swift",
            "Técnico luciano-araujo", 
            "Técnico gabriel-conceicao",
            "Técnico gabriel-machado",
            "Técnico silvio-godinho",
            "Técnico edson-joel"
        ]
        
        print("\n🔍 Testando determinação de nível por nome:")
        for name in test_names:
            level = glpi_service._get_technician_level_by_name(name)
            print(f"  {name} -> {level}")
        
        # Testar ranking com limite pequeno para ver os logs
        print("\n📊 Testando ranking com limite pequeno...")
        ranking = glpi_service.get_technician_ranking_with_filters(limit=5)
        
        if ranking:
            print(f"✅ Ranking obtido com {len(ranking)} técnicos:")
            for tech in ranking:
                print(f"  - {tech['name']}: {tech['total']} tickets, Nível: {tech['level']}")
        else:
            print("❌ Nenhum técnico encontrado no ranking")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de debug de níveis...")
    success = test_debug_levels()
    
    if success:
        print("\n✅ Teste de debug concluído!")
    else:
        print("\n❌ Teste de debug falhou!")
        sys.exit(1)