#!/usr/bin/env python3
"""
Script para investigar grupos disponíveis no GLPI e identificar
a configuração correta para os níveis N1-N4
"""

import os
import sys
import json
from dotenv import load_dotenv
from services.glpi_service import GLPIService
import requests

def main():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        # Garantir autenticação
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
            
        print("✅ Autenticado com sucesso no GLPI")
        print(f"URL: {service.glpi_url}")
        print(f"Session Token: {service.session_token[:20]}...")
        
        # Buscar grupos
        print("\n🔍 BUSCANDO GRUPOS DISPONÍVEIS...")
        
        headers = {
            'Session-Token': service.session_token,
            'App-Token': service.app_token,
            'Content-Type': 'application/json'
        }
        
        # Tentar diferentes abordagens para listar grupos
        endpoints = [
            '/Group',
            '/search/Group',
            '/Group?range=0-50'
        ]
        
        for endpoint in endpoints:
            print(f"\n📡 Testando endpoint: {endpoint}")
            try:
                response = requests.get(
                    f"{service.glpi_url}{endpoint}",
                    headers=headers,
                    timeout=30
                )
                
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code in [200, 206]:
                    data = response.json()
                    print(f"Tipo de resposta: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"Total de grupos encontrados: {len(data)}")
                        
                        # Mostrar primeiros 10 grupos
                        for i, group in enumerate(data[:10]):
                            if isinstance(group, dict):
                                group_id = group.get('id', group.get('2', 'N/A'))
                                group_name = group.get('name', group.get('1', 'N/A'))
                                print(f"  {i+1}. ID: {group_id}, Nome: {group_name}")
                            else:
                                print(f"  {i+1}. {group}")
                                
                        if len(data) > 10:
                            print(f"  ... e mais {len(data) - 10} grupos")
                            
                    elif isinstance(data, dict):
                        if 'data' in data:
                            groups = data['data']
                            print(f"Total de grupos encontrados: {len(groups)}")
                            
                            # Mostrar primeiros 10 grupos
                            for i, group in enumerate(groups[:10]):
                                if isinstance(group, dict):
                                    group_id = group.get('id', group.get('2', 'N/A'))
                                    group_name = group.get('name', group.get('1', 'N/A'))
                                    print(f"  {i+1}. ID: {group_id}, Nome: {group_name}")
                                else:
                                    print(f"  {i+1}. {group}")
                                    
                            if len(groups) > 10:
                                print(f"  ... e mais {len(groups) - 10} grupos")
                        else:
                            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                    
                    # Se encontrou dados, parar aqui
                    if (isinstance(data, list) and data) or (isinstance(data, dict) and data.get('data')):
                        break
                        
                else:
                    print(f"Erro: {response.status_code}")
                    print(f"Resposta: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"Erro ao acessar {endpoint}: {e}")
        
        # Verificar configuração atual
        print("\n⚙️ CONFIGURAÇÃO ATUAL DOS NÍVEIS:")
        print(f"service_levels = {service.service_levels}")
        print(f"status_map = {service.status_map}")
        
        # Verificar se o grupo 17 existe e tem tickets
        print("\n🎯 VERIFICANDO GRUPO 17 (ATUAL):")
        try:
            response = requests.get(
                f"{service.glpi_url}/Group/17",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                group_data = response.json()
                print(f"✅ Grupo 17 encontrado: {json.dumps(group_data, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ Grupo 17 não encontrado (status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Erro ao verificar grupo 17: {e}")
            
        # Buscar grupos que podem ser N1, N2, N3, N4
        print("\n🔍 BUSCANDO GRUPOS CANDIDATOS PARA N1-N4:")
        
        # Buscar por nomes que contenham N1, N2, etc.
        search_terms = ['N1', 'N2', 'N3', 'N4', 'Nível', 'Level', 'Suporte']
        
        for term in search_terms:
            try:
                # Usar search com critério de nome
                search_params = {
                    'criteria[0][field]': '1',  # Campo nome
                    'criteria[0][searchtype]': 'contains',
                    'criteria[0][value]': term
                }
                
                response = requests.get(
                    f"{service.glpi_url}/search/Group",
                    headers=headers,
                    params=search_params,
                    timeout=30
                )
                
                if response.status_code in [200, 206]:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data and data['data']:
                        print(f"\n📋 Grupos contendo '{term}':")
                        for group in data['data']:
                            if isinstance(group, dict):
                                group_id = group.get('2', 'N/A')  # ID
                                group_name = group.get('1', 'N/A')  # Nome
                                print(f"  - ID: {group_id}, Nome: {group_name}")
                                
            except Exception as e:
                print(f"Erro ao buscar grupos com '{term}': {e}")
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()