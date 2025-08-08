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
        'range': '0-50',
        'criteria[0][field]': '4',
        'criteria[0][searchtype]': 'equals', 
        'criteria[0][value]': '6',
        'forcedisplay[0]': '2',
        'forcedisplay[1]': '5'
    }
    
    response = requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/search/Profile_User', params=params, headers=headers)
    if response.ok:
        data = response.json()
        print(f'Total de Profile_User com perfil 6: {data.get("totalcount", 0)}')
        print('Primeiros 10 registros:')
        for i, item in enumerate(data.get('data', [])[:10]):
            print(f'{i+1}: {item}')
    else:
        print(f'Erro na busca: {response.status_code}')
        print(f'Resposta: {response.text}')
        
    # Logout
    requests.get('http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/killSession', headers=headers)
else:
    print('Erro no login')
    print(f'Status: {login_response.status_code}')
    print(f'Resposta: {login_response.text}')