#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para verificar se os filtros de data estão sendo aplicados corretamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
from datetime import datetime, timedelta
import logging
import requests

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_filters():
    """Debug dos filtros de data"""
    print("=== DEBUG DOS FILTROS DE DATA ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Testar autenticação
    if not glpi_service._ensure_authenticated():
        print("❌ Falha na autenticação")
        return False
    
    print("✅ Autenticação bem-sucedida")
    
    # Testar requisição direta para ver todos os tickets
    print("\n--- Teste direto da API ---")
    
    # Parâmetros básicos sem filtros de data
    search_params_basic = {
        "is_deleted": 0,
        "range": "0-0",
        "criteria[0][field]": "8",  # Grupo técnico
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "89",  # N1
        "criteria[1][link]": "AND",
        "criteria[1][field]": "12",  # Status
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "1",  # Novo
    }
    
    try:
        response_basic = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Ticket",
            params=search_params_basic
        )
        
        if response_basic and "Content-Range" in response_basic.headers:
            total_basic = int(response_basic.headers["Content-Range"].split("/")[-1])
            print(f"Total básico (N1/Novo): {total_basic}")
        else:
            print(f"Resposta básica: Status {response_basic.status_code if response_basic else 'None'}")
            total_basic = 0
    except Exception as e:
        print(f"Erro na consulta básica: {e}")
        total_basic = 0
    
    # Testar com filtro de data usando campo 15 e formato YYYY/MM/DD
    print("\n--- Teste com filtro de data (campo 15, formato YYYY/MM/DD) ---")
    
    search_params_filtered = {
        "is_deleted": 0,
        "range": "0-0",
        "criteria[0][field]": "8",  # Grupo técnico
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "89",  # N1
        "criteria[1][link]": "AND",
        "criteria[1][field]": "12",  # Status
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "1",  # Novo
        "criteria[2][link]": "AND",
        "criteria[2][field]": "15",  # Data de criação (campo correto)
        "criteria[2][searchtype]": "morethan",
        "criteria[2][value]": "2020/01/01",  # Formato YYYY/MM/DD
    }
    
    try:
        response_filtered = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Ticket",
            params=search_params_filtered
        )
        
        if response_filtered and "Content-Range" in response_filtered.headers:
            total_filtered = int(response_filtered.headers["Content-Range"].split("/")[-1])
            print(f"Total com filtro desde 2020 (campo 15): {total_filtered}")
        else:
            print(f"Resposta filtrada: Status {response_filtered.status_code if response_filtered else 'None'}")
            total_filtered = 0
    except Exception as e:
        print(f"Erro na consulta filtrada: {e}")
        total_filtered = 0
    
    # Testar com filtro futuro (deve retornar 0)
    print("\n--- Teste com filtro futuro ---")
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y/%m/%d')
    search_params_future = {
        "is_deleted": 0,
        "range": "0-0",
        "criteria[0][field]": "8",  # Grupo técnico
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "89",  # N1
        "criteria[1][link]": "AND",
        "criteria[1][field]": "12",  # Status
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "1",  # Novo
        "criteria[2][link]": "AND",
        "criteria[2][field]": "15",  # Data de criação
        "criteria[2][searchtype]": "morethan",
        "criteria[2][value]": tomorrow,  # Amanhã
    }
    
    try:
        response_future = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Ticket",
            params=search_params_future
        )
        
        if response_future and "Content-Range" in response_future.headers:
            total_future = int(response_future.headers["Content-Range"].split("/")[-1])
            print(f"Total com filtro futuro ({tomorrow}): {total_future}")
        else:
            print(f"Resposta futura: Status {response_future.status_code if response_future else 'None'}")
            total_future = 0
    except Exception as e:
        print(f"Erro na consulta futura: {e}")
        total_future = 0
    
    # Testar todos os tickets sem filtros de grupo/status
    print("\n--- Teste de todos os tickets ---")
    
    search_params_all = {
        "is_deleted": 0,
        "range": "0-0",
    }
    
    try:
        response_all = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Ticket",
            params=search_params_all
        )
        
        if response_all and "Content-Range" in response_all.headers:
            total_all = int(response_all.headers["Content-Range"].split("/")[-1])
            print(f"Total de todos os tickets: {total_all}")
        else:
            print(f"Resposta todos: Status {response_all.status_code if response_all else 'None'}")
            total_all = 0
    except Exception as e:
        print(f"Erro na consulta de todos: {e}")
        total_all = 0
    
    print("\n--- Análise ---")
    print(f"Todos os tickets: {total_all}")
    print(f"N1/Novo básico: {total_basic}")
    print(f"N1/Novo desde 2020: {total_filtered}")
    print(f"N1/Novo futuro: {total_future}")
    
    if total_all > 0:
        print("✅ Sistema tem tickets")
    else:
        print("❌ Sistema não tem tickets ou erro na consulta")
    
    if total_basic == total_filtered and total_basic > 0:
        print("⚠️  Filtro de data pode não estar funcionando (valores iguais)")
    elif total_filtered < total_basic:
        print("✅ Filtro de data parece estar funcionando (filtrado < básico)")
    elif total_filtered > total_basic:
        print("❓ Resultado inesperado (filtrado > básico)")
    
    if total_future == 0:
        print("✅ Filtro futuro funcionando (retornou 0)")
    else:
        print(f"⚠️  Filtro futuro pode não estar funcionando (retornou {total_future})")
    
    return True

if __name__ == "__main__":
    try:
        debug_filters()
    except Exception as e:
        logger.error(f"Erro durante o debug: {e}")
        sys.exit(1)