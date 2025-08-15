#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo para verificar se todos os níveis de técnicos estão sendo
corretamente identificados e filtrados no ranking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_all_levels():
    """Testa o ranking para todos os níveis de técnicos"""
    try:
        print("🚀 Iniciando teste completo de todos os níveis...")
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar cada nível individualmente
        levels_to_test = ['N1', 'N2', 'N3', 'N4']
        
        for level in levels_to_test:
            print(f"\n📊 Testando ranking para nível {level}...")
            ranking = glpi_service.get_technician_ranking_with_filters(level=level, limit=10)
            
            if ranking:
                print(f"✅ Ranking {level} obtido com {len(ranking)} técnicos")
                for tech in ranking:
                    print(f"  - {tech['name']}: {tech['total']} tickets, Nível: {tech['level']}")
                
                # Verificar se todos são realmente do nível correto
                all_correct_level = all(tech['level'] == level for tech in ranking)
                if all_correct_level:
                    print(f"✅ Todos os técnicos retornados são {level}")
                else:
                    print(f"❌ Nem todos os técnicos retornados são {level}")
                    incorrect = [tech for tech in ranking if tech['level'] != level]
                    for tech in incorrect:
                        print(f"  ⚠️ {tech['name']} está marcado como {tech['level']} mas deveria ser {level}")
            else:
                print(f"⚠️ Nenhum técnico {level} encontrado")
        
        # Testar ranking sem filtro de nível
        print(f"\n📊 Testando ranking sem filtro de nível...")
        ranking_all = glpi_service.get_technician_ranking_with_filters(limit=20)
        
        if ranking_all:
            print(f"✅ Ranking completo obtido com {len(ranking_all)} técnicos")
            
            # Contar técnicos por nível
            level_counts = {}
            for tech in ranking_all:
                level = tech['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print("📈 Distribuição por nível:")
            for level, count in sorted(level_counts.items()):
                print(f"  - {level}: {count} técnicos")
                
            # Mostrar alguns exemplos de cada nível
            print("\n👥 Exemplos por nível:")
            for level in ['N1', 'N2', 'N3', 'N4']:
                techs_of_level = [tech for tech in ranking_all if tech['level'] == level]
                if techs_of_level:
                    print(f"  {level}: {', '.join([tech['name'] for tech in techs_of_level[:3]])}")
                    if len(techs_of_level) > 3:
                        print(f"       ... e mais {len(techs_of_level) - 3} técnicos")
                else:
                    print(f"  {level}: Nenhum técnico encontrado")
        else:
            print("❌ Nenhum técnico encontrado no ranking completo")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste completo de níveis de técnicos...")
    success = test_all_levels()
    
    if success:
        print("\n✅ Teste completo concluído com sucesso!")
    else:
        print("\n❌ Teste completo falhou!")
        sys.exit(1)