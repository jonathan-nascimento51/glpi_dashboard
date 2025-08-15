#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar chaves duplicadas no React
Verifica dados da API em tempo real e identifica possíveis problemas
"""

import requests
import json
from collections import Counter
from datetime import datetime

def check_api_data():
    """Verifica dados da API para identificar possíveis chaves duplicadas"""
    base_url = "http://localhost:5000/api"
    
    print("🔍 Verificando dados da API em tempo real...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verificar métricas
    try:
        response = requests.get(f"{base_url}/metrics")
        if response.status_code == 200:
            data = response.json()
            print("📊 MÉTRICAS:")
            if 'data' in data:
                metrics_data = data['data']
                print(f"   Estrutura: {list(metrics_data.keys()) if isinstance(metrics_data, dict) else type(metrics_data)}")
                
                # Verificar se há níveis duplicados
                if isinstance(metrics_data, dict):
                    levels = list(metrics_data.keys())
                    level_counts = Counter(levels)
                    duplicates = {k: v for k, v in level_counts.items() if v > 1}
                    if duplicates:
                        print(f"   ⚠️  NÍVEIS DUPLICADOS: {duplicates}")
                    else:
                        print(f"   ✅ Níveis únicos: {levels}")
            print()
    except Exception as e:
        print(f"❌ Erro ao verificar métricas: {e}\n")
    
    # Verificar ranking de técnicos
    try:
        response = requests.get(f"{base_url}/technicians/ranking")
        if response.status_code == 200:
            data = response.json()
            print("👥 TÉCNICOS:")
            if 'data' in data and isinstance(data['data'], list):
                technicians = data['data']
                print(f"   Total: {len(technicians)}")
                
                # Verificar IDs duplicados
                ids = [t.get('id') for t in technicians if t.get('id')]
                id_counts = Counter(ids)
                id_duplicates = {k: v for k, v in id_counts.items() if v > 1}
                
                if id_duplicates:
                    print(f"   ⚠️  IDs DUPLICADOS: {id_duplicates}")
                    for dup_id, count in id_duplicates.items():
                        dupes = [t for t in technicians if t.get('id') == dup_id]
                        print(f"      ID {dup_id}: {[t.get('name', 'N/A') for t in dupes]}")
                else:
                    print(f"   ✅ IDs únicos: {len(set(ids))} de {len(ids)}")
                
                # Verificar levels duplicados
                levels = [t.get('level') for t in technicians if t.get('level')]
                level_counts = Counter(levels)
                print(f"   📊 Distribuiçáo de níveis: {dict(level_counts)}")
            print()
    except Exception as e:
        print(f"❌ Erro ao verificar técnicos: {e}\n")
    
    # Verificar tickets novos
    try:
        response = requests.get(f"{base_url}/tickets/new")
        if response.status_code == 200:
            data = response.json()
            print("🎫 TICKETS:")
            if 'data' in data and isinstance(data['data'], list):
                tickets = data['data']
                print(f"   Total: {len(tickets)}")
                
                # Verificar IDs duplicados
                ids = [t.get('id') for t in tickets if t.get('id')]
                id_counts = Counter(ids)
                id_duplicates = {k: v for k, v in id_counts.items() if v > 1}
                
                if id_duplicates:
                    print(f"   ⚠️  IDs DUPLICADOS: {id_duplicates}")
                else:
                    print(f"   ✅ IDs únicos: {len(set(ids))} de {len(ids)}")
                
                # Verificar status duplicados
                statuses = [t.get('status') for t in tickets if t.get('status')]
                status_counts = Counter(statuses)
                print(f"   📊 Distribuiçáo de status: {dict(status_counts)}")
            print()
    except Exception as e:
        print(f"❌ Erro ao verificar tickets: {e}\n")

def analyze_react_patterns():
    """Analisa padrões que podem causar chaves duplicadas no React"""
    print("🔧 ANÁLISE DE PADRÕES REACT:")
    print("\n📋 Possíveis causas de chaves duplicadas:")
    print("   1. Múltiplos componentes usando o mesmo status como key")
    print("   2. Componentes renderizados em loops diferentes com mesmas chaves")
    print("   3. Estados de loading/placeholder usando índices")
    print("   4. Componentes condicionais que podem duplicar chaves")
    print("\n🎯 Componentes suspeitos identificados:")
    print("   - MetricsGrid: usa card.status como key")
    print("   - LevelMetricsGrid: usa status como key")
    print("   - StatusItem: tem key={status} interno")
    print("   - Múltiplos skeleton loaders usando index")
    
    print("\n💡 Soluções recomendadas:")
    print("   1. Usar chaves compostas: key={`${component}-${status}`}")
    print("   2. Adicionar prefixos únicos por componente")
    print("   3. Usar UUIDs para componentes temporários")
    print("   4. Verificar se componentes estáo sendo renderizados múltiplas vezes")

def main():
    """Funçáo principal"""
    print("🚀 DEBUG DE CHAVES DUPLICADAS NO REACT")
    print("=" * 50)
    
    check_api_data()
    analyze_react_patterns()
    
    print("\n" + "=" * 50)
    print("✅ Análise concluída!")
    print("\n💡 Próximos passos:")
    print("   1. Verificar logs do navegador para mensagem específica")
    print("   2. Adicionar console.log nos componentes suspeitos")
    print("   3. Usar React DevTools para inspecionar árvore de componentes")
    print("   4. Implementar chaves únicas nos componentes identificados")

if __name__ == "__main__":
    main()
