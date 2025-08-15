#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import types

def test_gabriels_in_fixed_ranking():
    """Testa se os Gabriels aparecem no ranking corrigido"""
    print("=== TESTANDO GABRIELS NO RANKING CORRIGIDO ===")
    
    glpi = GLPIService()
    
    # Adicionar o método corrigido dinamicamente
    def get_technician_ranking_fixed(self, limit: int = None, start_date: str = None, end_date: str = None) -> list:
        """Versão CORRIGIDA do ranking de técnicos"""
        self.logger.info("=== RANKING CORRIGIDO INICIADO ===")
        
        # Verificar autenticação
        if not self._ensure_authenticated():
            self.logger.error("❌ Falha na autenticação")
            return []
        
        try:
            ranking = []
            
            # IDs dos grupos DTIC
            dtic_groups = ["89", "90", "91", "92"]  # N1, N2, N3, N4
            
            # Buscar todos os usuários dos grupos DTIC
            all_dtic_users = set()
            
            for group_id in dtic_groups:
                try:
                    response = self._make_authenticated_request(
                        'GET',
                        f"{self.glpi_url}/Group/{group_id}/Group_User"
                    )
                    
                    if response and response.ok:
                        group_users = response.json()
                        if isinstance(group_users, list):
                            for user_relation in group_users:
                                user_id = str(user_relation.get('users_id', ''))
                                if user_id and user_id != '0':
                                    all_dtic_users.add(user_id)
                                    print(f"  Usuário {user_id} encontrado no grupo {group_id}")
                    
                except Exception as e:
                    self.logger.error(f"Erro ao buscar usuários do grupo {group_id}: {e}")
                    continue
            
            print(f"\nTotal de usuários DTIC encontrados: {len(all_dtic_users)}")
            
            # Verificar se os Gabriels estão na lista
            gabriel_conceicao_id = "1404"
            gabriel_machado_id = "1291"
            
            if gabriel_conceicao_id in all_dtic_users:
                print(f"✅ Gabriel Conceição (ID {gabriel_conceicao_id}) encontrado nos grupos DTIC")
            else:
                print(f"❌ Gabriel Conceição (ID {gabriel_conceicao_id}) NÃO encontrado nos grupos DTIC")
            
            if gabriel_machado_id in all_dtic_users:
                print(f"✅ Gabriel Machado (ID {gabriel_machado_id}) encontrado nos grupos DTIC")
            else:
                print(f"❌ Gabriel Machado (ID {gabriel_machado_id}) NÃO encontrado nos grupos DTIC")
            
            # Para cada usuário DTIC, buscar seus tickets
            for user_id in all_dtic_users:
                try:
                    # Verificar se é técnico DTIC ativo
                    if not self._is_dtic_technician(user_id):
                        if user_id in [gabriel_conceicao_id, gabriel_machado_id]:
                            print(f"❌ Gabriel (ID {user_id}) não passou no filtro DTIC")
                        continue
                    
                    # Buscar tickets do técnico
                    tickets_data = self._get_technician_tickets(
                        int(user_id), 
                        start_date=start_date, 
                        end_date=end_date
                    )
                    
                    # Log especial para os Gabriels
                    if user_id in [gabriel_conceicao_id, gabriel_machado_id]:
                        print(f"\n🔍 Gabriel (ID {user_id}):")
                        print(f"  Tickets encontrados: {tickets_data['total']}")
                        print(f"  Abertos: {tickets_data['abertos']}")
                        print(f"  Fechados: {tickets_data['fechados']}")
                        print(f"  Pendentes: {tickets_data['pendentes']}")
                    
                    # Verificar se tem tickets suficientes (critério mínimo)
                    if tickets_data['total'] < 10:
                        if user_id in [gabriel_conceicao_id, gabriel_machado_id]:
                            print(f"❌ Gabriel (ID {user_id}) tem apenas {tickets_data['total']} tickets (mínimo: 10)")
                        continue
                    
                    # Buscar dados do usuário
                    user_response = self._make_authenticated_request(
                        'GET',
                        f"{self.glpi_url}/User/{user_id}"
                    )
                    
                    if not (user_response and user_response.ok):
                        if user_id in [gabriel_conceicao_id, gabriel_machado_id]:
                            print(f"❌ Não foi possível buscar dados do Gabriel (ID {user_id})")
                        continue
                    
                    user_data = user_response.json()
                    user_name = user_data.get('realname', '') + ' ' + user_data.get('firstname', '')
                    user_name = user_name.strip() or user_data.get('name', f'Usuário {user_id}')
                    
                    # Determinar nível do técnico
                    level = self._get_technician_level(user_id)
                    
                    # Calcular score
                    score = self._calculate_technician_score(tickets_data)
                    
                    # Adicionar ao ranking
                    ranking.append({
                        'id': int(user_id),
                        'nome': user_name,
                        'total': tickets_data['total'],
                        'abertos': tickets_data['abertos'],
                        'fechados': tickets_data['fechados'],
                        'pendentes': tickets_data['pendentes'],
                        'nivel': level,
                        'score': score,
                        'tempo_medio': tickets_data.get('tempo_medio', 0)
                    })
                    
                    # Log especial para os Gabriels
                    if user_id in [gabriel_conceicao_id, gabriel_machado_id]:
                        print(f"✅ Gabriel {user_name} (ID {user_id}) ADICIONADO ao ranking:")
                        print(f"  Total: {tickets_data['total']} tickets")
                        print(f"  Nível: {level}")
                        print(f"  Score: {score}")
                
                except Exception as e:
                    if user_id in [gabriel_conceicao_id, gabriel_machado_id]:
                        print(f"❌ Erro ao processar Gabriel (ID {user_id}): {e}")
                    continue
            
            # Ordenar ranking por total de tickets (decrescente)
            ranking.sort(key=lambda x: x['total'], reverse=True)
            
            # Aplicar limite se especificado
            if limit and limit > 0:
                ranking = ranking[:limit]
            
            print(f"\n✅ Ranking corrigido gerado com {len(ranking)} técnicos")
            
            return ranking
        
        except Exception as e:
            self.logger.error(f"Erro no ranking corrigido: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    
    # Adicionar o método à instância
    glpi.get_technician_ranking_fixed = types.MethodType(get_technician_ranking_fixed, glpi)
    
    # Testar o método corrigido SEM LIMITE para ver todos os técnicos
    print("\nExecutando método corrigido SEM LIMITE...")
    ranking = glpi.get_technician_ranking_fixed()
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Total de técnicos no ranking: {len(ranking)}")
    
    # Procurar pelos Gabriels no ranking
    gabriel_conceicao_found = False
    gabriel_machado_found = False
    
    for i, tech in enumerate(ranking, 1):
        if tech['id'] == 1404:  # Gabriel Conceição
            print(f"\n✅ Gabriel Conceição encontrado na posição {i}:")
            print(f"  Nome: {tech['nome']}")
            print(f"  Total: {tech['total']} tickets")
            print(f"  Nível: {tech['nivel']}")
            gabriel_conceicao_found = True
        
        elif tech['id'] == 1291:  # Gabriel Machado
            print(f"\n✅ Gabriel Machado encontrado na posição {i}:")
            print(f"  Nome: {tech['nome']}")
            print(f"  Total: {tech['total']} tickets")
            print(f"  Nível: {tech['nivel']}")
            gabriel_machado_found = True
    
    if not gabriel_conceicao_found:
        print(f"\n❌ Gabriel Conceição (ID 1404) NÃO foi encontrado no ranking")
    
    if not gabriel_machado_found:
        print(f"\n❌ Gabriel Machado (ID 1291) NÃO foi encontrado no ranking")
    
    # Mostrar top 15 para referência
    print(f"\n=== TOP 15 TÉCNICOS ===")
    for i, tech in enumerate(ranking[:15], 1):
        print(f"{i:2d}. {tech['nome']} (ID {tech['id']}): {tech['total']} tickets, nível {tech['nivel']}")
    
    return ranking

if __name__ == "__main__":
    test_gabriels_in_fixed_ranking()