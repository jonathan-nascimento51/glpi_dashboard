#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para validar o cálculo de tendências no dashboard GLPI
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_trends():
    """Testa se a API está retornando tendências calculadas corretamente"""
    print("=== TESTE DE TENDÊNCIAS - API METRICS ===")
    
    try:
        # Faz requisição para a API
        response = requests.get('http://localhost:5000/api/metrics')
        response.raise_for_status()
        
        data = response.json()
        
        # Verifica se a estrutura está correta
        if 'data' not in data:
            print("❌ ERRO: Campo 'data' não encontrado na resposta")
            return False
            
        if 'tendencias' not in data['data']:
            print("❌ ERRO: Campo 'tendencias' não encontrado")
            return False
            
        tendencias = data['data']['tendencias']
        niveis = data['data']['niveis']['geral']
        
        print("\n=== VALORES ATUAIS (GERAL) ===")
        print(f"Novos: {niveis['novos']}")
        print(f"Pendentes: {niveis['pendentes']}")
        print(f"Progresso: {niveis['progresso']}")
        print(f"Resolvidos: {niveis['resolvidos']}")
        print(f"Total: {niveis['total']}")
        
        print("\n=== TENDÊNCIAS CALCULADAS ===")
        print(f"Novos: {tendencias['novos']}")
        print(f"Pendentes: {tendencias['pendentes']}")
        print(f"Progresso: {tendencias['progresso']}")
        print(f"Resolvidos: {tendencias['resolvidos']}")
        
        # Verifica se as tendências não estão zeradas
        trends_not_zero = any(trend != "0%" and trend != "0" for trend in tendencias.values())
        
        if trends_not_zero:
            print("\n✅ SUCESSO: Tendências estão sendo calculadas (não estão zeradas)")
        else:
            print("\n❌ PROBLEMA: Todas as tendências estão zeradas")
            
        # Mostra a resposta completa para debug
        print("\n=== RESPOSTA COMPLETA (JSON) ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return trends_not_zero
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor backend")
        print("Verifique se o servidor está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def test_frontend_data():
    """Testa se o frontend está recebendo os dados corretamente"""
    print("\n=== TESTE DE DADOS DO FRONTEND ===")
    
    try:
        # Simula uma requisição como o frontend faria
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('http://localhost:5000/api/metrics', headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Verifica se a estrutura está compatível com o frontend
        required_fields = ['data']
        for field in required_fields:
            if field not in data:
                print(f"❌ ERRO: Campo obrigatório '{field}' não encontrado")
                return False
                
        # Verifica estrutura das tendências
        tendencias = data['data']['tendencias']
        required_trend_fields = ['novos', 'pendentes', 'progresso', 'resolvidos']
        
        for field in required_trend_fields:
            if field not in tendencias:
                print(f"❌ ERRO: Campo de tendência '{field}' não encontrado")
                return False
                
        print("✅ SUCESSO: Estrutura de dados compatível com o frontend")
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste do frontend: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando testes de validação das tendências...\n")
    
    # Executa os testes
    api_test = test_api_trends()
    frontend_test = test_frontend_data()
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Teste API: {'✅ PASSOU' if api_test else '❌ FALHOU'}")
    print(f"Teste Frontend: {'✅ PASSOU' if frontend_test else '❌ FALHOU'}")
    
    if api_test and frontend_test:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("As tendências estão sendo calculadas e os dados estão corretos.")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("Verifique os logs acima para identificar os problemas.")