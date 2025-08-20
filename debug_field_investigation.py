#!/usr/bin/env python3
"""
Script para investigar qual campo realmente contém os técnicos nos tickets do GLPI.
Este script vai analisar tickets aleatórios e mapear todos os campos para identificar
onde estão os IDs dos técnicos.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.glpi_service import GLPIService
from datetime import datetime, timedelta
import json

def investigate_ticket_fields():
    """Investiga os campos dos tickets para encontrar onde estão os técnicos."""
    
    print("=== INVESTIGAÇÃO DE CAMPOS DOS TICKETS ===")
    
    try:
        # Inicializar serviço GLPI
        glpi = GLPIService()
        
        print("\n1. Autenticando no GLPI...")
        if not glpi.authenticate():
            print("[ERRO] Falha na autenticação")
            return
        print("[OK] Autenticação bem-sucedida")
        
        print("\n2. Buscando tickets aleatórios para análise...")
        
        # Buscar tickets aleatórios
        search_params = {
            "is_deleted": 0,
            "range": "0-20",  # Pegar 20 tickets para análise
            "sort": "1",
            "order": "DESC"
        }
        
        response = glpi._make_authenticated_request(
            "GET",
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params
        )
        
        if not response or not response.ok:
            print(f"[ERRO] Falha ao buscar tickets: {response.status_code if response else 'Sem resposta'}")
            return
            
        data = response.json()
        if not isinstance(data, dict) or "data" not in data:
            print("[ERRO] Resposta não contém dados esperados")
            print(f"[DEBUG] Resposta: {data}")
            return
            
        tickets = data["data"]
        print(f"[OK] {len(tickets)} tickets encontrados para análise")
        
        print("\n3. Analisando estrutura dos tickets...")
        
        # Analisar os primeiros tickets para entender a estrutura
        field_analysis = {}
        technician_candidates = set()
        
        for i, ticket in enumerate(tickets[:10]):  # Analisar apenas os primeiros 10
            print(f"\n--- Ticket {i+1} (ID: {ticket.get('2', 'N/A')}) ---")
            
            # Mostrar todos os campos do ticket
            for field_id, value in ticket.items():
                if field_id not in field_analysis:
                    field_analysis[field_id] = []
                field_analysis[field_id].append(value)
                
                # Se o valor parece ser um ID de usuário (número entre 1 e 10000)
                if isinstance(value, (int, str)):
                    try:
                        num_value = int(value)
                        if 1 <= num_value <= 10000:  # Range típico de IDs de usuário
                            technician_candidates.add((field_id, num_value))
                            print(f"   Campo {field_id}: {value} (candidato a técnico)")
                        else:
                            print(f"   Campo {field_id}: {value}")
                    except (ValueError, TypeError):
                        print(f"   Campo {field_id}: {value}")
                else:
                    print(f"   Campo {field_id}: {value}")
        
        print("\n4. Resumo da análise de campos...")
        print(f"[INFO] Total de campos únicos encontrados: {len(field_analysis)}")
        print(f"[INFO] Candidatos a campo de técnico: {len(technician_candidates)}")
        
        # Agrupar candidatos por campo
        candidates_by_field = {}
        for field_id, user_id in technician_candidates:
            if field_id not in candidates_by_field:
                candidates_by_field[field_id] = set()
            candidates_by_field[field_id].add(user_id)
        
        print("\n5. Análise de candidatos a campo de técnico:")
        for field_id, user_ids in candidates_by_field.items():
            print(f"   Campo {field_id}: {len(user_ids)} técnicos únicos - {sorted(list(user_ids))}")
        
        print("\n6. Verificando campos conhecidos...")
        
        # Buscar informações sobre os campos
        field_info_response = glpi._make_authenticated_request(
            "GET",
            f"{glpi.glpi_url}/listSearchOptions/Ticket"
        )
        
        if field_info_response and field_info_response.ok:
            field_info = field_info_response.json()
            print("[OK] Informações de campos obtidas")
            
            # Procurar por campos relacionados a técnicos
            tech_related_fields = []
            for field_id, info in field_info.items():
                if isinstance(info, dict) and 'name' in info:
                    field_name = info['name'].lower()
                    if any(keyword in field_name for keyword in ['tecnico', 'technician', 'assign', 'atribuido', 'responsavel']):
                        tech_related_fields.append((field_id, info['name']))
                        print(f"   Campo {field_id}: {info['name']} (relacionado a técnico)")
            
            print(f"\n[INFO] {len(tech_related_fields)} campos relacionados a técnicos encontrados")
            
            # Comparar com os candidatos encontrados
            print("\n7. Comparação entre candidatos e campos conhecidos:")
            for field_id, field_name in tech_related_fields:
                if field_id in candidates_by_field:
                    user_count = len(candidates_by_field[field_id])
                    print(f"   [MATCH] Campo {field_id} ({field_name}): {user_count} técnicos encontrados")
                else:
                    print(f"   [NO MATCH] Campo {field_id} ({field_name}): não encontrado nos tickets")
        
        print("\n8. Testando contagem com diferentes campos...")
        
        # Testar contagem usando os campos candidatos mais promissores
        for field_id in sorted(candidates_by_field.keys()):
            if len(candidates_by_field[field_id]) >= 2:  # Pelo menos 2 técnicos diferentes
                print(f"\n   Testando campo {field_id}...")
                
                # Pegar um técnico deste campo para testar
                test_tech_id = list(candidates_by_field[field_id])[0]
                
                # Fazer uma busca usando este campo
                test_params = {
                    "is_deleted": 0,
                    "range": "0-0",  # Só queremos o count
                    f"criteria[0][field]": field_id,
                    f"criteria[0][searchtype]": "equals",
                    f"criteria[0][value]": test_tech_id
                }
                
                test_response = glpi._make_authenticated_request(
                    "GET",
                    f"{glpi.glpi_url}/search/Ticket",
                    params=test_params
                )
                
                if test_response and test_response.ok:
                    test_data = test_response.json()
                    total_count = test_data.get('totalcount', 0)
                    print(f"      Técnico {test_tech_id} no campo {field_id}: {total_count} tickets")
                    
                    if total_count > 0:
                        print(f"      [SUCESSO] Campo {field_id} parece ser o correto!")
        
        print("\n" + "="*60)
        print("=== CONCLUSÃO DA INVESTIGAÇÃO ===")
        print("Campos mais promissores para técnicos:")
        for field_id, user_ids in sorted(candidates_by_field.items(), key=lambda x: len(x[1]), reverse=True):
            if len(user_ids) >= 2:
                print(f"   Campo {field_id}: {len(user_ids)} técnicos únicos")
        
        # Encerrar sessão
        glpi.close_session()
        
    except Exception as e:
        print(f"[ERRO] Erro durante a investigação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_ticket_fields()