#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def clear_all_caches():
    """Limpa todos os caches do sistema"""
    try:
        print("=== LIMPANDO TODOS OS CACHES ===")
        
        # 1. Tentar limpar cache do backend (se existir endpoint)
        backend_endpoints = [
            'http://localhost:5000/api/cache/clear',
            'http://localhost:5000/api/clear-cache',
            'http://localhost:5000/cache/clear'
        ]
        
        for endpoint in backend_endpoints:
            try:
                response = requests.post(endpoint)
                if response.status_code == 200:
                    print(f"✅ Cache do backend limpo via {endpoint}")
                    break
            except:
                continue
        else:
            print("⚠️  Nenhum endpoint de limpeza de cache encontrado no backend")
        
        # 2. Fazer requisições com headers que forçam bypass de cache
        print("\n=== FORÇANDO BYPASS DE CACHE ===")
        
        bypass_headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        # Fazer requisição para forçar atualização
        response = requests.get('http://localhost:5000/api/technicians/ranking', headers=bypass_headers)
        
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', [])
            print(f"✅ Dados atualizados obtidos: {len(technicians)} técnicos")
            
            if technicians:
                first_tech = technicians[0]
                print(f"   Primeiro técnico: {first_tech.get('nome')} ({first_tech.get('nivel')})")
        
        # 3. Instruções para limpar cache do navegador
        print("\n=== INSTRUÇÕES PARA LIMPAR CACHE DO NAVEGADOR ===")
        print("1. Abra o DevTools (F12)")
        print("2. Vá para a aba Network")
        print("3. Marque 'Disable cache'")
        print("4. Faça um hard refresh (Ctrl+Shift+R)")
        print("5. Ou execute no console do navegador:")
        print("   window.location.reload(true);")
        
        # 4. Script para executar no console do navegador
        browser_script = """
// Execute este código no console do navegador (F12)
console.log('=== LIMPANDO CACHE DO FRONTEND ===');

// Limpar localStorage
if (window.localStorage) {
  const keysToRemove = Object.keys(localStorage).filter(key => 
    key.includes('technician') || key.includes('ranking') || key.includes('cache') || key.includes('metrics')
  );
  keysToRemove.forEach(key => localStorage.removeItem(key));
  console.log('LocalStorage limpo:', keysToRemove.length, 'chaves removidas');
}

// Limpar sessionStorage
if (window.sessionStorage) {
  const sessionKeysToRemove = Object.keys(sessionStorage).filter(key => 
    key.includes('technician') || key.includes('ranking') || key.includes('cache') || key.includes('metrics')
  );
  sessionKeysToRemove.forEach(key => sessionStorage.removeItem(key));
  console.log('SessionStorage limpo:', sessionKeysToRemove.length, 'chaves removidas');
}

// Limpar cache do sistema de cache personalizado (se existir)
if (window.debugCache) {
  window.debugCache.clear();
  console.log('Cache personalizado limpo');
}

// Forçar reload completo
console.log('Recarregando página...');
window.location.reload(true);
"""
        
        print("\n=== SCRIPT PARA CONSOLE DO NAVEGADOR ===")
        print(browser_script)
        
        # Salvar script em arquivo
        with open('clear_browser_cache.js', 'w', encoding='utf-8') as f:
            f.write(browser_script)
        
        print("\n✅ Script salvo em 'clear_browser_cache.js'")
        print("\n=== PRÓXIMOS PASSOS ===")
        print("1. Abra o navegador em http://localhost:3001")
        print("2. Abra o DevTools (F12)")
        print("3. Vá para a aba Console")
        print("4. Cole e execute o script acima")
        print("5. Aguarde o reload automático")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_all_caches()