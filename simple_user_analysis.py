#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
import requests
import json

def analyze_users():
    """Análise simples dos usuários no ranking"""
    
    print("🔍 ANÁLISE DOS USUÁRIOS NO RANKING DE TÉCNICOS")
    print("=" * 60)
    
    # Buscar dados do endpoint
    try:
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        if not response.ok:
            print(f"❌ Erro ao acessar endpoint: {response.status_code}")
            return
        
        data = response.json()
        technicians = data.get('data', [])
        
        print(f"📊 Total de técnicos no ranking: {len(technicians)}")
        print()
        
        # Inicializar serviço GLPI
        glpi = GLPIService()
        if not glpi._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        
        print("✅ Autenticado com GLPI")
        print()
        
        # Analisar usuários suspeitos (posições 17, 19-27)
        suspicious_positions = [16, 18] + list(range(19, 27))  # Convertendo para índice 0-based
        
        print("👥 USUÁRIOS SUSPEITOS (que não deveriam estar no ranking):")
        print("-" * 60)
        
        suspicious_users = []
        legitimate_users = []
        
        for i, tech in enumerate(technicians):
            user_data = {
                'position': i + 1,
                'id': tech['id'],
                'name': tech['name'],
                'score': tech['score'],
                'tickets_abertos': tech['tickets_abertos'],
                'tickets_fechados': tech['tickets_fechados']
            }
            
            # Buscar dados detalhados do usuário
            try:
                user_response = glpi._make_authenticated_request(
                    'GET',
                    f"{glpi.glpi_url}/User/{tech['id']}"
                )
                
                if user_response and user_response.ok:
                    user_details = user_response.json()
                    user_data.update({
                        'realname': user_details.get('realname', ''),
                        'firstname': user_details.get('firstname', ''),
                        'email': user_details.get('email', ''),
                        'is_active': user_details.get('is_active', 0),
                        'is_deleted': user_details.get('is_deleted', 0),
                        'locations_id': user_details.get('locations_id', 0),
                        'usertitles_id': user_details.get('usertitles_id', 0),
                        'usercategories_id': user_details.get('usercategories_id', 0)
                    })
                
            except Exception as e:
                print(f"⚠️  Erro ao buscar detalhes do usuário {tech['id']}: {e}")
            
            if i in suspicious_positions:
                suspicious_users.append(user_data)
                print(f"🚨 Posição {user_data['position']}: {user_data['name']} (ID: {user_data['id']})")
                print(f"   Nome real: {user_data.get('realname', 'N/A')}")
                print(f"   Primeiro nome: {user_data.get('firstname', 'N/A')}")
                print(f"   Email: {user_data.get('email', 'N/A')}")
                print(f"   Tickets abertos: {user_data['tickets_abertos']}")
                print(f"   Tickets fechados: {user_data['tickets_fechados']}")
                print(f"   Score: {user_data['score']}")
                print(f"   Location ID: {user_data.get('locations_id', 'N/A')}")
                print(f"   Title ID: {user_data.get('usertitles_id', 'N/A')}")
                print(f"   Category ID: {user_data.get('usercategories_id', 'N/A')}")
                print()
            else:
                legitimate_users.append(user_data)
        
        print("\n✅ USUÁRIOS LEGÍTIMOS (técnicos da DTIC):")
        print("-" * 60)
        
        for user in legitimate_users[:10]:  # Mostrar apenas os 10 primeiros
            print(f"✓ Posição {user['position']}: {user['name']} (ID: {user['id']})")
            print(f"   Nome real: {user.get('realname', 'N/A')}")
            print(f"   Primeiro nome: {user.get('firstname', 'N/A')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Tickets abertos: {user['tickets_abertos']}")
            print(f"   Tickets fechados: {user['tickets_fechados']}")
            print(f"   Score: {user['score']}")
            print(f"   Location ID: {user.get('locations_id', 'N/A')}")
            print(f"   Title ID: {user.get('usertitles_id', 'N/A')}")
            print(f"   Category ID: {user.get('usercategories_id', 'N/A')}")
            print()
        
        # Análise de padrões
        print("\n📊 ANÁLISE DE PADRÕES:")
        print("=" * 60)
        
        # Analisar locations_id
        suspicious_locations = [user.get('locations_id') for user in suspicious_users if user.get('locations_id')]
        legitimate_locations = [user.get('locations_id') for user in legitimate_users if user.get('locations_id')]
        
        print(f"🏢 Locations dos usuários suspeitos: {set(suspicious_locations)}")
        print(f"🏢 Locations dos usuários legítimos: {set(legitimate_locations)}")
        
        # Analisar usertitles_id
        suspicious_titles = [user.get('usertitles_id') for user in suspicious_users if user.get('usertitles_id')]
        legitimate_titles = [user.get('usertitles_id') for user in legitimate_users if user.get('usertitles_id')]
        
        print(f"👔 Títulos dos usuários suspeitos: {set(suspicious_titles)}")
        print(f"👔 Títulos dos usuários legítimos: {set(legitimate_titles)}")
        
        # Analisar usercategories_id
        suspicious_categories = [user.get('usercategories_id') for user in suspicious_users if user.get('usercategories_id')]
        legitimate_categories = [user.get('usercategories_id') for user in legitimate_users if user.get('usercategories_id')]
        
        print(f"📂 Categorias dos usuários suspeitos: {set(suspicious_categories)}")
        print(f"📂 Categorias dos usuários legítimos: {set(legitimate_categories)}")
        
        # Analisar tickets
        suspicious_total_tickets = [user['tickets_abertos'] + user['tickets_fechados'] for user in suspicious_users]
        legitimate_total_tickets = [user['tickets_abertos'] + user['tickets_fechados'] for user in legitimate_users]
        
        print(f"🎫 Total de tickets dos suspeitos: min={min(suspicious_total_tickets) if suspicious_total_tickets else 0}, max={max(suspicious_total_tickets) if suspicious_total_tickets else 0}, média={sum(suspicious_total_tickets)/len(suspicious_total_tickets) if suspicious_total_tickets else 0:.1f}")
        print(f"🎫 Total de tickets dos legítimos: min={min(legitimate_total_tickets) if legitimate_total_tickets else 0}, max={max(legitimate_total_tickets) if legitimate_total_tickets else 0}, média={sum(legitimate_total_tickets)/len(legitimate_total_tickets) if legitimate_total_tickets else 0:.1f}")
        
        print("\n💡 RECOMENDAÇÕES:")
        print("=" * 60)
        
        # Identificar diferenças claras
        location_diff = set(legitimate_locations) - set(suspicious_locations)
        title_diff = set(legitimate_titles) - set(suspicious_titles)
        category_diff = set(legitimate_categories) - set(suspicious_categories)
        
        if location_diff:
            print(f"🎯 Filtrar por locations_id: {location_diff}")
        if title_diff:
            print(f"🎯 Filtrar por usertitles_id: {title_diff}")
        if category_diff:
            print(f"🎯 Filtrar por usercategories_id: {category_diff}")
        
        # Analisar threshold de tickets
        if legitimate_total_tickets and suspicious_total_tickets:
            min_legitimate = min(legitimate_total_tickets)
            max_suspicious = max(suspicious_total_tickets)
            
            if min_legitimate > max_suspicious:
                print(f"🎯 Filtrar por número mínimo de tickets: >= {min_legitimate}")
        
        print("\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_users()