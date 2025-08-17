#!/usr/bin/env python3
"""
Script para investigar a estrutura hierárquica de grupos no GLPI
baseado na descoberta de 'CC-SE-SUBADM-DTIC > N1' no campo 8.
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
    print("=== INVESTIGAÇÃO DE ESTRUTURA HIERÁRQUICA DE GRUPOS ===")
    
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
        
        # 1. Analisar o campo 8 que mostrou a estrutura hierárquica
        print("1. Analisando campo 8 (estrutura hierárquica)...")
        
        try:
            # Buscar mais tickets para analisar o campo 8
            params = {
                "range": "0-100",  # Buscar 100 tickets
                "forcedisplay[0]": "8",  # Campo 8 que mostrou a hierarquia
                "forcedisplay[1]": "1",  # ID do ticket
                "forcedisplay[2]": "71", # Campo grupo (descoberto anteriormente)
            }
            
            response = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 206]:
                tickets_data = response.json()
                
                if isinstance(tickets_data, dict) and 'data' in tickets_data:
                    tickets = tickets_data['data']
                    print(f"   ✅ Analisando {len(tickets)} tickets")
                    
                    # Analisar valores do campo 8
                    field_8_values = defaultdict(int)
                    n_level_patterns = defaultdict(int)
                    
                    for ticket in tickets:
                        if isinstance(ticket, dict) and '8' in ticket:
                            field_8_value = ticket['8']
                            
                            if field_8_value:
                                # Se for lista, processar cada item
                                if isinstance(field_8_value, list):
                                    for item in field_8_value:
                                        if item:
                                            field_8_values[str(item)] += 1
                                            
                                            # Verificar se contém N1, N2, N3, N4
                                            item_str = str(item).upper()
                                            for level in ['N1', 'N2', 'N3', 'N4']:
                                                if level in item_str:
                                                    n_level_patterns[level] += 1
                                else:
                                    field_8_values[str(field_8_value)] += 1
                                    
                                    # Verificar se contém N1, N2, N3, N4
                                    value_str = str(field_8_value).upper()
                                    for level in ['N1', 'N2', 'N3', 'N4']:
                                        if level in value_str:
                                            n_level_patterns[level] += 1
                    
                    print(f"\n   📊 Padrões de níveis encontrados no campo 8:")
                    if n_level_patterns:
                        for level, count in sorted(n_level_patterns.items()):
                            print(f"      {level}: {count} ocorrências")
                    else:
                        print(f"      ⚠️ Nenhum padrão N1-N4 encontrado")
                    
                    print(f"\n   📋 Top 10 valores mais comuns no campo 8:")
                    sorted_values = sorted(field_8_values.items(), key=lambda x: x[1], reverse=True)
                    
                    for i, (value, count) in enumerate(sorted_values[:10], 1):
                        # Destacar valores que contêm N1-N4
                        highlight = ""
                        value_upper = value.upper()
                        for level in ['N1', 'N2', 'N3', 'N4']:
                            if level in value_upper:
                                highlight = f" ⭐ ({level})"
                                break
                        
                        print(f"      {i:>2}. {value}{highlight}: {count} tickets")
                    
                else:
                    print("   ⚠️ Formato de resposta inesperado")
            else:
                print(f"   ❌ Erro ao obter tickets: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao analisar campo 8: {e}")
        
        print("\n" + "="*60)
        
        # 2. Buscar tickets especificamente com padrões N1-N4 no campo 8
        print("2. Buscando tickets com padrões N1-N4...")
        
        # Descobrir field_ids necessários
        if not hasattr(service, 'field_ids') or not service.field_ids:
            service.discover_field_ids()
        
        for level in ['N1', 'N2', 'N3', 'N4']:
            try:
                print(f"\n   --- Buscando tickets com {level} ---")
                
                # Buscar no campo 8 (que parece conter a hierarquia)
                params = {
                    f"criteria[0][field]": "8",  # Campo 8
                    f"criteria[0][searchtype]": "contains",
                    f"criteria[0][value]": level
                }
                
                response = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params)
                
                if response.status_code in [200, 206]:
                    count = extract_count_from_response(response)
                    print(f"   ✅ {level}: {count} tickets encontrados")
                    
                    # Se encontrou tickets, buscar alguns exemplos
                    if count > 0:
                        params_sample = params.copy()
                        params_sample["range"] = "0-2"  # Buscar 3 exemplos
                        params_sample["forcedisplay[0]"] = "8"
                        params_sample["forcedisplay[1]"] = "1"
                        
                        response_sample = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params_sample)
                        
                        if response_sample.status_code in [200, 206]:
                            sample_data = response_sample.json()
                            if isinstance(sample_data, dict) and 'data' in sample_data:
                                print(f"   📋 Exemplos de valores do campo 8:")
                                for ticket in sample_data['data'][:3]:
                                    if isinstance(ticket, dict) and '8' in ticket:
                                        field_8_value = ticket['8']
                                        ticket_id = ticket.get('1', 'N/A')
                                        print(f"      Ticket {ticket_id}: {field_8_value}")
                else:
                    print(f"   ❌ {level}: Erro {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {level}: Erro - {e}")
        
        print("\n" + "="*60)
        
        # 3. Investigar se o campo 8 é o campo correto para usar
        print("3. Investigando se devemos usar o campo 8 em vez do campo 71...")
        
        try:
            # Comparar resultados usando campo 71 (GROUP) vs campo 8
            print(f"\n   Comparação de métodos de busca:")
            
            for level in ['N1', 'N2']:
                print(f"\n   --- {level} ---")
                
                # Método atual (campo 71 - GROUP)
                group_id = {'N1': '89', 'N2': '90'}.get(level)
                if group_id:
                    params_group = {
                        f"criteria[0][field]": "71",  # Campo GROUP
                        f"criteria[0][searchtype]": "equals",
                        f"criteria[0][value]": group_id
                    }
                    
                    response_group = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params_group)
                    
                    if response_group.status_code in [200, 206]:
                        count_group = extract_count_from_response(response_group)
                        print(f"   Campo 71 (GROUP={group_id}): {count_group} tickets")
                    else:
                        print(f"   Campo 71 (GROUP={group_id}): Erro {response_group.status_code}")
                
                # Método alternativo (campo 8 - hierarquia)
                params_field8 = {
                    f"criteria[0][field]": "8",
                    f"criteria[0][searchtype]": "contains",
                    f"criteria[0][value]": level
                }
                
                response_field8 = requests.get(f"{base_url}/search/Ticket", headers=headers, params=params_field8)
                
                if response_field8.status_code in [200, 206]:
                    count_field8 = extract_count_from_response(response_field8)
                    print(f"   Campo 8 (contains {level}): {count_field8} tickets")
                else:
                    print(f"   Campo 8 (contains {level}): Erro {response_field8.status_code}")
        
        except Exception as e:
            print(f"   ❌ Erro na comparação: {e}")
        
        print("\n=== INVESTIGAÇÃO CONCLUÍDA ===")
        
        # Resumo das descobertas
        print("\n📋 RESUMO DAS DESCOBERTAS:")
        print("1. Campo 8 contém estrutura hierárquica como 'CC-SE-SUBADM-DTIC > N1'")
        print("2. Grupos N1-N4 (IDs 89-92) existem mas podem estar inativos")
        print("3. Campo 8 pode ser a chave para encontrar tickets por nível")
        print("4. Estrutura sugere que N1-N4 são subcategorias de grupos maiores")
        print("\n💡 RECOMENDAÇÕES:")
        print("- Usar campo 8 com busca 'contains' em vez de campo 71 com 'equals'")
        print("- Modificar GLPIService para usar a estrutura hierárquica")
        print("- Considerar ativar os grupos N1-N4 se necessário")
        print("- Testar nova abordagem de busca no dashboard")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()