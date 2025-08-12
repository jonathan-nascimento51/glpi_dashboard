#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a funcionalidade de filtro por data de modificação

Este script testa:
1. A nova função get_dashboard_metrics_with_modification_date_filter
2. O endpoint /api/metrics com filter_type=modification
3. O novo endpoint /api/filter-types
4. Comparação entre filtros de criação e modificação
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from services.glpi_service import GLPIService
    from config.settings import Config
except ImportError:
    # Fallback para estrutura de diretórios alternativa
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'services'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'config'))
    from glpi_service import GLPIService
    from settings import Config

def test_modification_filter_service():
    """Testa a nova função de filtro por data de modificação no GLPIService"""
    print("\n=== Testando GLPIService - Filtro por Data de Modificação ===")
    
    try:
        # Inicializar serviço
        config = Config()
        glpi_service = GLPIService(config)
        
        # Definir período de teste (últimos 30 dias)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"Período de teste: {start_date} até {end_date}")
        
        # Testar filtro por data de criação (método existente)
        print("\n--- Filtro por Data de Criação ---")
        creation_metrics = glpi_service.get_dashboard_metrics_with_date_filter(
            start_date=start_date,
            end_date=end_date
        )
        
        if creation_metrics:
            totals_creation = creation_metrics.get('totals', {})
            print(f"Totais (Criação): {totals_creation}")
            print(f"Total geral (Criação): {sum(totals_creation.values())}")
        else:
            print("Erro ao obter métricas por data de criação")
        
        # Testar filtro por data de modificação (novo método)
        print("\n--- Filtro por Data de Modificação ---")
        modification_metrics = glpi_service.get_dashboard_metrics_with_modification_date_filter(
            start_date=start_date,
            end_date=end_date
        )
        
        if modification_metrics:
            totals_modification = modification_metrics.get('totals', {})
            filter_info = modification_metrics.get('filter_info', {})
            print(f"Totais (Modificação): {totals_modification}")
            print(f"Total geral (Modificação): {sum(totals_modification.values())}")
            print(f"Informações do filtro: {filter_info}")
            
            # Verificar se há diferenças significativas
            if creation_metrics:
                creation_total = sum(totals_creation.values())
                modification_total = sum(totals_modification.values())
                
                print(f"\n--- Comparação ---")
                print(f"Total Criação: {creation_total}")
                print(f"Total Modificação: {modification_total}")
                print(f"Diferença: {modification_total - creation_total}")
                
                if modification_total > creation_total:
                    print("✅ Filtro por modificação captura mais tickets (esperado)")
                elif modification_total == creation_total:
                    print("⚠️  Totais iguais - pode indicar que todos os tickets foram criados e modificados no mesmo período")
                else:
                    print("❌ Filtro por modificação captura menos tickets (inesperado)")
        else:
            print("Erro ao obter métricas por data de modificação")
            
    except Exception as e:
        print(f"Erro no teste do serviço: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """Testa os endpoints da API"""
    print("\n=== Testando Endpoints da API ===")
    
    base_url = "http://localhost:5000/api"
    
    # Testar endpoint /filter-types
    print("\n--- Testando /api/filter-types ---")
    try:
        response = requests.get(f"{base_url}/filter-types")
        if response.status_code == 200:
            filter_types = response.json()
            print("✅ Endpoint /filter-types funcionando")
            print(f"Tipos disponíveis: {list(filter_types.get('data', {}).keys())}")
            
            for filter_type, info in filter_types.get('data', {}).items():
                print(f"  - {filter_type}: {info.get('name')} ({'padrão' if info.get('default') else 'opcional'})")
        else:
            print(f"❌ Erro no endpoint /filter-types: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar /filter-types: {e}")
    
    # Definir período de teste
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Testar endpoint /metrics com filter_type=creation
    print("\n--- Testando /api/metrics com filter_type=creation ---")
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'filter_type': 'creation'
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        
        if response.status_code == 200:
            creation_data = response.json()
            if creation_data.get('success'):
                totals = creation_data.get('data', {}).get('totals', {})
                print(f"✅ Filtro por criação funcionando")
                print(f"Totais: {totals}")
                print(f"Total geral: {sum(totals.values())}")
            else:
                print(f"❌ Resposta indica erro: {creation_data.get('message')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar filtro por criação: {e}")
    
    # Testar endpoint /metrics com filter_type=modification
    print("\n--- Testando /api/metrics com filter_type=modification ---")
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'filter_type': 'modification'
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        
        if response.status_code == 200:
            modification_data = response.json()
            if modification_data.get('success'):
                totals = modification_data.get('data', {}).get('totals', {})
                filter_info = modification_data.get('data', {}).get('filter_info', {})
                print(f"✅ Filtro por modificação funcionando")
                print(f"Totais: {totals}")
                print(f"Total geral: {sum(totals.values())}")
                print(f"Tipo de filtro: {filter_info.get('type')}")
                print(f"Descrição: {filter_info.get('description')}")
            else:
                print(f"❌ Resposta indica erro: {modification_data.get('message')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar filtro por modificação: {e}")

def test_comparison():
    """Compara os resultados dos diferentes tipos de filtro"""
    print("\n=== Comparação Detalhada dos Filtros ===")
    
    base_url = "http://localhost:5000/api"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    results = {}
    
    # Testar ambos os filtros
    for filter_type in ['creation', 'modification']:
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'filter_type': filter_type
            }
            response = requests.get(f"{base_url}/metrics", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results[filter_type] = data.get('data', {})
                    print(f"✅ {filter_type.capitalize()}: {sum(results[filter_type].get('totals', {}).values())} tickets")
                else:
                    print(f"❌ Erro em {filter_type}: {data.get('message')}")
            else:
                print(f"❌ Erro HTTP em {filter_type}: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao testar {filter_type}: {e}")
    
    # Comparar resultados
    if len(results) == 2:
        print("\n--- Análise Comparativa ---")
        creation_totals = results['creation'].get('totals', {})
        modification_totals = results['modification'].get('totals', {})
        
        print(f"Período analisado: {start_date} até {end_date}")
        print("\nPor Status:")
        for status in ['novos', 'pendentes', 'progresso', 'resolvidos']:
            creation_count = creation_totals.get(status, 0)
            modification_count = modification_totals.get(status, 0)
            diff = modification_count - creation_count
            print(f"  {status.capitalize()}:")
            print(f"    Criação: {creation_count}")
            print(f"    Modificação: {modification_count}")
            print(f"    Diferença: {diff:+d}")
        
        creation_total = sum(creation_totals.values())
        modification_total = sum(modification_totals.values())
        
        print(f"\nTotal Geral:")
        print(f"  Criação: {creation_total}")
        print(f"  Modificação: {modification_total}")
        print(f"  Diferença: {modification_total - creation_total:+d}")
        
        if modification_total > creation_total:
            percentage = ((modification_total - creation_total) / creation_total * 100) if creation_total > 0 else 0
            print(f"  Aumento: {percentage:.1f}%")
            print("\n🎯 Resultado esperado: Filtro por modificação captura mais tickets")
        elif modification_total == creation_total:
            print("\n⚠️  Totais iguais - todos os tickets foram criados no período")
        else:
            print("\n❌ Resultado inesperado: Filtro por modificação captura menos tickets")

def main():
    """Função principal"""
    print("🧪 Teste da Funcionalidade de Filtro por Data de Modificação")
    print("=" * 60)
    
    # Testar serviço diretamente
    test_modification_filter_service()
    
    # Testar endpoints da API
    test_api_endpoints()
    
    # Comparação detalhada
    test_comparison()
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("\nPróximos passos:")
    print("1. Verificar se os resultados fazem sentido")
    print("2. Testar no frontend com a nova opção de filtro")
    print("3. Documentar a nova funcionalidade")

if __name__ == "__main__":
    main()