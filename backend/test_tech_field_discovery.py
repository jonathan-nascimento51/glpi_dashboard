#!/usr/bin/env python3
"""
Teste específico para verificar descoberta do tech_field_id e contagem de tickets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
from config.settings import Config
import logging

# Inicializar configurações
config = Config()

# Desabilitar logging para focar nos resultados
logging.getLogger().setLevel(logging.CRITICAL)

def test_tech_field_discovery():
    """Testa a descoberta do campo de técnico"""
    print("=== TESTE DE DESCOBERTA DO CAMPO DE TÉCNICO ===")
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Descobrir tech_field_id
        tech_field_id = glpi_service._discover_tech_field_id()
        print(f"Tech Field ID descoberto: {tech_field_id}")
        
        if not tech_field_id:
            print("ERRO: Não foi possível descobrir o tech_field_id")
            return None
            
        return tech_field_id
        
    except Exception as e:
        print(f"ERRO na descoberta do tech_field_id: {e}")
        return None

def test_ticket_count_for_specific_tech(tech_field_id, tech_id=721):
    """Testa contagem de tickets para um técnico específico"""
    print(f"\n=== TESTE DE CONTAGEM DE TICKETS PARA TÉCNICO {tech_id} ===")
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Contar tickets
        ticket_count = glpi_service._count_tickets_by_technician_optimized(tech_id, tech_field_id)
        print(f"Contagem de tickets para técnico {tech_id}: {ticket_count}")
        
        return ticket_count
        
    except Exception as e:
        print(f"ERRO na contagem de tickets: {e}")
        return None

def test_search_options():
    """Testa listagem de opções de busca para Ticket"""
    print("\n=== TESTE DE OPÇÕES DE BUSCA ===")
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Fazer requisição para listSearchOptions
        response = glpi_service._make_authenticated_request("GET", f"{config.GLPI_URL}/listSearchOptions/Ticket")
        
        if response and response.ok:
            search_options = response.json()
            print(f"Status da requisição: {response.status_code}")
            
            # Procurar campos relacionados a técnico
            tech_fields = {}
            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    if any(keyword in field_name.lower() for keyword in ["técnico", "atribuído", "assigned", "technician"]):
                        tech_fields[field_id] = field_name
            
            print(f"Campos relacionados a técnico encontrados: {tech_fields}")
            return tech_fields
        else:
            print(f"ERRO na requisição: Status {response.status_code if response else 'None'}")
            return None
            
    except Exception as e:
        print(f"ERRO ao listar opções de busca: {e}")
        return None

def main():
    """Função principal"""
    print("Iniciando testes de descoberta de campo e contagem de tickets...\n")
    
    # Teste 1: Listar opções de busca
    tech_fields = test_search_options()
    
    # Teste 2: Descobrir tech_field_id
    tech_field_id = test_tech_field_discovery()
    
    # Teste 3: Contar tickets para técnico específico
    if tech_field_id:
        ticket_count = test_ticket_count_for_specific_tech(tech_field_id)
        
        # Teste adicional com campo "5" se descoberto for diferente
        if tech_field_id != "5":
            print(f"\n=== TESTE ADICIONAL COM CAMPO 5 ===")
            ticket_count_field5 = test_ticket_count_for_specific_tech("5")
            print(f"Contagem com campo 5: {ticket_count_field5}")
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Campos de técnico encontrados: {tech_fields if tech_fields else 'Nenhum'}")
    print(f"Tech Field ID descoberto: {tech_field_id if tech_field_id else 'Falhou'}")
    print(f"Contagem de tickets funcionando: {'Sim' if tech_field_id and ticket_count is not None else 'Não'}")

if __name__ == "__main__":
    main()