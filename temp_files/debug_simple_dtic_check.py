#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_simple_dtic_check():
    """Debug simples para verificar se Gabriel Conceição passa no filtro DTIC"""
    glpi = GLPIService()
    
    print("=== DEBUG SIMPLES - FILTRO DTIC ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # IDs dos Gabriels
    gabriel_conceicao_id = 1404
    gabriel_machado_id = 1291
    
    print(f"\n--- Testando filtro DTIC manualmente ---")
    
    for gabriel_id, gabriel_name in [(gabriel_conceicao_id, "Gabriel Conceição"), (gabriel_machado_id, "Gabriel Machado")]:
        print(f"\n=== {gabriel_name} (ID: {gabriel_id}) ===")
        
        try:
            # 1. Verificar se o usuário existe e está ativo
            user_response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/User/{gabriel_id}"
            )
            
            if user_response and user_response.ok:
                user_data = user_response.json()
                user_name = user_data.get('name', '').lower()
                is_active = user_data.get('is_active', 0)
                is_deleted = user_data.get('is_deleted', 1)
                
                print(f"Nome: {user_name}")
                print(f"Ativo: {is_active == 1}")
                print(f"Não deletado: {is_deleted == 0}")
                
                # 2. Verificar se o usuário está ativo e não deletado
                if is_active == 1 and is_deleted == 0:
                    print("✅ Usuário ativo e não deletado")
                    
                    # 3. Contar total de tickets do usuário
                    tickets_response = glpi._make_authenticated_request(
                        'GET',
                        f"{glpi.glpi_url}/search/Ticket",
                        params={
                            "range": "0-1",
                            "criteria[0][field]": "5",  # Campo users_id_tech
                            "criteria[0][searchtype]": "equals",
                            "criteria[0][value]": str(gabriel_id),
                            "forcedisplay[0]": "2",  # ID do ticket
                        }
                    )
                    
                    if tickets_response and tickets_response.ok:
                        tickets_data = tickets_response.json()
                        total_tickets = tickets_data.get('totalcount', 0)
                        
                        print(f"Total de tickets: {total_tickets}")
                        
                        # 4. Filtro principal: técnicos da DTIC devem ter pelo menos 10 tickets
                        if total_tickets >= 10:
                            print(f"✅ {gabriel_name} PASSA no filtro DTIC - {total_tickets} tickets (>= 10)")
                            
                            # 5. Verificar nível
                            tech_level = glpi._get_technician_level(gabriel_id, total_tickets)
                            print(f"Nível determinado: {tech_level}")
                            
                        else:
                            print(f"❌ {gabriel_name} NÃO PASSA no filtro DTIC - apenas {total_tickets} tickets (mínimo: 10)")
                    else:
                        print("❌ Erro ao buscar tickets")
                        
                else:
                    print(f"❌ Usuário não está ativo ou foi deletado (ativo: {is_active}, deletado: {is_deleted})")
            else:
                print(f"❌ Erro ao buscar dados do usuário {gabriel_id}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_simple_dtic_check()