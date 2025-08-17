#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar o mapeamento de nomes de técnicos e verificar
por que apenas técnicos N2 e N3 aparecem no ranking.
"""

import json
import requests
from services.glpi_service import GLPIService
from config.settings import Config

def main():
    print("🔍 ANÁLISE DO MAPEAMENTO DE NOMES DE TÉCNICOS")
    print("=" * 60)
    
    # Inicializar serviço
    service = GLPIService()
    
    print("\n📋 ETAPA 1: Obter dados da API de ranking")
    
    # Testar API diretamente
    try:
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        if response.status_code == 200:
            api_data = response.json()
            if 'data' in api_data:
                technicians = api_data['data']
                print(f"✅ API retornou {len(technicians)} técnicos")
            else:
                technicians = api_data if isinstance(api_data, list) else []
                print(f"✅ API retornou {len(technicians)} técnicos (formato direto)")
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao chamar API: {e}")
        return
    
    print("\n📊 ETAPA 2: Analisar cada técnico retornado")
    
    # Agrupar por nível
    by_level = {"N1": [], "N2": [], "N3": [], "N4": []}
    
    for tech in technicians:
        tech_name = tech.get('name', 'N/A')
        tech_level = tech.get('level', 'N/A')
        tech_id = tech.get('id', 'N/A')
        tech_total = tech.get('total', 0)
        
        print(f"\n--- Técnico: {tech_name} ---")
        print(f"  ID: {tech_id}")
        print(f"  Nível: {tech_level}")
        print(f"  Total tickets: {tech_total}")
        
        # Testar mapeamento manual
        if tech_level in by_level:
            by_level[tech_level].append(tech)
        
        # Verificar se o nome está no mapeamento correto
        print(f"  Verificando mapeamento de nome...")
        
        # Simular o método _get_technician_level_by_name
        mapped_level = service._get_technician_level_by_name(tech_name)
        print(f"  Nível mapeado por nome: {mapped_level}")
        
        if mapped_level != tech_level:
            print(f"  ⚠️  INCONSISTÊNCIA: API retorna {tech_level}, mapeamento retorna {mapped_level}")
        else:
            print(f"  ✅ Mapeamento consistente")
    
    print("\n📈 ETAPA 3: Resumo por nível")
    
    for level in ["N1", "N2", "N3", "N4"]:
        techs = by_level[level]
        print(f"\n{level}: {len(techs)} técnicos")
        
        if techs:
            print("  Técnicos encontrados:")
            for tech in techs:
                print(f"    - {tech.get('name', 'N/A')} (ID: {tech.get('id', 'N/A')}) - {tech.get('total', 0)} tickets")
        else:
            print("  ❌ Nenhum técnico encontrado")
    
    print("\n🔍 ETAPA 4: Verificar mapeamento de nomes hardcoded")
    
    # Verificar os mapeamentos hardcoded
    n4_names = {
        "Anderson Oliveira", "Silvio Godinho", "Edson Joel", "Paulo Pedro", 
        "Pablo Hebling", "Leonardo Riela", "Alessandro Carbonera", 
        "Miguel Angelo", "José Barros", "Nicolas Nunez", "Wagner Mengue", "Silvio Valim",
        "anderson-oliveira", "silvio-godinho", "edson-joel", "paulo-pedo", "pablo-hebling",
        "leonardo-rielaantigo", "alessandro-carbonera", "miguelangelo-old",
        "jose-barros", "nicolas-nunez", "wagner-mengue", "silvio-valim"
    }
    
    n3_names = {
        "Gabriel Machado", "Luciano Marcelino", "Jorge Swift",
        "Anderson Morim", "Davi Freitas", "Lucas Sergio",
        "gabriel-machado", "luciano-marcelino", "jorge-swift",
        "anderson-morim", "davi-freitas", "lucas-sergio-t1"
    }
    
    n2_names = {
        "Gabriel Conceição", "Luciano Araújo", "Alice Dutra", "Luan Medeiros",
        "gabriel-conceicao", "luciano-araujo", "alice-dutra", "luan-medeiros"
    }
    
    n1_names = {
        "Jonathan Moletta", "Thales Lemos", "Leonardo Riela",
        "Luciano Silva", "Thales Leite",
        "jonathan-moletta", "thales-leite", "leonardo-riela",
        "luciano-silva"
    }
    
    print("\nMapeamento hardcoded:")
    print(f"  N1: {len(n1_names)} nomes")
    print(f"  N2: {len(n2_names)} nomes")
    print(f"  N3: {len(n3_names)} nomes")
    print(f"  N4: {len(n4_names)} nomes")
    
    print("\n🔍 ETAPA 5: Verificar se nomes da API estão no mapeamento")
    
    all_mapped_names = n1_names | n2_names | n3_names | n4_names
    
    for tech in technicians:
        tech_name = tech.get('name', '')
        tech_level = tech.get('level', '')
        
        # Verificar se o nome está em algum mapeamento
        found_in_mapping = False
        mapped_to_level = None
        
        if tech_name in n1_names:
            found_in_mapping = True
            mapped_to_level = "N1"
        elif tech_name in n2_names:
            found_in_mapping = True
            mapped_to_level = "N2"
        elif tech_name in n3_names:
            found_in_mapping = True
            mapped_to_level = "N3"
        elif tech_name in n4_names:
            found_in_mapping = True
            mapped_to_level = "N4"
        
        if not found_in_mapping:
            print(f"  ⚠️  {tech_name} (nível {tech_level}) NÃO está no mapeamento hardcoded")
            
            # Verificar correspondência parcial
            partial_matches = []
            for name in all_mapped_names:
                if name.lower() in tech_name.lower() or tech_name.lower() in name.lower():
                    partial_matches.append(name)
            
            if partial_matches:
                print(f"      Possíveis correspondências parciais: {partial_matches}")
        else:
            if mapped_to_level != tech_level:
                print(f"  ❌ {tech_name}: mapeado para {mapped_to_level}, mas API retorna {tech_level}")
            else:
                print(f"  ✅ {tech_name}: mapeamento correto ({tech_level})")
    
    print("\n🎯 ETAPA 6: Testar filtros específicos")
    
    # Testar filtros por nível
    for level in ["N1", "N2", "N3", "N4"]:
        try:
            response = requests.get(f'http://localhost:5000/api/technicians/ranking?level={level}')
            if response.status_code == 200:
                filtered_data = response.json()
                if 'data' in filtered_data:
                    filtered_techs = filtered_data['data']
                else:
                    filtered_techs = filtered_data if isinstance(filtered_data, list) else []
                
                print(f"\nFiltro {level}: {len(filtered_techs)} técnicos")
                
                # Verificar se todos os técnicos retornados são realmente do nível solicitado
                wrong_level = [t for t in filtered_techs if t.get('level') != level]
                if wrong_level:
                    print(f"  ❌ {len(wrong_level)} técnicos com nível incorreto:")
                    for tech in wrong_level[:3]:
                        print(f"    - {tech.get('name')} (retornado como {tech.get('level')})")
                else:
                    print(f"  ✅ Todos os técnicos são do nível {level}")
                    
                # Mostrar alguns exemplos
                if filtered_techs:
                    print(f"  Exemplos:")
                    for tech in filtered_techs[:3]:
                        print(f"    - {tech.get('name')} ({tech.get('total', 0)} tickets)")
            else:
                print(f"\nFiltro {level}: Erro {response.status_code}")
        except Exception as e:
            print(f"\nFiltro {level}: Erro {e}")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 60)

if __name__ == "__main__":
    main()