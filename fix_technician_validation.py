#!/usr/bin/env python3
"""
Script para corrigir a validação de técnicos no dashboard GLPI.
Este script implementa uma solução que usa dados diretamente do Profile_User
sem depender da validação individual de usuários que podem ter sido deletados.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
from config.settings import Config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Função principal para testar e corrigir a validação de técnicos."""
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    print("=== Teste de Correção da Validação de Técnicos ===")
    
    # 1. Autenticar no GLPI
    print("\n1. Autenticando no GLPI...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # 2. Buscar técnicos usando Profile_User diretamente
    print("\n2. Buscando técnicos via Profile_User...")
    try:
        # Buscar Profile_User com filtro para técnicos (profiles_id = 6)
        profile_user_url = f"{glpi_service.glpi_url}/search/Profile_User"
        profile_user_params = {
            'criteria[0][field]': '5',  # profiles_id
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': '6',  # ID do perfil de técnico
            'criteria[1][field]': '3',  # entities_id
            'criteria[1][searchtype]': 'equals', 
            'criteria[1][value]': '1',  # ID da entidade específica
            'criteria[1][link]': 'AND',
            'forcedisplay[0]': '2',  # ID
            'forcedisplay[1]': '4',  # users_id
            'forcedisplay[2]': '5',  # profiles_id
            'forcedisplay[3]': '3',  # entities_id
            'range': '0-200'
        }
        
        response = glpi_service._make_authenticated_request(
            "GET", profile_user_url, params=profile_user_params
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if 'data' in data:
                technicians_data = data['data']
                print(f"✅ Encontrados {len(technicians_data)} registros de técnicos em Profile_User")
                
                # Extrair IDs e nomes de usuário
                technician_ids = []
                for tech in technicians_data:
                    user_id = tech.get('4')  # users_id está no campo 4
                    if user_id:
                        technician_ids.append(user_id)
                
                print(f"📊 IDs de técnicos extraídos: {technician_ids[:10]}..." + 
                      (f" (e mais {len(technician_ids)-10})" if len(technician_ids) > 10 else ""))
                
                # 3. Implementar nova lógica de busca de nomes
                print("\n3. Implementando nova lógica de busca de nomes...")
                technician_names = {}
                
                # Buscar nomes em lote usando search/User
                if technician_ids:
                    # Criar critérios de busca para múltiplos IDs
                    user_search_url = f"{glpi_service.glpi_url}/search/User"
                    
                    # Buscar usuários ativos apenas
                    user_params = {
                        'criteria[0][field]': '8',  # is_active
                        'criteria[0][searchtype]': 'equals',
                        'criteria[0][value]': '1',
                        'forcedisplay[0]': '2',  # ID
                        'forcedisplay[1]': '1',  # name (username)
                        'forcedisplay[2]': '9',  # realname
                        'forcedisplay[3]': '34', # firstname
                        'range': '0-500'
                    }
                    
                    user_response = glpi_service._make_authenticated_request(
                        "GET", user_search_url, params=user_params
                    )
                    
                    if user_response and user_response.status_code == 200:
                        user_data = user_response.json()
                        if 'data' in user_data:
                            users = user_data['data']
                            print(f"✅ Encontrados {len(users)} usuários ativos no sistema")
                            
                            # Mapear usuários por ID
                            user_map = {}
                            for user in users:
                                user_id = user.get('2')  # ID
                                username = user.get('1', '')  # name
                                realname = user.get('9', '')  # realname
                                firstname = user.get('34', '')  # firstname
                                
                                # Construir nome completo
                                full_name = f"{firstname} {realname}".strip() if firstname or realname else username
                                if not full_name:
                                    full_name = f"Usuário {user_id}"
                                
                                user_map[user_id] = {
                                    'username': username,
                                    'full_name': full_name,
                                    'realname': realname,
                                    'firstname': firstname
                                }
                            
                            # Mapear técnicos encontrados
                            valid_technicians = []
                            missing_technicians = []
                            
                            for tech_id in technician_ids:
                                if tech_id in user_map:
                                    valid_technicians.append({
                                        'id': tech_id,
                                        'username': user_map[tech_id]['username'],
                                        'full_name': user_map[tech_id]['full_name']
                                    })
                                else:
                                    missing_technicians.append(tech_id)
                            
                            print(f"\n📈 Resultados da validação:")
                            print(f"   ✅ Técnicos válidos (ativos): {len(valid_technicians)}")
                            print(f"   ❌ Técnicos inválidos (inativos/deletados): {len(missing_technicians)}")
                            
                            if valid_technicians:
                                print(f"\n👥 Primeiros 5 técnicos válidos:")
                                for tech in valid_technicians[:5]:
                                    print(f"   - ID: {tech['id']}, Username: {tech['username']}, Nome: {tech['full_name']}")
                            
                            if missing_technicians:
                                print(f"\n⚠️  IDs de técnicos não encontrados (primeiros 10): {missing_technicians[:10]}")
                            
                            # 4. Testar nova implementação
                            print("\n4. Testando nova implementação...")
                            
                            # Simular a função corrigida
                            def get_valid_technicians_corrected():
                                """Versão corrigida que retorna apenas técnicos válidos."""
                                return [(tech['id'], tech['full_name']) for tech in valid_technicians]
                            
                            corrected_technicians = get_valid_technicians_corrected()
                            print(f"✅ Nova implementação retorna {len(corrected_technicians)} técnicos válidos")
                            
                            # 5. Comparar com implementação atual
                            print("\n5. Comparando com implementação atual...")
                            try:
                                current_technicians = glpi_service._get_all_technician_ids_and_names(entity_id=1)
                                print(f"📊 Implementação atual retorna {len(current_technicians)} técnicos")
                                print(f"📈 Diferença: {len(corrected_technicians) - len(current_technicians)} técnicos")
                            except Exception as e:
                                print(f"❌ Erro na implementação atual: {e}")
                            
                        else:
                            print("❌ Nenhum usuário encontrado na busca")
                    else:
                        print(f"❌ Erro na busca de usuários: {user_response.status_code if user_response else 'None'}")
                
            else:
                print("❌ Nenhum técnico encontrado em Profile_User")
        else:
            print(f"❌ Erro na busca Profile_User: {response.status_code if response else 'None'}")
            
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Fim do Teste ===")

if __name__ == "__main__":
    main()