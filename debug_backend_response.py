import requests
import json

def test_backend_response():
    """Testa a resposta do backend para o endpoint de ranking de técnicos"""
    try:
        # Fazer requisição para o endpoint
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== ESTRUTURA DA RESPOSTA ===")
            print(f"Success: {data.get('success')}")
            print(f"Cached: {data.get('cached')}")
            print(f"Data length: {len(data.get('data', []))}")
            
            # Examinar os primeiros técnicos
            technicians = data.get('data', [])
            if technicians:
                print("\n=== PRIMEIROS 3 TÉCNICOS ===")
                for i, tech in enumerate(technicians[:3]):
                    print(f"\nTécnico {i+1}:")
                    print(f"  Nome: {tech.get('name', 'N/A')}")
                    print(f"  Total: {tech.get('total', 'N/A')}")
                    print(f"  Total_tickets: {tech.get('total_tickets', 'N/A')}")
                    print(f"  Todas as chaves: {list(tech.keys())}")
                    
                    # Verificar se há algum campo com valor não-zero
                    non_zero_fields = {k: v for k, v in tech.items() if isinstance(v, (int, float)) and v != 0}
                    if non_zero_fields:
                        print(f"  Campos não-zero: {non_zero_fields}")
            else:
                print("Nenhum técnico encontrado na resposta")
        else:
            print(f"Erro na requisição: {response.text}")
            
    except Exception as e:
        print(f"Erro ao testar backend: {e}")

if __name__ == "__main__":
    test_backend_response()