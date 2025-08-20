import json

from services.glpi_service import GLPIService

service = GLPIService()
service._ensure_authenticated()

print("=== DEBUG RANKING STEP BY STEP ===")

# 1. Buscar Profile_User
print("1. Buscando Profile_User...")
profile_response = service._make_authenticated_request(
    "GET",
    f"{service.glpi_url}/search/Profile_User",
    params={
        "range": "0-5",  # Limitar para debug
        "criteria[0][field]": "4",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "forcedisplay[0]": "2",
    },
)

if profile_response.ok:
    profile_data = profile_response.json()
    print(f'Profile_Users encontrados: {profile_data.get("totalcount", 0)}')

    # 2. Extrair users_id
    print("\n2. Extraindo users_id...")
    technician_ids = []
    for item in profile_data["data"][:3]:  # Processar apenas 3 para debug
        profile_user_id = item["2"]
        print(f"Profile_User ID: {profile_user_id}")

        # Buscar detalhes
        detail_response = service._make_authenticated_request("GET", f"{service.glpi_url}/Profile_User/{profile_user_id}")

        if detail_response.ok:
            detail_data = detail_response.json()
            user_id = detail_data.get("users_id")
            print(f"  -> users_id: {user_id}")
            technician_ids.append(str(user_id))
        else:
            print(f"  -> Erro: {detail_response.status_code}")

    print(f"\nIDs dos técnicos extraídos: {technician_ids}")

    # 3. Para cada técnico, verificar nome e contagem
    print("\n3. Verificando dados dos técnicos...")
    ranking = []

    for tech_id in technician_ids:
        print(f"\nProcessando técnico {tech_id}:")

        # Obter nome
        tech_name = service._get_technician_name(tech_id)
        print(f"  Nome: {tech_name}")

        # Contar tickets
        ticket_count = service._count_tickets_with_date_filter(tech_id, "2024-12-01", "2024-12-31")
        print(f"  Tickets: {ticket_count}")

        # Obter nível
        try:
            tech_id_int = int(tech_id)
            tech_level = service._get_technician_level(tech_id_int, ticket_count)
        except (ValueError, TypeError):
            tech_level = service._get_technician_level_by_name(tech_name)
        print(f"  Nível: {tech_level}")

        ranking.append(
            {
                "id": tech_id,
                "name": tech_name,
                "total": ticket_count if ticket_count is not None else 0,
                "level": tech_level,
                "rank": 0,
            }
        )

    print(f"\n4. Ranking antes da ordenação:")
    for tech in ranking:
        print(f'  {tech["name"]}: {tech["total"]} tickets (nível {tech["level"]})')

    # 5. Ordenar
    ranking.sort(key=lambda x: x["total"], reverse=True)

    print(f"\n5. Ranking após ordenação:")
    for i, tech in enumerate(ranking):
        tech["rank"] = i + 1
        print(f'  {i+1}. {tech["name"]}: {tech["total"]} tickets (nível {tech["level"]})')

    print(f"\n6. Resultado final:")
    print(json.dumps(ranking, indent=2, ensure_ascii=False))

else:
    print(f"Erro na busca Profile_User: {profile_response.status_code}")
