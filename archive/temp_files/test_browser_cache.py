#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def test_browser_cache():
    """Testa se o problema pode estar relacionado ao cache do navegador"""
    try:
        print("=== TESTANDO CACHE DO NAVEGADOR ===")
        
        # Fazer múltiplas requisições com diferentes headers de cache
        headers_variants = [
            {'Cache-Control': 'no-cache'},
            {'Cache-Control': 'no-store'},
            {'Pragma': 'no-cache'},
            {'Cache-Control': 'no-cache, no-store, must-revalidate'},
            {}
        ]
        
        for i, headers in enumerate(headers_variants, 1):
            print(f"\n--- Teste {i}: {headers or 'Sem headers especiais'} ---")
            
            response = requests.get('http://localhost:5000/api/technicians/ranking', headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                technicians = data.get('data', [])
                
                if technicians:
                    first_tech = technicians[0]
                    print(f"✅ Primeiro técnico: {first_tech.get('nome')} ({first_tech.get('nivel')})")
                    print(f"   Total de técnicos: {len(technicians)}")
                else:
                    print("❌ Nenhum técnico retornado")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
            
            time.sleep(0.5)  # Pequena pausa entre requisições
        
        print("\n=== VERIFICANDO CONSISTÊNCIA DOS DADOS ===")
        
        # Fazer 3 requisições consecutivas para verificar consistência
        results = []
        for i in range(3):
            response = requests.get('http://localhost:5000/api/technicians/ranking')
            if response.status_code == 200:
                data = response.json()
                technicians = data.get('data', [])
                if technicians:
                    results.append(technicians[0].get('nome'))
                    
        if len(set(results)) == 1:
            print(f"✅ Dados consistentes: {results[0]}")
        else:
            print(f"❌ Dados inconsistentes: {results}")
            
        print("\n=== RECOMENDAÇÕES ===")
        print("1. Limpe o cache do navegador (Ctrl+Shift+Delete)")
        print("2. Abra o DevTools (F12) e vá para Network > Disable cache")
        print("3. Faça um hard refresh (Ctrl+F5 ou Ctrl+Shift+R)")
        print("4. Verifique se há Service Workers ativos em DevTools > Application")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_browser_cache()