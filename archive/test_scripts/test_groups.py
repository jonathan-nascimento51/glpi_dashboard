#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
import json

def test_groups():
    """Testa grupos existentes no GLPI"""
    print("🔍 Testando grupos existentes no GLPI...")
    
    service = GLPIService()
    
    # Autenticar
    if not service._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticado com sucesso")
    
    # Buscar grupos
    try:
        response = service._make_authenticated_request('GET', f'{service.glpi_url}/Group')
        
        if not response:
            print("❌ Resposta vazia")
            return
            
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code in [200, 206]:
            data = response.json()
            
            if isinstance(data, list):
                print(f"📈 Total de grupos encontrados: {len(data)}")
                
                # Mostrar primeiros 10 grupos
                print("\n🏷️  Primeiros 10 grupos:")
                for i, group in enumerate(data[:10]):
                    group_id = group.get('id', 'N/A')
                    group_name = group.get('name', 'Sem nome')
                    print(f"  {i+1}. ID: {group_id} - Nome: {group_name}")
                
                # Verificar se os grupos configurados existem
                print("\n🎯 Verificando grupos configurados:")
                configured_groups = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}
                
                existing_ids = [int(group.get('id', 0)) for group in data if group.get('id')]
                
                for level, group_id in configured_groups.items():
                    exists = group_id in existing_ids
                    status = "✅ Existe" if exists else "❌ Não existe"
                    print(f"  {level} (ID {group_id}): {status}")
                    
                    if exists:
                        # Encontrar o nome do grupo
                        group_data = next((g for g in data if int(g.get('id', 0)) == group_id), None)
                        if group_data:
                            print(f"    Nome: {group_data.get('name', 'Sem nome')}")
                
            else:
                print(f"❌ Formato de resposta inesperado: {type(data)}")
                print(f"Dados: {data}")
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar grupos: {e}")

if __name__ == "__main__":
    test_groups()