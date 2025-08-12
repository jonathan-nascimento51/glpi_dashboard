#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar por que apenas N2 e N3 aparecem no ranking de técnicos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def debug_ranking_levels():
    """Debugar níveis no ranking de técnicos"""
    print("🔍 Debugando níveis no ranking de técnicos...")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Obter ranking completo sem filtros
    print("\n📊 Obtendo ranking completo sem filtros...")
    technicians = glpi_service.get_technician_ranking_with_filters(limit=50)
    
    if not technicians:
        print("❌ Erro ao obter ranking")
        return
    print(f"✅ Encontrados {len(technicians)} técnicos no ranking")
    
    # Contar técnicos por nível
    level_counts = {}
    for tech in technicians:
        level = tech.get('level', 'N/A')
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print("\n📈 Distribuição por níveis:")
    for level, count in sorted(level_counts.items()):
        print(f"  {level}: {count} técnicos")
    
    # Mostrar alguns técnicos de cada nível
    print("\n👥 Exemplos de técnicos por nível:")
    for level in ['N1', 'N2', 'N3', 'N4']:
        techs_in_level = [t for t in technicians if t.get('level') == level]
        print(f"\n  {level} ({len(techs_in_level)} técnicos):")
        for i, tech in enumerate(techs_in_level[:5]):  # Mostrar apenas os primeiros 5
            print(f"    {i+1}. {tech['name']}: {tech['total']} tickets")
        if len(techs_in_level) > 5:
            print(f"    ... e mais {len(techs_in_level) - 5} técnicos")
    
    # Verificar se há técnicos com nível N/A ou outros
    other_levels = [level for level in level_counts.keys() if level not in ['N1', 'N2', 'N3', 'N4']]
    if other_levels:
        print(f"\n⚠️  Níveis inesperados encontrados: {other_levels}")
        for level in other_levels:
            techs_in_level = [t for t in technicians if t.get('level') == level]
            print(f"  {level}: {[t['name'] for t in techs_in_level[:3]]}")
    
    # Testar determinação de nível para alguns técnicos específicos
    print("\n🧪 Testando determinação de nível para técnicos específicos:")
    test_names = [
        "Gabriel Conceição",
        "Anderson Oliveira", 
        "Wagner Mengue",
        "Silvio Valim",
        "Jonathan Moletta",
        "Thales Leite"
    ]
    
    for name in test_names:
        level = glpi_service._get_technician_level_by_name(name)
        print(f"  {name}: {level}")
    
    print("\n✅ Debug dos níveis no ranking concluído!")

if __name__ == "__main__":
    debug_ranking_levels()