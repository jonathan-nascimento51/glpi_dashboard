#!/usr/bin/env python3
"""
Script para investigar todos os grupos existentes no GLPI
e descobrir onde estão os tickets não categorizados nos grupos N1-N4.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from collections import defaultdict

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService

def extract_count_from_response(response):
    """Extrai o count da resposta, seja do cabeçalho ou do corpo JSON"""
    # Primeiro tenta extrair do cabeçalho Content-Range
    content_range = response.headers.get('Content-Range')
    if content_range:
        try:
            total = content_range.split('/')[-1]
            return int(total)
        except (ValueError, IndexError):
            pass
    
    # Se não encontrou no cabeçalho, tenta extrair do corpo JSON
    try:
        data = response.json()
        if isinstance(data, dict):
            # Verifica se tem totalcount
            if 'totalcount' in data:
                return int(data['totalcount'])
            # Verifica se tem content-range no corpo
            if 'content-range' in data:
                content_range = data['content-range']
                total = content_range.split('/')[-1]
                return int(total)
        # Se é uma lista, retorna o tamanho
        elif isinstance(data, list):
            return len(data)
    except:
        pass
    
    return 0

def main():
    print("=== INVESTIGAÇÃO DE TODOS OS GRUPOS GLPI ===")
    
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
        session_token = headers.get('Session-Token', 'N/A')[:20] + '...'
        app_token = headers.get('App-Token', 'N/A')[:20] + '...' 
        print(f"🔑 Headers obtidos com sucesso")
        print(f"🔑 Session Token: {session_token}")
        print(f"🔑 App Token: {app_token}")
        print()
        
        # 1. Listar todos os grupos disponíveis
        print("1. Obtendo lista de todos os grupos...")
        try:
            response = requests.get(f"{base_url}/Group", headers=headers)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 206]:
                groups_data = response.json()
                if isinstance(groups_data, list) and groups_data:
                    print(f"   ✅ Encontrados {len(groups_data)} grupos")
                    print("\n   📋 Lista de grupos:")
                    for group in groups_data[:20]:  # Mostrar apenas os primeiros 20
                        group_id = group.get('id', 'N/A')
                        group_name = group.get('name', 'Sem nome')
                        print(f"      ID: {group_id:>3} | Nome: {group_name}")
                    
                    if len(groups_data) > 20:
                        print(f"      ... e mais {len(groups_data) - 20} grupos")
                else:
                    print("   ⚠️ Nenhum grupo encontrado ou formato inesperado")
            else:
                print(f"   ❌ Erro ao obter grupos: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Erro ao listar grupos: {e}")
        
        print("\n" + "="*60)
        
        # 2. Descobrir field_ids necessários
        print("2. Descobrindo field IDs...")
        if not hasattr(service, 'field_ids') or not service.field_ids:
            service.discover_field_ids()
        
        group_field_id = service.field_ids.get('GROUP')
        if not group_field_id:
            print("   ❌ Field ID para GROUP não encontrado")
            return
        
        print(f"   ✅ Field ID para GROUP: {group_field_id}")
        print()
        
        # 3. Analisar distribuição de tickets por grupo
        print("3. Analisando distribuição de tickets por grupo...")
        
        # Obter todos os tickets com seus grupos
        try:
            # Buscar tickets com informação de grupo
            params = {
                "range": "0-999",  # Limitar para não sobrecarregar
                "forcedisplay[0]": group_field_id,  # Forçar exibição do campo grupo
                "forcedisplay[1]": "1",  # ID do ticket
            }
            
            response = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 206]:
                tickets_data = response.json()
                
                if isinstance(tickets_data, dict) and 'data' in tickets_data:
                    tickets = tickets_data['data']
                    print(f"   ✅ Analisando {len(tickets)} tickets (amostra)")
                    
                    # Contar tickets por grupo
                    group_counts = defaultdict(int)
                    tickets_without_group = 0
                    
                    for ticket in tickets:
                        # O campo grupo pode estar em diferentes posições
                        group_value = None
                        
                        # Tentar encontrar o valor do grupo
                        if isinstance(ticket, dict):
                            # Procurar pelo field_id do grupo
                            group_value = ticket.get(group_field_id)
                            if not group_value:
                                # Tentar outras possibilidades
                                for key, value in ticket.items():
                                    if 'group' in str(key).lower() and value:
                                        group_value = value
                                        break
                        elif isinstance(ticket, list) and len(ticket) > 1:
                            # Se for lista, o grupo pode estar na segunda posição
                            group_value = ticket[1] if len(ticket) > 1 else None
                        
                        if group_value and str(group_value).strip() and str(group_value) != '0':
                            group_counts[str(group_value)] += 1
                        else:
                            tickets_without_group += 1
                    
                    print("\n   📊 Distribuição por grupo (amostra):")
                    
                    # Ordenar por quantidade (decrescente)
                    sorted_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    total_with_group = sum(group_counts.values())
                    total_analyzed = total_with_group + tickets_without_group
                    
                    print(f"      Tickets com grupo: {total_with_group}")
                    print(f"      Tickets sem grupo: {tickets_without_group}")
                    print(f"      Total analisado: {total_analyzed}")
                    print()
                    
                    # Mostrar top 10 grupos
                    print("   🏆 Top 10 grupos com mais tickets:")
                    for i, (group_id, count) in enumerate(sorted_groups[:10], 1):
                        percentage = (count / total_analyzed) * 100 if total_analyzed > 0 else 0
                        # Verificar se é um dos grupos N1-N4
                        level_info = ""
                        if group_id == "89":
                            level_info = " (N1)"
                        elif group_id == "90":
                            level_info = " (N2)"
                        elif group_id == "91":
                            level_info = " (N3)"
                        elif group_id == "92":
                            level_info = " (N4)"
                        
                        print(f"      {i:>2}. Grupo {group_id}{level_info}: {count:>4} tickets ({percentage:.2f}%)")
                    
                    if tickets_without_group > 0:
                        percentage = (tickets_without_group / total_analyzed) * 100
                        print(f"      --. Sem grupo: {tickets_without_group:>4} tickets ({percentage:.2f}%)")
                    
                else:
                    print("   ⚠️ Formato de resposta inesperado")
                    print(f"   Resposta: {str(tickets_data)[:200]}")
            else:
                print(f"   ❌ Erro ao obter tickets: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro ao analisar distribuição: {e}")
        
        print("\n" + "="*60)
        
        # 4. Verificar grupos N1-N4 especificamente
        print("4. Verificação específica dos grupos N1-N4...")
        
        n_groups = {
            "N1": "89",
            "N2": "90", 
            "N3": "91",
            "N4": "92"
        }
        
        for level, group_id in n_groups.items():
            try:
                params = {
                    f"criteria[0][field]": group_field_id,
                    f"criteria[0][searchtype]": "equals",
                    f"criteria[0][value]": group_id
                }
                
                response = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params)
                
                if response.status_code in [200, 206]:
                    count = extract_count_from_response(response)
                    print(f"   {level} (Grupo {group_id}): {count} tickets")
                else:
                    print(f"   {level} (Grupo {group_id}): Erro {response.status_code}")
                    
            except Exception as e:
                print(f"   {level} (Grupo {group_id}): Erro - {e}")
        
        print("\n=== INVESTIGAÇÃO CONCLUÍDA ===")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()