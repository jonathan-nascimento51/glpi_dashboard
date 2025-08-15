#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico específico para o ranking de técnicos
Identifica onde está o problema na busca de técnicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.glpi_service import GLPIService
from app.config import Config
import json
import traceback

def debug_ranking_step_by_step():
    """Debug passo a passo do ranking de técnicos"""
    print("=== DIAGNÓSTICO ESPECÍFICO DO RANKING DE TÉCNICOS ===")
    
    try:
        # Inicializar serviço GLPI
        config = Config()
        glpi_service = GLPIService(config)
        
        print("\n1. Testando autenticação...")
        if not glpi_service._ensure_authenticated():
            print(" FALHA NA AUTENTICAÇÃO")
            return
        print(" Autenticação OK")
        
        print("\n2. Buscando perfis de técnicos...")
        # Buscar Profile_User com perfil de técnico (ID 6)
        profile_response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Profile_User",
            params={
                "range": "0-999",
                "criteria[0][field]": "4",  # Campo profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # ID do perfil técnico
            }
        )
        
        if profile_response and profile_response.get('data'):
            profile_data = profile_response['data']
            print(f" Encontrados {len(profile_data)} registros de Profile_User")
            print(f"Amostra dos primeiros 3 registros:")
            for i, profile in enumerate(profile_data[:3]):
                print(f"  Registro {i+1}: {profile}")
        else:
            print(" Nenhum Profile_User encontrado")
            return
        
        print("\n3. Extraindo usernames dos técnicos...")
        tech_usernames = set()
        for profile_user in profile_data:
            if isinstance(profile_user, dict) and "5" in profile_user:
                username = str(profile_user["5"])
                tech_usernames.add(username)
        
        print(f" Extraídos {len(tech_usernames)} usernames únicos")
        print(f"Usernames: {list(tech_usernames)[:10]}")
        
        print("\n4. Buscando usuários ativos...")
        user_params = {
            'range': '0-999',
        }
        
        users_response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/User",
            params=user_params
        )
        
        if users_response and isinstance(users_response, list):
            all_users = users_response
            print(f" Encontrados {len(all_users)} usuários totais")
        else:
            print(" Falha ao buscar usuários")
            return
        
        print("\n5. Criando mapa de usuários ativos...")
        active_users_map = {}
        for user in all_users:
            if isinstance(user, dict) and "1" in user:
                username = str(user["1"])
                active_users_map[username] = user
        
        print(f" Mapeados {len(active_users_map)} usuários ativos")
        print(f"Amostra de usernames ativos: {list(active_users_map.keys())[:10]}")
        
        print("\n6. Filtrando técnicos ativos...")
        active_tech_usernames = []
        for username in tech_usernames:
            if username in active_users_map:
                user_data = active_users_map[username]
                # Verificar se não está deletado (campo 23)
                is_deleted = user_data.get("23", "0")
                if str(is_deleted) == "0":
                    active_tech_usernames.append(username)
                    print(f"   Técnico ativo: {username} (ID: {user_data.get('2', 'N/A')})")
                else:
                    print(f"   Técnico deletado: {username}")
            else:
                print(f"   Técnico não encontrado nos usuários ativos: {username}")
        
        print(f"\n Total de técnicos ativos válidos: {len(active_tech_usernames)}")
        
        if not active_tech_usernames:
            print(" PROBLEMA IDENTIFICADO: Nenhum técnico ativo encontrado!")
            print("\nPossíveis causas:")
            print("- Técnicos estão marcados como deletados")
            print("- Usernames não coincidem entre Profile_User e User")
            print("- Perfil de técnico incorreto (não é ID 6)")
            return
        
        print("\n7. Descobrindo field_id do técnico...")
        # Buscar um ticket para descobrir o field_id
        tickets_response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/Ticket",
            params={'range': '0-1'}
        )
        
        tech_field_id = None
        if tickets_response and isinstance(tickets_response, list) and tickets_response:
            ticket = tickets_response[0]
            # Procurar por campos que podem ser do técnico
            for field_id, value in ticket.items():
                if field_id in ['5', '6', '8']:  # Campos comuns para técnicos
                    if value and str(value).isdigit():
                        tech_field_id = field_id
                        break
        
        if not tech_field_id:
            tech_field_id = '5'  # Fallback padrão
        
        print(f" Field ID do técnico: {tech_field_id}")
        
        print("\n8. Testando contagem de tickets para um técnico...")
        if active_tech_usernames:
            test_username = active_tech_usernames[0]
            test_user_data = active_users_map[test_username]
            test_user_id = int(test_user_data['2'])
            
            print(f"Testando técnico: {test_username} (ID: {test_user_id})")
            
            # Testar contagem de tickets
            total_tickets = glpi_service._count_tickets_by_technician_optimized(test_user_id, tech_field_id)
            print(f"Total de tickets: {total_tickets}")
            
            if total_tickets is None:
                print(" PROBLEMA: Contagem de tickets retornou None")
            elif total_tickets == 0:
                print(" AVISO: Técnico tem 0 tickets")
            else:
                print(f" Técnico tem {total_tickets} tickets")
        
        print("\n=== DIAGNÓSTICO CONCLUÍDO ===")
        
    except Exception as e:
        print(f" ERRO CRÍTICO: {e}")
        print(f"Stack trace: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_ranking_step_by_step()
