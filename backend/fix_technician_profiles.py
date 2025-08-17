#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o método get_technician_ranking_knowledge_base
para buscar técnicos nos perfis corretos (13, 14, 15) em vez de apenas o perfil 6.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.glpi_service import GLPIService
import datetime

def test_current_method():
    """Testa o método atual para confirmar o problema"""
    print("=== TESTANDO MÉTODO ATUAL ===")
    service = GLPIService()
    
    if not service.authenticate():
        print("Erro: Falha na autenticação")
        return
    
    ranking = service._get_technician_ranking_knowledge_base()
    print(f"Ranking atual: {len(ranking)} técnicos encontrados")
    for tech in ranking:
        print(f"  - {tech['name']} ({tech['level']}): {tech['total']} tickets")
    
    return ranking

def test_correct_profiles():
    """Testa buscar técnicos nos perfis corretos"""
    print("\n=== TESTANDO PERFIS CORRETOS ===")
    service = GLPIService()
    
    if not service.authenticate():
        print("Erro: Falha na autenticação")
        return
    
    # Perfis corretos baseados no debug anterior
    correct_profiles = [13, 14, 15]  # N2, N3, N4
    all_technicians = []
    
    for profile_id in correct_profiles:
        print(f"\nBuscando usuários no perfil {profile_id}...")
        
        try:
            # Buscar usuários com este perfil
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/Profile_User",
                params={
                    'criteria[0][field]': 'profiles_id',
                    'criteria[0][searchtype]': 'equals',
                    'criteria[0][value]': profile_id,
                    'criteria[1][field]': 'is_active',
                    'criteria[1][searchtype]': 'equals', 
                    'criteria[1][value]': 1,
                    'criteria[2][field]': 'is_deleted',
                    'criteria[2][searchtype]': 'equals',
                    'criteria[2][value]': 0,
                    'forcedisplay[0]': 2,  # ID
                    'forcedisplay[1]': 5,  # Username
                    'range': '0-999'
                }
            )
            
            if response and response.ok:
                data = response.json()
                users = data.get('data', [])
                print(f"  Encontrados {len(users)} usuários no perfil {profile_id}")
                
                for user in users:
                    if isinstance(user, dict) and "5" in user:
                        username = str(user["5"])
                        user_id = str(user["2"]) if "2" in user else "N/A"
                        
                        # Buscar dados completos do usuário
                        user_response = service._make_authenticated_request(
                            'GET',
                            f"{service.glpi_url}/User/{user_id}"
                        )
                        
                        if user_response and user_response.ok:
                            user_data = user_response.json()
                            
                            # Construir nome de exibição
                            display_name = ""
                            if "realname" in user_data and "firstname" in user_data:
                                display_name = f"{user_data['firstname']} {user_data['realname']}"
                            elif "realname" in user_data:
                                display_name = user_data["realname"]
                            elif "name" in user_data:
                                display_name = user_data["name"]
                            else:
                                display_name = username
                            
                            # Determinar nível baseado no perfil
                            level_map = {13: "N2", 14: "N3", 15: "N4"}
                            level = level_map.get(profile_id, "N1")
                            
                            # Contar tickets (usando método existente)
                            tech_field_id = service._discover_tech_field_id()
                            if tech_field_id:
                                try:
                                    total_tickets = service._count_tickets_by_technician_optimized(int(user_id), tech_field_id)
                                    if total_tickets is None:
                                        total_tickets = 0
                                except Exception as e:
                                    print(f"    Erro ao contar tickets para {display_name}: {e}")
                                    total_tickets = 0
                            else:
                                total_tickets = 0
                            
                            all_technicians.append({
                                "id": user_id,
                                "nome": display_name,
                                "name": display_name,
                                "total": total_tickets,
                                "level": level,
                                "profile_id": profile_id
                            })
                            
                            print(f"    - {display_name} ({level}): {total_tickets} tickets")
                        else:
                            print(f"    Erro ao buscar dados do usuário {user_id}")
                            
            else:
                print(f"  Erro ao buscar perfil {profile_id}: {response.status_code if response else 'Sem resposta'}")
                
        except Exception as e:
            print(f"  Erro ao processar perfil {profile_id}: {e}")
    
    # Ordenar por total de tickets
    all_technicians.sort(key=lambda x: x.get("total", 0), reverse=True)
    
    # Adicionar rank
    for idx, tech in enumerate(all_technicians):
        tech["rank"] = idx + 1
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Total de técnicos encontrados: {len(all_technicians)}")
    for tech in all_technicians:
        print(f"  {tech['rank']}. {tech['name']} ({tech['level']}): {tech['total']} tickets")
    
    return all_technicians

def suggest_fix():
    """Sugere a correção para o método"""
    print("\n=== SUGESTÃO DE CORREÇÃO ===")
    print("O método get_technician_ranking_knowledge_base deve ser atualizado para:")
    print("1. Buscar usuários nos perfis 13, 14, 15 em vez de apenas 6")
    print("2. Mapear os perfis para os níveis corretos:")
    print("   - Perfil 13 -> N2")
    print("   - Perfil 14 -> N3")
    print("   - Perfil 15 -> N4")
    print("3. Verificar se existe um perfil N1 (possivelmente ID 12 ou outro)")
    print("4. Manter a lógica de contagem de tickets e ordenação")

if __name__ == "__main__":
    print(f"Iniciando correção dos perfis de técnicos - {datetime.datetime.now()}")
    
    # Testar método atual
    current_ranking = test_current_method()
    
    # Testar perfis corretos
    correct_ranking = test_correct_profiles()
    
    # Sugerir correção
    suggest_fix()
    
    print(f"\nScript finalizado - {datetime.datetime.now()}")