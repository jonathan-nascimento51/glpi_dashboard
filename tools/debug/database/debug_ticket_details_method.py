#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar o método _get_technician_ticket_details
Verifica se a contagem de tickets por técnico está funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ticket_details_method():
    """Testa o método _get_technician_ticket_details"""
    print("🔍 Testando método _get_technician_ticket_details")
    print("=" * 60)
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando com GLPI...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Descobrir field ID do técnico
    print("\n2. Descobrindo field ID do técnico...")
    tech_field_id = glpi_service._discover_tech_field_id()
    if not tech_field_id:
        print("❌ Falha ao descobrir field ID do técnico")
        return
    print(f"✅ Field ID do técnico: {tech_field_id}")
    
    # Obter alguns técnicos para teste
    print("\n3. Obtendo técnicos para teste...")
    try:
        # Usar o método que já sabemos que funciona
        tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names()
        if not tech_ids:
            print("❌ Nenhum técnico encontrado")
            return
        
        print(f"✅ Encontrados {len(tech_ids)} técnicos")
        
        # Testar com os primeiros 3 técnicos
        test_techs = tech_ids[:3]
        print(f"\n4. Testando contagem de tickets para {len(test_techs)} técnicos...")
        
        for tech_id in test_techs:
            tech_name = tech_names.get(str(tech_id), f"Técnico {tech_id}")
            print(f"\n--- Técnico: {tech_name} (ID: {tech_id}) ---")
            
            # Testar o método _get_technician_ticket_details
            ticket_details = glpi_service._get_technician_ticket_details(int(tech_id), tech_field_id)
            
            if ticket_details:
                print(f"✅ Dados obtidos com sucesso:")
                print(f"   Total de tickets: {ticket_details.get('total_tickets', 0)}")
                print(f"   Tickets resolvidos: {ticket_details.get('resolved_tickets', 0)}")
                print(f"   Tickets pendentes: {ticket_details.get('pending_tickets', 0)}")
                print(f"   Tempo médio de resolução: {ticket_details.get('avg_resolution_time', 0.0)}")
            else:
                print(f"❌ Falha ao obter dados de tickets")
                
            # Comparar com método manual
            print(f"\n   Comparação com contagem manual:")
            manual_count = glpi_service._count_tickets_by_technician(tech_id)
            print(f"   Contagem manual: {manual_count}")
            
            if ticket_details:
                auto_count = ticket_details.get('total_tickets', 0)
                if manual_count == auto_count:
                    print(f"   ✅ Contagens coincidem: {manual_count}")
                else:
                    print(f"   ⚠️  Diferença encontrada: manual={manual_count}, automático={auto_count}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    # Encerrar sessão
    print("\n5. Encerrando sessão...")
    glpi_service.close_session()
    print("✅ Sessão encerrada")

def test_field_discovery():
    """Testa especificamente a descoberta do field ID"""
    print("\n🔍 Testando descoberta de field ID")
    print("=" * 40)
    
    glpi_service = GLPIService()
    
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    
    # Testar descoberta de field ID
    tech_field_id = glpi_service._discover_tech_field_id()
    print(f"Field ID descoberto: {tech_field_id}")
    
    # Listar todos os campos disponíveis para debug
    try:
        response = glpi_service._make_authenticated_request("GET", f"{glpi_service.glpi_url}/listSearchOptions/Ticket")
        if response and response.ok:
            search_options = response.json()
            print("\nCampos disponíveis relacionados a técnico:")
            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    if any(keyword in field_name.lower() for keyword in ["técnico", "technician", "assigned", "atribuído"]):
                        print(f"  {field_id}: {field_name}")
    except Exception as e:
        print(f"Erro ao listar campos: {e}")
    
    glpi_service.close_session()

if __name__ == "__main__":
    print("🚀 Iniciando debug do método _get_technician_ticket_details")
    print("=" * 80)
    
    # Testar descoberta de field ID primeiro
    test_field_discovery()
    
    print("\n" + "=" * 80)
    
    # Testar método principal
    test_ticket_details_method()
    
    print("\n🏁 Debug concluído")