import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import logging

# Desabilitar logs de debug
logging.getLogger().setLevel(logging.CRITICAL)

def test_groups_simple():
    print("=== TESTE DE GRUPOS TECNICOS ===")
    print()
    
    # Configuração dos grupos técnicos
    service_levels = {
        'N1': 89,
        'N2': 90,
        'N3': 91,
        'N4': 92
    }
    
    try:
        print("1. Testando autenticacao...")
        glpi = GLPIService()
        
        # Testar autenticação
        if glpi._ensure_authenticated():
            print("OK Autenticacao bem-sucedida")
        else:
            print("ERRO Falha na autenticacao")
            return
            
        print()
        print("2. Verificando grupos tecnicos configurados...")
        
        # Testar cada grupo individualmente
        for level, group_id in service_levels.items():
            try:
                response = glpi._make_authenticated_request('GET', f'{glpi.glpi_url}/Group/{group_id}')
                if response and response.ok:
                    group_data = response.json()
                    group_name = group_data.get('name', 'Nome nao encontrado')
                    print(f"OK Grupo existe: {level} (ID: {group_id}) - Nome: {group_name}")
                else:
                    status_code = response.status_code if response else 'None'
                    print(f"ERRO Grupo nao encontrado: {level} (ID: {group_id}) - Status: {status_code}")
            except Exception as e:
                print(f"ERRO Erro ao verificar grupo {level} (ID: {group_id}): {str(e)}")
        
        print()
        print("3. Listando alguns grupos existentes para comparacao...")
        
        # Buscar grupos existentes
        try:
            search_params = {
                'range': '0-10',
                'is_deleted': 0,
                'forcedisplay[0]': '2',  # ID
                'forcedisplay[1]': '1',  # Nome
            }
            
            response = glpi._make_authenticated_request('GET', f'{glpi.glpi_url}/search/Group', params=search_params)
            if response and response.ok:
                data = response.json()
                if 'data' in data and data['data']:
                    print(f"Total de grupos encontrados: {data.get('totalcount', 0)}")
                    print("Primeiros 10 grupos:")
                    for group in data['data'][:10]:
                        print(f"  ID: {group.get('2', 'N/A')} - Nome: {group.get('1', 'N/A')}")
                else:
                    print("ERRO Nenhum grupo encontrado")
            else:
                status_code = response.status_code if response else 'None'
                print(f"ERRO Nao foi possivel listar grupos - Status: {status_code}")
        except Exception as e:
            print(f"ERRO Erro ao listar grupos: {str(e)}")
            
    except Exception as e:
        print(f"ERRO Erro geral: {str(e)}")
    
    print()
    print("=== FIM DO TESTE ===")

if __name__ == "__main__":
    test_groups_simple()