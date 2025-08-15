import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.glpi_service import GLPIService
import json

def test_discover_tech_field():
    print("=== Teste do método _discover_tech_field_id ===")
    
    # Criar instância do serviço GLPI
    glpi_service = GLPIService()
    
    try:
        # Autenticar
        print("Autenticando...")
        auth_success = glpi_service.authenticate()
        if not auth_success:
            print("ERRO: Falha na autenticação")
            return
        print(" Autenticação bem-sucedida")
        
        # Testar descoberta do field ID
        print("\nTestando _discover_tech_field_id...")
        tech_field_id = glpi_service._discover_tech_field_id()
        
        print(f"Field ID descoberto: {tech_field_id}")
        print(f"Tipo: {type(tech_field_id)}")
        
        if tech_field_id:
            print(" Field ID descoberto com sucesso")
            
            # Testar busca com esse field ID
            print(f"\nTestando busca de tickets com field ID {tech_field_id}...")
            
            # Buscar opções de pesquisa para confirmar
            search_options = glpi_service.get_search_options('Ticket')
            if search_options:
                print(f"Total de opções de pesquisa: {len(search_options)}")
                
                # Procurar o field específico
                field_info = search_options.get(str(tech_field_id))
                if field_info:
                    print(f"Informações do campo {tech_field_id}:")
                    print(f"  Nome: {field_info.get('name', 'N/A')}")
                    print(f"  Tabela: {field_info.get('table', 'N/A')}")
                    print(f"  Campo: {field_info.get('field', 'N/A')}")
                else:
                    print(f"AVISO: Campo {tech_field_id} não encontrado nas opções")
            
            # Testar uma busca simples
            print(f"\nTestando busca de tickets...")
            params = {
                'criteria': [
                    {
                        'field': tech_field_id,
                        'searchtype': 'equals',
                        'value': '1'  # Qualquer valor para testar
                    }
                ],
                'range': '0-4'
            }
            
            tickets = glpi_service.search_tickets(params)
            if tickets:
                print(f" Busca retornou {len(tickets)} tickets")
                if tickets:
                    print(f"Exemplo de ticket: {tickets[0].get('id', 'N/A')}")
            else:
                print(" Busca não retornou tickets (pode ser normal se não houver dados)")
                
        else:
            print(" Falha ao descobrir field ID")
            
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        try:
            glpi_service.logout()
            print("\n Logout realizado")
        except:
            pass

if __name__ == "__main__":
    test_discover_tech_field()
