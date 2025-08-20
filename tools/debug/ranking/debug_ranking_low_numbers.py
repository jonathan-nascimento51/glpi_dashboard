#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar por que o ranking de técnicos está retornando números muito baixos.
Este script irá:
1. Testar a busca de técnicos com perfil ID 6
2. Verificar se os técnicos estão sendo encontrados corretamente
3. Testar a contagem de tickets para técnicos específicos
4. Comparar diferentes métodos de contagem
5. Investigar possíveis problemas na lógica de ranking
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def test_profile_user_search(service):
    """Testa a busca de usuários com perfil de técnico (ID 6)"""
    print("\n=== TESTE 1: BUSCA DE PROFILE_USER (PERFIL 6) ===")

    try:
        # Parâmetros para buscar usuários com perfil de técnico
        profile_params = {
            "range": "0-999",
            "criteria[0][field]": "4",  # profiles_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",  # Perfil de técnico
            "forcedisplay[0]": "3",  # entities_id
            "forcedisplay[1]": "4",  # profiles_id
            "forcedisplay[2]": "5",  # users_id (username)
        }

        print(f"Buscando usuários com perfil ID 6...")
        print(f"Parâmetros: {profile_params}")

        response = service._make_authenticated_request("GET", f"{service.glpi_url}/search/Profile_User", params=profile_params)

        if response and response.ok:
            result = response.json()
            total_count = result.get("totalcount", 0)
            data = result.get("data", [])

            print(f"✅ Encontrados {total_count} registros de Profile_User")
            print(f"✅ Dados retornados: {len(data)} registros")

            # Mostrar alguns exemplos
            print("\n📋 Primeiros 5 registros:")
            for i, record in enumerate(data[:5]):
                print(f"  {i+1}. {record}")

            # Extrair usernames únicos
            usernames = set()
            for record in data:
                if isinstance(record, dict) and "5" in record:
                    usernames.add(str(record["5"]))

            print(f"\n📊 Total de usernames únicos: {len(usernames)}")
            print(f"📊 Primeiros 10 usernames: {list(usernames)[:10]}")

            return list(usernames)
        else:
            print(f"❌ Erro na busca: {response.status_code if response else 'No response'}")
            return []

    except Exception as e:
        print(f"❌ Erro na busca de Profile_User: {e}")
        import traceback

        traceback.print_exc()
        return []


def test_active_users_search(service):
    """Testa a busca de usuários ativos"""
    print("\n=== TESTE 2: BUSCA DE USUÁRIOS ATIVOS ===")

    try:
        # Parâmetros para buscar usuários ativos
        user_params = {
            "range": "0-999",
            "criteria[0][field]": "8",  # is_active
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "1",
            "criteria[1][field]": "23",  # is_deleted
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": "0",
            "forcedisplay[0]": "1",  # name (username)
            "forcedisplay[1]": "2",  # id
            "forcedisplay[2]": "34",  # firstname
            "forcedisplay[3]": "9",  # realname
        }

        print(f"Buscando usuários ativos...")
        print(f"Parâmetros: {user_params}")

        response = service._make_authenticated_request("GET", f"{service.glpi_url}/search/User", params=user_params)

        if response and response.ok:
            result = response.json()
            total_count = result.get("totalcount", 0)
            data = result.get("data", [])

            print(f"✅ Encontrados {total_count} usuários ativos")
            print(f"✅ Dados retornados: {len(data)} registros")

            # Criar mapa de usuários ativos
            active_users = {}
            for user in data:
                if isinstance(user, dict) and "1" in user:
                    username = str(user["1"])
                    active_users[username] = {
                        "id": user.get("2", ""),
                        "firstname": user.get("34", ""),
                        "realname": user.get("9", ""),
                        "username": username,
                    }

            print(f"\n📊 Total de usuários ativos mapeados: {len(active_users)}")
            print(f"📊 Primeiros 5 usuários ativos:")
            for i, (username, user_data) in enumerate(list(active_users.items())[:5]):
                print(f"  {i+1}. {username}: {user_data}")

            return active_users
        else:
            print(f"❌ Erro na busca: {response.status_code if response else 'No response'}")
            return {}

    except Exception as e:
        print(f"❌ Erro na busca de usuários ativos: {e}")
        import traceback

        traceback.print_exc()
        return {}


def test_technician_intersection(tech_usernames, active_users):
    """Testa a interseção entre técnicos e usuários ativos"""
    print("\n=== TESTE 3: INTERSEÇÃO TÉCNICOS x USUÁRIOS ATIVOS ===")

    print(f"📊 Total de técnicos (perfil 6): {len(tech_usernames)}")
    print(f"📊 Total de usuários ativos: {len(active_users)}")

    # Encontrar técnicos que estão ativos
    active_technicians = []
    inactive_technicians = []

    for username in tech_usernames:
        if username in active_users:
            active_technicians.append(username)
        else:
            inactive_technicians.append(username)

    print(f"\n✅ Técnicos ativos: {len(active_technicians)}")
    print(f"❌ Técnicos inativos/deletados: {len(inactive_technicians)}")

    if active_technicians:
        print(f"\n📋 Primeiros 10 técnicos ativos:")
        for i, username in enumerate(active_technicians[:10]):
            user_data = active_users[username]
            name = f"{user_data.get('firstname', '')} {user_data.get('realname', '')}".strip()
            print(f"  {i+1}. {username} -> {name} (ID: {user_data.get('id', 'N/A')})")

    if inactive_technicians:
        print(f"\n📋 Primeiros 10 técnicos inativos:")
        for i, username in enumerate(inactive_technicians[:10]):
            print(f"  {i+1}. {username}")

    return active_technicians


def test_ticket_counting_sample(service, active_technicians):
    """Testa contagem de tickets para uma amostra de técnicos"""
    print("\n=== TESTE 4: CONTAGEM DE TICKETS (AMOSTRA) ===")

    if not active_technicians:
        print("❌ Nenhum técnico ativo para testar")
        return

    # Testar apenas os primeiros 5 técnicos para não sobrecarregar
    sample_technicians = active_technicians[:5]
    print(f"🎫 Testando contagem de tickets para {len(sample_technicians)} técnicos")

    # Descobrir field ID do técnico
    tech_field_id = service._discover_tech_field_id()
    if not tech_field_id:
        print("❌ Não foi possível descobrir o field ID do técnico")
        return

    print(f"✅ Field ID do técnico: {tech_field_id}")

    # Buscar dados dos usuários para obter IDs
    active_users = test_active_users_search(service)

    total_tickets_found = 0
    successful_counts = 0

    for username in sample_technicians:
        try:
            if username not in active_users:
                print(f"❌ {username}: Não encontrado nos usuários ativos")
                continue

            user_data = active_users[username]
            user_id = user_data.get("id")

            if not user_id:
                print(f"❌ {username}: ID não encontrado")
                continue

            name = f"{user_data.get('firstname', '')} {user_data.get('realname', '')}".strip()
            print(f"\n🔍 Testando {username} ({name}) - ID: {user_id}")

            # Método 1: Usar o método otimizado
            try:
                count1 = service._count_tickets_by_technician_optimized(int(user_id), tech_field_id)
                print(f"  Método otimizado: {count1} tickets")
                if count1 and count1 > 0:
                    total_tickets_found += count1
                    successful_counts += 1
            except Exception as e:
                print(f"  ❌ Erro no método otimizado: {e}")

            # Método 2: Busca direta com campo 4 (users_id_tech)
            try:
                response = service._make_authenticated_request(
                    "GET",
                    f"{service.glpi_url}/search/Ticket",
                    params={
                        "criteria[0][field]": "4",  # users_id_tech
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id),
                        "range": "0-0",  # Apenas contagem
                    },
                )

                if response and response.ok:
                    if "Content-Range" in response.headers:
                        content_range = response.headers["Content-Range"]
                        if "/" in content_range:
                            count2 = int(content_range.split("/")[-1])
                            print(f"  Busca direta (campo 4): {count2} tickets")
                    else:
                        result = response.json()
                        count2 = result.get("totalcount", 0)
                        print(f"  Busca direta (JSON): {count2} tickets")
                else:
                    print(f"  ❌ Erro na busca direta: {response.status_code if response else 'No response'}")
            except Exception as e:
                print(f"  ❌ Erro na busca direta: {e}")

            # Método 3: Busca com campo 5 (users_id_assign)
            try:
                response = service._make_authenticated_request(
                    "GET",
                    f"{service.glpi_url}/search/Ticket",
                    params={
                        "criteria[0][field]": "5",  # users_id_assign
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id),
                        "range": "0-0",  # Apenas contagem
                    },
                )

                if response and response.ok:
                    if "Content-Range" in response.headers:
                        content_range = response.headers["Content-Range"]
                        if "/" in content_range:
                            count3 = int(content_range.split("/")[-1])
                            print(f"  Busca campo 5 (assign): {count3} tickets")
                    else:
                        result = response.json()
                        count3 = result.get("totalcount", 0)
                        print(f"  Busca campo 5 (JSON): {count3} tickets")
                else:
                    print(f"  ❌ Erro na busca campo 5: {response.status_code if response else 'No response'}")
            except Exception as e:
                print(f"  ❌ Erro na busca campo 5: {e}")

        except Exception as e:
            print(f"❌ Erro ao processar {username}: {e}")

    print(f"\n📊 RESUMO DA AMOSTRA:")
    print(f"  Técnicos testados: {len(sample_technicians)}")
    print(f"  Contagens bem-sucedidas: {successful_counts}")
    print(f"  Total de tickets encontrados: {total_tickets_found}")
    if successful_counts > 0:
        print(f"  Média de tickets por técnico: {total_tickets_found / successful_counts:.1f}")


def test_full_ranking_method(service):
    """Testa o método completo de ranking"""
    print("\n=== TESTE 5: MÉTODO COMPLETO DE RANKING ===")

    try:
        print("🔄 Executando get_technician_ranking()...")
        ranking = service.get_technician_ranking()

        print(f"✅ Ranking retornado: {len(ranking)} técnicos")

        if ranking:
            print(f"\n📊 Top 10 técnicos no ranking:")
            for i, tech in enumerate(ranking[:10]):
                print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets - {tech.get('level', 'N/A')}")

            # Estatísticas por nível
            by_level = {}
            total_tickets = 0
            for tech in ranking:
                level = tech.get("level", "N/A")
                tickets = tech.get("total", 0)

                if level not in by_level:
                    by_level[level] = {"count": 0, "tickets": 0}

                by_level[level]["count"] += 1
                by_level[level]["tickets"] += tickets
                total_tickets += tickets

            print(f"\n📊 Estatísticas por nível:")
            for level, stats in by_level.items():
                print(f"  {level}: {stats['count']} técnicos, {stats['tickets']} tickets total")

            print(f"\n📊 Total geral: {len(ranking)} técnicos, {total_tickets} tickets")
        else:
            print("❌ Ranking vazio retornado")

    except Exception as e:
        print(f"❌ Erro ao executar ranking completo: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Função principal"""
    print("🔍 INVESTIGAÇÃO: RANKING DE TÉCNICOS COM NÚMEROS BAIXOS")
    print("=" * 60)

    try:
        # Inicializar serviço
        service = GLPIService()

        if not service.authenticate():
            print("❌ Falha na autenticação")
            return

        print("✅ Autenticação bem-sucedida")

        # Teste 1: Buscar técnicos com perfil ID 6
        tech_usernames = test_profile_user_search(service)

        # Teste 2: Buscar usuários ativos
        active_users = test_active_users_search(service)

        # Teste 3: Interseção
        active_technicians = test_technician_intersection(tech_usernames, active_users)

        # Teste 4: Contagem de tickets (amostra)
        test_ticket_counting_sample(service, active_technicians)

        # Teste 5: Método completo
        test_full_ranking_method(service)

        print("\n" + "=" * 60)
        print("🏁 INVESTIGAÇÃO CONCLUÍDA")

        # Análise final
        print("\n📋 ANÁLISE DOS RESULTADOS:")
        print(f"  1. Técnicos com perfil 6: {len(tech_usernames)}")
        print(f"  2. Usuários ativos: {len(active_users)}")
        print(f"  3. Técnicos ativos: {len(active_technicians) if active_technicians else 0}")

        if len(active_technicians) < 50:
            print("\n⚠️  PROBLEMA IDENTIFICADO: Muito poucos técnicos ativos encontrados!")
            print("   Possíveis causas:")
            print("   - Perfil ID 6 pode não ser o correto para técnicos")
            print("   - Muitos técnicos podem estar marcados como inativos")
            print("   - Problema na lógica de interseção")

        if len(tech_usernames) == 0:
            print("\n⚠️  PROBLEMA CRÍTICO: Nenhum técnico encontrado com perfil ID 6!")
            print("   Recomendação: Verificar qual é o perfil correto para técnicos")

    except Exception as e:
        print(f"❌ Erro na investigação: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
