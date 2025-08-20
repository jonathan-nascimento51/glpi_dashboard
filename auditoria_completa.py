#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria Completa do Sistema de Ranking de Técnicos GLPI
Este script realiza uma auditoria completa de todas as funcionalidades implementadas.
"""

import sys
import os
import time
import requests
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(title):
    """Imprime um cabeçalho formatado"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Imprime uma seção formatada"""
    print(f"\n--- {title} ---")

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print_section("Testando Conexão com Banco de Dados")
    try:
        from services.glpi_service import GLPIService
        glpi_service = GLPIService()
        
        # Teste básico de autenticação
        result = glpi_service.authenticate()
        if result:
            print("✅ Conexão com banco de dados: OK")
            return True
        else:
            print("❌ Conexão com banco de dados: FALHOU")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def test_technician_search():
    """Testa a busca de técnicos"""
    print_section("Testando Busca de Técnicos")
    try:
        from services.glpi_service import GLPIService
        glpi_service = GLPIService()
        
        # Teste 1: Busca sem filtro
        print("Teste 1: Busca sem filtro de entidade")
        technician_ids, technician_names = glpi_service._get_all_technician_ids_and_names()
        print(f"   Técnicos encontrados: {len(technician_ids)}")
        if len(technician_ids) > 0:
            first_id = technician_ids[0]
            first_name = technician_names.get(first_id, f"Técnico {first_id}")
            print(f"   Primeiro técnico: {first_name}")
            print("✅ Busca sem filtro: OK")
        else:
            print("❌ Busca sem filtro: Nenhum técnico encontrado")
            return False
        
        # Teste 2: Busca com filtro de entidade (CAU)
        print("\nTeste 2: Busca com filtro de entidade (CAU - ID: 1)")
        technician_ids_cau, technician_names_cau = glpi_service._get_all_technician_ids_and_names(entity_id=1)
        print(f"   Técnicos CAU encontrados: {len(technician_ids_cau)}")
        if len(technician_ids_cau) > 0:
            first_id_cau = technician_ids_cau[0]
            first_name_cau = technician_names_cau.get(first_id_cau, f"Técnico {first_id_cau}")
            print(f"   Primeiro técnico CAU: {first_name_cau}")
            print("✅ Busca com filtro: OK")
        else:
            print("⚠️  Busca com filtro: Nenhum técnico encontrado (pode ser normal)")
        
        return True
    except Exception as e:
        print(f"❌ Erro na busca de técnicos: {e}")
        return False

def test_ranking_logic():
    """Testa a lógica de ranking"""
    print_section("Testando Lógica de Ranking")
    try:
        from services.glpi_service import GLPIService
        glpi_service = GLPIService()
        
        # Teste 1: Ranking sem filtro
        print("Teste 1: Ranking sem filtro de entidade")
        ranking = glpi_service.get_technician_ranking_with_filters()
        print(f"   Técnicos no ranking: {len(ranking)}")
        if len(ranking) > 0:
            top_tech = ranking[0]
            print(f"   Top 1: {top_tech.get('name', 'N/A')} - {top_tech.get('total', 0)} tickets")
            print("✅ Ranking sem filtro: OK")
        else:
            print("❌ Ranking sem filtro: Nenhum resultado")
            return False
        
        # Teste 2: Ranking com filtro de entidade
        print("\nTeste 2: Ranking com filtro de entidade (CAU - ID: 1)")
        ranking_cau = glpi_service.get_technician_ranking_with_filters(entity_id=1)
        print(f"   Técnicos CAU no ranking: {len(ranking_cau)}")
        if len(ranking_cau) > 0:
            top_tech_cau = ranking_cau[0]
            print(f"   Top 1 CAU: {top_tech_cau.get('name', 'N/A')} - {top_tech_cau.get('total', 0)} tickets")
            print("✅ Ranking com filtro: OK")
        else:
            print("⚠️  Ranking com filtro: Nenhum resultado (pode ser normal)")
        
        # Teste 3: Ranking com filtro de data
        print("\nTeste 3: Ranking com filtro de data (últimos 30 dias)")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        ranking_date = glpi_service.get_technician_ranking_with_filters(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        print(f"   Técnicos no ranking (30 dias): {len(ranking_date)}")
        if len(ranking_date) > 0:
            top_tech_date = ranking_date[0]
            print(f"   Top 1 (30 dias): {top_tech_date.get('name', 'N/A')} - {top_tech_date.get('total', 0)} tickets")
            print("✅ Ranking com filtro de data: OK")
        else:
            print("⚠️  Ranking com filtro de data: Nenhum resultado")
        
        return True
    except Exception as e:
        print(f"❌ Erro na lógica de ranking: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    print_section("Testando Endpoints da API")
    base_url = "http://localhost:5000/api"
    
    endpoints_tests = [
        {
            "name": "Busca de Técnicos",
            "url": f"{base_url}/technicians",
            "params": None
        },
        {
            "name": "Busca de Técnicos (CAU)",
            "url": f"{base_url}/technicians",
            "params": {"entity_id": 1}
        },
        {
            "name": "Ranking de Técnicos",
            "url": f"{base_url}/technicians/ranking",
            "params": None
        },
        {
            "name": "Ranking de Técnicos (CAU)",
            "url": f"{base_url}/technicians/ranking",
            "params": {"entity_id": 1}
        },
        {
            "name": "Ranking de Técnicos (30 dias)",
            "url": f"{base_url}/technicians/ranking",
            "params": {
                "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                "end_date": datetime.now().strftime('%Y-%m-%d')
            }
        }
    ]
    
    all_passed = True
    
    for test in endpoints_tests:
        print(f"\nTestando: {test['name']}")
        try:
            start_time = time.time()
            response = requests.get(test['url'], params=test['params'], timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            print(f"   Status: {response.status_code}")
            print(f"   Tempo de resposta: {response_time:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    if 'data' in data:
                        print(f"   Resultados: {len(data['data'])}")
                    elif 'technicians' in data:
                        print(f"   Resultados: {len(data['technicians'])}")
                    else:
                        print(f"   Estrutura: {list(data.keys())}")
                else:
                    print(f"   Resultados: {len(data) if isinstance(data, list) else 'N/A'}")
                print("✅ Endpoint: OK")
            else:
                print(f"❌ Endpoint falhou: {response.text[:100]}")
                all_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            all_passed = False
    
    return all_passed

def test_performance():
    """Testa a performance do sistema"""
    print_section("Testando Performance")
    base_url = "http://localhost:5000/api"
    
    # Teste de performance do ranking
    print("Teste de performance - Ranking completo")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/technicians/ranking", timeout=60)
        response_time = (time.time() - start_time) * 1000
        
        print(f"   Tempo de resposta: {response_time:.2f}ms")
        
        if response_time < 10000:  # Menos de 10 segundos
            print("✅ Performance: Excelente (< 10s)")
        elif response_time < 30000:  # Menos de 30 segundos
            print("⚠️  Performance: Aceitável (< 30s)")
        else:
            print("❌ Performance: Lenta (> 30s)")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def generate_audit_report():
    """Gera um relatório de auditoria completo"""
    print_header("AUDITORIA COMPLETA DO SISTEMA DE RANKING DE TÉCNICOS")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "database": test_database_connection(),
        "technician_search": test_technician_search(),
        "ranking_logic": test_ranking_logic(),
        "api_endpoints": test_api_endpoints(),
        "performance": test_performance()
    }
    
    print_header("RESUMO DA AUDITORIA")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nResultado Geral: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("\n🎉 AUDITORIA COMPLETA: TODOS OS TESTES PASSARAM!")
        print("   O sistema está funcionando corretamente.")
    elif passed_tests >= total_tests * 0.8:  # 80% ou mais
        print("\n⚠️  AUDITORIA COMPLETA: MAIORIA DOS TESTES PASSOU")
        print("   O sistema está funcionando, mas há algumas questões.")
    else:
        print("\n❌ AUDITORIA COMPLETA: MUITOS TESTES FALHARAM")
        print("   O sistema precisa de correções.")
    
    print("\n" + "="*60)
    print(" FIM DA AUDITORIA")
    print("="*60)

if __name__ == "__main__":
    generate_audit_report()