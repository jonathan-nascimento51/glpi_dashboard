#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

# Desabilitar logs de debug
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("glpi").setLevel(logging.CRITICAL)
logging.getLogger("alerting").setLevel(logging.CRITICAL)
logging.getLogger("structured_logging").setLevel(logging.CRITICAL)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def main():
    # Configurações dos grupos técnicos
    service_levels = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}

    print("=== TESTE DE GRUPOS TECNICOS ===")
    print()

    try:
        # Inicializar serviço GLPI
        glpi = GLPIService()

        # Autenticar
        glpi._ensure_authenticated()
        print("[INFO] Autenticacao realizada com sucesso")
        print()

        print("Verificando grupos tecnicos configurados...")
        print()

        grupos_encontrados = 0
        grupos_nao_encontrados = 0

        # Testar cada grupo individualmente
        for level, group_id in service_levels.items():
            try:
                response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/Group/{group_id}")
                if response and response.ok:
                    group_data = response.json()
                    group_name = group_data.get("name", "Nome nao encontrado")
                    print(f"[OK] {level} (ID: {group_id}) - Nome: '{group_name}'")
                    grupos_encontrados += 1
                else:
                    status_code = response.status_code if response else "None"
                    print(f"[ERRO] {level} (ID: {group_id}) - Status HTTP: {status_code}")
                    grupos_nao_encontrados += 1
            except Exception as e:
                print(f"[ERRO] {level} (ID: {group_id}) - Excecao: {str(e)}")
                grupos_nao_encontrados += 1

        print()
        print(f"Resumo: {grupos_encontrados} grupos encontrados, {grupos_nao_encontrados} grupos com problema")
        print()
        print("=== FIM DO TESTE ===")

    except Exception as e:
        print(f"[ERRO GERAL] {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
