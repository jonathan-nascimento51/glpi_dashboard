#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da implementação otimizada do ranking de técnicos
"""

import requests
import json
import time

def test_optimized_ranking():
    """Testa o ranking otimizado de técnicos"""
    base_url = "http://127.0.0.1:5000"
    
    print("🚀 Testando ranking otimizado de técnicos...")
    
    # Teste 1: Ranking sem filtros
    print("\n📊 Teste 1: Ranking sem filtros")
    start_time = time.time()
    
    try:
        response = requests.get(f"{base_url}/api/technicians/ranking?limit=10", timeout=30)
        elapsed = time.time() - start_time
        
        print(f"⏱️ Tempo de resposta: {elapsed:.2f}s")
        print(f"📈 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data)} técnicos encontrados")
            
            # Mostrar primeiros 3 técnicos
            for i, tech in enumerate(data[:3]):
                print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('total_tickets', 0)} tickets")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Ranking com filtros de data
    print("\n📊 Teste 2: Ranking com filtros de data")
    start_time = time.time()
    
    try:
        params = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'limit': 5
        }
        
        response = requests.get(f"{base_url}/api/technicians/ranking", params=params, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"⏱️ Tempo de resposta: {elapsed:.2f}s")
        print(f"📈 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data)} técnicos encontrados com filtros")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Verificar se o backend está respondendo
    print("\n🏥 Teste 3: Health check")
    try:
        response = requests.get(f"{base_url}/api/metrics", timeout=10)
        if response.status_code == 200:
            print("✅ Backend está funcionando!")
        else:
            print(f"⚠️ Backend respondeu com status {response.status_code}")
    except Exception as e:
        print(f"❌ Backend não está respondendo: {e}")
    
    print("\n🎯 Teste concluído!")

if __name__ == "__main__":
    test_optimized_ranking()