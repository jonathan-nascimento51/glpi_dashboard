#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o ranking atualizado após a correção do mapeamento hardcoded.
Verifica se todos os técnicos de todos os níveis (N1-N4) aparecem corretamente.
"""

import requests
import json
from collections import defaultdict

def test_ranking_api():
    """Testa a API de ranking e analisa a distribuição por níveis"""
    print("🧪 TESTE DO RANKING ATUALIZADO")
    print("=" * 60)
    
    base_url = "http://localhost:5000/api/technicians/ranking"
    
    print("\n📋 ETAPA 1: Testar ranking geral (sem filtros)")
    
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', data) if isinstance(data, dict) else data
            
            print(f"✅ API respondeu com {len(technicians)} técnicos")
            
            # Agrupar por nível
            by_level = defaultdict(list)
            for tech in technicians:
                level = tech.get('level', 'UNKNOWN')
                by_level[level].append(tech)
            
            print("\n📊 DISTRIBUIÇÃO POR NÍVEL:")
            for level in ['N1', 'N2', 'N3', 'N4']:
                count = len(by_level[level])
                print(f"  {level}: {count} técnicos")
                
                if by_level[level]:
                    print(f"    Top 3 técnicos {level}:")
                    for i, tech in enumerate(by_level[level][:3]):
                        name = tech.get('name', 'N/A')
                        total = tech.get('total', 0)
                        print(f"      {i+1}. {name} - {total} tickets")
                else:
                    print(f"    ❌ Nenhum técnico {level} encontrado")
            
            # Verificar se há técnicos com nível desconhecido
            unknown = by_level.get('UNKNOWN', [])
            if unknown:
                print(f"\n⚠️  {len(unknown)} técnicos com nível UNKNOWN:")
                for tech in unknown[:5]:
                    print(f"    - {tech.get('name', 'N/A')}")
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao chamar API: {e}")
        return False
    
    print("\n📋 ETAPA 2: Testar filtros por nível")
    
    for level in ['N1', 'N2', 'N3', 'N4']:
        try:
            response = requests.get(f"{base_url}?level={level}")
            if response.status_code == 200:
                data = response.json()
                filtered_techs = data.get('data', data) if isinstance(data, dict) else data
                
                print(f"\n{level}: {len(filtered_techs)} técnicos")
                
                # Verificar se todos são realmente do nível solicitado
                wrong_level = [t for t in filtered_techs if t.get('level') != level]
                if wrong_level:
                    print(f"  ❌ {len(wrong_level)} técnicos com nível incorreto")
                    for tech in wrong_level[:3]:
                        print(f"    - {tech.get('name')} (nível: {tech.get('level')})")
                else:
                    print(f"  ✅ Todos os técnicos são do nível {level}")
                
                # Mostrar exemplos
                if filtered_techs:
                    print(f"  Exemplos:")
                    for tech in filtered_techs[:3]:
                        name = tech.get('name', 'N/A')
                        total = tech.get('total', 0)
                        print(f"    - {name} ({total} tickets)")
                        
            else:
                print(f"\n{level}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"\n{level}: Erro {e}")
    
    print("\n📋 ETAPA 3: Comparar com estado anterior")
    
    # Verificar se agora temos técnicos em todos os níveis
    print("\nVerificando se o problema foi resolvido:")
    
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', data) if isinstance(data, dict) else data
            
            levels_with_techs = set()
            for tech in technicians:
                level = tech.get('level')
                if level:
                    levels_with_techs.add(level)
            
            missing_levels = set(['N1', 'N2', 'N3', 'N4']) - levels_with_techs
            
            if not missing_levels:
                print("✅ SUCESSO: Todos os níveis (N1-N4) têm técnicos no ranking!")
            else:
                print(f"⚠️  Ainda faltam técnicos nos níveis: {missing_levels}")
                
            print(f"\nNíveis com técnicos: {sorted(levels_with_techs)}")
            
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")
    
    print("\n📋 ETAPA 4: Salvar resultado para análise")
    
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', data) if isinstance(data, dict) else data
            
            # Salvar resultado completo
            with open('ranking_atualizado_completo.json', 'w', encoding='utf-8') as f:
                json.dump(technicians, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Ranking completo salvo em 'ranking_atualizado_completo.json'")
            print(f"📊 Total de técnicos no ranking: {len(technicians)}")
            
            # Estatísticas finais
            by_level = defaultdict(int)
            for tech in technicians:
                level = tech.get('level', 'UNKNOWN')
                by_level[level] += 1
            
            print("\n📈 ESTATÍSTICAS FINAIS:")
            for level in sorted(by_level.keys()):
                print(f"  {level}: {by_level[level]} técnicos")
                
    except Exception as e:
        print(f"❌ Erro ao salvar resultado: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_ranking_api()