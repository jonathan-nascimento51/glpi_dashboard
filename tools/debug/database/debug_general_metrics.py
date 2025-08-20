#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para investigar por que as métricas gerais estão retornando zero.
Este script testa especificamente o método _get_general_metrics_internal.
"""

import json
import os
import sys
import time
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import active_config
from services.glpi_service import GLPIService


def test_general_metrics_debug():
    """Testa o método _get_general_metrics_internal com debug detalhado"""
    print("=" * 80)
    print("DEBUG: Testando _get_general_metrics_internal")
    print("=" * 80)

    try:
        # Inicializar configurações
        settings = active_config
        print(f"✓ Configurações carregadas")

        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        print(f"✓ GLPIService inicializado")

        # Verificar configurações básicas
        print("\n--- Verificando Configurações ---")
        print(f"GLPI URL: {getattr(glpi_service, 'glpi_url', 'NÃO CONFIGURADO')}")
        print(f"Status Map: {len(getattr(glpi_service, 'status_map', {}))} itens")
        if hasattr(glpi_service, "status_map"):
            for status, id in glpi_service.status_map.items():
                print(f"  - {status}: {id}")

        # Autenticar
        print("\n--- Testando Autenticação ---")
        auth_result = glpi_service._ensure_authenticated()
        print(f"Autenticação: {'✓ Sucesso' if auth_result else '✗ Falhou'}")

        if not auth_result:
            print("❌ Não foi possível autenticar. Abortando teste.")
            return

        # Descobrir field_ids
        print("\n--- Descobrindo Field IDs ---")
        field_discovery = glpi_service.discover_field_ids()
        print(f"Field Discovery: {'✓ Sucesso' if field_discovery else '✗ Falhou'}")

        if hasattr(glpi_service, "field_ids"):
            print(f"Field IDs encontrados: {glpi_service.field_ids}")

        # Testar uma requisição manual para um status específico
        print("\n--- Testando Requisição Manual ---")
        if hasattr(glpi_service, "status_map") and glpi_service.status_map:
            # Pegar o primeiro status para teste
            first_status = list(glpi_service.status_map.keys())[0]
            first_status_id = glpi_service.status_map[first_status]

            print(f"Testando status: {first_status} (ID: {first_status_id})")

            # Construir parâmetros de busca manualmente
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": glpi_service.field_ids.get("STATUS", "12"),
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": int(first_status_id),
            }

            print(f"Parâmetros de busca: {json.dumps(search_params, indent=2)}")

            try:
                response = glpi_service._make_authenticated_request(
                    "GET",
                    f"{glpi_service.glpi_url}/search/Ticket",
                    params=search_params,
                )

                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")

                if "Content-Range" in response.headers:
                    content_range = response.headers["Content-Range"]
                    print(f"Content-Range: {content_range}")

                    if "/" in content_range:
                        total_str = content_range.split("/")[-1]
                        print(f"Total extraído: {total_str}")

                        if total_str.isdigit():
                            count = int(total_str)
                            print(f"✓ Contagem para {first_status}: {count}")
                        else:
                            print(f"❌ Total não é numérico: {total_str}")
                    else:
                        print(f"❌ Content-Range malformado: {content_range}")
                else:
                    print("❌ Sem Content-Range no cabeçalho")

                # Mostrar parte do conteúdo da resposta
                try:
                    response_data = response.json()
                    print(f"Resposta JSON (primeiros 500 chars): {str(response_data)[:500]}...")
                except:
                    print(f"Resposta texto (primeiros 500 chars): {response.text[:500]}...")

            except Exception as e:
                print(f"❌ Erro na requisição manual: {e}")

        # Testar o método _get_general_metrics_internal
        print("\n--- Testando _get_general_metrics_internal ---")
        start_time = time.time()

        try:
            general_metrics = glpi_service._get_general_metrics_internal()
            execution_time = (time.time() - start_time) * 1000

            print(f"Tempo de execução: {execution_time:.2f}ms")
            print(f"Tipo do resultado: {type(general_metrics)}")
            print(f"Resultado: {json.dumps(general_metrics, indent=2)}")

            # Verificar se todos os valores são zero
            if isinstance(general_metrics, dict):
                total_sum = sum(general_metrics.values())
                print(f"Soma total de todos os valores: {total_sum}")

                if total_sum == 0:
                    print("❌ PROBLEMA: Todas as métricas gerais são zero!")
                else:
                    print(f"✓ Métricas gerais têm valores: {total_sum} total")
            else:
                print(f"❌ PROBLEMA: Resultado não é um dicionário: {type(general_metrics)}")

        except Exception as e:
            print(f"❌ Erro ao executar _get_general_metrics_internal: {e}")
            import traceback

            traceback.print_exc()

        # Testar com filtros de data
        print("\n--- Testando com Filtros de Data ---")
        try:
            # Testar com data de hoje
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = datetime.now().replace(day=datetime.now().day - 1).strftime("%Y-%m-%d")

            print(f"Testando com data de ontem ({yesterday}) até hoje ({today})")

            general_metrics_filtered = glpi_service._get_general_metrics_internal(start_date=yesterday, end_date=today)

            print(f"Resultado com filtro: {json.dumps(general_metrics_filtered, indent=2)}")

        except Exception as e:
            print(f"❌ Erro ao testar com filtros de data: {e}")

        # Comparar com método público
        print("\n--- Comparando com get_general_metrics ---")
        try:
            public_metrics = glpi_service.get_general_metrics()
            print(f"get_general_metrics resultado: {json.dumps(public_metrics, indent=2)}")

        except Exception as e:
            print(f"❌ Erro ao executar get_general_metrics: {e}")

    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("DEBUG: Teste concluído")
    print("=" * 80)


def test_direct_api_call():
    """Testa uma chamada direta à API do GLPI para verificar se há tickets"""
    print("\n=== TESTE DIRETO DA API ===")

    try:
        settings = active_config
        glpi_service = GLPIService()

        # Autenticar
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return

        # Fazer uma busca simples por todos os tickets
        search_params = {
            "is_deleted": 0,
            "range": "0-10",  # Pegar apenas os primeiros 10 para ver se há dados
        }

        print(f"Fazendo busca simples por tickets...")
        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/Ticket", params=search_params
        )

        print(f"Status Code: {response.status_code}")

        if "Content-Range" in response.headers:
            content_range = response.headers["Content-Range"]
            print(f"Content-Range: {content_range}")

            if "/" in content_range:
                total_str = content_range.split("/")[-1]
                print(f"Total de tickets no sistema: {total_str}")

        # Mostrar alguns tickets
        try:
            response_data = response.json()
            if "data" in response_data and response_data["data"]:
                print(f"Encontrados {len(response_data['data'])} tickets na resposta")
                for i, ticket in enumerate(response_data["data"][:3]):
                    print(f"  Ticket {i+1}: ID={ticket.get('2', 'N/A')}, Status={ticket.get('12', 'N/A')}")
            else:
                print("❌ Nenhum ticket encontrado na resposta")
        except Exception as e:
            print(f"Erro ao processar resposta JSON: {e}")

    except Exception as e:
        print(f"❌ Erro no teste direto da API: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_general_metrics_debug()
    test_direct_api_call()
