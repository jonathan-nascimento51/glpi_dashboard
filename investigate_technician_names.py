#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar os nomes exatos dos técnicos no GLPI

Este script irá:
1. Buscar todos os técnicos ativos
2. Mostrar os nomes exatos como estão no GLPI
3. Comparar com o mapeamento esperado
4. Sugerir correções no mapeamento
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging
from difflib import SequenceMatcher

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def similarity(a, b):
    """Calcula a similaridade entre duas strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def investigate_technician_names():
    """Investiga os nomes exatos dos técnicos no GLPI"""
    
    print("=" * 80)
    print("INVESTIGAÇÃO DOS NOMES DOS TÉCNICOS NO GLPI")
    print("=" * 80)
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Mapeamento esperado dos técnicos
    expected_mapping = {
        'N1': ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez'],
        'N2': ['alessandro carbonera vieira', 'edson joel dos santos silva', 
               'luciano marcelino da silva', 'jonathan nascimento moletta',
               'leonardo trojan repiso riela', 'thales vinicius paz leite'],
        'N3': ['jorge antonio vicente junior', 'anderson da silva morim de oliveira',
               'miguelangelo ferreira', 'silvio godinho valim', 'pablo hebling guimaraes'],
        'N4': ['paulo cesar pedo nunes', 'luciano de araujo silva', 'wagner mengue',
               'alexandre rovinski almoarqueg', 'gabriel silva machado']
    }
    
    # Criar lista plana de todos os nomes esperados
    all_expected_names = []
    expected_level_map = {}
    for level, names in expected_mapping.items():
        for name in names:
            all_expected_names.append(name)
            expected_level_map[name] = level
    
    print("\n1. BUSCANDO TÉCNICOS ATIVOS NO GLPI...")
    
    try:
        # Obter ranking de técnicos
        ranking_data = glpi_service.get_technician_ranking()
        
        if not ranking_data:
            print("   ❌ Erro: Não foi possível obter dados do ranking")
            return
        
        print(f"   ✅ Encontrados {len(ranking_data)} técnicos ativos")
        
        print("\n2. NOMES EXATOS NO GLPI:")
        
        glpi_names = []
        name_mapping = {}
        
        for i, tech in enumerate(ranking_data, 1):
            name = tech.get('name', 'Nome não encontrado')
            user_id = tech.get('user_id', 'ID não encontrado')
            glpi_names.append(name.lower())
            name_mapping[name.lower()] = {
                'original': name,
                'user_id': user_id
            }
            print(f"   {i:2d}. {name} (ID: {user_id})")
        
        print("\n3. ANÁLISE DE CORRESPONDÊNCIA:")
        
        matches = []
        unmatched_expected = []
        unmatched_glpi = glpi_names.copy()
        
        for expected_name in all_expected_names:
            best_match = None
            best_similarity = 0
            
            for glpi_name in glpi_names:
                sim = similarity(expected_name, glpi_name)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match = glpi_name
            
            if best_similarity > 0.7:  # Threshold de similaridade
                matches.append({
                    'expected': expected_name,
                    'glpi': best_match,
                    'similarity': best_similarity,
                    'level': expected_level_map[expected_name],
                    'glpi_original': name_mapping[best_match]['original'],
                    'user_id': name_mapping[best_match]['user_id']
                })
                if best_match in unmatched_glpi:
                    unmatched_glpi.remove(best_match)
            else:
                unmatched_expected.append(expected_name)
        
        print("\n   CORRESPONDÊNCIAS ENCONTRADAS:")
        for match in sorted(matches, key=lambda x: x['level']):
            status = "✅" if match['similarity'] > 0.9 else "⚠️"
            print(f"   {status} {match['level']}: {match['expected']}")
            print(f"      → {match['glpi_original']} (ID: {match['user_id']}, Sim: {match['similarity']:.2f})")
        
        if unmatched_expected:
            print("\n   NOMES ESPERADOS NÃO ENCONTRADOS:")
            for name in unmatched_expected:
                level = expected_level_map[name]
                print(f"   ❌ {level}: {name}")
        
        if unmatched_glpi:
            print("\n   TÉCNICOS NO GLPI SEM CORRESPONDÊNCIA:")
            for name in unmatched_glpi:
                original = name_mapping[name]['original']
                user_id = name_mapping[name]['user_id']
                print(f"   ❓ {original} (ID: {user_id})")
        
        print("\n4. SUGESTÃO DE MAPEAMENTO CORRIGIDO:")
        
        # Gerar mapeamento corrigido
        corrected_mapping = {'N1': [], 'N2': [], 'N3': [], 'N4': []}
        
        for match in matches:
            corrected_mapping[match['level']].append(match['glpi'])
        
        print("\n   CÓDIGO PYTHON PARA ATUALIZAÇÃO:")
        print("   # Mapeamento manual baseado nos nomes reais do GLPI")
        
        for level in ['N1', 'N2', 'N3', 'N4']:
            names = corrected_mapping[level]
            if names:
                names_str = "', '".join(names)
                print(f"   {level.lower()}_names = ['{names_str}']")
            else:
                print(f"   {level.lower()}_names = []")
        
        # Salvar resultado detalhado
        with open('technician_names_investigation.txt', 'w', encoding='utf-8') as f:
            f.write("INVESTIGAÇÃO DOS NOMES DOS TÉCNICOS NO GLPI\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("NOMES EXATOS NO GLPI:\n")
            for i, tech in enumerate(ranking_data, 1):
                name = tech.get('name', 'Nome não encontrado')
                user_id = tech.get('user_id', 'ID não encontrado')
                f.write(f"{i:2d}. {name} (ID: {user_id})\n")
            
            f.write("\nCORRESPONDÊNCIAS ENCONTRADAS:\n")
            for match in sorted(matches, key=lambda x: x['level']):
                f.write(f"{match['level']}: {match['expected']}\n")
                f.write(f"  → {match['glpi_original']} (ID: {match['user_id']}, Similaridade: {match['similarity']:.2f})\n")
            
            if unmatched_expected:
                f.write("\nNOMES ESPERADOS NÃO ENCONTRADOS:\n")
                for name in unmatched_expected:
                    level = expected_level_map[name]
                    f.write(f"{level}: {name}\n")
            
            if unmatched_glpi:
                f.write("\nTÉCNICOS NO GLPI SEM CORRESPONDÊNCIA:\n")
                for name in unmatched_glpi:
                    original = name_mapping[name]['original']
                    user_id = name_mapping[name]['user_id']
                    f.write(f"{original} (ID: {user_id})\n")
            
            f.write("\nMAPEAMENTO CORRIGIDO:\n")
            for level in ['N1', 'N2', 'N3', 'N4']:
                names = corrected_mapping[level]
                f.write(f"{level}: {len(names)} técnicos\n")
                for name in names:
                    original = name_mapping[name]['original']
                    f.write(f"  - {original}\n")
                f.write("\n")
        
        print(f"\n   📄 Resultado detalhado salvo em: technician_names_investigation.txt")
        
    except Exception as e:
        logger.error(f"Erro durante a investigação: {e}")
        print(f"   ❌ Erro durante a investigação: {e}")

if __name__ == "__main__":
    investigate_technician_names()