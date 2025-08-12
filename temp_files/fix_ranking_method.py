#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def create_fixed_ranking_method():
    """Cria uma versão corrigida do método get_technician_ranking"""
    
    fixed_method = '''
    def get_technician_ranking_fixed(self, limit: int = None, start_date: str = None, end_date: str = None) -> list:
        """Versão CORRIGIDA do ranking de técnicos
        
        Esta versão:
        1. Primeiro busca todos os usuários dos grupos DTIC
        2. Para cada usuário, busca seus tickets individualmente
        3. Verifica se o usuário é técnico DTIC ativo
        4. Constrói o ranking baseado nos dados reais
        """
        self.logger.info("=== RANKING CORRIGIDO INICIADO ===")
        
        # Cache com chave específica para versão corrigida
        cache_key = f'technician_ranking_fixed_{start_date}_{end_date}_{limit}'
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            self.logger.info("✅ Retornando ranking corrigido do cache")
            return cached_data
        
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
                                    self.logger.debug(f"Usuário {user_id} encontrado no grupo {group_id}")
                    
                except Exception as e:
                    self.logger.error(f"Erro ao buscar usuários do grupo {group_id}: {e}")
                    continue
            
            self.logger.info(f"Total de usuários DTIC encontrados: {len(all_dtic_users)}")
            
            # Para cada usuário DTIC, buscar seus tickets
            for user_id in all_dtic_users:
                try:
                    # Verificar se é técnico DTIC ativo
                    if not self._is_dtic_technician(user_id):
                        self.logger.debug(f"Usuário {user_id} não passou no filtro DTIC")
                        continue
                    
                    # Buscar tickets do técnico
                    tickets_data = self._get_technician_tickets(
                        int(user_id), 
                        start_date=start_date, 
                        end_date=end_date
                    )
                    
                    # Verificar se tem tickets suficientes (critério mínimo)
                    if tickets_data['total'] < 10:
                        self.logger.debug(f"Usuário {user_id} tem apenas {tickets_data['total']} tickets (mínimo: 10)")
                        continue
                    
                    # Buscar dados do usuário
                    user_response = self._make_authenticated_request(
                        'GET',
                        f"{self.glpi_url}/User/{user_id}"
                    )
                    
                    if not (user_response and user_response.ok):
                        self.logger.warning(f"Não foi possível buscar dados do usuário {user_id}")
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
                    
                    self.logger.info(f"✅ {user_name} (ID {user_id}): {tickets_data['total']} tickets, nível {level}")
                
                except Exception as e:
                    self.logger.error(f"Erro ao processar usuário {user_id}: {e}")
                    continue
            
            # Ordenar ranking por total de tickets (decrescente)
            ranking.sort(key=lambda x: x['total'], reverse=True)
            
            # Aplicar limite se especificado
            if limit and limit > 0:
                ranking = ranking[:limit]
            
            self.logger.info(f"✅ Ranking corrigido gerado com {len(ranking)} técnicos")
            
            # Salvar no cache por 10 minutos
            self._set_cached_data(cache_key, ranking, ttl=600)
            
            return ranking
        
        except Exception as e:
            self.logger.error(f"Erro no ranking corrigido: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    '''
    
    print("=== MÉTODO CORRIGIDO CRIADO ===")
    print("\nEste é o método corrigido que deve substituir o get_technician_ranking atual:")
    print(fixed_method)
    
    # Salvar em arquivo para referência
    with open('fixed_ranking_method.txt', 'w', encoding='utf-8') as f:
        f.write(fixed_method)
    
    print("\n✅ Método salvo em 'fixed_ranking_method.txt'")
    
    return fixed_method

def test_fixed_method():
    """Testa o método corrigido"""
    print("\n=== TESTANDO MÉTODO CORRIGIDO ===")
    
    glpi = GLPIService()
    
    # Adicionar o método corrigido dinamicamente
    import types
    
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
                                    self.logger.debug(f"Usuário {user_id} encontrado no grupo {group_id}")
                    
                except Exception as e:
                    self.logger.error(f"Erro ao buscar usuários do grupo {group_id}: {e}")
                    continue
            
            self.logger.info(f"Total de usuários DTIC encontrados: {len(all_dtic_users)}")
            
            # Para cada usuário DTIC, buscar seus tickets
            for user_id in all_dtic_users:
                try:
                    # Verificar se é técnico DTIC ativo
                    if not self._is_dtic_technician(user_id):
                        self.logger.debug(f"Usuário {user_id} não passou no filtro DTIC")
                        continue
                    
                    # Buscar tickets do técnico
                    tickets_data = self._get_technician_tickets(
                        int(user_id), 
                        start_date=start_date, 
                        end_date=end_date
                    )
                    
                    # Verificar se tem tickets suficientes (critério mínimo)
                    if tickets_data['total'] < 10:
                        self.logger.debug(f"Usuário {user_id} tem apenas {tickets_data['total']} tickets (mínimo: 10)")
                        continue
                    
                    # Buscar dados do usuário
                    user_response = self._make_authenticated_request(
                        'GET',
                        f"{self.glpi_url}/User/{user_id}"
                    )
                    
                    if not (user_response and user_response.ok):
                        self.logger.warning(f"Não foi possível buscar dados do usuário {user_id}")
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
                    
                    self.logger.info(f"✅ {user_name} (ID {user_id}): {tickets_data['total']} tickets, nível {level}")
                
                except Exception as e:
                    self.logger.error(f"Erro ao processar usuário {user_id}: {e}")
                    continue
            
            # Ordenar ranking por total de tickets (decrescente)
            ranking.sort(key=lambda x: x['total'], reverse=True)
            
            # Aplicar limite se especificado
            if limit and limit > 0:
                ranking = ranking[:limit]
            
            self.logger.info(f"✅ Ranking corrigido gerado com {len(ranking)} técnicos")
            
            return ranking
        
        except Exception as e:
            self.logger.error(f"Erro no ranking corrigido: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    
    # Adicionar o método à instância
    glpi.get_technician_ranking_fixed = types.MethodType(get_technician_ranking_fixed, glpi)
    
    # Testar o método corrigido
    print("Executando método corrigido...")
    ranking = glpi.get_technician_ranking_fixed(limit=10)
    
    print(f"\n✅ Ranking corrigido retornou {len(ranking)} técnicos:")
    for i, tech in enumerate(ranking, 1):
        print(f"{i}. {tech['nome']} (ID {tech['id']}): {tech['total']} tickets, nível {tech['nivel']}")
    
    return ranking

if __name__ == "__main__":
    # Criar o método corrigido
    create_fixed_ranking_method()
    
    # Testar o método corrigido
    test_fixed_method()