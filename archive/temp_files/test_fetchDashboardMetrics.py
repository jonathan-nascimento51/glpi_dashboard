#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar especificamente a função fetchDashboardMetrics
"""

import requests
import json
from datetime import datetime

def test_api_response_format():
    """Testa o formato da resposta da API"""
    print("🔍 Testando formato da resposta da API...")
    
    try:
        response = requests.get('http://localhost:5000/api/metrics', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("📋 Estrutura da resposta:")
            print(f"- success: {data.get('success')}")
            print(f"- data: {type(data.get('data'))}")
            print(f"- tempo_execucao: {data.get('tempo_execucao')}")
            
            if 'data' in data:
                api_data = data['data']
                print(f"\n📊 Campos em data: {list(api_data.keys())}")
                
                # Verificar se tem a estrutura esperada pelo frontend
                expected_fields = ['niveis', 'tendencias']
                missing_fields = []
                
                for field in expected_fields:
                    if field in api_data:
                        print(f"✅ {field}: presente")
                        if field == 'niveis':
                            niveis = api_data[field]
                            print(f"   Níveis: {list(niveis.keys())}")
                            for nivel, dados in niveis.items():
                                if isinstance(dados, dict):
                                    print(f"   {nivel}: {list(dados.keys())}")
                        elif field == 'tendencias':
                            tendencias = api_data[field]
                            print(f"   Tendências: {list(tendencias.keys())}")
                    else:
                        missing_fields.append(field)
                        print(f"❌ {field}: ausente")
                
                if missing_fields:
                    print(f"\n⚠️ Campos ausentes: {missing_fields}")
                else:
                    print("\n✅ Todos os campos esperados estão presentes")
                
                return data
            else:
                print("❌ Campo 'data' não encontrado na resposta")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
    
    return None

def simulate_isApiResponse_check(api_response):
    """Simula a verificação isApiResponse do frontend"""
    print("\n🔍 Simulando verificação isApiResponse...")
    
    if not api_response:
        print("❌ Resposta da API é None")
        return False
    
    # Verificar se tem success = true
    if api_response.get('success') == True:
        print("✅ success = true")
        return True
    else:
        print(f"❌ success = {api_response.get('success')}")
        return False

def simulate_transformLegacyData(api_data):
    """Simula a função transformLegacyData do frontend"""
    print("\n🔄 Simulando transformLegacyData...")
    
    if not api_data:
        print("❌ api_data é None")
        return None
    
    # Estrutura padrão para níveis
    default_level = {
        'novos': 0,
        'pendentes': 0,
        'progresso': 0,
        'resolvidos': 0,
        'total': 0
    }
    
    print(f"📋 Dados recebidos: {list(api_data.keys())}")
    
    # Verificar se tem niveis
    if 'niveis' in api_data:
        print("✅ Campo 'niveis' encontrado")
        niveis_data = api_data['niveis']
        
        # Extrair dados dos níveis
        n1 = niveis_data.get('n1', default_level.copy())
        n2 = niveis_data.get('n2', default_level.copy())
        n3 = niveis_data.get('n3', default_level.copy())
        n4 = niveis_data.get('n4', default_level.copy())
        
        print(f"📊 N1: {n1}")
        print(f"📊 N2: {n2}")
        print(f"📊 N3: {n3}")
        print(f"📊 N4: {n4}")
        
        # Calcular geral
        geral = {
            'novos': n1.get('novos', 0) + n2.get('novos', 0) + n3.get('novos', 0) + n4.get('novos', 0),
            'pendentes': n1.get('pendentes', 0) + n2.get('pendentes', 0) + n3.get('pendentes', 0) + n4.get('pendentes', 0),
            'progresso': n1.get('progresso', 0) + n2.get('progresso', 0) + n3.get('progresso', 0) + n4.get('progresso', 0),
            'resolvidos': n1.get('resolvidos', 0) + n2.get('resolvidos', 0) + n3.get('resolvidos', 0) + n4.get('resolvidos', 0)
        }
        geral['total'] = geral['novos'] + geral['pendentes'] + geral['progresso'] + geral['resolvidos']
        
        print(f"📊 Geral calculado: {geral}")
        
        # Estrutura final
        result = {
            'niveis': {
                'n1': n1,
                'n2': n2,
                'n3': n3,
                'n4': n4,
                'geral': geral
            },
            'tendencias': api_data.get('tendencias', {})
        }
        
        print("✅ Transformação concluída com sucesso")
        return result
    else:
        print("❌ Campo 'niveis' não encontrado")
        print(f"Campos disponíveis: {list(api_data.keys())}")
        
        # Fallback
        result = {
            'niveis': {
                'n1': default_level.copy(),
                'n2': default_level.copy(),
                'n3': default_level.copy(),
                'n4': default_level.copy(),
                'geral': default_level.copy()
            },
            'tendencias': api_data.get('tendencias', {})
        }
        
        print("⚠️ Usando dados de fallback")
        return result

def simulate_fetchDashboardMetrics_flow():
    """Simula todo o fluxo da função fetchDashboardMetrics"""
    print("\n🔄 Simulando fluxo completo do fetchDashboardMetrics...")
    
    # Passo 1: Fazer requisição à API
    api_response = test_api_response_format()
    
    if not api_response:
        print("❌ Falha na requisição à API")
        return None
    
    # Passo 2: Verificar se é uma resposta de sucesso
    is_success = simulate_isApiResponse_check(api_response)
    
    if not is_success:
        print("❌ Resposta não é de sucesso")
        return None
    
    # Passo 3: Extrair dados
    api_data = api_response.get('data')
    
    if not api_data:
        print("❌ Campo 'data' não encontrado")
        return None
    
    # Passo 4: Transformar dados
    transformed_data = simulate_transformLegacyData(api_data)
    
    if transformed_data:
        print("\n🎉 FLUXO COMPLETO FUNCIONANDO!")
        print("✅ API responde corretamente")
        print("✅ Verificação de sucesso passa")
        print("✅ Dados são extraídos")
        print("✅ Transformação funciona")
        
        print("\n📊 Dados finais para o frontend:")
        print(json.dumps(transformed_data, indent=2, ensure_ascii=False))
        
        return transformed_data
    else:
        print("\n❌ FALHA NA TRANSFORMAÇÃO")
        return None

def main():
    """Função principal"""
    print("=== TESTE DA FUNÇÃO fetchDashboardMetrics ===")
    print(f"Timestamp: {datetime.now()}\n")
    
    result = simulate_fetchDashboardMetrics_flow()
    
    if result:
        print("\n✅ TESTE PASSOU - fetchDashboardMetrics deveria funcionar")
    else:
        print("\n❌ TESTE FALHOU - há problemas no fluxo")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    main()