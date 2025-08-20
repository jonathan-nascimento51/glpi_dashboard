import json
from collections import Counter

from services.glpi_service import GLPIService

service = GLPIService()
service._ensure_authenticated()

print("=== DEBUG DUPLICATAS NO RANKING ===")

# 1. Buscar todos os Profile_User
print("1. Buscando todos os Profile_User...")
profile_response = service._make_authenticated_request(
    "GET",
    f"{service.glpi_url}/search/Profile_User",
    params={
        "range": "0-99",
        "criteria[0][field]": "4",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "forcedisplay[0]": "2",
    },
)

if profile_response.ok:
    profile_data = profile_response.json()
    print(f'Total Profile_Users encontrados: {profile_data.get("totalcount", 0)}')

    # 2. Extrair users_id e verificar duplicatas
    print("\n2. Extraindo users_id...")
    profile_user_ids = []
    users_ids = []

    for item in profile_data["data"]:
        profile_user_id = item["2"]
        profile_user_ids.append(profile_user_id)

        # Buscar detalhes
        detail_response = service._make_authenticated_request("GET", f"{service.glpi_url}/Profile_User/{profile_user_id}")

        if detail_response.ok:
            detail_data = detail_response.json()
            user_id = detail_data.get("users_id")
            if user_id:
                users_ids.append(str(user_id))
                print(f"Profile_User {profile_user_id} -> users_id {user_id}")

    # 3. Verificar duplicatas
    print("\n3. Análise de duplicatas:")
    profile_counter = Counter(profile_user_ids)
    users_counter = Counter(users_ids)

    print(f"Profile_User IDs únicos: {len(set(profile_user_ids))}")
    print(f"Profile_User IDs totais: {len(profile_user_ids)}")
    print(f"users_id únicos: {len(set(users_ids))}")
    print(f"users_id totais: {len(users_ids)}")

    # Mostrar duplicatas de Profile_User
    profile_duplicates = {k: v for k, v in profile_counter.items() if v > 1}
    if profile_duplicates:
        print(f"\nProfile_User duplicados: {profile_duplicates}")
    else:
        print("\nNenhum Profile_User duplicado encontrado")

    # Mostrar duplicatas de users_id
    users_duplicates = {k: v for k, v in users_counter.items() if v > 1}
    if users_duplicates:
        print(f"\nusers_id duplicados: {users_duplicates}")

        # Para cada users_id duplicado, mostrar quais Profile_User o referenciam
        for user_id, count in users_duplicates.items():
            print(f"\nusers_id {user_id} aparece {count} vezes:")
            for item in profile_data["data"]:
                profile_user_id = item["2"]
                detail_response = service._make_authenticated_request(
                    "GET", f"{service.glpi_url}/Profile_User/{profile_user_id}"
                )
                if detail_response.ok:
                    detail_data = detail_response.json()
                    if str(detail_data.get("users_id")) == user_id:
                        print(f"  - Profile_User {profile_user_id}")
    else:
        print("\nNenhum users_id duplicado encontrado")

    # 4. Simular o processo de ranking para ver onde as duplicatas aparecem
    print("\n4. Simulando processo de ranking...")
    unique_users_ids = list(set(users_ids))
    print(f"IDs únicos para ranking: {unique_users_ids[:10]}...")

else:
    print(f"Erro na busca Profile_User: {profile_response.status_code}")
