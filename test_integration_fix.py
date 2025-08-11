#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar e corrigir a integração entre frontend e backend
"""

import requests
import json
from datetime import datetime

def test_backend_api():
    """Testa a API do backend diretamente"""
    print("🔍 Testando API do backend...")
    
    try:
        response = requests.get('http://localhost:5000/api/metrics', timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta da API:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar estrutura
            if 'success' in data and data['success']:
                if 'data' in data:
                    backend_data = data['data']
                    print("\n📊 Estrutura dos dados do backend:")
                    print(f"- Campos disponíveis: {list(backend_data.keys())}")
                    
                    # Verificar se tem niveis
                    if 'niveis' in backend_data:
                        print(f"- Níveis disponíveis: {list(backend_data['niveis'].keys())}")
                    else:
                        print("⚠️ Campo 'niveis' não encontrado")
                    
                    # Verificar se tem tendencias
                    if 'tendencias' in backend_data:
                        print(f"- Tendências disponíveis: {list(backend_data['tendencias'].keys())}")
                    else:
                        print("⚠️ Campo 'tendencias' não encontrado")
                    
                    return backend_data
                else:
                    print("❌ Campo 'data' não encontrado na resposta")
            else:
                print("❌ API retornou success=false")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
    
    return None

def simulate_frontend_processing(backend_data):
    """Simula o processamento do frontend"""
    print("\n🔄 Simulando processamento do frontend...")
    
    if not backend_data:
        print("❌ Dados do backend são None")
        return None
    
    # Simular a função transformLegacyData
    default_level = {
        'novos': 0,
        'pendentes': 0,
        'progresso': 0,
        'resolvidos': 0,
        'total': 0
    }
    
    print(f"📋 Dados recebidos do backend: {list(backend_data.keys())}")
    
    # Verificar se tem niveis
    if 'niveis' in backend_data:
        print("✅ Campo 'niveis' encontrado")
        niveis_data = backend_data['niveis']
        
        n1 = niveis_data.get('n1', default_level)
        n2 = niveis_data.get('n2', default_level)
        n3 = niveis_data.get('n3', default_level)
        n4 = niveis_data.get('n4', default_level)
        
        # Calcular geral
        geral = {
            'novos': n1.get('novos', 0) + n2.get('novos', 0) + n3.get('novos', 0) + n4.get('novos', 0),
            'pendentes': n1.get('pendentes', 0) + n2.get('pendentes', 0) + n3.get('pendentes', 0) + n4.get('pendentes', 0),
            'progresso': n1.get('progresso', 0) + n2.get('progresso', 0) + n3.get('progresso', 0) + n4.get('progresso', 0),
            'resolvidos': n1.get('resolvidos', 0) + n2.get('resolvidos', 0) + n3.get('resolvidos', 0) + n4.get('resolvidos', 0)
        }
        geral['total'] = geral['novos'] + geral['pendentes'] + geral['progresso'] + geral['resolvidos']
        
        processed_data = {
            'niveis': {
                'n1': n1,
                'n2': n2,
                'n3': n3,
                'n4': n4,
                'geral': geral
            },
            'tendencias': backend_data.get('tendencias', {})
        }
        
        print("✅ Dados processados pelo frontend:")
        print(json.dumps(processed_data, indent=2, ensure_ascii=False))
        
        return processed_data
    else:
        print("❌ Campo 'niveis' não encontrado nos dados do backend")
        print(f"Campos disponíveis: {list(backend_data.keys())}")
        return None

def test_api_response_structure():
    """Testa a estrutura da resposta da API"""
    print("\n🔬 Analisando estrutura da resposta da API...")
    
    try:
        response = requests.get('http://localhost:5000/api/metrics', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("📋 Estrutura completa da resposta:")
            
            def analyze_structure(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, (dict, list)):
                            print(f"{current_path}: {type(value).__name__}")
                            if isinstance(value, dict) and len(value) < 10:  # Evitar output muito longo
                                analyze_structure(value, current_path)
                        else:
                            print(f"{current_path}: {type(value).__name__} = {value}")
                elif isinstance(obj, list) and len(obj) > 0:
                    print(f"{prefix}[0]: {type(obj[0]).__name__}")
                    if isinstance(obj[0], dict):
                        analyze_structure(obj[0], f"{prefix}[0]")
            
            analyze_structure(data)
            
            return data
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao analisar estrutura: {e}")
    
    return None

def main():
    """Função principal"""
    print("=== TESTE DE INTEGRAÇÃO FRONTEND-BACKEND ===")
    print(f"Timestamp: {datetime.now()}\n")
    
    # Teste 1: API do backend
    backend_data = test_backend_api()
    
    # Teste 2: Estrutura da resposta
    test_api_response_structure()
    
    # Teste 3: Processamento do frontend
    if backend_data:
        frontend_data = simulate_frontend_processing(backend_data)
        
        if frontend_data:
            print("\n🎉 INTEGRAÇÃO FUNCIONANDO!")
            print("✅ Backend retorna dados")
            print("✅ Frontend consegue processar")
            print("✅ Estrutura de dados está correta")
        else:
            print("\n❌ PROBLEMA NO PROCESSAMENTO DO FRONTEND")
    else:
        print("\n❌ PROBLEMA NO BACKEND")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    main()