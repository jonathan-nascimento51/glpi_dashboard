#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o método atual de ranking de técnicos
e identificar onde está o problema que causa apenas N2 e N3 aparecerem.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.glpi_service import GLPIService
import json
from datetime import datetime

def test_current_ranking_method():
    """Testa o método atual de ranking para identificar o problema"""
    print("=== TESTE DO MÉTODO ATUAL DE RANKING ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Inicializar serviço
    glpi_service = GLPIService()
    
    # Testar autenticação
    print("\n1. Testando autenticação...")
    if not glpi_service.authenticate():
        print("❌ ERRO: Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Testar método get_technician_ranking (sem filtros)
    print("\n2. Testando get_technician_ranking (método principal)...")
    try:
        ranking = glpi_service.get_technician_ranking()
        print(f"✅ Ranking obtido: {len(ranking)} técnicos")
        
        if ranking:
            print("\n=== ANÁLISE DO RANKING ATUAL ===")
            
            # Contar por nível
            level_counts = {}
            for tech in ranking:
                level = tech.get('level', 'Desconhecido')
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print("\nDistribuição por nível:")
            for level, count in sorted(level_counts.items()):
                print(f"  {level}: {count} técnicos")
            
            print("\nPrimeiros 10 técnicos:")
            for i, tech in enumerate(ranking[:10]):
                print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('level', 'N/A')} - {tech.get('total', 0)} tickets")
            
            # Verificar se há técnicos N1 e N4
            n1_techs = [t for t in ranking if t.get('level') == 'N1']
            n4_techs = [t for t in ranking if t.get('level') == 'N4']
            
            print(f"\n=== ANÁLISE ESPECÍFICA ===")
            print(f"Técnicos N1: {len(n1_techs)}")
            if n1_techs:
                print("Técnicos N1 encontrados:")
                for tech in n1_techs[:5]:
                    print(f"  - {tech.get('name', 'N/A')} ({tech.get('total', 0)} tickets)")
            
            print(f"\nTécnicos N4: {len(n4_techs)}")
            if n4_techs:
                print("Técnicos N4 encontrados:")
                for tech in n4_techs[:5]:
                    print(f"  - {tech.get('name', 'N/A')} ({tech.get('total', 0)} tickets)")
            
            # Salvar resultado completo para análise
            with open('ranking_atual_completo.json', 'w', encoding='utf-8') as f:
                json.dump(ranking, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Ranking completo salvo em 'ranking_atual_completo.json'")
        else:
            print("❌ ERRO: Ranking vazio")
            
    except Exception as e:
        print(f"❌ ERRO no get_technician_ranking: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
    
    # Testar método _get_technician_ranking_knowledge_base diretamente
    print("\n3. Testando _get_technician_ranking_knowledge_base (método interno)...")
    try:
        ranking_kb = glpi_service._get_technician_ranking_knowledge_base()
        print(f"✅ Ranking KB obtido: {len(ranking_kb)} técnicos")
        
        if ranking_kb:
            # Contar por nível
            level_counts_kb = {}
            for tech in ranking_kb:
                level = tech.get('level', 'Desconhecido')
                level_counts_kb[level] = level_counts_kb.get(level, 0) + 1
            
            print("\nDistribuição por nível (método KB):")
            for level, count in sorted(level_counts_kb.items()):
                print(f"  {level}: {count} técnicos")
        
    except Exception as e:
        print(f"❌ ERRO no _get_technician_ranking_knowledge_base: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
    
    # Testar busca de usuários com perfil ID 6
    print("\n4. Testando busca direta de usuários com perfil ID 6...")
    try:
        profile_params = {
            "range": "0-999",
            "criteria[0][field]": "4",  # Campo Perfil na tabela Profile_User
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",  # ID do perfil técnico
            "forcedisplay[0]": "2",  # ID do Profile_User
            "forcedisplay[1]": "5",  # Usuário (users_id)
            "forcedisplay[2]": "4",  # Perfil
            "forcedisplay[3]": "80"  # Entidade
        }
        
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Profile_User",
            params=profile_params
        )
        
        if response and response.ok:
            profile_result = response.json()
            total_count = profile_result.get('totalcount', 0)
            print(f"✅ Usuários com perfil ID 6: {total_count}")
            
            if total_count > 0:
                profile_data = profile_result.get('data', [])
                print(f"Dados encontrados: {len(profile_data)} registros")
                
                # Mostrar alguns exemplos
                print("\nPrimeiros 5 usuários com perfil ID 6:")
                for i, user in enumerate(profile_data[:5]):
                    print(f"  {i+1}. {user}")
            else:
                print("❌ PROBLEMA: Nenhum usuário encontrado com perfil ID 6")
                print("   Isso explica por que o ranking está vazio ou limitado!")
        else:
            print(f"❌ ERRO na busca de Profile_User: {response.status_code if response else 'Sem resposta'}")
            
    except Exception as e:
        print(f"❌ ERRO na busca de perfil ID 6: {e}")
    
    # Verificar se existe um arquivo de log de debug
    print("\n5. Verificando logs de debug...")
    debug_log_path = 'debug_technician_ranking.log'
    if os.path.exists(debug_log_path):
        print(f"✅ Log de debug encontrado: {debug_log_path}")
        try:
            with open(debug_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print(f"   Total de linhas no log: {len(lines)}")
            
            # Mostrar últimas 10 linhas
            print("\nÚltimas 10 linhas do log:")
            for line in lines[-10:]:
                print(f"   {line.strip()}")
        except Exception as e:
            print(f"❌ ERRO ao ler log: {e}")
    else:
        print(f"⚠️  Log de debug não encontrado: {debug_log_path}")
    
    print("\n=== CONCLUSÕES ===")
    print("1. Se o ranking atual tem técnicos, mas apenas N2 e N3, o problema pode estar:")
    print("   - Na lógica de determinação de níveis (_get_technician_level)")
    print("   - No mapeamento de nomes para níveis")
    print("   - Na busca de grupos dos usuários")
    print("\n2. Se nenhum usuário foi encontrado com perfil ID 6:")
    print("   - O problema está na configuração de perfis no GLPI")
    print("   - Os técnicos podem estar em outros perfis (13, 14, 15)")
    print("\n3. Verifique o arquivo 'ranking_atual_completo.json' para análise detalhada")

if __name__ == "__main__":
    test_current_ranking_method()