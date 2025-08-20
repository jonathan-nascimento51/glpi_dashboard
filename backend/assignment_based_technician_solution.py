#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução final baseada em atribuições de tickets para identificar técnicos
Esta abordagem contorna as limitações dos grupos N1-N4 vazios
"""

import json
import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def get_technicians_by_assignments(service, days_back=30, min_tickets=3):
    """
    Identifica técnicos baseado em atribuições de tickets recentes

    Args:
        service: Instância do GLPIService
        days_back: Número de dias para buscar no histórico
        min_tickets: Número mínimo de tickets para considerar como técnico

    Returns:
        dict: Dicionário com técnicos identificados
    """
    print(f"🔍 Identificando técnicos por atribuições (últimos {days_back} dias, mín. {min_tickets} tickets)")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    try:
        # Buscar tickets com atribuições no período
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Ticket",
            params={
                "range": "0-999",
                "criteria[0][field]": "15",  # date
                "criteria[0][searchtype]": "morethan",
                "criteria[0][value]": start_date.strftime("%Y-%m-%d"),
                "criteria[1][field]": "5",  # users_id_tech
                "criteria[1][searchtype]": "contains",
                "criteria[1][value]": "",
                "criteria[1][link]": "AND",
                "forcedisplay[0]": "2",  # id
                "forcedisplay[1]": "5",  # users_id_tech
                "forcedisplay[2]": "15",  # date
                "forcedisplay[3]": "12",  # status
            },
        )

        if not response or not response.ok:
            print(f"❌ Falha ao buscar tickets: {response.status_code if response else 'Sem resposta'}")
            return {}

        data = response.json()

        if not data or not data.get("data"):
            print("❌ Nenhum ticket encontrado")
            return {}

        print(f"✅ {len(data['data'])} tickets encontrados no período")

        # Contar atribuições por técnico
        tech_counts = {}
        for ticket in data["data"]:
            tech_id = str(ticket.get("5", "")) if ticket.get("5") else None
            if tech_id and tech_id != "0":
                tech_counts[tech_id] = tech_counts.get(tech_id, 0) + 1

        print(f"📊 {len(tech_counts)} técnicos únicos com atribuições")

        # Filtrar técnicos com mínimo de tickets e obter dados
        technicians = {}
        for tech_id, count in tech_counts.items():
            if count >= min_tickets:
                try:
                    user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{tech_id}")

                    if user_response and user_response.ok:
                        user_data = user_response.json()

                        # Verificar se usuário está ativo
                        if user_data.get("is_active") == 1 and user_data.get("is_deleted") != 1:
                            firstname = (user_data.get("firstname") or "").strip()
                            realname = (user_data.get("realname") or "").strip()
                            username = (user_data.get("name") or "").strip()

                            if firstname and realname:
                                full_name = f"{firstname} {realname}"
                            elif realname:
                                full_name = realname
                            elif firstname:
                                full_name = firstname
                            elif username:
                                full_name = username
                            else:
                                full_name = f"Técnico {tech_id}"

                            # Determinar nível baseado na quantidade de tickets
                            if count >= 20:
                                level = "N4"  # Especialista
                            elif count >= 15:
                                level = "N3"  # Sênior
                            elif count >= 8:
                                level = "N2"  # Pleno
                            else:
                                level = "N1"  # Júnior

                            technicians[tech_id] = {
                                "id": tech_id,
                                "name": full_name,
                                "username": username,
                                "level": level,
                                "ticket_count": count,
                                "is_active": True,
                            }

                except Exception as e:
                    print(f"⚠️ Erro ao obter dados do técnico {tech_id}: {e}")

        print(f"✅ {len(technicians)} técnicos ativos identificados")

        # Mostrar resumo por nível
        level_counts = {}
        for tech in technicians.values():
            level = tech["level"]
            level_counts[level] = level_counts.get(level, 0) + 1

        print("\n📊 Distribuição por nível:")
        for level in ["N1", "N2", "N3", "N4"]:
            count = level_counts.get(level, 0)
            print(f"   {level}: {count} técnicos")

        return technicians

    except Exception as e:
        print(f"❌ Erro na identificação de técnicos: {e}")
        return {}


def test_ticket_counting_with_date_filter(service, technicians, start_date, end_date):
    """
    Testa a contagem de tickets com filtro de data para os técnicos identificados
    """
    print(f"\n=== TESTE DE CONTAGEM COM FILTRO DE DATA ===")
    print(f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")

    if not technicians:
        print("❌ Nenhum técnico para testar")
        return {}

    tech_ids = list(technicians.keys())
    print(f"🔍 Testando contagem para {len(tech_ids)} técnicos")

    try:
        # Método 1: Busca individual por técnico
        print("\n📋 Método 1: Busca individual por técnico")
        individual_counts = {}

        for tech_id in tech_ids[:5]:  # Testar apenas os primeiros 5 para não sobrecarregar
            tech_name = technicians[tech_id]["name"]

            response = service._make_authenticated_request(
                "GET",
                f"{service.glpi_url}/search/Ticket",
                params={
                    "range": "0-999",
                    "criteria[0][field]": "15",  # date
                    "criteria[0][searchtype]": "morethan",
                    "criteria[0][value]": start_date.strftime("%Y-%m-%d"),
                    "criteria[1][field]": "15",  # date
                    "criteria[1][searchtype]": "lessthan",
                    "criteria[1][value]": end_date.strftime("%Y-%m-%d"),
                    "criteria[1][link]": "AND",
                    "criteria[2][field]": "5",  # users_id_tech
                    "criteria[2][searchtype]": "equals",
                    "criteria[2][value]": tech_id,
                    "criteria[2][link]": "AND",
                    "forcedisplay[0]": "2",  # id
                    "forcedisplay[1]": "5",  # users_id_tech
                    "forcedisplay[2]": "15",  # date
                },
            )

            if response and response.ok:
                data = response.json()
                count = len(data.get("data", []))
                individual_counts[tech_id] = count
                print(f"   {tech_name}: {count} tickets")
            else:
                print(f"   {tech_name}: Erro na busca")

        # Método 2: Busca em lote (se disponível no serviço)
        print("\n📋 Método 2: Busca em lote")
        try:
            if hasattr(service, "_get_tickets_batch_with_date_filter"):
                batch_counts = service._get_tickets_batch_with_date_filter(
                    tech_ids,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )

                print(f"✅ Contagem em lote realizada para {len(batch_counts)} técnicos")

                # Comparar resultados
                print("\n🔍 Comparação de métodos:")
                for tech_id in individual_counts.keys():
                    individual = individual_counts.get(tech_id, 0)
                    batch = batch_counts.get(tech_id, 0)
                    tech_name = technicians[tech_id]["name"]

                    if individual == batch:
                        print(f"   ✅ {tech_name}: {individual} tickets (métodos concordam)")
                    else:
                        print(f"   ⚠️ {tech_name}: Individual={individual}, Lote={batch} (divergência)")

                return batch_counts
            else:
                print("⚠️ Método de busca em lote não disponível")
                return individual_counts

        except Exception as e:
            print(f"⚠️ Erro na busca em lote: {e}")
            return individual_counts

    except Exception as e:
        print(f"❌ Erro no teste de contagem: {e}")
        return {}


def generate_ranking_with_date_filter(service, technicians, start_date, end_date):
    """
    Gera ranking de técnicos com filtro de data
    """
    print(f"\n=== GERAÇÃO DE RANKING COM FILTRO DE DATA ===")
    print(f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")

    # Obter contagens com filtro de data
    ticket_counts = test_ticket_counting_with_date_filter(service, technicians, start_date, end_date)

    if not ticket_counts:
        print("❌ Não foi possível obter contagens")
        return []

    # Gerar ranking
    ranking = []
    for tech_id, count in ticket_counts.items():
        if tech_id in technicians:
            tech_data = technicians[tech_id].copy()
            tech_data["tickets_in_period"] = count
            ranking.append(tech_data)

    # Ordenar por número de tickets no período
    ranking.sort(key=lambda x: x["tickets_in_period"], reverse=True)

    print(f"\n🏆 RANKING DE TÉCNICOS ({len(ranking)} técnicos):")
    print("=" * 80)

    for i, tech in enumerate(ranking, 1):
        print(
            f"{i:2d}. {tech['name']:<25} | {tech['level']} | "
            f"{tech['tickets_in_period']:3d} tickets no período | "
            f"{tech['ticket_count']:3d} tickets totais"
        )

    return ranking


def save_solution_to_service(service, technicians):
    """
    Salva a solução no serviço GLPI para uso futuro
    """
    print("\n=== SALVANDO SOLUÇÃO NO SERVIÇO ===")

    try:
        # Criar mapeamento de técnicos para o serviço
        technician_mapping = {}

        for tech_id, tech_data in technicians.items():
            technician_mapping[tech_id] = {
                "name": tech_data["name"],
                "level": tech_data["level"],
                "username": tech_data["username"],
            }

        # Salvar no cache do serviço
        if hasattr(service, "_cache"):
            service._cache["assignment_based_technicians"] = {
                "data": technician_mapping,
                "timestamp": datetime.now().timestamp(),
                "ttl": 3600,  # 1 hora
            }

            print(f"✅ {len(technician_mapping)} técnicos salvos no cache do serviço")

        # Gerar código para integração
        integration_code = f"""
# Código para integração no GLPIService
def get_technicians_by_assignments(self, days_back=30, min_tickets=3):
    \"\"\"
    Identifica técnicos baseado em atribuições de tickets
    \"\"\"
    # Verificar cache primeiro
    cache_key = 'assignment_based_technicians'
    if self._is_cache_valid(cache_key):
        return self._cache[cache_key]['data']
    
    # Implementação da busca por atribuições
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    response = self._make_authenticated_request(
        'GET',
        f"{{self.glpi_url}}/search/Ticket",
        params={{
            "range": "0-999",
            "criteria[0][field]": "15",
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date.strftime('%Y-%m-%d'),
            "criteria[1][field]": "5",
            "criteria[1][searchtype]": "contains",
            "criteria[1][value]": "",
            "criteria[1][link]": "AND",
            "forcedisplay[0]": "2",
            "forcedisplay[1]": "5",
        }}
    )
    
    technicians = {{}}
    if response and response.ok:
        data = response.json()
        if data and data.get('data'):
            tech_counts = {{}}
            
            for ticket in data['data']:
                tech_id = str(ticket.get('5', '')) if ticket.get('5') else None
                if tech_id and tech_id != '0':
                    tech_counts[tech_id] = tech_counts.get(tech_id, 0) + 1
            
            for tech_id, count in tech_counts.items():
                if count >= min_tickets:
                    user_response = self._make_authenticated_request(
                        'GET',
                        f"{{self.glpi_url}}/User/{{tech_id}}"
                    )
                    
                    if user_response and user_response.ok:
                        user_data = user_response.json()
                        if user_data.get('is_active') == 1:
                            # Determinar nível baseado na quantidade
                            if count >= 20:
                                level = "N4"
                            elif count >= 15:
                                level = "N3"
                            elif count >= 8:
                                level = "N2"
                            else:
                                level = "N1"
                            
                            technicians[tech_id] = {{
                                'name': f"{{user_data.get('firstname', '')}} {{user_data.get('realname', '')}}".strip(),
                                'level': level,
                                'username': user_data.get('name', ''),
                                'ticket_count': count
                            }}
    
    # Salvar no cache
    self._cache[cache_key] = {{
        'data': technicians,
        'timestamp': datetime.now().timestamp(),
        'ttl': 3600
    }}
    
    return technicians
"""

        print("\n📝 Código de integração gerado")
        print("\n" + "=" * 50)
        print(integration_code)
        print("=" * 50)

        return integration_code

    except Exception as e:
        print(f"❌ Erro ao salvar solução: {e}")
        return None


def main():
    print("=== SOLUÇÃO BASEADA EM ATRIBUIÇÕES DE TICKETS ===")
    print("Implementação da abordagem alternativa para identificar técnicos\n")

    # Carregar variáveis de ambiente
    load_dotenv()

    try:
        # Inicializar serviço
        service = GLPIService()

        if not service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return

        print("✅ Autenticado com sucesso no GLPI")

        # 1. Identificar técnicos por atribuições
        print("\n" + "=" * 60)
        technicians = get_technicians_by_assignments(service, days_back=60, min_tickets=3)

        if not technicians:
            print("❌ Nenhum técnico identificado")
            return

        # 2. Testar filtro de data (últimos 7 dias)
        print("\n" + "=" * 60)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        ranking = generate_ranking_with_date_filter(service, technicians, start_date, end_date)

        # 3. Salvar solução
        print("\n" + "=" * 60)
        integration_code = save_solution_to_service(service, technicians)

        print("\n=== RESUMO FINAL ===")
        print(f"✅ {len(technicians)} técnicos identificados por atribuições")
        print(f"✅ Ranking gerado para período de {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
        print(f"✅ Código de integração preparado")

        # Estatísticas finais
        total_tickets_period = sum(tech.get("tickets_in_period", 0) for tech in ranking)
        total_tickets_overall = sum(tech["ticket_count"] for tech in technicians.values())

        print(f"\n📊 Estatísticas:")
        print(f"   - Tickets no período testado: {total_tickets_period}")
        print(f"   - Tickets totais (últimos 60 dias): {total_tickets_overall}")
        print(f"   - Média de tickets por técnico: {total_tickets_overall / len(technicians):.1f}")

        print("\n✅ Solução implementada com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
