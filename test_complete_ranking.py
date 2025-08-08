#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste completo para validar o ranking de técnicos
Testa todos os aspectos do sistema de ranking para garantir consistência
"""

import requests
import json
from datetime import datetime
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_api_endpoint():
    """Testa o endpoint da API do ranking"""
    print("\n=== TESTE 1: Endpoint da API ===")
    try:
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint funcionando - Status: {response.status_code}")
            print(f"✅ Total de técnicos retornados: {len(data['data'])}")
            
            # Verificar estrutura dos dados
            if data['data']:
                first_tech = data['data'][0]
                required_fields = ['id', 'name', 'score', 'tickets_abertos', 'tickets_fechados']
                missing_fields = [field for field in required_fields if field not in first_tech]
                
                if not missing_fields:
                    print("✅ Estrutura dos dados está correta")
                else:
                    print(f"❌ Campos faltando: {missing_fields}")
                    
                return data['data']
            else:
                print("❌ Nenhum técnico retornado")
                return []
        else:
            print(f"❌ Erro no endpoint - Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return []

def test_glpi_service_direct():
    """Testa o serviço GLPI diretamente"""
    print("\n=== TESTE 2: Serviço GLPI Direto ===")
    try:
        service = GLPIService()
        ranking = service.get_technician_ranking()
        
        if ranking:
            print(f"✅ Serviço GLPI funcionando - {len(ranking)} técnicos encontrados")
            return ranking
        else:
            print("❌ Serviço GLPI não retornou dados")
            return []
    except Exception as e:
        print(f"❌ Erro no serviço GLPI: {e}")
        return []

def test_data_consistency(api_data, service_data):
    """Testa a consistência entre API e serviço direto"""
    print("\n=== TESTE 3: Consistência dos Dados ===")
    
    if not api_data or not service_data:
        print("❌ Não é possível testar consistência - dados faltando")
        return False
    
    # Comparar quantidade
    if len(api_data) == len(service_data):
        print(f"✅ Quantidade consistente: {len(api_data)} técnicos")
    else:
        print(f"❌ Quantidade inconsistente - API: {len(api_data)}, Serviço: {len(service_data)}")
    
    # Comparar IDs dos técnicos
    api_ids = set(tech['id'] for tech in api_data)
    service_ids = set(tech['id'] for tech in service_data)
    
    if api_ids == service_ids:
        print("✅ IDs dos técnicos são consistentes")
    else:
        missing_in_api = service_ids - api_ids
        missing_in_service = api_ids - service_ids
        if missing_in_api:
            print(f"❌ IDs faltando na API: {missing_in_api}")
        if missing_in_service:
            print(f"❌ IDs faltando no serviço: {missing_in_service}")
    
    return api_ids == service_ids

def test_ranking_logic(data):
    """Testa a lógica do ranking"""
    print("\n=== TESTE 4: Lógica do Ranking ===")
    
    if not data:
        print("❌ Não há dados para testar")
        return False
    
    # Verificar se está ordenado por score (decrescente)
    scores = [tech['score'] for tech in data]
    is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
    
    if is_sorted:
        print("✅ Ranking está ordenado corretamente por score")
    else:
        print("❌ Ranking não está ordenado corretamente")
    
    # Verificar se todos têm score >= 0
    negative_scores = [tech for tech in data if tech['score'] < 0]
    if not negative_scores:
        print("✅ Todos os scores são válidos (>= 0)")
    else:
        print(f"❌ {len(negative_scores)} técnicos com score negativo")
    
    # Verificar se técnicos com tickets têm score > 0
    zero_score_with_tickets = [
        tech for tech in data 
        if tech['score'] == 0 and (tech['tickets_abertos'] > 0 or tech['tickets_fechados'] > 0)
    ]
    
    if not zero_score_with_tickets:
        print("✅ Lógica de score está correta")
    else:
        print(f"❌ {len(zero_score_with_tickets)} técnicos com tickets mas score zero")
    
    return is_sorted and not negative_scores and not zero_score_with_tickets

def test_data_completeness(data):
    """Testa a completude dos dados"""
    print("\n=== TESTE 5: Completude dos Dados ===")
    
    if not data:
        print("❌ Não há dados para testar")
        return False
    
    # Verificar campos obrigatórios
    required_fields = ['id', 'name', 'score', 'tickets_abertos', 'tickets_fechados']
    incomplete_records = []
    
    for tech in data:
        missing_fields = [field for field in required_fields if field not in tech or tech[field] is None]
        if missing_fields:
            incomplete_records.append((tech.get('id', 'N/A'), missing_fields))
    
    if not incomplete_records:
        print("✅ Todos os registros estão completos")
    else:
        print(f"❌ {len(incomplete_records)} registros incompletos:")
        for tech_id, missing in incomplete_records[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - Técnico {tech_id}: faltando {missing}")
    
    # Verificar nomes vazios
    empty_names = [tech for tech in data if not tech.get('name') or tech['name'].strip() == '']
    if not empty_names:
        print("✅ Todos os técnicos têm nomes válidos")
    else:
        print(f"❌ {len(empty_names)} técnicos com nomes vazios")
    
    return not incomplete_records and not empty_names

def generate_summary_report(data):
    """Gera um relatório resumo"""
    print("\n=== RELATÓRIO RESUMO ===")
    
    if not data:
        print("❌ Não há dados para gerar relatório")
        return
    
    print(f"📊 Total de técnicos no ranking: {len(data)}")
    
    # Top 10 técnicos
    print("\n🏆 Top 10 Técnicos:")
    for i, tech in enumerate(data[:10], 1):
        print(f"   {i:2d}. {tech['name']} (ID: {tech['id']}) - Score: {tech['score']:.1f}")
    
    # Estatísticas
    scores = [tech['score'] for tech in data]
    total_tickets_abertos = sum(tech['tickets_abertos'] for tech in data)
    total_tickets_fechados = sum(tech['tickets_fechados'] for tech in data)
    
    print(f"\n📈 Estatísticas:")
    print(f"   - Score máximo: {max(scores):.1f}")
    print(f"   - Score mínimo: {min(scores):.1f}")
    print(f"   - Score médio: {sum(scores)/len(scores):.1f}")
    print(f"   - Total tickets abertos: {total_tickets_abertos}")
    print(f"   - Total tickets fechados: {total_tickets_fechados}")
    
    # Técnicos ativos (com tickets)
    active_techs = [tech for tech in data if tech['tickets_abertos'] > 0 or tech['tickets_fechados'] > 0]
    print(f"   - Técnicos ativos: {len(active_techs)} de {len(data)}")

def main():
    """Função principal"""
    print("🔍 INICIANDO TESTES COMPLETOS DO RANKING DE TÉCNICOS")
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar testes
    api_data = test_api_endpoint()
    service_data = test_glpi_service_direct()
    
    consistency_ok = test_data_consistency(api_data, service_data)
    ranking_logic_ok = test_ranking_logic(api_data)
    data_complete_ok = test_data_completeness(api_data)
    
    # Gerar relatório
    generate_summary_report(api_data)
    
    # Resultado final
    print("\n=== RESULTADO FINAL ===")
    all_tests_passed = consistency_ok and ranking_logic_ok and data_complete_ok
    
    if all_tests_passed:
        print("✅ TODOS OS TESTES PASSARAM - Sistema funcionando corretamente!")
    else:
        print("❌ ALGUNS TESTES FALHARAM - Verificar problemas acima")
    
    print(f"\n📋 Resumo:")
    print(f"   - Consistência: {'✅' if consistency_ok else '❌'}")
    print(f"   - Lógica do ranking: {'✅' if ranking_logic_ok else '❌'}")
    print(f"   - Completude dos dados: {'✅' if data_complete_ok else '❌'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)