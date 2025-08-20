#!/usr/bin/env python3
"""
Script detalhado para investigar por que apenas técnicos N2 e N3 aparecem no ranking
"""

import json
import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_ranking_levels():
    """Debug detalhado dos níveis no ranking"""
    try:
        print("=== DEBUG DETALHADO: NÍVEIS NO RANKING ===")

        # Carregar configurações
        load_dotenv()

        # Inicializar serviço
        service = GLPIService()

        # Autenticar
        if not service.authenticate():
            print("❌ Falha na autenticação")
            return

        print("✅ Autenticado com sucesso")

        # 1. Obter ranking atual
        print("\n🔍 ETAPA 1: Obter ranking atual")
        ranking = service.get_technician_ranking()

        print(f"📊 Total de técnicos no ranking: {len(ranking)}")

        # Contar por nível
        levels_count = {"N1": 0, "N2": 0, "N3": 0, "N4": 0}

        print("\n📋 TÉCNICOS POR NÍVEL:")
        for level in ["N1", "N2", "N3", "N4"]:
            print(f"\n--- {level} ---")
            level_techs = [t for t in ranking if t.get("level") == level]
            levels_count[level] = len(level_techs)

            if level_techs:
                for tech in level_techs:
                    print(f"  • {tech.get('name', 'N/A')} (ID: {tech.get('id', 'N/A')}) - {tech.get('total', 0)} tickets")
            else:
                print(f"  ❌ Nenhum técnico encontrado no nível {level}")

        print(f"\n📊 RESUMO DE CONTAGEM:")
        for level, count in levels_count.items():
            print(f"  {level}: {count} técnicos")

        # 2. Verificar técnicos ativos que deveriam estar em N1 e N4
        print("\n🔍 ETAPA 2: Verificar técnicos que deveriam estar em N1 e N4")

        # Buscar todos os técnicos ativos
        active_techs = service._get_active_technicians()
        print(f"📊 Total de técnicos ativos encontrados: {len(active_techs)}")

        # Verificar cada técnico ativo individualmente
        missing_levels = {"N1": [], "N4": []}

        for tech_id in active_techs:
            try:
                tech_name = service._get_technician_name(tech_id)
                tech_id_int = int(tech_id)
                tech_level = service._get_technician_level(tech_id_int, 0)

                # Se é N1 ou N4, verificar se está no ranking
                if tech_level in ["N1", "N4"]:
                    in_ranking = any(t.get("id") == str(tech_id) for t in ranking)

                    if not in_ranking:
                        missing_levels[tech_level].append({"id": tech_id, "name": tech_name, "level": tech_level})
                        print(f"⚠️ Técnico {tech_name} (ID: {tech_id}) é {tech_level} mas NÃO está no ranking")
                    else:
                        print(f"✅ Técnico {tech_name} (ID: {tech_id}) é {tech_level} e ESTÁ no ranking")

            except Exception as e:
                print(f"❌ Erro ao processar técnico {tech_id}: {e}")

        print(f"\n📊 TÉCNICOS AUSENTES DO RANKING:")
        for level, techs in missing_levels.items():
            print(f"\n{level}: {len(techs)} técnicos ausentes")
            for tech in techs:
                print(f"  • {tech['name']} (ID: {tech['id']})")

        # 3. Verificar método get_technician_ranking_with_filters
        print("\n🔍 ETAPA 3: Testar ranking com filtros por nível")

        for level in ["N1", "N2", "N3", "N4"]:
            try:
                filtered_ranking = service.get_technician_ranking_with_filters(level=level)
                print(f"\n{level} (com filtro): {len(filtered_ranking)} técnicos")

                for tech in filtered_ranking[:5]:  # Top 5
                    print(f"  • {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")

            except Exception as e:
                print(f"❌ Erro ao obter ranking filtrado para {level}: {e}")

        # 4. Verificar se há filtros ou condições que excluem N1 e N4
        print("\n🔍 ETAPA 4: Verificar condições de exclusão")

        # Verificar se há filtros de tickets mínimos
        print("\n📊 Análise de tickets por nível:")

        all_active_with_levels = []
        for tech_id in active_techs:
            try:
                tech_name = service._get_technician_name(tech_id)
                tech_id_int = int(tech_id)
                tech_level = service._get_technician_level(tech_id_int, 0)
                ticket_count = service._count_tickets_with_date_filter(tech_id, None, None)

                all_active_with_levels.append(
                    {
                        "id": tech_id,
                        "name": tech_name,
                        "level": tech_level,
                        "tickets": ticket_count,
                    }
                )

            except Exception as e:
                print(f"❌ Erro ao processar técnico {tech_id}: {e}")

        # Agrupar por nível e mostrar estatísticas
        for level in ["N1", "N2", "N3", "N4"]:
            level_techs = [t for t in all_active_with_levels if t["level"] == level]

            if level_techs:
                total_tickets = sum(t["tickets"] for t in level_techs)
                avg_tickets = total_tickets / len(level_techs)
                min_tickets = min(t["tickets"] for t in level_techs)
                max_tickets = max(t["tickets"] for t in level_techs)

                print(f"\n{level}: {len(level_techs)} técnicos")
                print(f"  Total tickets: {total_tickets}")
                print(f"  Média tickets: {avg_tickets:.1f}")
                print(f"  Min tickets: {min_tickets}")
                print(f"  Max tickets: {max_tickets}")

                # Mostrar técnicos com 0 tickets
                zero_tickets = [t for t in level_techs if t["tickets"] == 0]
                if zero_tickets:
                    print(f"  ⚠️ Técnicos com 0 tickets: {len(zero_tickets)}")
                    for tech in zero_tickets:
                        print(f"    • {tech['name']} (ID: {tech['id']})")
            else:
                print(f"\n{level}: 0 técnicos encontrados")

        print("\n=== FIM DO DEBUG DETALHADO ===")

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_ranking_levels()
