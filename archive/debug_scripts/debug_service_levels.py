#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar a configuração dos service_levels
e entender por que apenas N2 e N3 aparecem no ranking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def debug_service_levels():
    """Debugar configuração dos service_levels"""
    print("🔍 Debugando configuração dos service_levels...")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Verificar configuração atual
    print("\n📋 Configuração atual dos service_levels:")
    for level, group_id in glpi_service.service_levels.items():
        print(f"  {level}: Grupo {group_id}")
    
    # Verificar se todos os níveis apontam para o mesmo grupo
    unique_groups = set(glpi_service.service_levels.values())
    print(f"\n🔢 Grupos únicos configurados: {unique_groups}")
    
    if len(unique_groups) == 1:
        print("⚠️  PROBLEMA IDENTIFICADO: Todos os níveis apontam para o mesmo grupo!")
        print("   Isso significa que todos os técnicos do grupo 17 terão o mesmo nível.")
        print("   A lógica de determinação de nível está usando fallback por nome.")
    else:
        print("✅ Configuração parece correta - diferentes grupos para diferentes níveis.")
    
    # Testar alguns técnicos conhecidos
    print("\n🧪 Testando determinação de nível para técnicos conhecidos:")
    
    # Técnicos com IDs numéricos conhecidos
    test_technicians = [
        ("gabriel-conceicao", "Gabriel Conceição"),
        ("anderson-oliveira", "Anderson Oliveira"),
        ("wagner-mengue", "Wagner Mengue"),
        ("silvio-valim", "Silvio Valim")
    ]
    
    for tech_id, tech_name in test_technicians:
        try:
            # Testar determinação por nome
            level_by_name = glpi_service._get_technician_level_by_name(tech_name)
            print(f"  {tech_name} ({tech_id}): Nível por nome = {level_by_name}")
        except Exception as e:
            print(f"  {tech_name} ({tech_id}): Erro = {e}")
    
    print("\n💡 Recomendações:")
    print("1. Verificar se os grupos 89, 90, 91, 92 existem no GLPI")
    print("2. Atualizar service_levels para usar os grupos corretos")
    print("3. Ou manter o mapeamento por nome como está funcionando")
    
    print("\n✅ Debug dos service_levels concluído!")

if __name__ == "__main__":
    debug_service_levels()