import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.glpi_service import GLPIService
import json

def debug_discover_tech_field():
    print("=== Debug detalhado do _discover_tech_field_id ===")
    
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
        
        # Buscar opções de pesquisa usando a mesma lógica do método
        print("\nBuscando opções de pesquisa para Ticket...")
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/listSearchOptions/Ticket"
        )
        
        if not response:
            print("ERRO: Não foi possível obter resposta da API")
            return
            
        search_options = response.json()
        print(f"Total de opções encontradas: {len(search_options)}")
        
        # Verificar mapeamento predefinido
        tech_field_mapping = {
            "5": "Técnico",
            "95": "Técnico encarregado"
        }
        
        print("\n=== Verificando mapeamento predefinido ===")
        for field_id, field_name in tech_field_mapping.items():
            if field_id in search_options:
                field_info = search_options[field_id]
                print(f" Campo {field_id} ({field_name}) encontrado:")
                print(f"  Nome: {field_info.get('name', 'N/A')}")
                print(f"  Tabela: {field_info.get('table', 'N/A')}")
                print(f"  Campo: {field_info.get('field', 'N/A')}")
                
                # Verificar se o nome contém a palavra esperada
                field_actual_name = field_info.get('name', '').lower()
                expected_lower = field_name.lower()
                if expected_lower in field_actual_name:
                    print(f"   Nome contém '{field_name}'")
                    print(f"  >>> ESTE CAMPO DEVERIA SER RETORNADO <<<")
                else:
                    print(f"   Nome NÃO contém '{field_name}'")
                    print(f"  Nome real: '{field_info.get('name', '')}'")
            else:
                print(f" Campo {field_id} ({field_name}) NÃO encontrado")
        
        # Buscar campos relacionados a técnico usando as palavras-chave do método
        print("\n=== Buscando campos com palavras-chave ===")
        tech_keywords = ["Técnico", "Atribuído", "Assigned to", "Technician", "Técnico encarregado"]
        
        found_fields = []
        for field_id, field_info in search_options.items():
            field_name = field_info.get('name', '').lower()
            for keyword in tech_keywords:
                if keyword.lower() in field_name:
                    found_fields.append((field_id, field_info))
                    print(f"Campo {field_id}: {field_info.get('name', 'N/A')} (tabela: {field_info.get('table', 'N/A')})")
                    break
        
        if not found_fields:
            print("Nenhum campo relacionado a técnico encontrado com as palavras-chave")
            
            # Listar campos que podem ser relacionados
            print("\n=== Campos que podem ser relacionados a usuário/técnico ===")
            user_related = []
            for field_id, field_info in search_options.items():
                field_name = field_info.get('name', '').lower()
                table = field_info.get('table', '').lower()
                if ('user' in field_name or 'usuário' in field_name or 
                    'assign' in field_name or 'atrib' in field_name or
                    'tech' in field_name or 'técn' in field_name or
                    'glpi_users' in table):
                    user_related.append((field_id, field_info))
            
            for field_id, field_info in user_related[:10]:  # Primeiros 10
                print(f"Campo {field_id}: {field_info.get('name', 'N/A')} (tabela: {field_info.get('table', 'N/A')})")
        
        # Simular a lógica exata do método
        print("\n=== Simulando lógica exata do método ===")
        
        # Primeiro, tentar os campos conhecidos
        for field_id, expected_name in tech_field_mapping.items():
            if field_id in search_options:
                field_data = search_options[field_id]
                field_name = field_data.get('name', '').lower()
                if expected_name.lower() in field_name:
                    print(f" SUCESSO: Campo {field_id} encontrado e validado")
                    print(f"  Nome esperado: {expected_name}")
                    print(f"  Nome real: {field_data.get('name', '')}")
                    return field_id
                else:
                    print(f"Campo {field_id} existe mas nome não confere")
                    print(f"  Esperado: {expected_name}")
                    print(f"  Real: {field_data.get('name', '')}")
        
        # Fallback: procurar por palavras-chave
        print("\nUsando fallback - procurando por palavras-chave...")
        for field_id, field_data in search_options.items():
            field_name = field_data.get('name', '').lower()
            for keyword in tech_keywords:
                if keyword.lower() in field_name:
                    print(f" FALLBACK SUCESSO: Campo {field_id} encontrado")
                    print(f"  Palavra-chave: {keyword}")
                    print(f"  Nome do campo: {field_data.get('name', '')}")
                    return field_id
        
        print(" FALHA: Nenhum campo de técnico encontrado")
        return None
                
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
    result = debug_discover_tech_field()
    print(f"\nResultado final: {result}")
