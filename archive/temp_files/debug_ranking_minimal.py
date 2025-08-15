#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_ranking_minimal():
    """Debug mínimo do ranking focando apenas nos Gabriels"""
    glpi = GLPIService()
    
    print("=== DEBUG RANKING MÍNIMO - APENAS GABRIELS ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # IDs dos Gabriels
    gabriel_conceicao_id = 1404
    gabriel_machado_id = 1291
    
    print(f"\n--- Simulando processo do ranking apenas para os Gabriels ---")
    
    try:
        # Simular o dicionário technician_stats como no método original
        technician_stats = {
            str(gabriel_conceicao_id): {
                'total': 48,
                'abertos': 10,
                'fechados': 35,
                'pendentes': 3
            },
            str(gabriel_machado_id): {
                'total': 217,
                'abertos': 50,
                'fechados': 150,
                'pendentes': 17
            }
        }
        
        print(f"Stats simuladas:")
        for tech_id, stats in technician_stats.items():
            print(f"  {tech_id}: {stats}")
        
        # Simular o loop do ranking
        ranking = []
        for tech_id, stats in technician_stats.items():
            print(f"\n--- Processando técnico {tech_id} ---")
            
            try:
                # Garantir que tech_id é um número válido
                tech_id_int = int(tech_id)
                print(f"✅ ID válido: {tech_id_int}")
                
                # Verificar se o técnico pertence aos grupos da DTIC (N1-N4)
                print(f"Verificando se é técnico DTIC...")
                is_dtic = glpi._is_dtic_technician(tech_id)
                print(f"É DTIC: {is_dtic}")
                
                if not is_dtic:
                    print(f"❌ Técnico {tech_id} não pertence à DTIC - ignorado no ranking")
                    continue
                
                print(f"Buscando nome do usuário...")
                user_name = glpi._get_user_name(tech_id)
                print(f"Nome: {user_name}")
                
                if user_name:
                    print(f"Determinando nível do técnico...")
                    # Determinar nível do técnico baseado nos grupos
                    tech_level = glpi._get_technician_level(tech_id_int, stats['total'])
                    print(f"Nível: {tech_level}")
                    
                    tech_data = {
                        'id': tech_id_int,
                        'name': user_name,
                        'realname': None,
                        'firstname': None,
                        'total_tickets': stats['total'],
                        'tickets_abertos': stats['abertos'],
                        'tickets_fechados': stats['fechados'],
                        'tickets_pendentes': stats['pendentes'],
                        'score': float(stats['total']),
                        'tempo_medio_resolucao': 0,
                        'level': tech_level
                    }
                    
                    ranking.append(tech_data)
                    print(f"✅ Técnico adicionado ao ranking: {tech_data}")
                else:
                    print(f"❌ Nome do usuário não encontrado")
                    
            except ValueError:
                print(f"❌ ID de técnico inválido ignorado: {tech_id}")
                continue
            except Exception as e:
                print(f"❌ Erro ao processar técnico {tech_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n--- Resultado final ---")
        print(f"Total de técnicos no ranking: {len(ranking)}")
        
        # Ordenar por total de tickets (descendente)
        ranking.sort(key=lambda x: x['total_tickets'], reverse=True)
        
        for i, tech in enumerate(ranking):
            print(f"{i+1}. {tech['name']} (ID: {tech['id']}) - Nível: {tech['level']} - Tickets: {tech['total_tickets']}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ranking_minimal()