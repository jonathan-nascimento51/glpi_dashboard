import json

from services.glpi_service import GLPIService

service = GLPIService()
service._ensure_authenticated()

# Primeiro, vamos buscar o Profile_User específico pelo ID para ver o users_id
print("=== BUSCANDO PROFILE_USER PELO ID ===")
profile_id = 709  # ID do primeiro técnico
profile_detail_response = service._make_authenticated_request("GET", f"{service.glpi_url}/Profile_User/{profile_id}")

if profile_detail_response.ok:
    profile_detail = profile_detail_response.json()
    user_id = profile_detail.get("users_id")
    print(f"Profile_User ID: {profile_id}")
    print(f"users_id: {user_id}")
else:
    print("Erro ao buscar Profile_User:", profile_detail_response.status_code)
    exit()

# Agora vamos buscar com vários campos para encontrar qual contém o users_id
print("\n=== TESTANDO CAMPOS NA BUSCA ===")
for field_range in [range(1, 11), range(11, 21), range(21, 31)]:
    forcedisplay_params = {}
    for i, field_num in enumerate(field_range):
        forcedisplay_params[f"forcedisplay[{i}]"] = str(field_num)

    params = {
        "range": "0-1",
        "criteria[0][field]": "4",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
    }
    params.update(forcedisplay_params)

    response = service._make_authenticated_request("GET", f"{service.glpi_url}/search/Profile_User", params=params)

    if response.ok:
        data = response.json()
        if data.get("data"):
            item = data["data"][0]
            print(f"\nCampos {field_range.start}-{field_range.stop-1}:")
            for key, value in item.items():
                if str(value) == str(user_id):  # Encontrou o campo que contém o users_id
                    print(f"*** ENCONTRADO! Campo {key} = {value} (users_id) ***")
                else:
                    print(f"Campo {key}: {value}")
    else:
        print(f"Erro na busca campos {field_range.start}-{field_range.stop-1}: {response.status_code}")
