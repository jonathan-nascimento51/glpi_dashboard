#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para identificar o formato correto dos critérios de data na API GLPI
"""

import requests
import json
from datetime import datetime, timedelta
from backend.services.glpi_service import GLPIService

def test_criteria_formats():
    """Testa diferentes formatos de critérios de data"""
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    print("=== Teste de Formatos de Critérios de Data ===")
    print(f"Autenticando...")
    
    # Autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticado com sucesso")
    
    # Descobrir IDs dos campos
    glpi.discover_field_ids()
    print(f"Campo DATE_CREATION: {glpi.field_ids.get('DATE_CREATION', 'Não encontrado')}")
    
    # Forçar campo 15 para data de criação
    glpi.field_ids["DATE_CREATION"] = "15"
    print(f"Campo DATE_CREATION forçado para: {glpi.field_ids['DATE_CREATION']}")
    
    # Datas de teste
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
    end_date = datetime.now().strftime('%Y/%m/%d')
    
    print(f"\nTestando filtros de data:")
    print(f"Data início: {start_date}")
    print(f"Data fim: {end_date}")
    
    # Teste 1: Formato original (sem indexação correta)
    print("\n--- Teste 1: Formato Original ---")
    params1 = {
        'is_deleted': 0,
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'morethan',
        'criteria[0][value]': f'{start_date} 00:00:00',
        'criteria[0][link]': 'AND',
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'lessthan',
        'criteria[0][value]': f'{end_date} 23:59:59'
    }
    
    result1 = test_search_request(glpi, params1, "Formato Original")
    
    # Teste 2: Formato com indexação correta <mcreference link="https://forum.glpi-project.org/viewtopic.php?id=287842" index="1">1</mcreference>
    print("\n--- Teste 2: Formato com Indexação Correta ---")
    params2 = {
        'is_deleted': 0,
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'morethan',
        'criteria[0][value]': f'{start_date} 00:00:00',
        'criteria[0][link]': 'AND',
        'criteria[1][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[1][searchtype]': 'lessthan',
        'criteria[1][value]': f'{end_date} 23:59:59',
        'criteria[1][link]': 'AND'
    }
    
    result2 = test_search_request(glpi, params2, "Formato com Indexação Correta")
    
    # Teste 3: Formato ISO com indexação correta <mcreference link="https://glpi-developer-documentation.readthedocs.io/en/master/devapi/search.html" index="2">2</mcreference>
    print("\n--- Teste 3: Formato ISO com Indexação Correta ---")
    start_date_iso = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date_iso = datetime.now().strftime('%Y-%m-%d')
    
    params3 = {
        'is_deleted': 0,
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'morethan',
        'criteria[0][value]': f'{start_date_iso} 00:00:00',
        'criteria[0][link]': 'AND',
        'criteria[1][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[1][searchtype]': 'lessthan',
        'criteria[1][value]': f'{end_date_iso} 23:59:59',
        'criteria[1][link]': 'AND'
    }
    
    result3 = test_search_request(glpi, params3, "Formato ISO com Indexação Correta")
    
    # Teste 4: Sem horário
    print("\n--- Teste 4: Sem Horário ---")
    params4 = {
        'is_deleted': 0,
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'morethan',
        'criteria[0][value]': start_date_iso,
        'criteria[0][link]': 'AND',
        'criteria[1][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[1][searchtype]': 'lessthan',
        'criteria[1][value]': end_date_iso,
        'criteria[1][link]': 'AND'
    }
    
    result4 = test_search_request(glpi, params4, "Sem Horário")
    
    # Teste 5: Apenas um filtro (morethan)
    print("\n--- Teste 5: Apenas Filtro 'morethan' ---")
    params5 = {
        'is_deleted': 0,
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'morethan',
        'criteria[0][value]': start_date_iso
    }
    
    result5 = test_search_request(glpi, params5, "Apenas 'morethan'")
    
    # Teste 6: Apenas um filtro (lessthan)
    print("\n--- Teste 6: Apenas Filtro 'lessthan' ---")
    params6 = {
        'is_deleted': 0,
        'criteria[0][field]': glpi.field_ids["DATE_CREATION"],
        'criteria[0][searchtype]': 'lessthan',
        'criteria[0][value]': end_date_iso
    }
    
    result6 = test_search_request(glpi, params6, "Apenas 'lessthan'")
    
    # Obter contagem base sem filtros
    base_count = test_search_request(glpi, {'is_deleted': 0}, "Sem filtros")
    
    # Resumo dos resultados
    print("\n=== RESUMO DOS RESULTADOS ===")
    results = [
        ("Sem filtros", base_count),
        ("Formato Original", result1),
        ("Indexação Correta", result2),
        ("ISO com Indexação", result3),
        ("Sem Horário", result4),
        ("Apenas 'morethan'", result5),
        ("Apenas 'lessthan'", result6)
    ]
    
    for name, count in results:
        print(f"{name}: {count} tickets")
    
    # Identificar qual formato funciona melhor
    base_count = results[0][1]
    print(f"\n=== ANÁLISE ===")
    print(f"Total de tickets sem filtros: {base_count}")
    
    for name, count in results[1:]:
        if count != base_count and count > 0:
            print(f"✅ {name} parece estar funcionando (filtrou {base_count - count} tickets)")
        elif count == base_count:
            print(f"❌ {name} não está filtrando (mesmo número de tickets)")
        else:
            print(f"⚠️  {name} retornou {count} tickets")

def test_search_request(glpi, params, test_name):
    """Executa uma requisição de busca e retorna o número de tickets"""
    try:
        print(f"Testando {test_name}...")
        print(f"Parâmetros: {json.dumps(params, indent=2)}")
        
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=params
        )
        
        if response and "Content-Range" in response.headers:
            total = int(response.headers["Content-Range"].split("/")[-1])
            print(f"Resultado: {total} tickets encontrados")
            return total
        elif response and response.status_code == 200:
            print(f"Resultado: 0 tickets encontrados (sem Content-Range)")
            return 0
        else:
            status_code = response.status_code if response else "None"
            response_text = response.text if response else "Sem resposta"
            print(f"Erro HTTP {status_code}: {response_text}")
            return -1
            
    except Exception as e:
        print(f"Erro na requisição: {str(e)}")
        return -1

if __name__ == "__main__":
    test_criteria_formats()