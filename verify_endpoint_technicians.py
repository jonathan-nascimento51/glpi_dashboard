import requests
import json

# Fazer autenticação usando tokens
headers = {
    "Content-Type": "application/json",
    "App-Token": "c1U4Emxp0n7ClNDz7Kd2jSkcVB5gG4XFTLlnTm85",
    "Authorization": "user_token WPjwz02rLe4jLt3YzJrpJJTzQmIwIXkKFvDsJpEU",
}

login_response = requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/initSession', headers=headers)

if login_response.ok:
    session_token = login_response.json()['session_token']
    headers = {'Session-Token': session_token, 'App-Token': 'c1U4Emxp0n7ClNDz7Kd2jSkcVB5gG4XFTLlnTm85'}
    
    # Buscar técnicos do endpoint
    endpoint_response = requests.get('http://localhost:5000/api/technicians/ranking')
    
    if endpoint_response.ok:
        endpoint_data = endpoint_response.json()
        technicians_from_endpoint = endpoint_data.get('data', [])
        
        print(f'Verificando {len(technicians_from_endpoint)} técnicos do endpoint...')
        print('\n=== VERIFICAÇÃO DE STATUS DOS TÉCNICOS ===')
        
        active_count = 0
        inactive_count = 0
        deleted_count = 0
        error_count = 0
        
        for tech in technicians_from_endpoint:
            user_id = tech['id']
            name = tech['name']
            
            # Buscar dados completos do usuário
            user_detail_response = requests.get(
                f'http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/User/{user_id}',
                headers=headers
            )
            
            if user_detail_response.ok:
                user_data = user_detail_response.json()
                is_deleted = user_data.get('is_deleted', 0)
                is_active = user_data.get('is_active', 0)
                username = user_data.get('name', 'N/A')
                
                status = ''
                if is_deleted == 1:
                    status = '❌ DELETADO'
                    deleted_count += 1
                elif is_active == 0:
                    status = '⚠️  INATIVO'
                    inactive_count += 1
                else:
                    status = '✅ ATIVO'
                    active_count += 1
                
                print(f'{status} - {name} (ID: {user_id}, Username: {username})')
            else:
                print(f'❓ ERRO - {name} (ID: {user_id}) - Não foi possível verificar status')
                error_count += 1
        
        print(f'\n=== RESUMO ===')
        print(f'Total de técnicos no endpoint: {len(technicians_from_endpoint)}')
        print(f'Técnicos ativos: {active_count}')
        print(f'Técnicos inativos: {inactive_count}')
        print(f'Técnicos deletados: {deleted_count}')
        print(f'Erros na verificação: {error_count}')
        
        if inactive_count > 0 or deleted_count > 0:
            print(f'\n⚠️  PROBLEMA IDENTIFICADO: {inactive_count + deleted_count} técnicos não deveriam estar na lista!')
        else:
            print(f'\n✅ Todos os técnicos estão ativos e não deletados.')
    
    else:
        print(f'Erro ao buscar técnicos do endpoint: {endpoint_response.status_code}')
    
    # Logout
    requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/killSession', headers=headers)
else:
    print('Erro no login')
    print(f'Status: {login_response.status_code}')
    print(f'Resposta: {login_response.text}')