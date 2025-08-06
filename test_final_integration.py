#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final de integração para verificar se os filtros de data estão funcionando
"""

import requests
import json
from datetime import datetime, timedelta

def test_final_integration():
    """Teste final para confirmar que tudo está funcionando"""
    base_url = "http://localhost:5000/api"
    
    print("=== TESTE FINAL DE INTEGRAÇÃO ===")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Carregamento inicial (sem filtro)
    print("\n1. CARREGAMENTO INICIAL (sem filtro):")
    try:
        response = requests.get(f"{base_url}/metrics")
        if response.status_code == 200:
            data = response.json().get('data', {})
            total = data.get('total', 0)
            filtro = data.get('filtro_data')
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total de tickets: {total}")
            print(f"✅ Filtro aplicado: {'Nenhum' if not filtro else filtro}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Filtro de 7 dias
    print("\n2. FILTRO DE 7 DIAS:")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        params = {'start_date': start_date, 'end_date': end_date}
        response = requests.get(f"{base_url}/metrics", params=params)
        if response.status_code == 200:
            data = response.json().get('data', {})
            total = data.get('total', 0)
            filtro = data.get('filtro_data', {})
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total de tickets: {total}")
            print(f"✅ Período: {filtro.get('data_inicio')} até {filtro.get('data_fim')}")
            
            # Verificar se o filtro foi aplicado corretamente
            if filtro.get('data_inicio') == start_date and filtro.get('data_fim') == end_date:
                print(f"✅ Filtro aplicado corretamente!")
            else:
                print(f"❌ Filtro não aplicado corretamente")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Filtro de 30 dias
    print("\n3. FILTRO DE 30 DIAS:")
    start_date_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        params = {'start_date': start_date_30, 'end_date': end_date}
        response = requests.get(f"{base_url}/metrics", params=params)
        if response.status_code == 200:
            data = response.json().get('data', {})
            total = data.get('total', 0)
            filtro = data.get('filtro_data', {})
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total de tickets: {total}")
            print(f"✅ Período: {filtro.get('data_inicio')} até {filtro.get('data_fim')}")
            
            # Verificar se o filtro foi aplicado corretamente
            if filtro.get('data_inicio') == start_date_30 and filtro.get('data_fim') == end_date:
                print(f"✅ Filtro aplicado corretamente!")
            else:
                print(f"❌ Filtro não aplicado corretamente")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: Verificar estrutura completa da resposta
    print("\n4. VERIFICAÇÃO DA ESTRUTURA DA RESPOSTA:")
    try:
        params = {'start_date': start_date, 'end_date': end_date}
        response = requests.get(f"{base_url}/metrics", params=params)
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            # Verificar campos essenciais
            campos_essenciais = ['total', 'novos', 'pendentes', 'progresso', 'resolvidos', 'niveis']
            campos_presentes = [campo for campo in campos_essenciais if campo in data]
            campos_ausentes = [campo for campo in campos_essenciais if campo not in data]
            
            print(f"✅ Campos presentes: {campos_presentes}")
            if campos_ausentes:
                print(f"❌ Campos ausentes: {campos_ausentes}")
            else:
                print(f"✅ Todos os campos essenciais estão presentes!")
                
            # Verificar níveis
            niveis = data.get('niveis', {})
            niveis_esperados = ['n1', 'n2', 'n3', 'n4']
            niveis_presentes = [nivel for nivel in niveis_esperados if nivel in niveis]
            print(f"✅ Níveis presentes: {niveis_presentes}")
            
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n=== RESUMO DO TESTE ===")
    print("✅ Se todos os testes acima mostraram '✅', a API está funcionando perfeitamente!")
    print("✅ Os filtros de data estão sendo aplicados corretamente.")
    print("✅ A estrutura da resposta está completa.")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Teste o frontend no navegador (http://localhost:3002)")
    print("2. Clique nos filtros de data (7 dias, 30 dias, etc.)")
    print("3. Verifique se os números mudam conforme esperado")
    print("4. Abra o DevTools (F12) e veja a aba Network para confirmar as chamadas da API")

if __name__ == "__main__":
    test_final_integration()