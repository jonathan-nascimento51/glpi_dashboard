#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import json

def debug_technician_level_method():
    """Debug específico do método _get_technician_level"""
    
    print("🔍 DEBUG: Método _get_technician_level")
    print("=" * 60)
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Mapeamento esperado
    expected_mapping = {
        'N1': ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez'],
        'N2': ['alessandro carbonera vieira', 'jonathan nascimento moletta', 
               'thales vinicius paz leite', 'leonardo trojan repiso riela',
               'edson joel dos santos silva', 'luciano marcelino da silva'],
        'N3': ['anderson da silva morim de oliveira', 'silvio godinho valim',
               'jorge antonio vicente júnior', 'pablo hebling guimaraes', 
               'miguelangelo ferreira'],
        'N4': ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue',
               'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
    }
    
    try:
        # Buscar dados dos técnicos
        technicians_data = glpi_service.get_technician_ranking()
        
        print(f"\n📊 Total de técnicos encontrados: {len(technicians_data)}")
        
        # Testar alguns técnicos específicos
        test_cases = [
            'Anderson Da Silva Morim De Oliveira',
            'Silvio Godinho Valim', 
            'Jorge Antonio Vicente Júnior',
            'Gabriel Silva Machado',
            'Jonathan Nascimento Moletta'
        ]
        
        for tech_data in technicians_data:
            if tech_data.get('name') in test_cases:
                user_id = int(tech_data['id'])
                user_name = tech_data['name']
                
                print(f"\n👤 Testando: {user_name} (ID: {user_id})")
                
                # Chamar diretamente o método _get_technician_level
                level = glpi_service._get_technician_level(user_id, tech_data['total'], technicians_data)
                
                print(f"   Nível retornado: {level}")
                
                # Verificar qual deveria ser o nível esperado
                user_name_lower = user_name.lower().strip()
                expected_level = None
                for level_key, names in expected_mapping.items():
                    if user_name_lower in names:
                        expected_level = level_key
                        break
                
                print(f"   Nível esperado: {expected_level}")
                
                if level != expected_level:
                    print(f"   🚨 DISCREPÂNCIA DETECTADA!")
                    
                    # Debug detalhado do matching
                    print(f"   Debug do matching:")
                    print(f"     Nome normalizado: '{user_name_lower}'")
                    
                    # Verificar as listas manualmente
                    n4_names = ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 
                               'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
                    n3_names = ['jorge antonio vicente júnior', 'miguelangelo ferreira', 'pablo hebling guimaraes', 
                               'anderson da silva morim de oliveira', 'silvio godinho valim']
                    n2_names = ['jonathan nascimento moletta', 'leonardo trojan repiso riela', 'alessandro carbonera vieira', 
                               'edson joel dos santos silva', 'thales vinicius paz leite', 'silvio godinho valim']
                    n1_names = ['nicolas fernando muniz nunez', 'anderson da silva morim de oliveira']
                    
                    print(f"     Em N4: {user_name_lower in n4_names}")
                    print(f"     Em N3: {user_name_lower in n3_names}")
                    print(f"     Em N2: {user_name_lower in n2_names}")
                    print(f"     Em N1: {user_name_lower in n1_names}")
                    
                    # Verificar se há caracteres especiais ou diferenças
                    print(f"     Caracteres do nome: {[ord(c) for c in user_name_lower]}")
                    
                    # Verificar se está em alguma lista esperada
                    for level_key, names in expected_mapping.items():
                        for name in names:
                            if name == user_name_lower:
                                print(f"     ✅ Encontrado em {level_key}: '{name}'")
                            elif name.replace(' ', '') == user_name_lower.replace(' ', ''):
                                print(f"     ⚠️  Possível match sem espaços em {level_key}: '{name}'")
                else:
                    print(f"   ✅ Classificação correta!")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_technician_level_method()