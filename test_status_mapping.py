#!/usr/bin/env python3
"""
Script para testar o mapeamento de status e verificar se os status 1-4 existem no GLPI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import requests

def test_status_mapping():
    """Testa o mapeamento de status e verifica quais existem no GLPI"""
    print("=== Teste de Mapeamento de Status ===")
    
    # Inicializar serviço
    glpi = GLPIService()
    
    try:
        # Autenticar
        if not glpi._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        print("✅ Autenticação bem-sucedida")
        
        # Descobrir field_ids
        if not glpi.discover_field_ids():
            print("❌ Falha ao descobrir field_ids")
            return
        print(f"✅ Field IDs descobertos: {glpi.field_ids}")
        
        # Verificar status_map atual
        print(f"\n📋 Status Map atual: {glpi.status_map}")
        
        # Testar cada status individualmente com grupo 17
        group_id = 17
        print(f"\n🔍 Testando contagens com grupo {group_id}:")
        
        for status_name, status_id in glpi.status_map.items():
            count = glpi.get_ticket_count(group_id, status_id)
            print(f"  - {status_name} (ID {status_id}): {count} tickets")
        
        # Testar status adicionais que podem existir
        print("\n🔍 Testando status adicionais (1-10):")
        for status_id in range(1, 11):
            if status_id not in glpi.status_map.values():
                count = glpi.get_ticket_count(group_id, status_id)
                if count > 0:
                    print(f"  - Status ID {status_id}: {count} tickets (não mapeado!)")
        
        # Buscar todos os status disponíveis no GLPI
        print("\n🔍 Buscando todos os status disponíveis no GLPI...")
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/Ticket/Status"
            )
            
            if response and response.ok:
                status_data = response.json()
                print(f"Status disponíveis no GLPI: {status_data}")
            else:
                print("❌ Não foi possível buscar status do GLPI")
        except Exception as e:
            print(f"❌ Erro ao buscar status: {e}")
        
        # Buscar informações sobre o grupo 17
        print(f"\n🔍 Verificando informações do grupo {group_id}...")
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/Group/{group_id}"
            )
            
            if response and response.ok:
                group_data = response.json()
                print(f"Dados do grupo {group_id}: {group_data}")
            else:
                print(f"❌ Não foi possível buscar dados do grupo {group_id}")
        except Exception as e:
            print(f"❌ Erro ao buscar grupo: {e}")
        
        # Fazer uma busca geral de tickets para ver quais status realmente existem
        print("\n🔍 Fazendo busca geral de tickets para identificar status únicos...")
        try:
            search_params = {
                "is_deleted": 0,
                "range": "0-50",  # Buscar apenas 50 tickets para análise
                "criteria[0][field]": glpi.field_ids["GROUP"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
            }
            
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and response.ok:
                data = response.json()
                if 'data' in data and data['data']:
                    status_field_id = glpi.field_ids["STATUS"]
                    unique_statuses = set()
                    
                    for ticket in data['data']:
                        if status_field_id in ticket:
                            unique_statuses.add(ticket[status_field_id])
                    
                    print(f"Status únicos encontrados nos tickets do grupo {group_id}: {sorted(unique_statuses)}")
                    
                    # Verificar se algum status não está mapeado
                    mapped_statuses = set(str(s) for s in glpi.status_map.values())
                    unmapped_statuses = unique_statuses - mapped_statuses
                    if unmapped_statuses:
                        print(f"⚠️  Status não mapeados encontrados: {unmapped_statuses}")
                else:
                    print("Nenhum ticket encontrado para análise")
            else:
                print("❌ Falha na busca geral de tickets")
        except Exception as e:
            print(f"❌ Erro na busca geral: {e}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        # Fechar sessão
        try:
            glpi.close_session()
            print("\n✅ Sessão encerrada")
        except:
            pass

if __name__ == "__main__":
    test_status_mapping()