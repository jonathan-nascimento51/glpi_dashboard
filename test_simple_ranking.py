#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar o ranking com poucos técnicos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_simple_ranking():
    """Testa o ranking com limite muito pequeno"""
    try:
        print("🚀 Iniciando teste simples de ranking...")
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar ranking com limite muito pequeno
        print("\n📊 Testando ranking com limite de 3 técnicos...")
        ranking = glpi_service.get_technician_ranking_with_filters(limit=3)
        
        if ranking:
            print(f"✅ Ranking obtido com {len(ranking)} técnicos:")
            for i, tech in enumerate(ranking, 1):
                print(f"  {i}. {tech['name']}: {tech['total']} tickets, Nível: {tech['level']}")
        else:
            print("❌ Nenhum técnico encontrado no ranking")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste simples de ranking...")
    success = test_simple_ranking()
    
    if success:
        print("\n✅ Teste simples concluído!")
    else:
        print("\n❌ Teste simples falhou!")
        sys.exit(1)