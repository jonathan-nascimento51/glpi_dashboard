#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
import json

def test_status():
    """Testa status existentes no GLPI"""
    print("🔍 Testando status existentes no GLPI...")
    
    service = GLPIService()
    
    # Autenticar
    if not service._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticado com sucesso")
    
    # Buscar tickets para ver quais status existem
    try:
        # Buscar alguns tickets para ver os status
        response = service._make_authenticated_request('GET', f'{service.glpi_url}/search/Ticket', params={'range': '0-10'})
        
        if not response:
            print("❌ Resposta vazia")
            return
            
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code in [200, 206]:
            data = response.json()
            
            if isinstance(data, dict) and 'data' in data:
                tickets = data['data']
                print(f"📈 Total de tickets encontrados: {len(tickets)}")
                
                # Coletar status únicos
                status_set = set()
                group_set = set()
                
                print("\n🎫 Primeiros 5 tickets:")
                for i, ticket in enumerate(tickets[:5]):
                    ticket_id = ticket.get('2', 'N/A')  # ID do ticket
                    ticket_name = ticket.get('1', 'Sem nome')  # Nome do ticket
                    status_id = ticket.get('12', 'N/A')  # Status
                    group_id = ticket.get('8', 'N/A')  # Grupo
                    
                    print(f"  {i+1}. ID: {ticket_id} - Nome: {ticket_name[:50]}...")
                    print(f"      Status ID: {status_id}, Grupo ID: {group_id}")
                    
                    if status_id != 'N/A':
                        status_set.add(str(status_id))
                    if group_id != 'N/A':
                        if isinstance(group_id, list):
                            for g in group_id:
                                if isinstance(g, str) and '>' in g:
                                    # Extrair ID do grupo se estiver no formato "Nome > Nível"
                                    continue
                                else:
                                    group_set.add(str(g))
                        else:
                            group_set.add(str(group_id))
                
                print(f"\n📋 Status únicos encontrados: {sorted(status_set)}")
                print(f"🏷️  Grupos únicos encontrados: {sorted(group_set)}")
                
                # Testar contagem com status e grupos reais
                print("\n🧪 Testando contagens com dados reais:")
                if status_set:
                    test_status = list(status_set)[0]
                    
                    # Usar um grupo conhecido que existe (ID 17 = CC-SE-SUBADM-DTIC)
                    test_group = 17
                    
                    print(f"Testando grupo {test_group} com status {test_status}...")
                    try:
                        count = service.get_ticket_count(test_group, int(test_status))
                        print(f"Resultado: {count} tickets")
                    except Exception as e:
                        print(f"Erro: {e}")
                        
                    # Testar também com status 1 (novo) se existir
                    print(f"\nTestando grupo {test_group} com status 1 (novo)...")
                    try:
                        count = service.get_ticket_count(test_group, 1)
                        print(f"Resultado: {count} tickets")
                    except Exception as e:
                        print(f"Erro: {e}")
                
            else:
                print(f"❌ Formato de resposta inesperado: {type(data)}")
                print(f"Dados: {data}")
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar tickets: {e}")

if __name__ == "__main__":
    test_status()