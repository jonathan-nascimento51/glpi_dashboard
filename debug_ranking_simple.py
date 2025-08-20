#!/usr/bin/env python3
"""
Script simplificado para investigar problemas no ranking de técnicos
"""

import json
import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório backend ao path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

from services.glpi_service import GLPIService

def debug_ranking_simple():
    print("=== DEBUG SIMPLIFICADO: RANKING DE TÉCNICOS ===")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        # Desabilitar logs de debug
        import logging
        logging.getLogger('glpi.external').setLevel(logging.CRITICAL)
        logging.getLogger('glpi.internal').setLevel(logging.CRITICAL)
        logging.getLogger('observability').setLevel(logging.CRITICAL)
        
        # Garantir autenticação
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        print("✅ Autenticação bem-sucedida")
        
        print("\n🔍 ETAPA 1: Buscar técnicos com perfil ID 6")
        
        # Buscar usuários com perfil de técnico (ID 6)
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Profile_User",
            params={
                "range": "0-999",
                "criteria[0][field]": "4",  # Campo profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # Perfil de técnico
                "forcedisplay[0]": "4",  # profiles_id
                "forcedisplay[1]": "5",  # users_id
            },
        )
        
        if not response or not response.ok:
            print("❌ Falha ao buscar usuários com perfil de técnico")
            return
        
        profile_result = response.json()
        
        if "data" not in profile_result or not profile_result["data"]:
            print("❌ Nenhum técnico encontrado")
            return
        
        # Extrair IDs dos técnicos
        technician_ids = []
        for item in profile_result["data"]:
            if "5" in item:  # Campo users_id
                technician_ids.append(item["5"])
        
        print(f"✅ Encontrados {len(technician_ids)} técnicos com perfil ID 6")
        
        print("\n🔍 ETAPA 2: Analisar técnicos por nível")
        
        technicians_by_level = {"N1": [], "N2": [], "N3": [], "N4": [], "Sem_Nivel": []}
        
        for tech_id in technician_ids:
            try:
                tech_name = service._get_technician_name(tech_id)
                tech_id_int = int(tech_id)
                tech_level = service._get_technician_level(tech_id_int, 0)
                
                # Contar tickets do técnico
                ticket_count = service._count_tickets_with_date_filter(tech_id, None, None)
                
                technicians_by_level[tech_level].append({
                    "id": tech_id,
                    "name": tech_name,
                    "level": tech_level,
                    "tickets": ticket_count,
                })
                
            except Exception as e:
                print(f"❌ Erro ao processar técnico {tech_id}: {e}")
                technicians_by_level["Sem_Nivel"].append({
                    "id": tech_id, 
                    "name": "ERRO", 
                    "level": "ERRO", 
                    "tickets": 0
                })
        
        print("\n📊 RESUMO POR NÍVEL:")
        for level, techs in technicians_by_level.items():
            print(f"\n{level}: {len(techs)} técnicos")
            for tech in techs:
                print(f"  - {tech['name']} (ID: {tech['id']}) - {tech['tickets']} tickets")
        
        print("\n🔍 ETAPA 3: Testar método get_technician_ranking atual")
        
        try:
            ranking = service.get_technician_ranking()
            print(f"\n📈 RANKING ATUAL: {len(ranking)} técnicos")
            
            ranking_by_level = {"N1": [], "N2": [], "N3": [], "N4": [], "Outros": []}
            
            for tech in ranking:
                level = tech.get('level', 'Outros')
                if level in ranking_by_level:
                    ranking_by_level[level].append(tech)
                else:
                    ranking_by_level['Outros'].append(tech)
            
            print("\n📊 RANKING POR NÍVEL:")
            for level, techs in ranking_by_level.items():
                print(f"\n{level}: {len(techs)} técnicos no ranking")
                for i, tech in enumerate(techs[:5]):  # Mostrar top 5 de cada nível
                    print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
                    
        except Exception as e:
            print(f"❌ Erro ao obter ranking: {e}")
        
        print("\n=== ANÁLISE CONCLUÍDA ===")
        
    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ranking_simple()