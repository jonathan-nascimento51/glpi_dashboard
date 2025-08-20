import requests
import json

def test_ranking_methods():
    """Testa ambos os métodos de ranking para comparar as respostas"""
    base_url = 'http://localhost:5000/api/technicians/ranking'
    
    print("=== TESTE DOS MÉTODOS DE RANKING ===")
    
    # Teste 1: Sem filtros (chama get_technician_ranking)
    print("\n1. Testando SEM filtros (get_technician_ranking):")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', [])
            print(f"   Status: {response.status_code}")
            print(f"   Técnicos retornados: {len(technicians)}")
            
            if technicians:
                first_tech = technicians[0]
                print(f"   Primeiro técnico:")
                print(f"     Nome: {first_tech.get('name', 'N/A')}")
                print(f"     Campos disponíveis: {list(first_tech.keys())}")
                print(f"     Campo 'total': {first_tech.get('total', 'AUSENTE')}")
                print(f"     Campo 'total_tickets': {first_tech.get('total_tickets', 'AUSENTE')}")
        else:
            print(f"   Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    
    # Teste 2: Com filtros (chama get_technician_ranking_with_filters)
    print("\n2. Testando COM filtros (get_technician_ranking_with_filters):")
    try:
        params = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', [])
            print(f"   Status: {response.status_code}")
            print(f"   Técnicos retornados: {len(technicians)}")
            
            if technicians:
                first_tech = technicians[0]
                print(f"   Primeiro técnico:")
                print(f"     Nome: {first_tech.get('name', 'N/A')}")
                print(f"     Campos disponíveis: {list(first_tech.keys())}")
                print(f"     Campo 'total': {first_tech.get('total', 'AUSENTE')}")
                print(f"     Campo 'total_tickets': {first_tech.get('total_tickets', 'AUSENTE')}")
        else:
            print(f"   Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    
    # Teste 3: Com filtro de entidade (chama get_technician_ranking_with_filters)
    print("\n3. Testando COM filtro de entidade (get_technician_ranking_with_filters):")
    try:
        params = {
            'entity_id': '1'
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', [])
            print(f"   Status: {response.status_code}")
            print(f"   Técnicos retornados: {len(technicians)}")
            
            if technicians:
                first_tech = technicians[0]
                print(f"   Primeiro técnico:")
                print(f"     Nome: {first_tech.get('name', 'N/A')}")
                print(f"     Campos disponíveis: {list(first_tech.keys())}")
                print(f"     Campo 'total': {first_tech.get('total', 'AUSENTE')}")
                print(f"     Campo 'total_tickets': {first_tech.get('total_tickets', 'AUSENTE')}")
        else:
            print(f"   Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")

if __name__ == "__main__":
    test_ranking_methods()