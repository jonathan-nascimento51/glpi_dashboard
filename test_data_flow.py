#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do fluxo de dados do dashboard
Verifica se os dados estão sendo processados corretamente do backend para o frontend
"""

import requests
import json
from datetime import datetime, timedelta

def test_backend_data():
    """Testa os dados do backend"""
    print("🔍 Testando dados do backend...")
    
    try:
        # Testar endpoint de métricas
        response = requests.get('http://localhost:5000/api/metrics')
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend respondeu com sucesso")
            print(f"📊 Estrutura dos dados: {list(data.keys())}")
            
            # Verificar estrutura esperada
            if 'niveis' in data:
                print("✅ Campo 'niveis' encontrado")
                niveis = data['niveis']
                print(f"📊 Níveis disponíveis: {list(niveis.keys())}")
                
                # Verificar cada nível
                for nivel in ['n1', 'n2', 'n3', 'n4', 'geral']:
                    if nivel in niveis:
                        nivel_data = niveis[nivel]
                        print(f"✅ Nível {nivel}: {nivel_data}")
                    else:
                        print(f"❌ Nível {nivel} não encontrado")
            else:
                print("❌ Campo 'niveis' não encontrado")
                
            # Verificar tendências
            if 'tendencias' in data:
                print("✅ Campo 'tendencias' encontrado")
                print(f"📊 Tendências: {data['tendencias']}")
            else:
                print("❌ Campo 'tendencias' não encontrado")
                
            return data
        else:
            print(f"❌ Backend retornou erro: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        return None

def simulate_frontend_transformation(backend_data):
    """Simula a transformação que o frontend faz nos dados"""
    print("\n🔄 Simulando transformação do frontend...")
    
    if not backend_data:
        print("❌ Nenhum dado do backend para transformar")
        return None
        
    # Simular a função transformLegacyData
    def transform_legacy_data(legacy_data):
        default_level = {
            'novos': 0,
            'pendentes': 0,
            'progresso': 0,
            'resolvidos': 0,
            'total': 0
        }
        
        if legacy_data and 'niveis' in legacy_data:
            n1 = legacy_data['niveis'].get('n1', default_level)
            n2 = legacy_data['niveis'].get('n2', default_level)
            n3 = legacy_data['niveis'].get('n3', default_level)
            n4 = legacy_data['niveis'].get('n4', default_level)
            
            # Calcular totais gerais somando todos os níveis
            geral = {
                'novos': n1.get('novos', 0) + n2.get('novos', 0) + n3.get('novos', 0) + n4.get('novos', 0),
                'pendentes': n1.get('pendentes', 0) + n2.get('pendentes', 0) + n3.get('pendentes', 0) + n4.get('pendentes', 0),
                'progresso': n1.get('progresso', 0) + n2.get('progresso', 0) + n3.get('progresso', 0) + n4.get('progresso', 0),
                'resolvidos': n1.get('resolvidos', 0) + n2.get('resolvidos', 0) + n3.get('resolvidos', 0) + n4.get('resolvidos', 0),
            }
            geral['total'] = geral['novos'] + geral['pendentes'] + geral['progresso'] + geral['resolvidos']
            
            return {
                'niveis': {
                    'n1': n1,
                    'n2': n2,
                    'n3': n3,
                    'n4': n4,
                    'geral': geral
                },
                'tendencias': legacy_data.get('tendencias'),
                'filtros_aplicados': legacy_data.get('filtros_aplicados'),
                'tempo_execucao': legacy_data.get('tempo_execucao'),
                'timestamp': legacy_data.get('timestamp'),
                'systemStatus': legacy_data.get('systemStatus'),
                'technicianRanking': legacy_data.get('technicianRanking')
            }
        
        return legacy_data
    
    transformed_data = transform_legacy_data(backend_data)
    
    print("✅ Transformação concluída")
    if transformed_data and 'niveis' in transformed_data and 'geral' in transformed_data['niveis']:
        geral = transformed_data['niveis']['geral']
        print(f"📊 Dados gerais calculados: {geral}")
        
        # Simular o que o App.tsx faz
        metrics_for_app = {
            'novos': geral.get('novos', 0),
            'pendentes': geral.get('pendentes', 0),
            'progresso': geral.get('progresso', 0),
            'resolvidos': geral.get('resolvidos', 0),
            'total': geral.get('novos', 0) + geral.get('pendentes', 0) + geral.get('progresso', 0) + geral.get('resolvidos', 0),
            'niveis': transformed_data['niveis'],
            'tendencias': transformed_data.get('tendencias', {})
        }
        
        print(f"📊 Métricas para o App: {metrics_for_app}")
        return metrics_for_app
    else:
        print("❌ Falha na transformação - dados gerais não encontrados")
        return None

def test_with_date_filters():
    """Testa com filtros de data"""
    print("\n🗓️ Testando com filtros de data...")
    
    # Testar com últimos 7 dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.get('http://localhost:5000/api/metrics', params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dados com filtro de data: {data.get('filtros_aplicados', 'Nenhum filtro')}")
            return data
        else:
            print(f"❌ Erro com filtros: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao testar filtros: {e}")
        return None

def main():
    print("🚀 Iniciando teste do fluxo de dados...")
    print("=" * 50)
    
    # Teste 1: Dados básicos do backend
    backend_data = test_backend_data()
    
    # Teste 2: Transformação do frontend
    if backend_data:
        frontend_data = simulate_frontend_transformation(backend_data)
        
        if frontend_data:
            print("\n✅ SUCESSO: Fluxo de dados funcionando corretamente")
            print(f"📊 Total de tickets: {frontend_data.get('total', 0)}")
            print(f"📊 Novos: {frontend_data.get('novos', 0)}")
            print(f"📊 Pendentes: {frontend_data.get('pendentes', 0)}")
            print(f"📊 Em Progresso: {frontend_data.get('progresso', 0)}")
            print(f"📊 Resolvidos: {frontend_data.get('resolvidos', 0)}")
        else:
            print("\n❌ FALHA: Problema na transformação dos dados")
    else:
        print("\n❌ FALHA: Problema na obtenção dos dados do backend")
    
    # Teste 3: Dados com filtros
    filtered_data = test_with_date_filters()
    if filtered_data:
        filtered_frontend = simulate_frontend_transformation(filtered_data)
        if filtered_frontend:
            print("\n✅ Filtros funcionando corretamente")
        else:
            print("\n❌ Problema com dados filtrados")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído")

if __name__ == '__main__':
    main()