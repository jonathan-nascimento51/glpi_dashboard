#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir a classificação atual dos técnicos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_current_classification():
    """Verifica a classificação atual e mostra os problemas"""
    
    print("=" * 80)
    print("VERIFICAÇÃO DA CLASSIFICAÇÃO ATUAL DOS TÉCNICOS")
    print("=" * 80)
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Mapeamento correto esperado
    expected_mapping = {
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
    
    print("\n1. MAPEAMENTO ESPERADO:")
    for level, names in expected_mapping.items():
        print(f"   {level}: {len(names)} técnicos")
        for name in names:
            print(f"      - {name.title()}")
    
    print("\n2. OBTENDO CLASSIFICAÇÃO ATUAL DO SISTEMA:")
    
    try:
        # Obter ranking atual
        ranking_data = glpi_service.get_technician_ranking()
        
        if not ranking_data:
            print("   ❌ Erro: Não foi possível obter dados do ranking")
            return
        
        print(f"   ✅ Encontrados {len(ranking_data)} técnicos")
        
        # Agrupar por nível atual
        current_classification = {'N1': [], 'N2': [], 'N3': [], 'N4': []}
        
        for tech in ranking_data:
            level = tech.get('level', 'N1')
            name = tech.get('name', '').lower()
            current_classification[level].append(name)
        
        print("\n3. CLASSIFICAÇÃO ATUAL:")
        for level in ['N1', 'N2', 'N3', 'N4']:
            names = current_classification[level]
            print(f"   {level}: {len(names)} técnicos")
            for name in names:
                print(f"      - {name.title()}")
        
        print("\n4. ANÁLISE DE DISCREPÂNCIAS:")
        
        all_problems = []
        
        for level in ['N1', 'N2', 'N3', 'N4']:
            expected = set(expected_mapping[level])
            current = set(current_classification[level])
            
            # Técnicos que deveriam estar neste nível mas não estão
            missing = expected - current
            # Técnicos que estão neste nível mas não deveriam
            extra = current - expected
            
            if missing or extra:
                print(f"\n   {level}:")
                if missing:
                    print(f"      ❌ FALTANDO ({len(missing)}):")
                    for name in missing:
                        print(f"         - {name.title()}")
                        all_problems.append(f"{name} deveria estar em {level}")
                
                if extra:
                    print(f"      ⚠️  EXTRAS ({len(extra)}):")
                    for name in extra:
                        print(f"         - {name.title()}")
                        # Encontrar onde deveria estar
                        correct_level = None
                        for exp_level, exp_names in expected_mapping.items():
                            if name in exp_names:
                                correct_level = exp_level
                                break
                        if correct_level:
                            all_problems.append(f"{name} está em {level} mas deveria estar em {correct_level}")
                        else:
                            all_problems.append(f"{name} está em {level} mas não está no mapeamento esperado")
        
        print(f"\n5. RESUMO DOS PROBLEMAS ({len(all_problems)} encontrados):")
        for i, problem in enumerate(all_problems, 1):
            print(f"   {i:2d}. {problem.title()}")
        
        # Salvar relatório
        with open('classification_problems_report.txt', 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE PROBLEMAS NA CLASSIFICAÇÃO\n")
            f.write("=" * 40 + "\n\n")
            
            f.write("MAPEAMENTO ESPERADO:\n")
            for level, names in expected_mapping.items():
                f.write(f"{level}: {len(names)} técnicos\n")
                for name in names:
                    f.write(f"  - {name.title()}\n")
                f.write("\n")
            
            f.write("CLASSIFICAÇÃO ATUAL:\n")
            for level in ['N1', 'N2', 'N3', 'N4']:
                names = current_classification[level]
                f.write(f"{level}: {len(names)} técnicos\n")
                for name in names:
                    f.write(f"  - {name.title()}\n")
                f.write("\n")
            
            f.write("PROBLEMAS ENCONTRADOS:\n")
            for i, problem in enumerate(all_problems, 1):
                f.write(f"{i:2d}. {problem.title()}\n")
        
        print(f"\n💾 Relatório detalhado salvo em: classification_problems_report.txt")
        
        # Sugerir correção
        if all_problems:
            print("\n6. SUGESTÃO DE CORREÇÃO:")
            print("   O problema parece estar na lógica de matching dos nomes.")
            print("   Vou verificar se os nomes estão sendo comparados corretamente.")
            
            # Testar matching individual
            print("\n7. TESTE DE MATCHING INDIVIDUAL:")
            for tech in ranking_data[:5]:  # Testar apenas os primeiros 5
                name = tech.get('name', '').lower()
                level = tech.get('level', 'N1')
                
                print(f"\n   Técnico: {name.title()} -> Classificado como: {level}")
                
                # Verificar em qual nível deveria estar
                correct_level = None
                for exp_level, exp_names in expected_mapping.items():
                    if name in exp_names:
                        correct_level = exp_level
                        break
                
                if correct_level:
                    if correct_level == level:
                        print(f"      ✅ CORRETO: Deveria estar em {correct_level}")
                    else:
                        print(f"      ❌ ERRO: Deveria estar em {correct_level}, mas está em {level}")
                else:
                    print(f"      ⚠️  AVISO: Nome não encontrado no mapeamento esperado")
        
        glpi_service.close_session()
        
    except Exception as e:
        logger.error(f"Erro na verificação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_current_classification()