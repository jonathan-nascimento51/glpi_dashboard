#!/usr/bin/env python3
"""
Script para corrigir o método de ranking de técnicos
Baseado na descoberta de que os técnicos são atribuídos diretamente aos tickets
"""

import sys
import os
import requests
import json
from datetime import datetime
from collections import defaultdict

# Configurações GLPI (do arquivo .env)
GLPI_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
GLPI_USER_TOKEN = "TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"
GLPI_APP_TOKEN = "aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"

def get_session_token():
    """Obtém token de sessão"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {GLPI_USER_TOKEN}',
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        response = requests.get(f"{GLPI_URL}/initSession", headers=headers)
        if response.status_code == 200:
            session_data = response.json()
            return session_data.get('session_token')
        else:
            print(f"Erro na conexão: {response.text}")
            return None
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def get_technicians_from_tickets(session_token, limit=1000):
    """Extrai técnicos diretamente dos tickets"""
    print(f"\n=== EXTRAINDO TÉCNICOS DOS TICKETS (limite: {limit}) ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    technician_counts = defaultdict(int)
    technician_ids = set()
    
    try:
        # Buscar tickets com técnicos atribuídos
        response = requests.get(
            f"{GLPI_URL}/search/Ticket",
            headers=headers,
            params={
                'criteria[0][field]': '5',  # users_id_tech
                'criteria[0][searchtype]': 'isnotnull',
                'criteria[0][value]': '',
                'range': f'0-{limit-1}',
                'forcedisplay[0]': '2',   # id
                'forcedisplay[1]': '5',   # users_id_tech
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            tickets_data = result.get('data', [])
            total_count = result.get('totalcount', 0)
            
            print(f"  Total de tickets com técnicos: {total_count}")
            print(f"  Tickets analisados: {len(tickets_data)}")
            
            for ticket in tickets_data:
                tech_field = ticket.get('5')  # users_id_tech
                
                if tech_field:
                    # O campo pode ser uma string, lista ou número
                    if isinstance(tech_field, list):
                        # Múltiplos técnicos
                        for tech_id in tech_field:
                            if tech_id and str(tech_id).isdigit():
                                tech_id = int(tech_id)
                                technician_counts[tech_id] += 1
                                technician_ids.add(tech_id)
                    elif isinstance(tech_field, (str, int)):
                        # Técnico único
                        if str(tech_field).isdigit():
                            tech_id = int(tech_field)
                            technician_counts[tech_id] += 1
                            technician_ids.add(tech_id)
            
            print(f"  Técnicos únicos encontrados: {len(technician_ids)}")
            print(f"  Top 10 técnicos por número de tickets:")
            
            # Ordenar por número de tickets
            sorted_techs = sorted(technician_counts.items(), key=lambda x: x[1], reverse=True)
            for i, (tech_id, count) in enumerate(sorted_techs[:10]):
                print(f"    {i+1}. Técnico ID {tech_id}: {count} tickets")
            
            return technician_ids, technician_counts
        else:
            print(f"  Erro ao buscar tickets: {response.text}")
            return set(), {}
            
    except Exception as e:
        print(f"  Erro ao buscar tickets: {e}")
        return set(), {}

def get_user_details_batch(session_token, user_ids):
    """Busca detalhes dos usuários em lotes"""
    print(f"\n=== BUSCANDO DETALHES DE {len(user_ids)} TÉCNICOS ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    users_details = {}
    batch_size = 50
    user_ids_list = list(user_ids)
    
    for i in range(0, len(user_ids_list), batch_size):
        batch_ids = user_ids_list[i:i+batch_size]
        print(f"  Processando lote {i//batch_size + 1}: IDs {batch_ids[0]} a {batch_ids[-1]}")
        
        try:
            # Buscar usuários por ID
            for user_id in batch_ids:
                response = requests.get(
                    f"{GLPI_URL}/User/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    users_details[user_id] = {
                        'id': user_data.get('id'),
                        'name': user_data.get('name'),
                        'realname': user_data.get('realname', ''),
                        'firstname': user_data.get('firstname', ''),
                        'is_active': user_data.get('is_active', 0)
                    }
                else:
                    print(f"    Erro ao buscar usuário {user_id}: {response.status_code}")
                    
        except Exception as e:
            print(f"  Erro ao processar lote: {e}")
    
    active_users = {uid: data for uid, data in users_details.items() if data.get('is_active') == 1}
    print(f"  Usuários ativos encontrados: {len(active_users)}")
    
    return active_users

def generate_ranking(technician_counts, users_details):
    """Gera o ranking de técnicos"""
    print("\n=== GERANDO RANKING ===")
    
    ranking = []
    
    for tech_id, ticket_count in technician_counts.items():
        if tech_id in users_details:
            user_data = users_details[tech_id]
            
            # Determinar nível baseado no número de tickets (exemplo)
            if ticket_count >= 100:
                level = "N4"
            elif ticket_count >= 50:
                level = "N3"
            elif ticket_count >= 20:
                level = "N2"
            else:
                level = "N1"
            
            ranking.append({
                'id': tech_id,
                'name': f"{user_data['realname']} {user_data['firstname']}".strip() or user_data['name'],
                'username': user_data['name'],
                'total_tickets': ticket_count,
                'level': level
            })
    
    # Ordenar por número de tickets (decrescente)
    ranking.sort(key=lambda x: x['total_tickets'], reverse=True)
    
    print(f"  Ranking gerado com {len(ranking)} técnicos")
    
    return ranking

def main():
    """Função principal"""
    print(f"Iniciando correção do ranking em {datetime.now()}")
    
    # 1. Obter token de sessão
    session_token = get_session_token()
    if not session_token:
        print("Falha na autenticação")
        return
    
    print(f"Conectado com sucesso!")
    
    # 2. Extrair técnicos dos tickets
    technician_ids, technician_counts = get_technicians_from_tickets(session_token, limit=2000)
    
    if not technician_ids:
        print("Nenhum técnico encontrado nos tickets")
        return
    
    # 3. Buscar detalhes dos técnicos
    users_details = get_user_details_batch(session_token, technician_ids)
    
    if not users_details:
        print("Nenhum detalhe de usuário encontrado")
        return
    
    # 4. Gerar ranking
    ranking = generate_ranking(technician_counts, users_details)
    
    # 5. Exibir resultado
    print("\n=== RANKING FINAL ===")
    for i, tech in enumerate(ranking[:10]):
        print(f"{i+1:2d}. {tech['name']} ({tech['username']}) - {tech['total_tickets']} tickets - {tech['level']}")
    
    # 6. Salvar resultado
    output_file = "ranking_corrigido.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, indent=2, ensure_ascii=False)
    
    print(f"\nRanking salvo em: {output_file}")
    print(f"Total de técnicos no ranking: {len(ranking)}")
    
    return ranking

if __name__ == "__main__":
    ranking = main()