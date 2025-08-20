#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script minimal para debugar Profile_User
"""

import sys
import os
import logging

# Desabilitar TODOS os logs
logging.disable(logging.CRITICAL)

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Redirecionar stderr para evitar logs
class NullWriter:
    def write(self, txt): pass
    def flush(self): pass

original_stderr = sys.stderr
sys.stderr = NullWriter()

try:
    from services.glpi_service import GLPIService
    
    def minimal_debug():
        # Restaurar stderr temporariamente para nosso output
        sys.stderr = original_stderr
        
        print("=== MINIMAL DEBUG ===")
        
        # Redirecionar stderr novamente
        sys.stderr = NullWriter()
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Restaurar stderr para output
        sys.stderr = original_stderr
        
        # Autenticar
        print("\n1. Autenticando...")
        
        # Redirecionar stderr
        sys.stderr = NullWriter()
        auth_result = glpi_service.authenticate()
        sys.stderr = original_stderr
        
        if not auth_result:
            print("❌ Falha na autenticação")
            return
        print("✅ Autenticado")
        
        # Buscar perfis
        print("\n2. Buscando perfis...")
        
        sys.stderr = NullWriter()
        try:
            response = glpi_service._make_authenticated_request(
                "GET",
                f"{glpi_service.glpi_url}/Profile",
                params={"range": "0-20"}
            )
            sys.stderr = original_stderr
            
            if response and response.ok:
                profiles = response.json()
                print(f"✅ {len(profiles)} perfis encontrados:")
                for p in profiles:
                    print(f"   ID: {p.get('id')} - {p.get('name')}")
            else:
                print("❌ Erro ao buscar perfis")
                return
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
            return
        
        # Testar Profile_User com perfil 6 (técnico)
        print("\n3. Testando Profile_User com perfil 6...")
        
        sys.stderr = NullWriter()
        try:
            params = {
                "range": "0-5",
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
                print(f"✅ Profile_User com perfil 6: {len(profile_users)} registros")
                if profile_users:
                    for i, pu in enumerate(profile_users[:3]):
                        print(f"   {i+1}: {pu}")
                else:
                    print("   ❌ PROBLEMA: Nenhum registro encontrado com perfil 6")
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                
        except Exception as e:
            sys.stderr = original_stderr
            print(f"❌ Erro: {e}")
        
        print("\n=== DEBUG CONCLUÍDO ===")
    
    if __name__ == "__main__":
        minimal_debug()
        
finally:
    # Restaurar stderr
    sys.stderr = original_stderr