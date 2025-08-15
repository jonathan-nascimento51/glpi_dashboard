#!/usr/bin/env python3
"""
Script para testar especificamente o método _discover_tech_field_id
"""

import sys
sys.path.append('.')

from app.services.glpi_service import GLPIService

def main():
    print("=== Teste Específico do Método _discover_tech_field_id ===")
    
    # Instanciar o serviço
    glpi_service = GLPIService()
    
    print('Autenticando...')
    if not glpi_service.authenticate():
        print('Falha na autenticação!')
        return
    
    print('Autenticação bem-sucedida!')
    
    # Buscar opções de pesquisa manualmente
    print('\nBuscando opções de pesquisa...')
    try:
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/listSearchOptions/Ticket"
        )
        
        search_options = response.json()
        
        # Simular exatamente o que o método faz
        print('\n=== Simulando o método _discover_tech_field_id ===')
        
        # Mapeamento exato do método
        tech_field_mapping = {
            "5": "Técnico",
            "95": "Técnico encarregado"
        }
        
        print(f'Mapeamento usado: {tech_field_mapping}')
        
        # Primeiro loop: campos conhecidos
        print('\n--- Testando campos conhecidos ---')
        for field_id, expected_name in tech_field_mapping.items():
            print(f'\nTestando campo {field_id}:')
            print(f'  Nome esperado: "{expected_name}"')
            
            if field_id in search_options:
                field_data = search_options[field_id]
                print(f'  Campo encontrado: {field_data}')
                
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    print(f'  Nome real: "{field_name}"')
                    print(f'  Tipo do nome real: {type(field_name)}')
                    print(f'  Tipo do nome esperado: {type(expected_name)}')
                    
                    # Teste de igualdade
                    is_equal = field_name == expected_name
                    print(f'  "{field_name}" == "{expected_name}": {is_equal}')
                    
                    # Teste byte a byte
                    print(f'  Bytes nome real: {field_name.encode("utf-8")}')
                    print(f'  Bytes nome esperado: {expected_name.encode("utf-8")}')
                    
                    if is_equal:
                        print(f'   MATCH! Campo {field_id} encontrado!')
                        return field_id
                    else:
                        print(f'   Não match')
                else:
                    print(f'   Campo não é dict ou não tem "name"')
            else:
                print(f'   Campo {field_id} não existe em search_options')
        
        # Segundo loop: fallback
        print('\n--- Testando fallback ---')
        tech_field_names = ["Técnico", "Atribuído", "Assigned to", "Technician", "Técnico encarregado"]
        print(f'Nomes de fallback: {tech_field_names}')
        
        for field_id, field_data in search_options.items():
            if isinstance(field_data, dict) and "name" in field_data:
                field_name = field_data["name"]
                if field_name in tech_field_names:
                    print(f'   FALLBACK MATCH! Campo {field_id}: "{field_name}"')
                    return field_id
        
        print('\n Nenhum campo encontrado!')
        return None
                    
    except Exception as e:
        print(f'Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    result = main()
    print(f'\nResultado final: {result}')
