#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para conexáo GLPI
"""

import os
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# Adicionar o diretório pai ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configurações do GLPI (do .env)
GLPI_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
GLPI_USER_TOKEN = "WPjwz02rLe4jLt3YzJrpJJTzQmIwIXkKFvDsJpEU"
GLPI_APP_TOKEN = "c1U4Emxp0n7ClNDz7Kd2jSkcVB5gG4XFTLlnTm85"

async def test_glpi_connection():
    """Testa a conexáo básica com o GLPI"""
    print("=== TESTE DE CONEXáO GLPI ===")
    print(f"URL: {GLPI_URL}")
    print(f"User Token: {GLPI_USER_TOKEN[:10]}...")
    print(f"App Token: {GLPI_APP_TOKEN[:10]}...")
    print()
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': GLPI_APP_TOKEN,
        'Authorization': f'user_token {GLPI_USER_TOKEN}'
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            # Teste 1: Iniciar sessáo
            print("1. Testando autenticaçáo...")
            async with session.post(f"{GLPI_URL}/initSession", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    session_token = data.get('session_token')
                    print(f"   Session Token: {session_token[:10] if session_token else 'None'}...")
                    
                    if session_token:
                        # Atualizar headers com session token
                        headers['Session-Token'] = session_token
                        
                        # Teste 2: Buscar informações básicas
                        print("\n2. Testando busca de tickets...")
                        search_url = f"{GLPI_URL}/search/Ticket"
                        params = {
                            'criteria[0][field]': '12',  # Status
                            'criteria[0][searchtype]': 'equals',
                            'criteria[0][value]': '1',   # Novo
                            'range': '0-4'  # Limitar a 5 resultados
                        }
                        
                        async with session.get(search_url, headers=headers, params=params) as search_response:
                            print(f"   Status: {search_response.status}")
                            print(f"   Headers: {dict(search_response.headers)}")
                            
                            if search_response.status == 200:
                                search_data = await search_response.json()
                                print(f"   Dados recebidos: {len(str(search_data))} caracteres")
                                print(f"   Tipo de dados: {type(search_data)}")
                                if isinstance(search_data, dict):
                                    print(f"   Chaves: {list(search_data.keys())}")
                            else:
                                error_text = await search_response.text()
                                print(f"   Erro: {error_text[:200]}...")
                        
                        # Teste 3: Encerrar sessáo
                        print("\n3. Encerrando sessáo...")
                        async with session.delete(f"{GLPI_URL}/killSession", headers=headers) as kill_response:
                            print(f"   Status: {kill_response.status}")
                    
                else:
                    error_text = await response.text()
                    print(f"   Erro na autenticaçáo: {error_text}")
                    
        except Exception as e:
            print(f"Erro durante o teste: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_glpi_connection())

