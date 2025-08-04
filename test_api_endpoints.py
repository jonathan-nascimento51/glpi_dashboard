#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar os endpoints da API e diagnosticar problemas de conectividade
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, endpoint_name):
    """Testa um endpoint específico"""
    try:
        print(f"\n🔍 Testando {endpoint_name}: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Sucesso - Dados recebidos")
                print(f"   📊 Tamanho da resposta: {len(json.dumps(data))} caracteres")
                
                # Mostra uma amostra dos dados
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]  # Primeiras 5 chaves
                    print(f"   🔑 Chaves principais: {keys}")
                elif isinstance(data, list):
                    print(f"   📋 Lista com {len(data)} itens")
                    
                return True, data
            except json.JSONDecodeError:
                print(f"   ⚠️  Resposta não é JSON válido")
                print(f"   📄 Conteúdo: {response.text[:200]}...")
                return False, response.text
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
            print(f"   📄 Conteúdo: {response.text[:200]}...")
            return False, response.text
            
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Erro de conexão - Servidor não está rodando")
        return False, "Connection Error"
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - Servidor demorou para responder")
        return False, "Timeout"
    except Exception as e:
        print(f"   💥 Erro inesperado: {str(e)}")
        return False, str(e)

def main():
    """Função principal para testar todos os endpoints"""
    print("🚀 Iniciando teste dos endpoints da API")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Endpoints para testar
    endpoints = [
        ("http://localhost:5000/api/metrics", "Métricas"),
        ("http://localhost:5000/api/status", "Status do Sistema"),
        ("http://localhost:5000/api/technicians/ranking", "Ranking de Técnicos"),
        ("http://localhost:5000/api/alerts", "Alertas"),
    ]
    
    results = {}
    
    for url, name in endpoints:
        success, data = test_endpoint(url, name)
        results[name] = {
            'success': success,
            'data': data,
            'url': url
        }
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for name, result in results.items():
        status = "✅ SUCESSO" if result['success'] else "❌ FALHOU"
        print(f"   {status} - {name}")
        if result['success']:
            successful += 1
        else:
            failed += 1
            print(f"     └─ Erro: {result['data']}")
    
    print(f"\n📈 Estatísticas:")
    print(f"   ✅ Sucessos: {successful}/{len(endpoints)}")
    print(f"   ❌ Falhas: {failed}/{len(endpoints)}")
    print(f"   📊 Taxa de sucesso: {(successful/len(endpoints)*100):.1f}%")
    
    # Diagnóstico
    print("\n🔧 DIAGNÓSTICO:")
    if successful == len(endpoints):
        print("   🎉 Todos os endpoints estão funcionando perfeitamente!")
        print("   ✨ Os erros de conectividade foram resolvidos.")
    elif successful > 0:
        print(f"   ⚠️  Alguns endpoints estão funcionando ({successful}/{len(endpoints)})")
        print("   🔍 Verifique os endpoints que falharam acima.")
    else:
        print("   🚨 Nenhum endpoint está funcionando!")
        print("   🔌 Verifique se o servidor backend está rodando na porta 5000.")
        print("   💡 Execute: python app.py")
    
    # Recomendações
    print("\n💡 PRÓXIMOS PASSOS:")
    if failed > 0:
        print("   1. Verifique se o servidor Flask está rodando: python app.py")
        print("   2. Confirme se a porta 5000 está disponível")
        print("   3. Verifique os logs do servidor para erros específicos")
        print("   4. Teste manualmente: curl http://localhost:5000/api/status")
    else:
        print("   1. Abra o dashboard: http://localhost:3001")
        print("   2. Verifique se os alertas de monitoramento diminuíram")
        print("   3. Teste as funcionalidades do dashboard")
        print("   4. Monitore os logs para garantir estabilidade")
    
    print("\n" + "=" * 60)
    print("🏁 Teste concluído!")
    
    return successful == len(endpoints)

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal: {str(e)}")
        exit(1)