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
    
    # Buscar Profile_User com perfil ID 6 (técnico)
    params = {
        'range': '0-100',
        'criteria[0][field]': '4',
        'criteria[0][searchtype]': 'equals', 
        'criteria[0][value]': '6',
        'forcedisplay[0]': '2',
        'forcedisplay[1]': '5'
    }
    
    response = requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/search/Profile_User', params=params, headers=headers)
    if response.ok:
        data = response.json()
        profile_data = data.get('data', [])
        print(f'Total de Profile_User com perfil 6: {data.get("totalcount", 0)}')
        
        # Extrair usernames dos técnicos
        tech_usernames = []
        for profile_user in profile_data:
            if isinstance(profile_user, dict) and "5" in profile_user:
                username = str(profile_user["5"])
                tech_usernames.append(username)
        
        print(f'Usernames de técnicos encontrados: {len(tech_usernames)}')
        
        # Buscar usuários ativos
        user_params = {
            'range': '0-999',
            'criteria[0][field]': '8',  # Campo is_active
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': '1',
            'forcedisplay[0]': '2',  # ID
            'forcedisplay[1]': '1',  # Nome de usuário
        }
        
        user_response = requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/search/User', params=user_params, headers=headers)
        if user_response.ok:
            user_result = user_response.json()
            all_users = user_result.get('data', [])
            print(f'Total de usuários ativos: {len(all_users)}')
            
            # Verificar quais técnicos estão ativos e não deletados
            active_tech_count = 0
            deleted_tech_count = 0
            inactive_tech_count = 0
            
            for username in tech_usernames:
                # Buscar o usuário específico para verificar is_deleted
                user_found = False
                user_id = None
                
                # Encontrar o ID do usuário
                for user in all_users:
                    if isinstance(user, dict) and "1" in user:
                        if str(user["1"]) == username:
                            user_id = str(user["2"])
                            user_found = True
                            break
                
                if user_found and user_id:
                    # Buscar dados completos do usuário
                    user_detail_response = requests.get(
                        f'http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/User/{user_id}',
                        headers=headers
                    )
                    
                    if user_detail_response.ok:
                        user_data = user_detail_response.json()
                        is_deleted = user_data.get('is_deleted', 0)
                        is_active = user_data.get('is_active', 0)
                        
                        if is_deleted == 0 and is_active == 1:
                            active_tech_count += 1
                            print(f'✓ {username} - Ativo e não deletado')
                        elif is_deleted == 1:
                            deleted_tech_count += 1
                            print(f'✗ {username} - Deletado')
                        elif is_active == 0:
                            inactive_tech_count += 1
                            print(f'✗ {username} - Inativo')
                else:
                    print(f'? {username} - Não encontrado nos usuários ativos')
            
            print(f'\nResumo:')
            print(f'Total de técnicos: {len(tech_usernames)}')
            print(f'Técnicos ativos e não deletados: {active_tech_count}')
            print(f'Técnicos deletados: {deleted_tech_count}')
            print(f'Técnicos inativos: {inactive_tech_count}')
            print(f'Técnicos não encontrados: {len(tech_usernames) - active_tech_count - deleted_tech_count - inactive_tech_count}')
        else:
            print(f'Erro na busca de usuários: {user_response.status_code}')
    else:
        print(f'Erro na busca de Profile_User: {response.status_code}')
        
    # Logout
    requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/killSession', headers=headers)
else:
    print('Erro no login')
    print(f'Status: {login_response.status_code}')
    print(f'Resposta: {login_response.text}')