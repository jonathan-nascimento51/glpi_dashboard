#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar métricas por nível - investigar dados zerados
"""

import json
import os
import sys
from datetime import datetime

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.glpi_service import GLPIService


def debug_level_metrics() -> None:
    """Debug das métricas por nível"""
    print("=" * 80)
    print("DEBUG: MÉTRICAS POR NÍVEL - INVESTIGAÇÃO DE DADOS ZERADOS")
    print("=" * 80)

    try:
        # Inicializar serviço GLPI
        glpi = GLPIService()

        print("\n1. VERIFICANDO AUTENTICAÇÃO")
        print("-" * 50)
        if not glpi._ensure_authenticated():
            print("❌ ERRO: Falha na autenticação")
            return
        print("✅ Autenticação bem-sucedida")

        print("\n2. VERIFICANDO DESCOBERTA DE FIELD IDs")
        print("-" * 50)
        if not glpi.discover_field_ids():
            print("❌ ERRO: Falha ao descobrir field IDs")
            return
        print("✅ Field IDs descobertos:")
        for field_name, field_id in glpi.field_ids.items():
            print(f"  - {field_name}: {field_id}")

        print("\n3. VERIFICANDO CONFIGURAÇÃO DOS GRUPOS")
        print("-" * 50)
        print("Grupos configurados:")
        for level, group_id in glpi.service_levels.items():
            print(f"  - {level}: {group_id}")

        print("\n4. VERIFICANDO STATUS CONFIGURADOS")
        print("-" * 50)
        print("Status configurados:")
        for status_name, status_id in glpi.status_map.items():
            print(f"  - {status_name}: {status_id}")

        print("\n5. TESTANDO CONTAGEM INDIVIDUAL POR GRUPO E STATUS")
        print("-" * 50)

        for level_name, group_id in glpi.service_levels.items():
            print(f"\n🔍 Testando {level_name} (Grupo ID: {group_id}):")
            level_total = 0

            for status_name, status_id in glpi.status_map.items():
                print(f"  Buscando {status_name} (Status ID: {status_id})...", end=" ")

                try:
                    count = glpi.get_ticket_count(group_id, status_id)
                    print(f"✅ {count} tickets")
                    level_total += count if count is not None else 0
                except Exception as e:
                    print(f"❌ ERRO: {e}")

            print(f"  📊 Total do {level_name}: {level_total} tickets")

        print("\n6. TESTANDO FUNÇÃO _get_metrics_by_level_internal")
        print("-" * 50)

        try:
            raw_metrics = glpi._get_metrics_by_level_internal()
            print("✅ Métricas obtidas com sucesso:")
            print(json.dumps(raw_metrics, indent=2, ensure_ascii=False))

            # Calcular totais
            grand_total = 0
            for level_name, level_data in raw_metrics.items():
                level_total = sum(level_data.values())
                grand_total += level_total
                print(f"\n📊 {level_name}: {level_total} tickets")
                for status, count in level_data.items():
                    if count > 0:
                        print(f"  - {status}: {count}")

            print(f"\n🎯 TOTAL GERAL DOS NÍVEIS: {grand_total} tickets")

        except Exception as e:
            print(f"❌ ERRO na função _get_metrics_by_level_internal: {e}")
            import traceback

            traceback.print_exc()

        print("\n7. VERIFICANDO SE OS GRUPOS EXISTEM NO GLPI")
        print("-" * 50)

        for level_name, group_id in glpi.service_levels.items():
            print(f"\n🔍 Verificando existência do grupo {group_id} ({level_name}):")

            try:
                response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/Group/{group_id}")

                if response and response.ok:
                    group_data = response.json()
                    group_name = group_data.get("name", "Nome não encontrado")
                    print(f"  ✅ Grupo existe: {group_name}")
                else:
                    print(f"  ❌ Grupo não encontrado ou inacessível (Status: {response.status_code if response else 'None'})")

            except Exception as e:
                print(f"  ❌ ERRO ao verificar grupo: {e}")

        print("\n8. TESTANDO BUSCA DIRETA DE TICKETS POR GRUPO")
        print("-" * 50)

        for level_name, group_id in glpi.service_levels.items():
            print(f"\n🔍 Buscando tickets do grupo {group_id} ({level_name}):")

            try:
                search_params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": glpi.field_ids["GROUP"],
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": group_id,
                }

                response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=search_params)

                if response and "Content-Range" in response.headers:
                    total = int(response.headers["Content-Range"].split("/")[-1])
                    print(f"  ✅ Total de tickets no grupo: {total}")
                else:
                    print(f"  ❌ Não foi possível obter contagem (Status: {response.status_code if response else 'None'})")
                    if response:
                        print(f"  Headers: {dict(response.headers)}")

            except Exception as e:
                print(f"  ❌ ERRO na busca: {e}")

        print("\n" + "=" * 80)
        print("DEBUG CONCLUÍDO")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_level_metrics()
