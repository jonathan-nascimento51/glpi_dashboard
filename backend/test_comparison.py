import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.glpi_service import GLPIService

def test_exact_comparison():
    print("=== Testando comparação exata vs contém ===")
    
    glpi_service = GLPIService()
    
    try:
        # Autenticar
        auth_success = glpi_service.authenticate()
        if not auth_success:
            print("ERRO: Falha na autenticação")
            return
        
        # Buscar opções de pesquisa
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/listSearchOptions/Ticket"
        )
        
        if not response:
            print("ERRO: Não foi possível obter resposta da API")
            return
            
        search_options = response.json()
        
        # Testar campo 5
        field_id = "5"
        expected_name = "Técnico"
        
        if field_id in search_options:
            field_data = search_options[field_id]
            actual_name = field_data.get("name", "")
            
            print(f"Campo {field_id}:")
            print(f"  Nome esperado: '{expected_name}'")
            print(f"  Nome real: '{actual_name}'")
            print(f"  Comparação exata (==): {actual_name == expected_name}")
            print(f"  Comparação contém (in): {expected_name in actual_name}")
            
            # Verificar caracteres especiais
            print(f"  Bytes do nome esperado: {expected_name.encode('utf-8')}")
            print(f"  Bytes do nome real: {actual_name.encode('utf-8')}")
            
            # Testar diferentes encodings
            print(f"  Nome real (repr): {repr(actual_name)}")
            print(f"  Nome esperado (repr): {repr(expected_name)}")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            glpi_service.logout()
        except:
            pass

if __name__ == "__main__":
    test_exact_comparison()
