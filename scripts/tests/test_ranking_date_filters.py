#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para validar os filtros de data no ranking de técnicos

Este script testa:
1. Ranking sem filtros de data
2. Ranking com filtro de data inicial
3. Ranking com filtro de data final
4. Ranking com ambos os filtros de data
5. Comparação dos resultados para validar a aplicação dos filtros
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config

def test_ranking_date_filters():
    """Testa os filtros de data no ranking de técnicos"""
    print("=== TESTE DE FILTROS DE DATA NO RANKING DE TÉCNICOS ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Testar autenticação primeiro
    print("\n0. Testando autenticação...")
    if glpi_service._ensure_authenticated():
        print("   ✅ Autenticação bem-sucedida")
    else:
        print("   ❌ ERRO: Falha na autenticação")
        return False
    
    # Definir datas para teste
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 dias atrás
    end_date = today.strftime('%Y-%m-%d')  # Hoje
    
    print(f"Período de teste: {start_date} até {end_date}")
    
    try:
        # Teste 1: Ranking sem filtros de data
        print("\n1. Testando ranking SEM filtros de data...")
        ranking_sem_filtros = glpi_service.get_technician_ranking(limit=5)
        if ranking_sem_filtros is None:
            print("   ❌ ERRO: Método retornou None")
            ranking_sem_filtros = []
        else:
            print(f"   Resultado: {len(ranking_sem_filtros)} técnicos encontrados")
        if ranking_sem_filtros:
            print(f"   Primeiro técnico: {ranking_sem_filtros[0].get('name', 'N/A')} - Total: {ranking_sem_filtros[0].get('total', 0)}")
        
        # Teste 2: Ranking com filtro de data inicial
        print("\n2. Testando ranking COM filtro de data inicial...")
        ranking_com_start = glpi_service.get_technician_ranking(limit=5, start_date=start_date)
        if ranking_com_start is None:
            print("   ❌ ERRO: Método retornou None")
            ranking_com_start = []
        else:
            print(f"   Resultado: {len(ranking_com_start)} técnicos encontrados")
        if ranking_com_start:
            print(f"   Primeiro técnico: {ranking_com_start[0].get('name', 'N/A')} - Total: {ranking_com_start[0].get('total', 0)}")
        
        # Teste 3: Ranking com filtro de data final
        print("\n3. Testando ranking COM filtro de data final...")
        ranking_com_end = glpi_service.get_technician_ranking(limit=5, end_date=end_date)
        if ranking_com_end is None:
            print("   ❌ ERRO: Método retornou None")
            ranking_com_end = []
        else:
            print(f"   Resultado: {len(ranking_com_end)} técnicos encontrados")
        if ranking_com_end:
            print(f"   Primeiro técnico: {ranking_com_end[0].get('name', 'N/A')} - Total: {ranking_com_end[0].get('total', 0)}")
        
        # Teste 4: Ranking com ambos os filtros de data
        print("\n4. Testando ranking COM ambos os filtros de data...")
        ranking_com_ambos = glpi_service.get_technician_ranking(limit=5, start_date=start_date, end_date=end_date)
        if ranking_com_ambos is None:
            print("   ❌ ERRO: Método retornou None")
            ranking_com_ambos = []
        else:
            print(f"   Resultado: {len(ranking_com_ambos)} técnicos encontrados")
        if ranking_com_ambos:
            print(f"   Primeiro técnico: {ranking_com_ambos[0].get('name', 'N/A')} - Total: {ranking_com_ambos[0].get('total', 0)}")
        
        # Teste 5: Comparação dos resultados
        print("\n5. Análise dos resultados:")
        print(f"   - Sem filtros: {len(ranking_sem_filtros)} técnicos")
        print(f"   - Com data inicial: {len(ranking_com_start)} técnicos")
        print(f"   - Com data final: {len(ranking_com_end)} técnicos")
        print(f"   - Com ambas as datas: {len(ranking_com_ambos)} técnicos")
        
        # Verificar se os filtros estão sendo aplicados
        if ranking_sem_filtros and ranking_com_ambos:
            total_sem_filtros = sum(t.get('total', 0) for t in ranking_sem_filtros)
            total_com_filtros = sum(t.get('total', 0) for t in ranking_com_ambos)
            print(f"   - Total de tickets sem filtros: {total_sem_filtros}")
            print(f"   - Total de tickets com filtros: {total_com_filtros}")
            
            if total_com_filtros <= total_sem_filtros:
                print("   ✅ FILTROS FUNCIONANDO: Total com filtros <= Total sem filtros")
            else:
                print("   ❌ POSSÍVEL PROBLEMA: Total com filtros > Total sem filtros")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Testa o endpoint da API com filtros de data"""
    print("\n=== TESTE DO ENDPOINT DA API ===")
    
    base_url = "http://localhost:5000/api"
    
    # Definir datas para teste
    today = datetime.now()
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')  # 7 dias atrás
    end_date = today.strftime('%Y-%m-%d')  # Hoje
    
    try:
        # Teste 1: Endpoint sem filtros
        print("\n1. Testando endpoint SEM filtros...")
        response = requests.get(f"{base_url}/technicians/ranking")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso: {len(data.get('data', []))} técnicos retornados")
        else:
            print(f"   ❌ Erro: Status {response.status_code}")
        
        # Teste 2: Endpoint com filtros de data
        print("\n2. Testando endpoint COM filtros de data...")
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'limit': 5
        }
        response = requests.get(f"{base_url}/technicians/ranking", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso: {len(data.get('data', []))} técnicos retornados")
            print(f"   Filtros aplicados: {start_date} até {end_date}")
        else:
            print(f"   ❌ Erro: Status {response.status_code}")
            print(f"   Resposta: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API. Certifique-se de que o servidor está rodando.")
        return False
    except Exception as e:
        print(f"❌ ERRO durante o teste da API: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando testes de filtros de data no ranking de técnicos...")
    
    # Teste 1: Serviço GLPI diretamente
    success_service = test_ranking_date_filters()
    
    # Teste 2: Endpoint da API
    success_api = test_api_endpoint()
    
    # Resultado final
    print("\n=== RESULTADO FINAL ===")
    if success_service and success_api:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("Os filtros de data estão funcionando corretamente.")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os logs acima para identificar os problemas.")