import requests
import sys

def test_system():
    print("=== VALIDACAO VISUAL DO SISTEMA GLPI DASHBOARD ===")
    print()
    
    backend_base = "http://localhost:5000"
    frontend_url = "http://localhost:3001"
    
    endpoints = [
        (f"{backend_base}/api/v1/metrics", "Metricas Dashboard"),
        (f"{backend_base}/api/v1/status", "Status Sistema"),
        (f"{backend_base}/api/v1/technicians/ranking", "Ranking Tecnicos")
    ]
    
    print("TESTANDO ENDPOINTS DO BACKEND MOCK:")
    backend_ok = 0
    
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f" {name}: OK (Status {response.status_code})")
                backend_ok += 1
                
                if "metrics" in url:
                    total_tickets = data.get("data", {}).get("geral", {}).get("total_tickets", 0)
                    mock_mode = data.get("mock_mode", False)
                    print(f"    Total Tickets: {total_tickets}")
                    print(f"    Mock Mode: {mock_mode}")
                    
                    if total_tickets > 0 and mock_mode:
                        print(f"    Dados mock validos detectados")
                    else:
                        print(f"    Dados podem estar zerados")
            else:
                print(f" {name}: ERRO (Status {response.status_code})")
        except Exception as e:
            print(f" {name}: ERRO DE CONEXAO - {str(e)}")
    
    print()
    print("TESTANDO ACESSIBILIDADE DO FRONTEND:")
    frontend_ok = False
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200 and len(response.content) > 500:
            print(f" Frontend acessivel: {len(response.content)} bytes")
            frontend_ok = True
        else:
            print(f" Frontend: Status {response.status_code}, Tamanho: {len(response.content)}")
    except Exception as e:
        print(f" Frontend: ERRO DE CONEXAO - {str(e)}")
    
    print()
    print("=== RESUMO DA VALIDACAO ===")
    print(f"Backend: {backend_ok}/{len(endpoints)} endpoints OK")
    print(f"Frontend: {' Acessivel' if frontend_ok else ' Inacessivel'}")
    
    overall_success = (backend_ok == len(endpoints)) and frontend_ok
    
    if overall_success:
        print()
        print(" SISTEMA TOTALMENTE FUNCIONAL!")
        print(" Backend mock respondendo corretamente")
        print(" Frontend acessivel")
        print(" Dados mock disponiveis")
    else:
        print()
        print(" SISTEMA COM PROBLEMAS DETECTADOS")
        if backend_ok < len(endpoints):
            print(f" {len(endpoints) - backend_ok} endpoint(s) do backend com falha")
        if not frontend_ok:
            print(" Frontend inacessivel")
    
    print()
    print(" URLS DE ACESSO:")
    print(f"Frontend: {frontend_url}")
    print(f"Backend API: {backend_base}/api/v1/metrics")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = test_system()
    sys.exit(exit_code)
