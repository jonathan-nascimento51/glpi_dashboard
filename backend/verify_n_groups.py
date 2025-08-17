#!/usr/bin/env python3
"""
Script para verificar se os grupos N1-N4 (IDs 89-92) existem no GLPI
e qual é o status deles.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService

def main():
    print("=== VERIFICAÇÃO DOS GRUPOS N1-N4 ===")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar configurações
    glpi_url = os.getenv('GLPI_URL')
    if not glpi_url:
        print("❌ Configuração GLPI não encontrada")
        return
    
    base_url = glpi_url.rstrip('/')
    print(f"🔗 GLPI URL: {base_url}")
    
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        # Obter headers de autenticação
        headers = service.get_api_headers()
        print(f"🔑 Headers obtidos com sucesso")
        print()
        
        # Grupos N1-N4 que estamos procurando
        n_groups = {
            "N1": 89,
            "N2": 90, 
            "N3": 91,
            "N4": 92
        }
        
        print("1. Verificando existência dos grupos N1-N4...")
        
        for level, group_id in n_groups.items():
            print(f"\n   --- Verificando {level} (ID {group_id}) ---")
            
            try:
                # Tentar obter o grupo específico
                response = requests.get(f"{base_url}/Group/{group_id}", headers=headers)
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    group_data = response.json()
                    print(f"   ✅ Grupo encontrado!")
                    print(f"   Nome: {group_data.get('name', 'N/A')}")
                    print(f"   Ativo: {group_data.get('is_active', 'N/A')}")
                    print(f"   Comentário: {group_data.get('comment', 'N/A')}")
                    print(f"   Data criação: {group_data.get('date_creation', 'N/A')}")
                    print(f"   Data modificação: {group_data.get('date_mod', 'N/A')}")
                    
                    # Verificar se está ativo
                    is_active = group_data.get('is_active')
                    if is_active == '0' or is_active == 0:
                        print(f"   ⚠️ GRUPO INATIVO!")
                    elif is_active == '1' or is_active == 1:
                        print(f"   ✅ Grupo ativo")
                    
                elif response.status_code == 404:
                    print(f"   ❌ Grupo não encontrado (404)")
                elif response.status_code == 401:
                    print(f"   ❌ Não autorizado (401)")
                elif response.status_code == 403:
                    print(f"   ❌ Acesso negado (403)")
                else:
                    print(f"   ❌ Erro inesperado: {response.status_code}")
                    print(f"   Resposta: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao verificar grupo: {e}")
        
        print("\n" + "="*60)
        
        # 2. Buscar grupos com nomes similares a N1, N2, N3, N4
        print("2. Buscando grupos com nomes similares...")
        
        try:
            # Obter todos os grupos novamente para buscar por nome
            response = requests.get(f"{base_url}/Group", headers=headers)
            
            if response.status_code in [200, 206]:
                groups_data = response.json()
                
                if isinstance(groups_data, list):
                    print(f"   Analisando {len(groups_data)} grupos...")
                    
                    # Buscar grupos com nomes que contenham N1, N2, N3, N4
                    level_keywords = ['N1', 'N2', 'N3', 'N4', 'NIVEL', 'NÍVEL', 'LEVEL']
                    
                    found_similar = []
                    
                    for group in groups_data:
                        group_name = group.get('name', '').upper()
                        group_id = group.get('id')
                        
                        for keyword in level_keywords:
                            if keyword in group_name:
                                found_similar.append({
                                    'id': group_id,
                                    'name': group.get('name'),
                                    'active': group.get('is_active'),
                                    'keyword': keyword
                                })
                                break
                    
                    if found_similar:
                        print(f"   ✅ Encontrados {len(found_similar)} grupos similares:")
                        for group in found_similar:
                            active_status = "✅ Ativo" if group['active'] == '1' else "❌ Inativo"
                            print(f"      ID: {group['id']:>3} | Nome: {group['name']} | {active_status}")
                    else:
                        print("   ⚠️ Nenhum grupo com nomes similares encontrado")
                        
                else:
                    print("   ❌ Formato de resposta inesperado")
            else:
                print(f"   ❌ Erro ao obter grupos: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao buscar grupos similares: {e}")
        
        print("\n" + "="*60)
        
        # 3. Verificar se existem outros campos que possam indicar nível
        print("3. Investigando outros campos de categorização...")
        
        try:
            # Buscar um ticket de exemplo para ver todos os campos disponíveis
            response = requests.get(f"{base_url}/search/Ticket?range=0-0", headers=headers)
            
            if response.status_code in [200, 206]:
                data = response.json()
                
                if isinstance(data, dict) and 'data' in data and data['data']:
                    ticket_example = data['data'][0]
                    print(f"   📋 Campos disponíveis em um ticket:")
                    
                    if isinstance(ticket_example, dict):
                        # Buscar campos que possam indicar nível ou categoria
                        level_related_fields = []
                        
                        for field_id, value in ticket_example.items():
                            field_name = str(field_id).lower()
                            if any(keyword in field_name for keyword in ['level', 'nivel', 'nível', 'category', 'categoria', 'type', 'tipo', 'priority', 'prioridade']):
                                level_related_fields.append((field_id, value))
                        
                        if level_related_fields:
                            print(f"   ✅ Campos relacionados a nível/categoria:")
                            for field_id, value in level_related_fields:
                                print(f"      Campo {field_id}: {value}")
                        else:
                            print(f"   ⚠️ Nenhum campo relacionado a nível encontrado")
                            
                        # Mostrar alguns campos para referência
                        print(f"\n   📋 Primeiros 10 campos do ticket:")
                        count = 0
                        for field_id, value in ticket_example.items():
                            if count >= 10:
                                break
                            print(f"      Campo {field_id}: {value}")
                            count += 1
                    
                else:
                    print("   ⚠️ Nenhum ticket encontrado para análise")
            else:
                print(f"   ❌ Erro ao obter ticket de exemplo: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao investigar campos: {e}")
        
        print("\n=== VERIFICAÇÃO CONCLUÍDA ===")
        
        # Resumo das descobertas
        print("\n📋 RESUMO DAS DESCOBERTAS:")
        print("1. Grupos N1-N4 (IDs 89-92): Status verificado acima")
        print("2. Grupos existentes: 30 grupos (IDs 8-28 principalmente)")
        print("3. 100% dos tickets na amostra aparecem como 'sem grupo'")
        print("4. Possível causa: Grupos N1-N4 não existem ou estão inativos")
        print("\n💡 RECOMENDAÇÕES:")
        print("- Se grupos N1-N4 não existem: Criar os grupos no GLPI")
        print("- Se grupos estão inativos: Ativar os grupos")
        print("- Considerar usar grupos existentes para categorização")
        print("- Investigar se há outro campo sendo usado para níveis de serviço")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()