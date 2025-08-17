#!/usr/bin/env python3
"""
Script para investigar a distribuição de tickets entre grupos e identificar
tickets não associados aos grupos N1-N4.
"""

import sys
sys.path.append('.')

from services.glpi_service import GLPIService
import json
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    print("=== INVESTIGAÇÃO DA DISTRIBUIÇÃO DE TICKETS ===")
    
    service = GLPIService()
    
    # Verificar configuração
    if not service.glpi_url:
        print("❌ Erro: GLPI URL não encontrada")
        return
    
    print(f"🔗 GLPI URL: {service.glpi_url}")
    
    # Obter headers autenticados do serviço
    headers = service.get_api_headers()
    if not headers:
        print("❌ Erro: Não foi possível obter headers de autenticação")
        return
    
    print(f"🔑 Headers obtidos com sucesso")
    print(f"🔑 Session Token: {headers.get('Session-Token', '')[:20]}...")
    print(f"🔑 App Token: {headers.get('App-Token', '')[:20]}...")
    
    try:
        # 1. Obter total geral de tickets
        print("\n1. Obtendo total geral de tickets...")
        general_url = f"{service.glpi_url}/search/Ticket"
        general_params = {
            'range': '0-0',
            'forcedisplay[0]': '2'  # ID do ticket
        }
        
        response = requests.get(general_url, headers=headers, params=general_params, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 206]:
            content_range = response.headers.get('Content-Range', '')
            if content_range:
                total_geral = int(content_range.split('/')[-1])
                print(f"   ✅ Total geral de tickets: {total_geral}")
            else:
                print("   ❌ Content-Range não encontrado no cabeçalho")
                # Tentar extrair do JSON
                try:
                    data = response.json()
                    total_geral = data.get('totalcount', 0)
                    print(f"   ✅ Total geral de tickets (JSON): {total_geral}")
                except:
                    print("   ❌ Não foi possível extrair total do JSON")
                    return
        else:
            print(f"   ❌ Erro na requisição: {response.status_code}")
            return
        
        # 2. Obter tickets por grupo específico
        print("\n2. Obtendo tickets por grupo...")
        grupos = {
            'N1': 89,
            'N2': 90, 
            'N3': 91,
            'N4': 92
        }
        
        total_por_grupos = 0
        detalhes_grupos = {}
        
        for nivel, group_id in grupos.items():
            print(f"\n   --- {nivel} (Grupo {group_id}) ---")
            
            # Buscar field_id para GROUP
            if not hasattr(service, 'field_ids') or not service.field_ids:
                service.discover_field_ids()
            
            group_field_id = service.field_ids.get('GROUP')
            if not group_field_id:
                print(f"   ❌ Field ID para GROUP não encontrado")
                continue
            
            # Parâmetros para busca por grupo
            group_params = {
                'range': '0-0',
                'forcedisplay[0]': '2',  # ID do ticket
                f'criteria[0][field]': group_field_id,
                f'criteria[0][searchtype]': 'equals',
                f'criteria[0][value]': group_id
            }
            
            group_response = requests.get(general_url, headers=headers, params=group_params, timeout=30)
            print(f"   Status Code: {group_response.status_code}")
            
            if group_response.status_code in [200, 206]:
                # Tentar extrair do cabeçalho primeiro
                content_range = group_response.headers.get('Content-Range', '')
                if content_range:
                    total_grupo = int(content_range.split('/')[-1])
                    print(f"   ✅ Total {nivel}: {total_grupo} (cabeçalho)")
                else:
                    # Tentar extrair do JSON
                    try:
                        data = group_response.json()
                        total_grupo = data.get('totalcount', 0)
                        print(f"   ✅ Total {nivel}: {total_grupo} (JSON)")
                        
                        # Debug: mostrar content-range do JSON se existir
                        if 'content-range' in data:
                            print(f"   📋 Content-range JSON: {data['content-range']}")
                    except Exception as e:
                        print(f"   ❌ Erro ao processar JSON: {e}")
                        total_grupo = 0
                
                detalhes_grupos[nivel] = total_grupo
                total_por_grupos += total_grupo
            else:
                print(f"   ❌ Erro na requisição: {group_response.status_code}")
                detalhes_grupos[nivel] = 0
        
        # 3. Análise dos resultados
        print("\n=== ANÁLISE DOS RESULTADOS ===")
        print(f"📊 Total geral de tickets: {total_geral}")
        print(f"📊 Total por grupos N1-N4: {total_por_grupos}")
        print(f"📊 Diferença: {total_geral - total_por_grupos}")
        print(f"📊 Percentual em grupos: {(total_por_grupos/total_geral*100):.2f}%")
        
        print("\n📋 Detalhes por grupo:")
        for nivel, total in detalhes_grupos.items():
            percentual = (total/total_geral*100) if total_geral > 0 else 0
            print(f"   {nivel}: {total} tickets ({percentual:.2f}%)")
        
        # 4. Investigar tickets sem grupo
        print("\n4. Investigando tickets sem grupo definido...")
        
        # Buscar tickets onde o campo GROUP está vazio ou nulo
        no_group_params = {
            'range': '0-0',
            'forcedisplay[0]': '2',  # ID do ticket
            f'criteria[0][field]': group_field_id,
            f'criteria[0][searchtype]': 'empty',
            f'criteria[0][value]': ''
        }
        
        no_group_response = requests.get(general_url, headers=headers, params=no_group_params, timeout=30)
        print(f"   Status Code: {no_group_response.status_code}")
        
        if no_group_response.status_code in [200, 206]:
            content_range = no_group_response.headers.get('Content-Range', '')
            if content_range:
                tickets_sem_grupo = int(content_range.split('/')[-1])
                print(f"   ✅ Tickets sem grupo: {tickets_sem_grupo}")
            else:
                try:
                    data = no_group_response.json()
                    tickets_sem_grupo = data.get('totalcount', 0)
                    print(f"   ✅ Tickets sem grupo (JSON): {tickets_sem_grupo}")
                except:
                    tickets_sem_grupo = 0
                    print(f"   ❌ Não foi possível determinar tickets sem grupo")
        else:
            print(f"   ❌ Erro na requisição: {no_group_response.status_code}")
            tickets_sem_grupo = 0
        
        # 5. Resumo final
        print("\n=== RESUMO FINAL ===")
        print(f"📊 Total geral: {total_geral}")
        print(f"📊 Em grupos N1-N4: {total_por_grupos}")
        print(f"📊 Sem grupo: {tickets_sem_grupo}")
        print(f"📊 Outros grupos: {total_geral - total_por_grupos - tickets_sem_grupo}")
        
        if total_geral > 0:
            print(f"\n📈 Percentuais:")
            print(f"   Grupos N1-N4: {(total_por_grupos/total_geral*100):.2f}%")
            print(f"   Sem grupo: {(tickets_sem_grupo/total_geral*100):.2f}%")
            print(f"   Outros grupos: {((total_geral - total_por_grupos - tickets_sem_grupo)/total_geral*100):.2f}%")
        
    except Exception as e:
        print(f"❌ Erro durante a investigação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()