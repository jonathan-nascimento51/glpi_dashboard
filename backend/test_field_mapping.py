#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o mapeamento de campos de técnico no GLPI
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_field_mapping():
    """Testa o mapeamento de campos de técnico"""
    
    # Configurações do GLPI
    glpi_url = os.getenv('GLPI_URL')
    user_token = os.getenv('GLPI_USER_TOKEN')
    app_token = os.getenv('GLPI_APP_TOKEN')
    
    if not all([glpi_url, user_token, app_token]):
        print(" Tokens não configurados")
        return False
    
    print(f" Conectando ao GLPI: {glpi_url}")
    
    # Headers para autenticação
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {user_token}',
        'App-Token': app_token
    }
    
    try:
        # 1. Iniciar sessão
        print("\n1 Iniciando sessão...")
        init_response = requests.get(
            f"{glpi_url}/initSession",
            headers=headers,
            timeout=30
        )
        
        if init_response.status_code != 200:
            print(f" Falha na autenticação: {init_response.status_code}")
            print(f"Resposta: {init_response.text}")
            return False
        
        session_data = init_response.json()
        session_token = session_data.get('session_token')
        
        if not session_token:
            print(" Token de sessão não encontrado")
            return False
        
        print(f" Sessão iniciada: {session_token[:20]}...")
        
        # Atualizar headers com session token
        headers['Session-Token'] = session_token
        
        # 2. Buscar opções de pesquisa para tickets
        print("\n2 Buscando opções de pesquisa...")
        search_response = requests.get(
            f"{glpi_url}/listSearchOptions/Ticket",
            headers=headers,
            timeout=30
        )
        
        if search_response.status_code != 200:
            print(f" Falha ao buscar opções: {search_response.status_code}")
            return False
        
        search_options = search_response.json()
        print(f" Encontradas {len(search_options)} opções de pesquisa")
        
        # 3. Analisar campos de técnico
        print("\n3 Analisando campos de técnico...")
        
        # Mapeamento conhecido
        tech_field_mapping = {
            "5": "Técnico",
            "95": "Técnico encarregado"
        }
        
        print("\n Campos conhecidos:")
        for field_id, expected_name in tech_field_mapping.items():
            if field_id in search_options:
                field_data = search_options[field_id]
                if isinstance(field_data, dict) and "name" in field_data:
                    actual_name = field_data["name"]
                    status = "" if actual_name == expected_name else ""
                    print(f"  {status} Campo {field_id}: '{actual_name}' (esperado: '{expected_name}')")
                else:
                    print(f"   Campo {field_id}: dados inválidos - {field_data}")
            else:
                print(f"   Campo {field_id}: não encontrado")
        
        # 4. Buscar todos os campos relacionados a técnico
        print("\n4 Buscando todos os campos relacionados a técnico...")
        tech_related_fields = []
        
        tech_keywords = ["técnico", "technician", "atribuído", "assigned", "encarregado"]
        
        for field_id, field_data in search_options.items():
            if isinstance(field_data, dict) and "name" in field_data:
                field_name = field_data["name"].lower()
                for keyword in tech_keywords:
                    if keyword in field_name:
                        tech_related_fields.append({
                            "id": field_id,
                            "name": field_data["name"],
                            "table": field_data.get("table", "N/A"),
                            "field": field_data.get("field", "N/A")
                        })
                        break
        
        print(f"\n Encontrados {len(tech_related_fields)} campos relacionados a técnico:")
        for field in tech_related_fields:
            print(f"   ID {field['id']}: '{field['name']}' (tabela: {field['table']}, campo: {field['field']})")
        
        # 5. Testar busca com campo específico
        print("\n5 Testando busca com campo de técnico...")
        
        # Usar o primeiro campo encontrado ou o campo "5" como fallback
        test_field_id = tech_related_fields[0]["id"] if tech_related_fields else "5"
        
        print(f"Testando com campo ID: {test_field_id}")
        
        # Buscar tickets com técnico atribuído
        search_criteria = {
            "criteria": [
                {
                    "field": test_field_id,
                    "searchtype": "contains",
                    "value": ""
                }
            ],
            "range": "0-4"  # Apenas 5 resultados para teste
        }
        
        tickets_response = requests.get(
            f"{glpi_url}/search/Ticket",
            headers=headers,
            params={'criteria': json.dumps(search_criteria)},
            timeout=30
        )
        
        if tickets_response.status_code == 200:
            tickets_data = tickets_response.json()
            total_count = tickets_data.get('totalcount', 0)
            print(f" Busca bem-sucedida: {total_count} tickets encontrados")
            
            if 'data' in tickets_data and tickets_data['data']:
                print("\n Exemplo de tickets:")
                for i, ticket in enumerate(tickets_data['data'][:3]):
                    ticket_id = ticket.get('2', 'N/A')  # Campo 2 é geralmente o ID
                    tech_field = ticket.get(test_field_id, 'N/A')
                    print(f"   Ticket {ticket_id}: Técnico = {tech_field}")
        else:
            print(f" Falha na busca de tickets: {tickets_response.status_code}")
            print(f"Resposta: {tickets_response.text[:200]}...")
        
        # 6. Encerrar sessão
        print("\n6 Encerrando sessão...")
        kill_response = requests.get(
            f"{glpi_url}/killSession",
            headers=headers,
            timeout=30
        )
        
        if kill_response.status_code == 200:
            print(" Sessão encerrada com sucesso")
        else:
            print(f" Aviso: Falha ao encerrar sessão: {kill_response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f" Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f" Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print(" Teste de Mapeamento de Campos de Técnico - GLPI")
    print("=" * 50)
    
    success = test_field_mapping()
    
    print("\n" + "=" * 50)
    if success:
        print(" Teste concluído com sucesso!")
    else:
        print(" Teste falhou!")
    
    sys.exit(0 if success else 1)
