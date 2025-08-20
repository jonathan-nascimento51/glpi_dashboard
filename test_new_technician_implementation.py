#!/usr/bin/env python3
"""
Script para testar a nova implementação de busca de técnicos via tickets atribuídos.
Este script testa a correção que contorna o problema da tabela Profile_User vazia.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
from config.settings import Config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Função principal para testar a nova implementação de busca de técnicos."""
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    print("=== Teste da Nova Implementação de Busca de Técnicos ===")
    
    # 1. Autenticar no GLPI
    print("\n1. Autenticando no GLPI...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # 2. Testar a nova implementação sem filtro de entidade
    print("\n2. Testando busca de técnicos (todas as entidades)...")
    try:
        tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names()
        
        print(f"✅ Encontrados {len(tech_ids)} técnicos ativos")
        print(f"📊 IDs dos técnicos: {tech_ids[:10]}" + (f" (e mais {len(tech_ids)-10})" if len(tech_ids) > 10 else ""))
        
        if tech_names:
            print(f"\n👥 Primeiros 5 técnicos encontrados:")
            for i, tech_id in enumerate(tech_ids[:5]):
                name = tech_names.get(tech_id, f"Técnico {tech_id}")
                print(f"   - ID: {tech_id}, Nome: {name}")
        
    except Exception as e:
        print(f"❌ Erro na busca geral: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Testar com filtro de entidade específica
    print("\n3. Testando busca de técnicos (entidade ID: 1)...")
    try:
        tech_ids_entity, tech_names_entity = glpi_service._get_all_technician_ids_and_names(entity_id=1)
        
        print(f"✅ Encontrados {len(tech_ids_entity)} técnicos ativos na entidade 1")
        print(f"📊 IDs dos técnicos: {tech_ids_entity[:10]}" + (f" (e mais {len(tech_ids_entity)-10})" if len(tech_ids_entity) > 10 else ""))
        
        if tech_names_entity:
            print(f"\n👥 Primeiros 5 técnicos da entidade 1:")
            for i, tech_id in enumerate(tech_ids_entity[:5]):
                name = tech_names_entity.get(tech_id, f"Técnico {tech_id}")
                print(f"   - ID: {tech_id}, Nome: {name}")
        
    except Exception as e:
        print(f"❌ Erro na busca por entidade: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Testar função de ranking de técnicos
    print("\n4. Testando ranking de técnicos...")
    try:
        # Usar a função que depende da busca de técnicos
        ranking_data = glpi_service.get_technician_ranking_with_filters(entity_id=1)
        
        if ranking_data and 'technicians' in ranking_data:
            technicians = ranking_data['technicians']
            print(f"✅ Ranking gerado com {len(technicians)} técnicos")
            
            if technicians:
                print(f"\n🏆 Top 3 técnicos no ranking:")
                for i, tech in enumerate(technicians[:3]):
                    print(f"   {i+1}. {tech.get('name', 'Nome não disponível')} - "
                          f"Total: {tech.get('total_tickets', 0)}, "
                          f"Resolvidos: {tech.get('resolved_tickets', 0)}")
        else:
            print("❌ Falha ao gerar ranking de técnicos")
            
    except Exception as e:
        print(f"❌ Erro no teste de ranking: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Verificar logs de debug
    print("\n5. Verificando logs de debug...")
    try:
        if os.path.exists("debug_ranking.log"):
            with open("debug_ranking.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                
            print(f"📝 Últimas {len(recent_lines)} linhas do log de debug:")
            for line in recent_lines:
                if "[DEBUG]" in line:
                    print(f"   {line.strip()}")
        else:
            print("📝 Arquivo de debug não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao ler logs: {e}")
    
    print("\n=== Fim do Teste ===")

if __name__ == "__main__":
    main()