#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o mapeamento de níveis baseado nos resultados do debug
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_level_mapping():
    """Corrige o mapeamento de níveis baseado no debug anterior"""
    
    print("=" * 80)
    print("CORREÇÃO DO MAPEAMENTO DE NÍVEIS")
    print("=" * 80)
    
    # Mapeamento correto baseado no debug_level_assignment.txt
    correct_mapping = {
        'N1': ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez'],
        'N2': ['alessandro carbonera vieira', 'jonathan nascimento moletta', 
               'thales vinicius paz leite', 'leonardo trojan repiso riela',
               'edson joel dos santos silva', 'luciano marcelino da silva'],
        'N3': ['anderson da silva morim de oliveira', 'silvio godinho valim',
               'jorge antonio vicente júnior', 'pablo hebling guimaraes', 
               'miguelangelo ferreira'],
        'N4': ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue',
               'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
    }
    
    print("\n1. MAPEAMENTO CORRETO (baseado no debug):")
    for level, names in correct_mapping.items():
        print(f"   {level}: {len(names)} técnicos")
        for name in names:
            print(f"      - {name.title()}")
    
    # Gerar código Python para atualizar o glpi_service.py
    print("\n2. CÓDIGO PYTHON PARA ATUALIZAR O MAPEAMENTO:")
    print("-" * 50)
    print("# Substitua as listas no método _get_technician_level por:")
    print()
    print(f"n1_names = {correct_mapping['N1']}")
    print(f"n2_names = {correct_mapping['N2']}")
    print(f"n3_names = {correct_mapping['N3']}")
    print(f"n4_names = {correct_mapping['N4']}")
    
    # Salvar em arquivo
    with open('corrected_level_mapping.txt', 'w', encoding='utf-8') as f:
        f.write("MAPEAMENTO CORRETO DE NÍVEIS\n")
        f.write("=" * 30 + "\n\n")
        
        for level, names in correct_mapping.items():
            f.write(f"{level}: {len(names)} técnicos\n")
            for name in names:
                f.write(f"  - {name.title()}\n")
            f.write("\n")
        
        f.write("\nCÓDIGO PYTHON:\n")
        f.write(f"n1_names = {correct_mapping['N1']}\n")
        f.write(f"n2_names = {correct_mapping['N2']}\n")
        f.write(f"n3_names = {correct_mapping['N3']}\n")
        f.write(f"n4_names = {correct_mapping['N4']}\n")
    
    print(f"\n💾 Mapeamento correto salvo em: corrected_level_mapping.txt")
    
    # Testar se conseguimos aplicar a correção automaticamente
    print("\n3. APLICANDO CORREÇÃO AUTOMATICAMENTE...")
    
    try:
        # Ler o arquivo atual
        glpi_file_path = 'backend/services/glpi_service.py'
        with open(glpi_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontrar e substituir as listas
        old_n1 = "n1_names = ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez']"
        old_n2 = """n2_names = ['alessandro carbonera vieira', 'edson joel dos santos silva', 
                               'luciano marcelino da silva', 'jonathan nascimento moletta',
                               'leonardo trojan repiso riela', 'thales vinicius paz leite']"""
        old_n3 = """n3_names = ['jorge antonio vicente júnior', 'anderson da silva morim de oliveira',
                               'miguelangelo ferreira', 'silvio godinho valim', 'pablo hebling guimaraes']"""
        old_n4 = """n4_names = ['paulo césar pedó nunes', 'luciano de araujo silva', 'wagner mengue',
                               'alexandre rovinski almoarqueg', 'gabriel silva machado']"""
        
        new_n1 = f"n1_names = {correct_mapping['N1']}"
        new_n2 = f"n2_names = {correct_mapping['N2']}"
        new_n3 = f"n3_names = {correct_mapping['N3']}"
        new_n4 = f"n4_names = {correct_mapping['N4']}"
        
        # Aplicar substituições
        if old_n1 in content:
            content = content.replace(old_n1, new_n1)
            print("   ✅ Lista N1 atualizada")
        
        # Para N2, N3, N4 vamos usar uma abordagem mais simples
        # Procurar por padrões mais específicos
        import re
        
        # Substituir N2
        n2_pattern = r"n2_names = \[.*?\]"
        if re.search(n2_pattern, content, re.DOTALL):
            content = re.sub(n2_pattern, new_n2, content, flags=re.DOTALL)
            print("   ✅ Lista N2 atualizada")
        
        # Substituir N3
        n3_pattern = r"n3_names = \[.*?\]"
        if re.search(n3_pattern, content, re.DOTALL):
            content = re.sub(n3_pattern, new_n3, content, flags=re.DOTALL)
            print("   ✅ Lista N3 atualizada")
        
        # Substituir N4
        n4_pattern = r"n4_names = \[.*?\]"
        if re.search(n4_pattern, content, re.DOTALL):
            content = re.sub(n4_pattern, new_n4, content, flags=re.DOTALL)
            print("   ✅ Lista N4 atualizada")
        
        # Salvar o arquivo atualizado
        with open(glpi_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n🎉 CORREÇÃO APLICADA COM SUCESSO!")
        print("   O arquivo glpi_service.py foi atualizado com o mapeamento correto.")
        
    except Exception as e:
        print(f"\n❌ Erro ao aplicar correção automaticamente: {e}")
        print("   Por favor, aplique a correção manualmente usando o código gerado.")

if __name__ == "__main__":
    fix_level_mapping()