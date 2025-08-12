#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de filtragem por nível específico
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_level_filtering():
    """Testa a filtragem por nível específico"""
    print("🚀 Iniciando teste de filtragem por nível...")
    
    service = GLPIService()
    
    # Testar cada nível individualmente
    levels = ['N1', 'N2', 'N3', 'N4']
    
    for level in levels:
        print(f"\n📊 Testando filtro para nível {level}...")
        
        try:
            ranking = service.get_technician_ranking_with_filters(
                limit=5,
                level=level
            )
            
            if ranking and 'technicians' in ranking:
                techs = ranking['technicians']
                print(f"✅ Encontrados {len(techs)} técnicos {level}:")
                
                for i, tech in enumerate(techs, 1):
                    tech_level = tech.get('level', 'N/A')
                    print(f"  {i}. {tech['name']}: {tech['ticket_count']} tickets, Nível: {tech_level}")
                    
                    # Verificar se todos os técnicos retornados são do nível correto
                    if tech_level != level:
                        print(f"❌ ERRO: Técnico {tech['name']} tem nível {tech_level}, mas deveria ser {level}")
                        return False
                        
                print(f"✅ Todos os técnicos retornados são {level}")
            else:
                print(f"ℹ️ Nenhum técnico {level} encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao testar nível {level}: {e}")
            return False
    
    print("\n✅ Teste de filtragem por nível concluído com sucesso!")
    return True

if __name__ == "__main__":
    test_level_filtering()