#!/usr/bin/env python3
"""
Script para debugar o método _get_tickets_batch_without_date_filter
Verifica se a query está sendo construída corretamente e se retorna dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import json

def debug_batch_method():
    print("=== DEBUG: Método _get_tickets_batch_without_date_filter ===")
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação bem-sucedida")
    
    # Obter lista de técnicos
    print("\n1. Obtendo lista de técnicos...")
    technicians_result = glpi._get_all_technician_ids_and_names()
    
    # Verificar o tipo de retorno
    print(f"Tipo de retorno: {type(technicians_result)}")
    
    # Extrair IDs baseado no tipo de retorno
    if isinstance(technicians_result, tuple) and len(technicians_result) == 2:
        tech_ids_list, tech_names = technicians_result
        print(f"✅ Tupla extraída com sucesso")
        print(f"   - IDs: {len(tech_ids_list)} técnicos")
        print(f"   - Nomes: {len(tech_names)} técnicos")
        print(f"   - Primeiros 5 IDs: {tech_ids_list[:5]}")
        print(f"   - Primeiros 5 nomes: {dict(list(tech_names.items())[:5])}")
        
        tech_ids = tech_ids_list[:5]  # Pegar apenas 5 técnicos para teste
        technicians = tech_names
    else:
        print(f"❌ Tipo de retorno inesperado: {type(technicians_result)}")
        print(f"   Conteúdo: {technicians_result}")
        return
    
    if not tech_ids:
        print("❌ Nenhum técnico encontrado")
        return
    
    print(f"✅ {len(tech_ids)} técnicos selecionados para teste: {tech_ids}")
    print(f"Técnicos: {[(tech_id, technicians.get(tech_id, f'Técnico {tech_id}')) for tech_id in tech_ids]}")
    
    # Testar construção da query
    print("\n2. Testando construção da query...")
    
    # Construir parâmetros manualmente para debug
    search_params = {
        "is_deleted": 0,
        "range": "0-9999",
        "forcedisplay[0]": "4",  # users_id_tech
        "forcedisplay[1]": "2",  # id
    }
    
    # Adicionar critérios para cada técnico com OR
    criteria_index = 0
    for i, tech_id in enumerate(tech_ids):
        if i == 0:
            # Primeiro critério não precisa de link
            search_params.update({
                f"criteria[{criteria_index}][field]": "4",  # users_id_tech
                f"criteria[{criteria_index}][searchtype]": "equals",
                f"criteria[{criteria_index}][value]": str(tech_id)
            })
        else:
            # Demais critérios usam OR
            search_params.update({
                f"criteria[{criteria_index}][link]": "OR",
                f"criteria[{criteria_index}][field]": "4",  # users_id_tech
                f"criteria[{criteria_index}][searchtype]": "equals",
                f"criteria[{criteria_index}][value]": str(tech_id)
            })
        criteria_index += 1
    
    print("\nParâmetros da query:")
    for key, value in search_params.items():
        print(f"  {key}: {value}")
    
    # Fazer requisição manual
    print("\n3. Fazendo requisição manual...")
    url = f"{glpi.glpi_url}/search/Ticket"
    
    try:
        response = glpi._make_authenticated_request("GET", url, params=search_params)
        
        if not response:
            print("❌ Resposta vazia")
            return
        
        if not response.ok:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text[:500]}")
            return
        
        data = response.json()
        print(f"✅ Requisição bem-sucedida")
        print(f"Status: {response.status_code}")
        print(f"Total count: {data.get('totalcount', 'N/A')}")
        print(f"Count: {data.get('count', 'N/A')}")
        print(f"Data length: {len(data.get('data', []))}")
        
        # Analisar dados retornados
        if "data" in data and data["data"]:
            print("\n4. Analisando dados retornados...")
            ticket_counts = {tech_id: 0 for tech_id in tech_ids}
            
            for i, ticket in enumerate(data["data"][:10]):  # Mostrar apenas 10 primeiros
                tech_id = str(ticket.get("4", ""))  # users_id_tech
                ticket_id = ticket.get("2", "N/A")  # id
                print(f"  Ticket {i+1}: ID={ticket_id}, Técnico={tech_id}")
                
                if tech_id in ticket_counts:
                    ticket_counts[tech_id] += 1
            
            # Contar todos os tickets
            for ticket in data["data"]:
                tech_id = str(ticket.get("4", ""))
                if tech_id in ticket_counts:
                    ticket_counts[tech_id] += 1
            
            print("\n5. Contagem final por técnico:")
            total_tickets = 0
            for tech_id, count in ticket_counts.items():
                tech_name = technicians.get(tech_id, f"Técnico {tech_id}")
                print(f"  {tech_name} (ID: {tech_id}): {count} tickets")
                total_tickets += count
            
            print(f"\nTotal de tickets encontrados: {total_tickets}")
        else:
            print("❌ Nenhum dado retornado")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Testar método original
    print("\n6. Testando método original _get_tickets_batch_without_date_filter...")
    try:
        result = glpi._get_tickets_batch_without_date_filter(tech_ids)
        print(f"✅ Método original executado")
        print(f"Resultado: {result}")
        
        total_original = sum(result.values())
        print(f"Total pelo método original: {total_original}")
        
    except Exception as e:
        print(f"❌ Erro no método original: {e}")
    
    print("\n=== FIM DO DEBUG ===")

if __name__ == "__main__":
    debug_batch_method()