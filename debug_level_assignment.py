#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar detalhadamente a classificação de técnicos

Este script irá:
1. Simular exatamente o processo de classificação
2. Mostrar cada passo do matching
3. Identificar onde está o problema
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_level_assignment():
    """Debug detalhado da classificação de técnicos"""
    
    print("=" * 80)
    print("DEBUG DETALHADO DA CLASSIFICAÇÃO DE TÉCNICOS")
    print("=" * 80)
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Mapeamento esperado dos técnicos (exatamente como no código)
    expected_mapping = {
        'N1': ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez'],
        'N2': ['alessandro carbonera vieira', 'edson joel dos santos silva', 
               'luciano marcelino da silva', 'jonathan nascimento moletta',
               'leonardo trojan repiso riela', 'thales vinicius paz leite'],
        'N3': ['jorge antonio vicente júnior', 'anderson da silva morim de oliveira',
               'miguelangelo ferreira', 'silvio godinho valim', 'pablo hebling guimaraes'],
        'N4': ['paulo césar pedó nunes', 'luciano de araujo silva', 'wagner mengue',
               'alexandre rovinski almoarqueg', 'gabriel silva machado']
    }
    
    print("\n1. SIMULANDO O PROCESSO DE CLASSIFICAÇÃO:")
    
    try:
        # Obter ranking de técnicos
        ranking_data = glpi_service.get_technician_ranking()
        
        if not ranking_data:
            print("   ❌ Erro: Não foi possível obter dados do ranking")
            return
        
        print(f"   ✅ Encontrados {len(ranking_data)} técnicos")
        
        # Simular o processo de classificação para cada técnico
        classification_results = []
        
        for tech in ranking_data:
            name = tech.get('name', 'Nome não encontrado')
            user_id = tech.get('user_id', 'ID não encontrado')
            
            print(f"\n2. PROCESSANDO: {name} (ID: {user_id})")
            
            # Simular a busca por grupos (que sabemos que não vai funcionar)
            print("   2.1. Tentando buscar grupos do usuário...")
            print("        (Sabemos que isso não vai funcionar pois os grupos não estão configurados)")
            
            # Simular o fallback por nome
            print("   2.2. Usando fallback por nome:")
            user_name_lower = name.lower()
            print(f"        Nome em lowercase: '{user_name_lower}'")
            
            # Testar cada nível
            found_level = None
            
            for level, names in expected_mapping.items():
                print(f"        Testando {level}: {names}")
                
                for expected_name in names:
                    if expected_name in user_name_lower:
                        print(f"        ✅ MATCH! '{expected_name}' encontrado em '{user_name_lower}'")
                        found_level = level
                        break
                    else:
                        print(f"        ❌ '{expected_name}' NÃO encontrado em '{user_name_lower}'")
                
                if found_level:
                    break
            
            if not found_level:
                print("        ⚠️  Nenhum match encontrado - usando N1 como padrão")
                found_level = "N1"
            
            classification_results.append({
                'name': name,
                'user_id': user_id,
                'classified_level': found_level,
                'name_lower': user_name_lower
            })
            
            print(f"        RESULTADO: {name} → {found_level}")
        
        print("\n3. RESUMO DA CLASSIFICAÇÃO:")
        
        # Agrupar por nível
        by_level = {'N1': [], 'N2': [], 'N3': [], 'N4': []}
        
        for result in classification_results:
            by_level[result['classified_level']].append(result)
        
        for level in ['N4', 'N3', 'N2', 'N1']:
            techs = by_level[level]
            expected_count = len(expected_mapping[level])
            actual_count = len(techs)
            status = "✅" if expected_count == actual_count else "❌"
            
            print(f"\n   {level}: {actual_count} técnicos (esperado: {expected_count}) {status}")
            
            for tech in techs:
                print(f"      - {tech['name']}")
        
        print("\n4. ANÁLISE DETALHADA DOS PROBLEMAS:")
        
        # Verificar cada nome esperado
        for level, expected_names in expected_mapping.items():
            print(f"\n   {level} - Verificando nomes esperados:")
            
            for expected_name in expected_names:
                found = False
                for result in classification_results:
                    if result['classified_level'] == level and expected_name in result['name_lower']:
                        found = True
                        print(f"      ✅ '{expected_name}' → {result['name']}")
                        break
                
                if not found:
                    print(f"      ❌ '{expected_name}' NÃO ENCONTRADO")
                    
                    # Procurar onde esse nome foi parar
                    for other_level, other_results in by_level.items():
                        if other_level != level:
                            for result in other_results:
                                if expected_name in result['name_lower']:
                                    print(f"         → Encontrado em {other_level}: {result['name']}")
                                    break
        
        print("\n5. POSSÍVEIS SOLUÇÕES:")
        print("   1. Verificar se os nomes estão exatamente corretos")
        print("   2. Usar matching mais flexível (substring parcial)")
        print("   3. Implementar matching por similaridade")
        print("   4. Configurar os grupos corretamente no GLPI")
        
        # Salvar debug detalhado
        with open('debug_level_assignment.txt', 'w', encoding='utf-8') as f:
            f.write("DEBUG DETALHADO DA CLASSIFICAÇÃO DE TÉCNICOS\n")
            f.write("=" * 50 + "\n\n")
            
            for result in classification_results:
                f.write(f"Nome: {result['name']}\n")
                f.write(f"Nome lowercase: {result['name_lower']}\n")
                f.write(f"Nível classificado: {result['classified_level']}\n")
                f.write(f"User ID: {result['user_id']}\n")
                f.write("-" * 30 + "\n")
            
            f.write("\nRESUMO POR NÍVEL:\n")
            for level in ['N4', 'N3', 'N2', 'N1']:
                techs = by_level[level]
                f.write(f"{level}: {len(techs)} técnicos\n")
                for tech in techs:
                    f.write(f"  - {tech['name']}\n")
                f.write("\n")
        
        print(f"\n   📄 Debug detalhado salvo em: debug_level_assignment.txt")
        
    except Exception as e:
        logger.error(f"Erro durante o debug: {e}")
        print(f"   ❌ Erro durante o debug: {e}")

if __name__ == "__main__":
    debug_level_assignment()