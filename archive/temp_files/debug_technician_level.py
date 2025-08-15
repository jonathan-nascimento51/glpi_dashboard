#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar o método _get_technician_level
Verifica como os nomes estão sendo construídos e comparados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def debug_technician_level():
    """Debug do método _get_technician_level"""
    
    print("=== DEBUG DO MÉTODO _get_technician_level ===")
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    # Focar apenas no Gabriel Machado para debug
    gabriel_machado_id = 1291
    
    test_users = [gabriel_machado_id]
    
    for user_id in test_users:
        print(f"\n--- Testando usuário ID: {user_id} ---")
        
        try:
            # Buscar dados do usuário diretamente
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/User/{user_id}"
            )
            
            if response and response.ok:
                user_data = response.json()
                print(f"Dados do usuário: {user_data}")
                
                # Construir nome como no método _get_technician_level
                display_name = ""
                if "realname" in user_data and "firstname" in user_data:
                    display_name = f"{user_data['firstname']} {user_data['realname']}"
                elif "realname" in user_data:
                    display_name = user_data["realname"]
                elif "name" in user_data:
                    display_name = user_data["name"]
                elif "1" in user_data:
                    display_name = user_data["1"]
                
                user_name = display_name.lower().strip()
                print(f"Nome construído para comparação: '{user_name}'")
                
                # Listas de nomes do método
                n1_names = ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez']
                n2_names = ['alessandro carbonera vieira', 'jonathan nascimento moletta', 'thales vinicius paz leite', 'leonardo trojan repiso riela', 'edson joel dos santos silva', 'luciano marcelino da silva']
                n3_names = ['anderson da silva morim de oliveira', 'silvio godinho valim', 'jorge antonio vicente júnior', 'pablo hebling guimaraes', 'miguelangelo ferreira']
                n4_names = ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
                
                # Verificar em qual lista está
                found_level = None
                if user_name in n4_names:
                    found_level = "N4"
                elif user_name in n3_names:
                    found_level = "N3"
                elif user_name in n2_names:
                    found_level = "N2"
                elif user_name in n1_names:
                    found_level = "N1"
                
                print(f"Nível encontrado por nome: {found_level}")
                
                # Chamar o método real para comparar
                real_level = glpi._get_technician_level(user_id, 100)
                print(f"Nível retornado pelo método: {real_level}")
                
                # Verificar se está nas listas
                print(f"\nVerificação detalhada:")
                print(f"  Está em N1: {user_name in n1_names}")
                print(f"  Está em N2: {user_name in n2_names}")
                print(f"  Está em N3: {user_name in n3_names}")
                print(f"  Está em N4: {user_name in n4_names}")
                
                # Mostrar nomes similares
                print(f"\nNomes similares em N4:")
                for name in n4_names:
                    if 'gabriel' in name:
                        print(f"  '{name}'")
                        
                print(f"\nNomes similares em N1:")
                for name in n1_names:
                    if 'gabriel' in name:
                        print(f"  '{name}'")
                
            else:
                print(f"❌ Erro ao buscar usuário {user_id}")
                
        except Exception as e:
            print(f"❌ Erro ao processar usuário {user_id}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_technician_level()