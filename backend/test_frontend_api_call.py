#!/usr/bin/env python3
"""
Script para testar como o frontend está chamando a API de ranking de técnicos
Verifica se há filtros sendo aplicados automaticamente
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração da API
BASE_URL = "http://localhost:5000"
API_ENDPOINTS = {
    "ranking": f"{BASE_URL}/api/technicians/ranking",
    "health": f"{BASE_URL}/api/health"
}

def test_api_call(endpoint, params=None, description=""):
    """Testa uma chamada da API"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTE: {description}")
    print(f"📡 Endpoint: {endpoint}")
    print(f"📋 Parâmetros: {params or 'Nenhum'}")
    print(f"{'='*60}")
    
    try:
        if params:
            response = requests.get(endpoint, params=params, timeout=30)
        else:
            response = requests.get(endpoint, timeout=30)
        
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Tempo de resposta: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar se a resposta tem o formato esperado
            if isinstance(data, dict) and 'data' in data:
                technicians = data['data']
                print(f"📊 Total de técnicos retornados: {len(technicians)}")
                
                # Analisar distribuição por nível
                levels = {}
                for tech in technicians:
                    level = tech.get('level', 'Desconhecido')
                    levels[level] = levels.get(level, 0) + 1
                
                print(f"📈 Distribuição por nível:")
                for level, count in sorted(levels.items()):
                    print(f"   {level}: {count} técnicos")
                
                # Mostrar primeiros 5 técnicos
                print(f"\n🏆 Primeiros 5 técnicos:")
                for i, tech in enumerate(technicians[:5]):
                    print(f"   {i+1}. {tech.get('name', 'N/A')} ({tech.get('level', 'N/A')}) - {tech.get('total', 0)} tickets")
                
                # Salvar dados completos
                filename = f"frontend_api_test_{description.replace(' ', '_').lower()}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Dados salvos em: {filename}")
                
                return technicians
                
            elif isinstance(data, list):
                print(f"📊 Total de técnicos retornados: {len(data)}")
                
                # Analisar distribuição por nível
                levels = {}
                for tech in data:
                    level = tech.get('level', 'Desconhecido')
                    levels[level] = levels.get(level, 0) + 1
                
                print(f"📈 Distribuição por nível:")
                for level, count in sorted(levels.items()):
                    print(f"   {level}: {count} técnicos")
                
                # Mostrar primeiros 5 técnicos
                print(f"\n🏆 Primeiros 5 técnicos:")
                for i, tech in enumerate(data[:5]):
                    print(f"   {i+1}. {tech.get('name', 'N/A')} ({tech.get('level', 'N/A')}) - {tech.get('total', 0)} tickets")
                
                # Salvar dados completos
                filename = f"frontend_api_test_{description.replace(' ', '_').lower()}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Dados salvos em: {filename}")
                
                return data
            else:
                print(f"📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return data
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def main():
    print("🚀 TESTE DE CHAMADAS DA API DO FRONTEND")
    print(f"⏰ Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste de conectividade
    print(f"\n{'='*60}")
    print("🔍 TESTE DE CONECTIVIDADE")
    print(f"{'='*60}")
    
    health_response = test_api_call(
        API_ENDPOINTS["health"],
        description="Health check"
    )
    
    if not health_response:
        print("❌ Servidor não está respondendo. Abortando testes.")
        return
    
    # Teste 1: Chamada sem filtros (como o frontend faz inicialmente)
    data_no_filters = test_api_call(
        API_ENDPOINTS["ranking"],
        description="Sem filtros (chamada padrão do frontend)"
    )
    
    # Teste 2: Chamada com filtros de data (últimos 30 dias)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    data_with_dates = test_api_call(
        API_ENDPOINTS["ranking"],
        params={
            'start_date': start_date,
            'end_date': end_date
        },
        description="Com filtros de data (últimos 30 dias)"
    )
    
    # Teste 3: Chamada com filtro de nível específico
    data_n1 = test_api_call(
        API_ENDPOINTS["ranking"],
        params={'level': 'N1'},
        description="Com filtro de nível N1"
    )
    
    # Teste 4: Chamada com filtro de nível N2
    data_n2 = test_api_call(
        API_ENDPOINTS["ranking"],
        params={'level': 'N2'},
        description="Com filtro de nível N2"
    )
    
    # Teste 5: Chamada com filtro de nível N3
    data_n3 = test_api_call(
        API_ENDPOINTS["ranking"],
        params={'level': 'N3'},
        description="Com filtro de nível N3"
    )
    
    # Teste 6: Chamada com filtro de nível N4
    data_n4 = test_api_call(
        API_ENDPOINTS["ranking"],
        params={'level': 'N4'},
        description="Com filtro de nível N4"
    )
    
    # Análise comparativa
    print(f"\n{'='*60}")
    print("🔍 ANÁLISE COMPARATIVA DOS RESULTADOS")
    print(f"{'='*60}")
    
    if data_no_filters:
        # Extrair lista de técnicos
        if isinstance(data_no_filters, dict) and 'data' in data_no_filters:
            technicians_no_filters = data_no_filters['data']
        else:
            technicians_no_filters = data_no_filters
        
        print(f"📊 Sem filtros: {len(technicians_no_filters)} técnicos")
        
        # Contar por nível
        levels_count = {}
        for tech in technicians_no_filters:
            level = tech.get('level', 'Desconhecido')
            levels_count[level] = levels_count.get(level, 0) + 1
        
        print("📈 Distribuição detalhada por nível:")
        for level in ['N1', 'N2', 'N3', 'N4']:
            count = levels_count.get(level, 0)
            print(f"   {level}: {count} técnicos")
            
            # Mostrar técnicos deste nível
            if count > 0:
                level_techs = [t for t in technicians_no_filters if t.get('level') == level]
                print(f"      Técnicos {level}:")
                for tech in level_techs[:3]:  # Mostrar apenas os 3 primeiros
                    print(f"        - {tech.get('name', 'N/A')} ({tech.get('total', 0)} tickets)")
                if len(level_techs) > 3:
                    print(f"        ... e mais {len(level_techs) - 3} técnicos")
        
        # Verificar se há técnicos sem nível definido
        unknown_level = levels_count.get('Desconhecido', 0)
        if unknown_level > 0:
            print(f"⚠️  {unknown_level} técnicos sem nível definido")
    
    # Verificar filtros por nível
    level_tests = {
        'N1': data_n1,
        'N2': data_n2,
        'N3': data_n3,
        'N4': data_n4
    }
    
    print(f"\n📋 Resultados dos filtros por nível:")
    for level, data in level_tests.items():
        if data:
            if isinstance(data, dict) and 'data' in data:
                count = len(data['data'])
            else:
                count = len(data) if isinstance(data, list) else 0
            print(f"   {level}: {count} técnicos")
        else:
            print(f"   {level}: Erro ou sem dados")
    
    print(f"\n{'='*60}")
    print("✅ TESTE CONCLUÍDO")
    print(f"{'='*60}")
    
    # Conclusões
    print("\n🎯 CONCLUSÕES:")
    if data_no_filters:
        if isinstance(data_no_filters, dict) and 'data' in data_no_filters:
            total_techs = len(data_no_filters['data'])
        else:
            total_techs = len(data_no_filters) if isinstance(data_no_filters, list) else 0
        
        print(f"   • API está funcionando e retorna {total_techs} técnicos")
        print(f"   • Distribuição por nível: {levels_count}")
        
        if levels_count.get('N1', 0) == 0:
            print("   ⚠️  PROBLEMA: Nenhum técnico N1 encontrado")
        if levels_count.get('N4', 0) == 0:
            print("   ⚠️  PROBLEMA: Nenhum técnico N4 encontrado")
        
        if levels_count.get('N2', 0) > 0 and levels_count.get('N3', 0) > 0:
            print("   ✅ Técnicos N2 e N3 estão sendo retornados corretamente")
    else:
        print("   ❌ API não está funcionando corretamente")

if __name__ == "__main__":
    main()