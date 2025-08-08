import requests
import json

response = requests.get('http://localhost:5000/api/technicians/ranking')

if response.ok:
    data = response.json()
    print(f'Tipo da resposta: {type(data)}')
    print(f'Conteúdo da resposta:')
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f'Erro: {response.status_code}')
    print(response.text)