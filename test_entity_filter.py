#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para filtro de entidade
"""

import sys
import os
import logging

# Desabilitar logs verbosos
logging.disable(logging.CRITICAL)

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class NullWriter:
    def write(self, txt): pass
    def flush(self): pass

original_stderr = sys.stderr
sys.stderr = NullWriter()

try:
    from services.glpi_service import GLPIService
    
    def test_entity_filter():
        sys.stderr = original_stderr
        print("=== TESTE FILTRO DE ENTIDADE ===")
        
        sys.stderr = NullWriter()
        glpi_service = GLPIService()
        auth_result = glpi_service.authenticate()
        sys.stderr = original_stderr
        
        if not auth_result:
            print("❌ Falha na autenticação")
            return
        print("✅ Autenticado")
        
        # Teste 1: Profile_User SEM filtro de entidade
        print("\n1. Profile_User SEM filtro de entidade (perfil 6):")
        sys.stderr = NullWriter()
        try:
            params = {
                "range": "0-10",
                "criteria[0][field]": "4",  # profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "5",  # users_id
                "forcedisplay[2]": "4",  # profiles_id
                "forcedisplay[3]": "80", # entities_id
            }
            
            response = glpi_service._make_authenticated_request(
                "GET",
                f"{glpi_service.glpi_url}/search/Profile_User",
                params=params
            )
            sys.stderr = original_stderr
            
            if response and response.ok:
                data = response.json()
                profile_users = data.get('data', [])
                print(f"✅ Encontrados {len(profile_users)} registros")
                for i, pu in enumerate(profile_users[:3]):
                    print(f"   {i+1}: {pu}")
            else:
                print(f"❌ Erro: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
        
        # Teste 2: Profile_User COM filtro de entidade (ID 1)
        print("\n2. Profile_User COM filtro de entidade ID 1 (perfil 6):")
        sys.stderr = NullWriter()
        try:
            params = {
                "range": "0-10",
                "criteria[0][field]": "4",  # profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",
                "criteria[1][field]": "80",  # entities_id
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": "1",
                "criteria[1][link]": "AND",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "5",  # users_id
                "forcedisplay[2]": "4",  # profiles_id
                "forcedisplay[3]": "80", # entities_id
            }
            
            response = glpi_service._make_authenticated_request(
                "GET",
                f"{glpi_service.glpi_url}/search/Profile_User",
                params=params
            )
            sys.stderr = original_stderr
            
            if response and response.ok:
                data = response.json()
                profile_users = data.get('data', [])
                print(f"✅ Encontrados {len(profile_users)} registros")
                for i, pu in enumerate(profile_users[:3]):
                    print(f"   {i+1}: {pu}")
            else:
                print(f"❌ Erro: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
        
        # Teste 3: Listar entidades disponíveis
        print("\n3. Listando entidades disponíveis:")
        sys.stderr = NullWriter()
        try:
            response = glpi_service._make_authenticated_request(
                "GET",
                f"{glpi_service.glpi_url}/Entity",
                params={"range": "0-20"}
            )
            sys.stderr = original_stderr
            
            if response and response.ok:
                entities = response.json()
                print(f"✅ Encontradas {len(entities)} entidades:")
                for entity in entities:
                    print(f"   ID: {entity.get('id')} - {entity.get('name')}")
            else:
                print(f"❌ Erro ao buscar entidades: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
        
        # Teste 4: Testar função _get_all_technician_ids_and_names sem filtro
        print("\n4. Testando _get_all_technician_ids_and_names SEM filtro:")
        sys.stderr = NullWriter()
        try:
            tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names()
            sys.stderr = original_stderr
            print(f"✅ Encontrados {len(tech_ids)} técnicos")
            for i, tech_id in enumerate(tech_ids[:3]):
                print(f"   {i+1}: ID={tech_id}, Nome={tech_names.get(tech_id, 'N/A')}")
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
        
        # Teste 5: Testar função _get_all_technician_ids_and_names com filtro entidade 1
        print("\n5. Testando _get_all_technician_ids_and_names COM filtro entidade 1:")
        sys.stderr = NullWriter()
        try:
            tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names(entity_id=1)
            sys.stderr = original_stderr
            print(f"✅ Encontrados {len(tech_ids)} técnicos")
            for i, tech_id in enumerate(tech_ids[:3]):
                print(f"   {i+1}: ID={tech_id}, Nome={tech_names.get(tech_id, 'N/A')}")
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
        
        print("\n=== TESTE CONCLUÍDO ===")
    
    if __name__ == "__main__":
        test_entity_filter()
        
finally:
    sys.stderr = original_stderr