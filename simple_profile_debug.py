#!/usr/bin/env python3
"""
Script simples para debug da busca Profile_User
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import json

def main():
    """Função principal para debug simples."""
    
    print("=== Debug Simples Profile_User ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # 1. Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # 2. Buscar Profile_User sem filtros específicos
    print("\n2. Buscando Profile_User (sem filtros)...")
    try:
        profile_user_url = f"{glpi_service.glpi_url}/search/Profile_User"
        profile_user_params = {
            'range': '0-10',  # Apenas 10 primeiros
            'forcedisplay[0]': '2',  # ID
            'forcedisplay[1]': '4',  # users_id
            'forcedisplay[2]': '5',  # profiles_id
            'forcedisplay[3]': '3',  # entities_id
        }
        
        response = glpi_service._make_authenticated_request(
            "GET", profile_user_url, params=profile_user_params
        )
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida com status 200")
            print(f"📊 Chaves na resposta: {list(data.keys())}")
            
            if 'data' in data:
                records = data['data']
                print(f"📈 Total de registros encontrados: {len(records)}")
                
                if records:
                    print("\n📋 Primeiros 3 registros:")
                    for i, record in enumerate(records[:3]):
                        print(f"   Registro {i+1}: {record}")
                        
                    # Verificar se há técnicos (profiles_id = 6)
                    technicians = [r for r in records if r.get('5') == '6']
                    print(f"\n🔧 Técnicos encontrados nesta amostra: {len(technicians)}")
                    
                    if technicians:
                        print("   Técnicos:")
                        for tech in technicians:
                            print(f"     - ID: {tech.get('2')}, User ID: {tech.get('4')}, Entity: {tech.get('3')}")
                else:
                    print("❌ Nenhum registro encontrado")
            else:
                print("❌ Chave 'data' não encontrada na resposta")
                print(f"📄 Resposta completa: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erro na busca: {response.status_code if response else 'None'}")
            if response:
                print(f"📄 Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Buscar Profile_User com filtro de técnicos
    print("\n3. Buscando Profile_User (apenas técnicos)...")
    try:
        profile_user_params_tech = {
            'criteria[0][field]': '5',  # profiles_id
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': '6',  # ID do perfil de técnico
            'range': '0-50',
            'forcedisplay[0]': '2',  # ID
            'forcedisplay[1]': '4',  # users_id
            'forcedisplay[2]': '5',  # profiles_id
            'forcedisplay[3]': '3',  # entities_id
        }
        
        response = glpi_service._make_authenticated_request(
            "GET", profile_user_url, params=profile_user_params_tech
        )
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida com status 200")
            
            if 'data' in data:
                records = data['data']
                print(f"📈 Total de técnicos encontrados: {len(records)}")
                
                if records:
                    print("\n🔧 Primeiros 5 técnicos:")
                    for i, record in enumerate(records[:5]):
                        print(f"   Técnico {i+1}: ID={record.get('2')}, User_ID={record.get('4')}, Entity={record.get('3')}")
                else:
                    print("❌ Nenhum técnico encontrado")
            else:
                print("❌ Chave 'data' não encontrada na resposta")
                print(f"📄 Resposta completa: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erro na busca de técnicos: {response.status_code if response else 'None'}")
            if response:
                print(f"📄 Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro durante a busca de técnicos: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()