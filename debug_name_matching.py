#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import json

def debug_name_matching():
    """Debug detalhado do matching de nomes"""
    
    # Mapeamento esperado baseado nos grupos do GLPI
    expected_mapping = {
        'N1': ['nicolas fernando muniz nunez', 'anderson da silva morim de oliveira'],
        'N2': ['jonathan nascimento moletta', 'leonardo trojan repiso riela', 'alessandro carbonera vieira', 
               'edson joel dos santos silva', 'thales vinicius paz leite', 'silvio godinho valim'],
        'N3': ['jorge antonio vicente júnior', 'miguelangelo ferreira', 'pablo hebling guimaraes', 
               'anderson da silva morim de oliveira', 'silvio godinho valim'],
        'N4': ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 
               'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
    }
    
    print("🔍 DEBUG: Matching de Nomes dos Técnicos")
    print("=" * 60)
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    try:
        # Buscar todos os técnicos
        technicians_data = glpi_service.get_technician_ranking()
        
        print(f"\n📊 Total de técnicos encontrados: {len(technicians_data)}")
        
        # Debug individual de cada técnico
        for tech in technicians_data:
            user_id = tech.get('user_id')
            user_name = tech.get('user_name', '').lower().strip()
            current_level = glpi_service._get_technician_level(user_id)
            
            print(f"\n👤 Técnico ID: {user_id}")
            print(f"   Nome original: {tech.get('user_name', '')}")
            print(f"   Nome normalizado: '{user_name}'")
            print(f"   Nível atual: {current_level}")
            
            # Verificar em qual nível deveria estar
            expected_level = None
            for level, names in expected_mapping.items():
                if user_name in names:
                    expected_level = level
                    break
            
            print(f"   Nível esperado: {expected_level}")
            
            # Verificar matching detalhado
            print("   Matching detalhado:")
            
            # Verificar N4
            n4_names = ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 
                       'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
            n4_match = user_name in n4_names
            print(f"     N4: {n4_match} (lista: {n4_names})")
            
            # Verificar N3
            n3_names = ['jorge antonio vicente júnior', 'miguelangelo ferreira', 'pablo hebling guimaraes', 
                       'anderson da silva morim de oliveira', 'silvio godinho valim']
            n3_match = user_name in n3_names
            print(f"     N3: {n3_match} (lista: {n3_names})")
            
            # Verificar N2
            n2_names = ['jonathan nascimento moletta', 'leonardo trojan repiso riela', 'alessandro carbonera vieira', 
                       'edson joel dos santos silva', 'thales vinicius paz leite', 'silvio godinho valim']
            n2_match = user_name in n2_names
            print(f"     N2: {n2_match} (lista: {n2_names})")
            
            # Verificar N1
            n1_names = ['nicolas fernando muniz nunez', 'anderson da silva morim de oliveira']
            n1_match = user_name in n1_names
            print(f"     N1: {n1_match} (lista: {n1_names})")
            
            # Verificar se há conflito
            matches = []
            if n4_match: matches.append('N4')
            if n3_match: matches.append('N3')
            if n2_match: matches.append('N2')
            if n1_match: matches.append('N1')
            
            if len(matches) > 1:
                print(f"   ⚠️  CONFLITO: Nome encontrado em múltiplos níveis: {matches}")
            elif len(matches) == 0:
                print(f"   ❌ ERRO: Nome não encontrado em nenhum nível")
            else:
                print(f"   ✅ Match único: {matches[0]}")
            
            if current_level != expected_level:
                print(f"   🚨 DISCREPÂNCIA: Atual={current_level}, Esperado={expected_level}")
            
            print("-" * 40)
    
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_name_matching()