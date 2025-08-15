#!/usr/bin/env python3
"""
Script para debugar a descoberta do campo de técnico no GLPI
"""

import sys
sys.path.append('.')

from app.core.config import Config
from app.services.glpi_service import GLPIService

def main():
    print("=== Debug da Descoberta do Campo de Técnico ===")
    
    # Instanciar o serviço
    glpi_service = GLPIService(
        url=Config.GLPI_URL,
        app_token=Config.GLPI_APP_TOKEN,
        user_token=Config.GLPI_USER_TOKEN
    )
    
    print('Autenticando...')
    if not glpi_service.authenticate():
        print('Falha na autenticação!')
        return
    
    print('Autenticação bem-sucedida!')
    
    # Buscar opções de pesquisa
    print('\nBuscando opções de pesquisa...')
    search_options = glpi_service._get_search_options('Ticket')
    
    if not search_options:
        print('Nenhuma opção de pesquisa encontrada!')
        return
    
    print(f'Total de opções encontradas: {len(search_options)}')
    
    # Procurar campo 5 especificamente
    field_5 = search_options.get('5')
    if field_5:
        print(f'\nCampo 5 encontrado:')
        print(f'Nome: {field_5.get("name", "N/A")}')
        print(f'Tabela: {field_5.get("table", "N/A")}')
        print(f'Campo: {field_5.get("field", "N/A")}')
        print(f'Tipo: {field_5.get("datatype", "N/A")}')
    else:
        print('\nCampo 5 não encontrado!')
    
    # Buscar campos relacionados a técnico
    print('\n=== Campos relacionados a técnico ===')
    tech_related_fields = {}
    
    for field_id, field_info in search_options.items():
        field_name = field_info.get('name', '').lower()
        if any(term in field_name for term in ['técnico', 'tecnico', 'assigned', 'atribuído', 'atribuido']):
            tech_related_fields[field_id] = field_info
            print(f'Campo {field_id}: {field_info.get("name", "N/A")} (tabela: {field_info.get("table", "N/A")})')
    
    if not tech_related_fields:
        print('Nenhum campo relacionado a técnico encontrado!')
    
    # Testar o método _discover_tech_field_id
    print('\n=== Testando método _discover_tech_field_id ===')
    discovered_field_id = glpi_service._discover_tech_field_id()
    print(f'Field ID descoberto: {discovered_field_id}')
    
    # Listar primeiros 20 campos para referência
    print('\n=== Primeiros 20 campos (para referência) ===')
    for i, (key, value) in enumerate(search_options.items()):
        if i >= 20:
            break
        print(f'{key}: {value.get("name", "N/A")}')

if __name__ == '__main__':
    main()
