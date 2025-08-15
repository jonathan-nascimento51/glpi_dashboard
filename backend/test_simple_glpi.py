import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("GLPI_URL")
app_token = os.getenv("GLPI_APP_TOKEN")
user_token = os.getenv("GLPI_USER_TOKEN")

print("=== TESTE SIMPLES GLPI ===")
print(f"URL: {url}")
print(f"App Token length: {len(app_token) if app_token else 0}")
print(f"User Token length: {len(user_token) if user_token else 0}")
print(f"App Token: {app_token[:10]}...{app_token[-5:] if len(app_token) > 15 else app_token}")
print(f"User Token: {user_token[:10]}...{user_token[-5:] if len(user_token) > 15 else user_token}")

headers = {
    "Content-Type": "application/json",
    "App-Token": app_token,
    "Authorization": f"user_token {user_token}"
}

print("\nTentando autenticaçáo...")
try:
    response = requests.get(f"{url}/initSession", headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        print(" AUTENTICAÇáO SUCESSO!")
    else:
        print(" AUTENTICAÇáO FALHOU!")
        
except Exception as e:
    print(f"Erro na requisiçáo: {e}")

