#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar um mapeamento completo de todos os técnicos
baseado nos nomes reais obtidos do GLPI.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from services.glpi_service import GLPIService
import json

def generate_complete_mapping():
    print("🔧 GERAÇÃO DE MAPEAMENTO COMPLETO DE TÉCNICOS")
    print("=" * 60)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    try:
        # Inicializar serviço
        service = GLPIService()
        
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        print("✅ Autenticado com sucesso")
        
        print("\n📋 ETAPA 1: Buscar todos os técnicos")
        
        # Buscar usuários com perfil de técnico
        profile_params = {
            "range": "0-999",
            "criteria[0][field]": "4",  # Campo Perfil
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",  # ID do perfil técnico
            "forcedisplay[0]": "2",  # ID do Profile_User
            "forcedisplay[1]": "5",  # Usuário (users_id)
            "forcedisplay[2]": "4",  # Perfil
            "forcedisplay[3]": "80"  # Entidade
        }
        
        response = service._make_authenticated_request(
            'GET',
            f"{service.glpi_url}/search/Profile_User",
            params=profile_params
        )
        
        if not response or not response.ok:
            print("❌ Falha ao buscar técnicos")
            return
        
        profile_result = response.json()
        
        if 'data' not in profile_result or not profile_result['data']:
            print("❌ Nenhum técnico encontrado")
            return
        
        # Extrair IDs dos técnicos
        technician_ids = []
        for item in profile_result['data']:
            if '5' in item:  # Campo users_id
                technician_ids.append(item['5'])
        
        print(f"✅ Encontrados {len(technician_ids)} técnicos")
        
        print("\n📋 ETAPA 2: Obter nomes completos de todos os técnicos")
        
        all_technicians = []
        
        for tech_id in technician_ids:
            try:
                # Obter dados do técnico
                user_response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/User/{tech_id}"
                )
                
                if user_response and user_response.ok:
                    user_data = user_response.json()
                    
                    # Construir nome completo como no método original
                    display_name = ""
                    if "realname" in user_data and "firstname" in user_data:
                        display_name = f"{user_data['firstname']} {user_data['realname']}"
                    elif "realname" in user_data:
                        display_name = user_data["realname"]
                    elif "name" in user_data:
                        display_name = user_data["name"]
                    elif "1" in user_data:
                        display_name = user_data["1"]
                    
                    if display_name and display_name.strip():
                        all_technicians.append({
                            'id': tech_id,
                            'name': display_name.strip(),
                            'name_lower': display_name.lower().strip(),
                            'username': user_data.get('name', tech_id)
                        })
                        print(f"  ✅ {display_name} (ID: {tech_id}, Username: {user_data.get('name', tech_id)})")
                    else:
                        print(f"  ⚠️  Técnico {tech_id}: Nome vazio ou inválido")
                else:
                    print(f"  ❌ Erro ao obter dados do técnico {tech_id}")
                    
            except Exception as e:
                print(f"  ❌ Erro ao processar técnico {tech_id}: {e}")
        
        print(f"\n✅ Processados {len(all_technicians)} técnicos com nomes válidos")
        
        print("\n📋 ETAPA 3: Verificar mapeamento atual")
        
        # Mapeamento atual hardcoded
        current_mapping = {
            'N1': ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez'],
            'N2': ['alessandro carbonera vieira', 'jonathan nascimento moletta', 'thales vinicius paz leite', 
                   'leonardo trojan repiso riela', 'edson joel dos santos silva', 'luciano marcelino da silva'],
            'N3': ['anderson da silva morim de oliveira', 'silvio godinho valim', 'jorge antonio vicente júnior', 
                   'pablo hebling guimaraes', 'miguelangelo ferreira'],
            'N4': ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 
                   'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
        }
        
        # Verificar quais técnicos estão no mapeamento atual
        mapped_technicians = set()
        for level, names in current_mapping.items():
            mapped_technicians.update(names)
        
        unmapped_technicians = []
        mapped_found = []
        
        for tech in all_technicians:
            if tech['name_lower'] in mapped_technicians:
                mapped_found.append(tech)
            else:
                unmapped_technicians.append(tech)
        
        print(f"\n📊 ANÁLISE DO MAPEAMENTO ATUAL:")
        print(f"  ✅ Técnicos já mapeados: {len(mapped_found)}")
        print(f"  ⚠️  Técnicos NÃO mapeados: {len(unmapped_technicians)}")
        
        print("\n📋 TÉCNICOS JÁ MAPEADOS:")
        for tech in mapped_found:
            # Encontrar em qual nível está
            for level, names in current_mapping.items():
                if tech['name_lower'] in names:
                    print(f"  {level}: {tech['name']} (ID: {tech['id']})")
                    break
        
        print("\n📋 TÉCNICOS NÃO MAPEADOS:")
        for tech in unmapped_technicians:
            print(f"  ❓ {tech['name']} (ID: {tech['id']}, Username: {tech['username']})")
        
        print("\n📋 ETAPA 4: Propor distribuição para técnicos não mapeados")
        
        # Distribuir técnicos não mapeados de forma equilibrada
        levels = ['N1', 'N2', 'N3', 'N4']
        current_counts = {level: len(names) for level, names in current_mapping.items()}
        
        print(f"\n📊 DISTRIBUIÇÃO ATUAL:")
        for level, count in current_counts.items():
            print(f"  {level}: {count} técnicos")
        
        # Propor nova distribuição
        proposed_mapping = {level: list(names) for level, names in current_mapping.items()}
        
        # Distribuir técnicos não mapeados de forma equilibrada
        level_index = 0
        for tech in unmapped_technicians:
            level = levels[level_index]
            proposed_mapping[level].append(tech['name_lower'])
            level_index = (level_index + 1) % len(levels)
        
        print(f"\n📊 DISTRIBUIÇÃO PROPOSTA:")
        for level in levels:
            count = len(proposed_mapping[level])
            print(f"  {level}: {count} técnicos")
            for name in proposed_mapping[level]:
                if name not in current_mapping.get(level, []):
                    print(f"    + {name} (NOVO)")
                else:
                    print(f"    - {name}")
        
        print("\n📋 ETAPA 5: Gerar código Python para o novo mapeamento")
        
        python_code = "# Mapeamento completo de técnicos por nível\n"
        python_code += "# Gerado automaticamente em " + str(__import__('datetime').datetime.now()) + "\n\n"
        
        for level in levels:
            python_code += f"{level.lower()}_names = [\n"
            for name in sorted(proposed_mapping[level]):
                python_code += f"    '{name}',\n"
            python_code += "]\n\n"
        
        # Salvar em arquivo
        with open('proposed_technician_mapping.py', 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        # Salvar dados completos em JSON
        mapping_data = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'total_technicians': len(all_technicians),
            'mapped_technicians': len(mapped_found),
            'unmapped_technicians': len(unmapped_technicians),
            'current_mapping': current_mapping,
            'proposed_mapping': proposed_mapping,
            'all_technicians': all_technicians,
            'unmapped_list': unmapped_technicians
        }
        
        with open('complete_technician_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Arquivos gerados:")
        print("  📄 proposed_technician_mapping.py - Código Python para novo mapeamento")
        print("  📄 complete_technician_analysis.json - Análise completa em JSON")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("  1. Revisar a distribuição proposta")
        print("  2. Ajustar manualmente se necessário")
        print("  3. Atualizar o método _get_technician_level no GLPIService")
        print("  4. Testar o ranking com todos os técnicos")
        
        print("\n=" * 60)
        print("✅ GERAÇÃO DE MAPEAMENTO CONCLUÍDA")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_complete_mapping()