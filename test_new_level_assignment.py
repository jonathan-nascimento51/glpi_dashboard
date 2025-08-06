#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a nova implementação de classificação de técnicos por grupos do GLPI

Este script irá:
1. Testar a nova lógica de atribuição de níveis baseada nos grupos do GLPI
2. Verificar se os técnicos estão sendo classificados corretamente
3. Mostrar o mapeamento atual dos técnicos por nível
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_technician_level_assignment():
    """Testa a nova implementação de classificação de técnicos"""
    
    print("=" * 80)
    print("TESTE DA NOVA CLASSIFICAÇÃO DE TÉCNICOS POR GRUPOS DO GLPI")
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
    
    print("\n1. MAPEAMENTO ESPERADO:")
    for level, names in expected_mapping.items():
        print(f"   {level}: {len(names)} técnicos")
        for name in names:
            print(f"      - {name.title()}")
    
    print("\n2. TESTANDO CLASSIFICAÇÃO ATUAL:")
    
    try:
        # Obter ranking de técnicos
        ranking_data = glpi_service.get_technician_ranking()
        
        if not ranking_data:
            print("   ❌ Erro: Não foi possível obter dados do ranking")
            return
        
        # Agrupar técnicos por nível
        technicians_by_level = {'N1': [], 'N2': [], 'N3': [], 'N4': []}
        
        for tech in ranking_data:
            level = tech.get('level', 'N1')
            name = tech.get('name', 'Nome não encontrado')
            user_id = tech.get('user_id', 'ID não encontrado')
            total_tickets = tech.get('total_tickets', 0)
            
            technicians_by_level[level].append({
                'name': name,
                'user_id': user_id,
                'total_tickets': total_tickets
            })
        
        print("\n3. RESULTADO DA CLASSIFICAÇÃO:")
        total_classified = 0
        
        for level in ['N4', 'N3', 'N2', 'N1']:  # Ordem decrescente
            techs = technicians_by_level[level]
            total_classified += len(techs)
            
            print(f"\n   {level}: {len(techs)} técnicos")
            
            if techs:
                for tech in sorted(techs, key=lambda x: x['total_tickets'], reverse=True):
                    print(f"      - {tech['name']} (ID: {tech['user_id']}, Tickets: {tech['total_tickets']})")
            else:
                print("      (Nenhum técnico classificado)")
        
        print(f"\n4. RESUMO:")
        print(f"   Total de técnicos classificados: {total_classified}")
        
        # Verificar se a distribuição está correta
        print("\n5. VERIFICAÇÃO DA DISTRIBUIÇÃO:")
        
        expected_totals = {level: len(names) for level, names in expected_mapping.items()}
        actual_totals = {level: len(techs) for level, techs in technicians_by_level.items()}
        
        all_correct = True
        for level in ['N1', 'N2', 'N3', 'N4']:
            expected = expected_totals[level]
            actual = actual_totals[level]
            status = "✅" if expected == actual else "❌"
            
            print(f"   {level}: Esperado {expected}, Atual {actual} {status}")
            
            if expected != actual:
                all_correct = False
        
        if all_correct:
            print("\n   🎉 SUCESSO: Todos os técnicos foram classificados corretamente!")
        else:
            print("\n   ⚠️  ATENÇÃO: Há discrepâncias na classificação.")
            print("      Isso pode indicar que:")
            print("      - Alguns técnicos não estão nos grupos corretos no GLPI")
            print("      - Os nomes no GLPI não correspondem exatamente aos fornecidos")
            print("      - Alguns técnicos podem estar inativos ou deletados")
        
        # Salvar resultado detalhado
        with open('technician_level_test_results.txt', 'w', encoding='utf-8') as f:
            f.write("RESULTADO DO TESTE DE CLASSIFICAÇÃO DE TÉCNICOS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("MAPEAMENTO ESPERADO:\n")
            for level, names in expected_mapping.items():
                f.write(f"{level}: {len(names)} técnicos\n")
                for name in names:
                    f.write(f"  - {name.title()}\n")
                f.write("\n")
            
            f.write("RESULTADO ATUAL:\n")
            for level in ['N4', 'N3', 'N2', 'N1']:
                techs = technicians_by_level[level]
                f.write(f"{level}: {len(techs)} técnicos\n")
                for tech in sorted(techs, key=lambda x: x['total_tickets'], reverse=True):
                    f.write(f"  - {tech['name']} (ID: {tech['user_id']}, Tickets: {tech['total_tickets']})\n")
                f.write("\n")
            
            f.write(f"Total de técnicos: {total_classified}\n")
        
        print(f"\n   📄 Resultado detalhado salvo em: technician_level_test_results.txt")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        print(f"   ❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    test_technician_level_assignment()