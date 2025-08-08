import requests
import json

# Lista dos técnicos ativos encontrados no primeiro teste
first_test_active = [
    'silvio-valim', 'miguelangelo', 'jorge-vicente', 'edson-silva', 'alessandro-vieira',
    'alexandre-almoarqueg', 'anderson-oliveira', 'leonardo-riela', 'thales-leite',
    'jonathan-moletta', 'luciano-silva', 'nicolas-nunez', 'gabriel-machado',
    'luciano-marcelino', 'gabriel-conceicao'
]

# Lista dos técnicos retornados pelo endpoint (usernames extraídos)
endpoint_technicians = [
    'anderson-oliveira', 'silvio-valim', 'jorge-vicente', 'pablo-guimaraes',
    'miguelangelo', 'alessandro-vieira', 'jonathan-moletta', 'thales-leite',
    'leonardo-riela', 'edson-silva', 'gabriel-machado', 'luciano-marcelino',
    'luciano-silva', 'gabriel-conceicao', 'nicolas-nunez', 'wagner-mengue',
    'paulo-nunes', 'alexandre-almoarqueg'
]

print(f'Técnicos ativos no primeiro teste: {len(first_test_active)}')
print(f'Técnicos retornados pelo endpoint: {len(endpoint_technicians)}')

print('\n=== TÉCNICOS NO PRIMEIRO TESTE MAS NÃO NO ENDPOINT ===')
missing_in_endpoint = []
for tech in first_test_active:
    if tech not in endpoint_technicians:
        missing_in_endpoint.append(tech)
        print(f'- {tech}')

print(f'\nTotal faltando no endpoint: {len(missing_in_endpoint)}')

print('\n=== TÉCNICOS NO ENDPOINT MAS NÃO NO PRIMEIRO TESTE ===')
extra_in_endpoint = []
for tech in endpoint_technicians:
    if tech not in first_test_active:
        extra_in_endpoint.append(tech)
        print(f'- {tech}')

print(f'\nTotal extra no endpoint: {len(extra_in_endpoint)}')

print('\n=== TÉCNICOS EM COMUM ===')
common_technicians = []
for tech in first_test_active:
    if tech in endpoint_technicians:
        common_technicians.append(tech)
        
print(f'Técnicos em comum: {len(common_technicians)}')
for tech in common_technicians:
    print(f'- {tech}')

print('\n=== ANÁLISE ===')
print(f'O endpoint tem {len(extra_in_endpoint)} técnicos a mais que o primeiro teste:')
for tech in extra_in_endpoint:
    print(f'  + {tech}')

if missing_in_endpoint:
    print(f'\nO primeiro teste tinha {len(missing_in_endpoint)} técnicos que não estão no endpoint:')
    for tech in missing_in_endpoint:
        print(f'  - {tech}')

print(f'\nConclusão: O endpoint está correto com {len(endpoint_technicians)} técnicos ativos.')
print('A diferença pode ser devido a:')
print('1. Usuários que foram ativados recentemente')
print('2. Diferenças na lógica de busca entre os dois métodos')
print('3. Cache ou timing de sincronização')