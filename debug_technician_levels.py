#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_technician_levels():
    """Debug dos níveis dos técnicos"""
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        print("=== DEBUG DOS NÍVEIS DOS TÉCNICOS ===")
        print(f"Service levels configurados: {service.service_levels}")
        print()
        
        # Obter ranking de técnicos
        print("Obtendo ranking de técnicos...")
        ranking = service.get_technician_ranking()
        
        if not ranking:
            print("Nenhum técnico encontrado no ranking")
            return
        
        print(f"\nEncontrados {len(ranking)} técnicos:")
        print("-" * 80)
        
        # Analisar cada técnico
        for i, tech in enumerate(ranking[:10], 1):  # Mostrar apenas os 10 primeiros
            print(f"{i:2d}. {tech['name']:25} | Nível: {tech['level']:2} | Tickets: {tech['total']:3d}")
        
        # Contar técnicos por nível
        level_counts = {}
        for tech in ranking:
            level = tech['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("\n=== DISTRIBUIÇÃO POR NÍVEL ===")
        for level in ['N1', 'N2', 'N3', 'N4']:
            count = level_counts.get(level, 0)
            print(f"{level}: {count} técnicos")
        
        # Debug detalhado para alguns técnicos
        print("\n=== DEBUG DETALHADO (3 primeiros técnicos) ===")
        for tech in ranking[:3]:
            user_id = int(tech['id'])
            print(f"\nTécnico: {tech['name']} (ID: {user_id})")
            
            # Buscar grupos manualmente
            try:
                response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "4",  # Campo users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4"   # users_id
                    }
                )
                
                if response and response.ok:
                    group_data = response.json()
                    print(f"  Resposta da API: {group_data.get('totalcount', 0)} grupos encontrados")
                    
                    if group_data.get('data'):
                        print("  Grupos do usuário:")
                        for group_entry in group_data['data']:
                            if isinstance(group_entry, dict) and "3" in group_entry:
                                group_id = int(group_entry["3"])
                                print(f"    - Grupo ID: {group_id}")
                                
                                # Verificar se é um grupo de nível
                                for level, level_group_id in service.service_levels.items():
                                    if group_id == level_group_id:
                                        print(f"      -> MATCH! Este é o grupo {level}")
                    else:
                        print("  Nenhum grupo encontrado nos dados")
                else:
                    print(f"  Erro na busca de grupos: {response.status_code if response else 'Sem resposta'}")
                    
            except Exception as e:
                print(f"  Erro ao buscar grupos: {e}")
        
        service.close_session()
        
    except Exception as e:
        logger.error(f"Erro no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_technician_levels()