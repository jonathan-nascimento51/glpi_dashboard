#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se os filtros de data estão funcionando corretamente
no ranking de técnicos do GLPI Dashboard.

Este script testa:
1. Ranking sem filtros
2. Ranking com filtros de data
3. Comparação dos resultados
4. Validação da estrutura de dados
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

API_BASE_URL = 'http://localhost:5000/api'

def test_technician_ranking_without_filters():
    """Testa o ranking de técnicos sem filtros"""
    print("\n=== TESTE 1: Ranking sem filtros ===")
    
    try:
        response = requests.get(f'{API_BASE_URL}/technicians/ranking')
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                ranking = data.get('data', [])
                print(f"✅ Sucesso: {len(ranking)} técnicos encontrados")
                
                # Mostrar primeiros 3 técnicos
                for i, tech in enumerate(ranking[:3], 1):
                    print(f"  {i}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets - Nível: {tech.get('level', 'N/A')}")
                
                return ranking
            else:
                print(f"❌ API retornou erro: {data.get('error', 'Erro desconhecido')}")
                return None
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_technician_ranking_with_date_filters():
    """Testa o ranking de técnicos com filtros de data"""
    print("\n=== TESTE 2: Ranking com filtros de data ===")
    
    # Definir período de teste (últimos 30 dias)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Período: {start_date} até {end_date}")
    
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'limit': 10
        }
        
        response = requests.get(f'{API_BASE_URL}/technicians/ranking', params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                ranking = data.get('data', [])
                print(f"✅ Sucesso: {len(ranking)} técnicos encontrados com filtros")
                
                # Mostrar primeiros 3 técnicos
                for i, tech in enumerate(ranking[:3], 1):
                    print(f"  {i}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets - Nível: {tech.get('level', 'N/A')}")
                
                return ranking
            else:
                print(f"❌ API retornou erro: {data.get('error', 'Erro desconhecido')}")
                return None
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_different_date_ranges():
    """Testa diferentes períodos de data"""
    print("\n=== TESTE 3: Diferentes períodos de data ===")
    
    periods = [
        ('Últimos 7 dias', 7),
        ('Últimos 15 dias', 15),
        ('Últimos 60 dias', 60)
    ]
    
    results = {}
    
    for period_name, days in periods:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"\n--- {period_name} ({start_date} até {end_date}) ---")
        
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'limit': 5
            }
            
            response = requests.get(f'{API_BASE_URL}/technicians/ranking', params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    ranking = data.get('data', [])
                    results[period_name] = ranking
                    
                    print(f"✅ {len(ranking)} técnicos encontrados")
                    
                    if ranking:
                        top_tech = ranking[0]
                        print(f"  Top: {top_tech.get('name', 'N/A')} - {top_tech.get('total', 0)} tickets")
                else:
                    print(f"❌ Erro: {data.get('error', 'Erro desconhecido')}")
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return results

def validate_data_structure(ranking_data):
    """Valida a estrutura dos dados retornados"""
    print("\n=== TESTE 4: Validação da estrutura de dados ===")
    
    if not ranking_data:
        print("❌ Nenhum dado para validar")
        return False
    
    required_fields = ['id', 'name', 'total', 'level', 'rank']
    valid = True
    
    for i, tech in enumerate(ranking_data[:3]):
        print(f"\n--- Técnico {i+1}: {tech.get('name', 'N/A')} ---")
        
        for field in required_fields:
            if field in tech:
                print(f"  ✅ {field}: {tech[field]}")
            else:
                print(f"  ❌ {field}: AUSENTE")
                valid = False
    
    if valid:
        print("\n✅ Estrutura de dados válida")
    else:
        print("\n❌ Estrutura de dados inválida")
    
    return valid

def main():
    """Função principal do teste"""
    print("🧪 TESTE DE FILTROS DE DATA NO RANKING DE TÉCNICOS")
    print("=" * 60)
    
    # Teste 1: Ranking sem filtros
    ranking_without_filters = test_technician_ranking_without_filters()
    
    # Teste 2: Ranking com filtros de data
    ranking_with_filters = test_technician_ranking_with_date_filters()
    
    # Teste 3: Diferentes períodos
    different_periods = test_different_date_ranges()
    
    # Teste 4: Validação da estrutura
    if ranking_with_filters:
        validate_data_structure(ranking_with_filters)
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    if ranking_without_filters:
        print(f"✅ Ranking sem filtros: {len(ranking_without_filters)} técnicos")
    else:
        print("❌ Ranking sem filtros: FALHOU")
    
    if ranking_with_filters:
        print(f"✅ Ranking com filtros: {len(ranking_with_filters)} técnicos")
    else:
        print("❌ Ranking com filtros: FALHOU")
    
    print(f"✅ Diferentes períodos testados: {len(different_periods)}")
    
    # Verificar se os filtros fazem diferença
    if ranking_without_filters and ranking_with_filters:
        if len(ranking_without_filters) != len(ranking_with_filters):
            print("✅ Filtros de data estão funcionando (resultados diferentes)")
        else:
            print("⚠️ Filtros podem não estar funcionando (resultados iguais)")
    
    print("\n🎯 Teste concluído!")

if __name__ == '__main__':
    main()