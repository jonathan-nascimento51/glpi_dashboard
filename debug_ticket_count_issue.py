#!/usr/bin/env python3
"""
Script para debugar o problema de contagem de tickets retornando 0
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def debug_ticket_counting():
    """Debug detalhado da contagem de tickets"""
    print("=== DEBUG: PROBLEMA DE CONTAGEM DE TICKETS ===\n")
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    try:
        # Autenticar
        print("1. Autenticando no GLPI...")
        if not glpi.authenticate():
            print("[ERRO] Falha na autenticacao")
            return
        print("[OK] Autenticacao bem-sucedida\n")
        
        # Descobrir field IDs
        print("2. Descobrindo field IDs...")
        if not glpi.discover_field_ids():
            print("[ERRO] Falha ao descobrir field IDs")
            return
        print(f"[OK] Field IDs descobertos: {glpi.field_ids}\n")
        
        # Descobrir campo do técnico
        print("3. Descobrindo campo do técnico...")
        tech_field = glpi._discover_tech_field_id()
        print(f"[OK] Campo do tecnico: {tech_field}\n")
        
        # Buscar alguns técnicos para teste
        print("4. Buscando técnicos ativos...")
        tech_ids, tech_names = glpi._get_all_technician_ids_and_names()
        if not tech_ids:
            print("[ERRO] Nenhum tecnico encontrado")
            return
        
        print(f"[OK] {len(tech_ids)} tecnicos encontrados")
        test_techs = tech_ids[:3]  # Testar apenas os primeiros 3
        
        for tech_id in test_techs:
            tech_name = tech_names.get(tech_id, f"Técnico {tech_id}")
            print(f"\n--- Testando: {tech_name} (ID: {tech_id}) ---")
            
            # Teste 1: Busca direta na API sem filtros
            print("\n[TESTE 1] Busca direta sem filtros")
            search_params_direct = {
                "is_deleted": 0,
                "criteria[0][field]": tech_field,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech_id),
                "range": "0-4"  # Buscar apenas os primeiros 5 tickets
            }
            
            response = glpi._make_authenticated_request(
                "GET", 
                f"{glpi.glpi_url}/search/Ticket", 
                params=search_params_direct
            )
            
            if response and response.ok:
                try:
                    data = response.json()
                    if isinstance(data, dict) and "data" in data:
                        tickets_found = len(data["data"])
                        print(f"   [RESULTADO] Tickets encontrados na busca direta: {tickets_found}")
                        
                        # Mostrar alguns tickets se encontrados
                        if tickets_found > 0:
                            print("   [INFO] Primeiros tickets encontrados:")
                            for i, ticket in enumerate(data["data"][:3]):
                                ticket_id = ticket.get("2", "N/A")  # Campo ID
                                ticket_title = ticket.get("1", "N/A")  # Campo título
                                print(f"      - Ticket {ticket_id}: {ticket_title}")
                    else:
                        print("   [ERRO] Resposta nao contem dados esperados")
                        print(f"   [DEBUG] Resposta: {data}")
                except Exception as e:
                    print(f"   [ERRO] Erro ao processar resposta: {e}")
            else:
                print(f"   [ERRO] Falha na requisicao: {response.status_code if response else 'Sem resposta'}")
            
            # Teste 2: Contagem usando range 0-0
            print("\n[TESTE 2] Contagem usando range 0-0")
            search_params_count = {
                "is_deleted": 0,
                "criteria[0][field]": tech_field,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech_id),
                "range": "0-0"  # Apenas contagem
            }
            
            response = glpi._make_authenticated_request(
                "GET", 
                f"{glpi.glpi_url}/search/Ticket", 
                params=search_params_count
            )
            
            if response and response.ok:
                # Verificar Content-Range
                if "Content-Range" in response.headers:
                    content_range = response.headers["Content-Range"]
                    print(f"   [INFO] Content-Range: {content_range}")
                    try:
                        total = int(content_range.split("/")[-1])
                        print(f"   [INFO] Total de tickets (Content-Range): {total}")
                    except:
                        print(f"   [ERRO] Erro ao parsear Content-Range: {content_range}")
                else:
                    print("   [ERRO] Content-Range não encontrado nos headers")
                    print(f"   [INFO] Headers: {dict(response.headers)}")
            else:
                print(f"   [ERRO] Falha na requisição: {response.status_code if response else 'Sem resposta'}")
            
            # Teste 3: Método _count_tickets_with_date_filter sem filtros
            print("\n[TESTE 3] Método _count_tickets_with_date_filter (sem filtros)")
            count_no_filter = glpi._count_tickets_with_date_filter(tech_id)
            print(f"   [RESULTADO] Resultado: {count_no_filter} tickets")
            
            # Teste 4: Método _count_tickets_with_date_filter com filtros amplos
            print("\n[TESTE 4] Método _count_tickets_with_date_filter (com filtros amplos)")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 1 ano atrás
            
            count_with_filter = glpi._count_tickets_with_date_filter(
                tech_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            print(f"   [RESULTADO] Resultado (1 ano): {count_with_filter} tickets")
            
            # Teste 5: Verificar se o técnico existe nos tickets
            print("\n[TESTE 5] Verificar presença do técnico em tickets aleatórios")
            search_params_random = {
                "is_deleted": 0,
                "range": "0-9",  # Buscar 10 tickets aleatórios
                "forcedisplay[0]": "4",  # users_id_tech
                "forcedisplay[1]": "2",  # id
                "forcedisplay[2]": "1",  # name/title
            }
            
            response = glpi._make_authenticated_request(
                "GET", 
                f"{glpi.glpi_url}/search/Ticket", 
                params=search_params_random
            )
            
            if response and response.ok:
                try:
                    data = response.json()
                    if isinstance(data, dict) and "data" in data:
                        print(f"   [INFO] {len(data['data'])} tickets aleatórios encontrados")
                        tech_found_in_random = False
                        for ticket in data["data"]:
                            ticket_tech_id = ticket.get("4", "0")  # users_id_tech
                            if str(ticket_tech_id) == str(tech_id):
                                tech_found_in_random = True
                                ticket_id = ticket.get("2", "N/A")
                                print(f"   [OK] Técnico encontrado no ticket {ticket_id}")
                                break
                        
                        if not tech_found_in_random:
                            print(f"   [ERRO] Técnico {tech_id} não encontrado nos tickets aleatórios")
                            # Mostrar alguns técnicos que foram encontrados
                            print("   [INFO] Técnicos encontrados nos tickets aleatórios:")
                            unique_techs = set()
                            for ticket in data["data"]:
                                tech_in_ticket = ticket.get("4", "0")
                                if tech_in_ticket != "0":
                                    unique_techs.add(tech_in_ticket)
                            for tech in list(unique_techs)[:5]:
                                print(f"      - Técnico ID: {tech}")
                except Exception as e:
                    print(f"   [ERRO] Erro ao processar tickets aleatórios: {e}")
            
            print("\n" + "="*60)
        
        print("\n=== RESUMO DO DEBUG ===")
        print("Se todos os métodos retornaram 0 tickets, o problema pode ser:")
        print("1. Campo do técnico incorreto (verificar se field_id está correto)")
        print("2. Dados não existem no GLPI para estes técnicos")
        print("3. Problema na autenticação ou permissões")
        print("4. Estrutura de dados diferente do esperado")
        
    except Exception as e:
        print(f"[ERRO] Erro durante o debug: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar sessão
        try:
            glpi.close_session()
        except:
            pass

if __name__ == "__main__":
    debug_ticket_counting()