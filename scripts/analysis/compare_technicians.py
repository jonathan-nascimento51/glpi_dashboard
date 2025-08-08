#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Lista dos 19 técnicos ativos que encontramos no teste anterior
active_technicians_expected = [
    'miguelangelo', 'jorge-vicente', 'edson-silva', 'alessandro-vieira',
    'alexandre-almoarqueg', 'anderson-oliveira', 'leonardo-riela',
    'thales-leite', 'jonathan-moletta', 'luciano-silva',
    'nicolas-nunez', 'gabriel-machado', 'luciano-marcelino',
    'gabriel-conceicao'
]

# Buscar técnicos do endpoint
response = requests.get('http://localhost:5000/api/technicians/ranking')

if response.ok:
    data = response.json()
    technicians_from_endpoint = data.get('data', [])
    
    print(f'Técnicos esperados (ativos): {len(active_technicians_expected)}')
    print(f'Técnicos retornados pelo endpoint: {len(technicians_from_endpoint)}')
    
    # Extrair nomes dos técnicos do endpoint
    endpoint_names = []
    endpoint_ids = []
    for tech in technicians_from_endpoint:
        endpoint_names.append(tech['name'])
        endpoint_ids.append(tech['id'])
    
    print('\nTécnicos retornados pelo endpoint:')
    for i, tech in enumerate(technicians_from_endpoint):
        print(f'{i+1}. {tech["name"]} (ID: {tech["id"]})')
    
    # Verificar quais técnicos esperados não estão no endpoint
    print('\n=== ANÁLISE ===')
    print('\nTécnicos que deveriam estar mas não estão no endpoint:')
    missing_count = 0
    for expected in active_technicians_expected:
        found = False
        for tech in technicians_from_endpoint:
            # Verificar se o nome contém partes do username esperado
            if expected.replace('-', ' ').lower() in tech['name'].lower():
                found = True
                break
        if not found:
            print(f'- {expected}')
            missing_count += 1
    
    print(f'\nTotal de técnicos faltando: {missing_count}')
    
    # Verificar se há técnicos no endpoint que não deveriam estar
    print('\nTécnicos no endpoint que podem não ser ativos:')
    suspicious_count = 0
    for tech in technicians_from_endpoint:
        found = False
        for expected in active_technicians_expected:
            if expected.replace('-', ' ').lower() in tech['name'].lower():
                found = True
                break
        if not found:
            print(f'- {tech["name"]} (ID: {tech["id"]})')
            suspicious_count += 1
    
    print(f'\nTotal de técnicos suspeitos: {suspicious_count}')
    
else:
    print(f'Erro: {response.status_code}')
    print(response.text)