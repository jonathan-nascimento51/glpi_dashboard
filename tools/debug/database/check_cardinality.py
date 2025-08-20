#!/usr/bin/env python3
"""Script para verificar cardinalidade dos técnicos no ranking"""

import requests
import json
from collections import Counter

def check_technician_cardinality():
    """Verifica a cardinalidade dos técnicos no ranking"""
    try:
        # Fazer requisição para o endpoint de ranking
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        response.raise_for_status()
        
        data = response.json()
        technicians = data.get('data', [])
        
        print("=== VERIFICAÇÃO DE CARDINALIDADE DOS TÉCNICOS ===")
        print(f"Total de técnicos: {len(technicians)}")
        
        # Verificar IDs únicos
        ids = [tech.get('id') for tech in technicians if tech.get('id')]
        unique_ids = set(ids)
        print(f"IDs únicos: {len(unique_ids)}")
        print(f"IDs duplicados: {len(ids) - len(unique_ids)}")
        
        # Verificar nomes únicos
        names = [tech.get('name') for tech in technicians if tech.get('name')]
        unique_names = set(names)
        print(f"Nomes únicos: {len(unique_names)}")
        print(f"Nomes duplicados: {len(names) - len(unique_names)}")
        
        # Distribuição por nível
        levels = [tech.get('level') for tech in technicians if tech.get('level')]
        level_distribution = Counter(levels)
        print("\nDistribuição por nível:")
        for level, count in sorted(level_distribution.items()):
            print(f"  {level}: {count} técnicos")
        
        # Verificar se está dentro do esperado (≤ 18)
        expected_max = 18
        print(f"\nCardinalidade esperada: ≤ {expected_max}")
        print(f"Cardinalidade atual: {len(technicians)}")
        
        if len(technicians) <= expected_max:
            print("✅ Cardinalidade dentro do esperado")
        else:
            print("❌ Cardinalidade acima do esperado")
        
        # Verificar duplicações
        if len(ids) == len(unique_ids) and len(names) == len(unique_names):
            print("✅ Nenhuma duplicação encontrada")
        else:
            print("❌ Duplicações encontradas")
            
            # Mostrar duplicações de IDs
            if len(ids) != len(unique_ids):
                id_counts = Counter(ids)
                duplicated_ids = {k: v for k, v in id_counts.items() if v > 1}
                print(f"IDs duplicados: {duplicated_ids}")
            
            # Mostrar duplicações de nomes
            if len(names) != len(unique_names):
                name_counts = Counter(names)
                duplicated_names = {k: v for k, v in name_counts.items() if v > 1}
                print(f"Nomes duplicados: {duplicated_names}")
        
        # Mostrar amostra dos dados
        print("\nAmostra dos primeiros 5 técnicos:")
        for i, tech in enumerate(technicians[:5]):
            print(f"  {i+1}. ID: {tech.get('id')}, Nome: {tech.get('name')}, Nível: {tech.get('level')}, Total: {tech.get('total')}")
        
        return len(technicians) <= expected_max and len(ids) == len(unique_ids) and len(names) == len(unique_names)
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = check_technician_cardinality()
    exit(0 if success else 1)