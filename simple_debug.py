#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para debugar Profile_User
"""

import sys
import os
import logging

# Desabilitar logs verbosos
logging.getLogger().setLevel(logging.ERROR)

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def simple_debug():
    print("=== SIMPLE DEBUG ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticado")
    
    # Buscar perfis
    print("\n2. Buscando perfis...")
    try:
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/Profile",
            params={"range": "0-20"}
        )
        
        if response and response.ok:
            profiles = response.json()
            print(f"✅ {len(profiles)} perfis encontrados:")
            for p in profiles:
                print(f"   ID: {p.get('id')} - {p.get('name')}")
        else:
            print("❌ Erro ao buscar perfis")
            return
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # Testar Profile_User com perfil 6 (técnico)
    print("\n3. Testando Profile_User com perfil 6...")
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
        
        if response and response.ok:
            data = response.json()
            profile_users = data.get('data', [])
            print(f"✅ Profile_User com perfil 6: {len(profile_users)} registros")
            if profile_users:
                for i, pu in enumerate(profile_users[:3]):
                    print(f"   {i+1}: {pu}")
            else:
                print("   Nenhum registro encontrado")
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar Profile_User sem filtro
    print("\n4. Testando Profile_User sem filtro...")
    try:
        params = {
            "range": "0-5",
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
        
        if response and response.ok:
            data = response.json()
            profile_users = data.get('data', [])
            print(f"✅ Profile_User sem filtro: {len(profile_users)} registros")
            if profile_users:
                for i, pu in enumerate(profile_users[:3]):
                    print(f"   {i+1}: {pu}")
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n=== DEBUG CONCLUÍDO ===")

if __name__ == "__main__":
    simple_debug()