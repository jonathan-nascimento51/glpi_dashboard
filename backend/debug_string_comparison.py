#!/usr/bin/env python3
"""
Script para testar comparação de strings dos campos de técnico
"""

import sys
sys.path.append('.')

from app.services.glpi_service import GLPIService

def main():
    print("=== Teste de Comparação de Strings ===")
    
    # Instanciar o serviço
    glpi_service = GLPIService()
    
    print('Autenticando...')
    if not glpi_service.authenticate():
        print('Falha na autenticação!')
        return
    
    print('Autenticação bem-sucedida!')
    
    # Buscar opções de pesquisa
    print('\nBuscando opções de pesquisa...')
    try:
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/listSearchOptions/Ticket"
        )
        
        search_options = response.json()
        
        # Testar campos específicos
        field_5 = search_options.get('5')
        field_95 = search_options.get('95')
        
        print(f'\nCampo 5:')
        if field_5:
            field_name_5 = field_5.get('name', '')
            print(f'Nome real: "{field_name_5}"')
            print(f'Bytes: {field_name_5.encode("utf-8")}')
            print(f'Repr: {repr(field_name_5)}')
            
            # Testar comparações
            expected_names = ["Técnico", "Tecnico", "técnico", "tecnico"]
            for expected in expected_names:
                print(f'  "{field_name_5}" == "{expected}": {field_name_5 == expected}')
                print(f'  "{field_name_5.lower()}" == "{expected.lower()}": {field_name_5.lower() == expected.lower()}')
        
        print(f'\nCampo 95:')
        if field_95:
            field_name_95 = field_95.get('name', '')
            print(f'Nome real: "{field_name_95}"')
            print(f'Bytes: {field_name_95.encode("utf-8")}')
            print(f'Repr: {repr(field_name_95)}')
            
            # Testar comparações
            expected_names = ["Técnico encarregado", "Tecnico encarregado"]
            for expected in expected_names:
                print(f'  "{field_name_95}" == "{expected}": {field_name_95 == expected}')
                print(f'  "{field_name_95.lower()}" == "{expected.lower()}": {field_name_95.lower() == expected.lower()}')
        
        # Testar o mapeamento atual
        print(f'\n=== Testando Mapeamento Atual ===')
        tech_field_mapping = {
            "5": "Técnico",
            "95": "Técnico encarregado"
        }
        
        for field_id, expected_name in tech_field_mapping.items():
            if field_id in search_options:
                field_data = search_options[field_id]
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    match = field_name == expected_name
                    print(f'Campo {field_id}: "{field_name}" == "{expected_name}" -> {match}')
                    
                    # Testar comparação case-insensitive
                    match_lower = field_name.lower() == expected_name.lower()
                    print(f'Campo {field_id} (lower): "{field_name.lower()}" == "{expected_name.lower()}" -> {match_lower}')
                    
                    # Testar se contém
                    contains = expected_name.lower() in field_name.lower()
                    print(f'Campo {field_id} (contains): "{expected_name.lower()}" in "{field_name.lower()}" -> {contains}')
                    
    except Exception as e:
        print(f'Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
