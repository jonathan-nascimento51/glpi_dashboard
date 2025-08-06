#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar as categorias de usuários no GLPI
e verificar se podem ser usadas para níveis de atendimento
"""

import logging
from backend.services.glpi_service import GLPIService

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def investigate_user_categories():
    """Investiga as categorias de usuários para classificação por níveis"""
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        print("=== INVESTIGAÇÃO DAS CATEGORIAS DE USUÁRIOS ===")
        print()
        
        # 1. Buscar todas as categorias disponíveis
        print("1. CATEGORIAS DISPONÍVEIS:")
        print("-" * 27)
        
        try:
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/UserCategory",
                params={
                    "range": "0-100",
                    "is_deleted": 0
                }
            )
            
            if response and response.ok:
                categories_data = response.json()
                print(f"Total de categorias encontradas: {len(categories_data)}")
                
                categories_list = []
                for category in categories_data:
                    if isinstance(category, dict):
                        cat_id = category.get('id')
                        cat_name = category.get('name', '')
                        cat_comment = category.get('comment', '')
                        
                        categories_list.append({
                            'id': cat_id,
                            'name': cat_name,
                            'comment': cat_comment
                        })
                        
                        print(f"  ID {cat_id}: {cat_name}")
                        if cat_comment:
                            print(f"    Comentário: {cat_comment}")
                
                # Procurar por categorias relacionadas a níveis
                level_related = []
                keywords = ['n1', 'n2', 'n3', 'n4', 'nivel', 'nível', 'tecnico', 'técnico', 'atendimento', 'suporte']
                
                for cat in categories_list:
                    cat_name_lower = cat['name'].lower()
                    cat_comment_lower = cat['comment'].lower()
                    
                    if any(keyword in cat_name_lower or keyword in cat_comment_lower for keyword in keywords):
                        level_related.append(cat)
                
                if level_related:
                    print(f"\n📋 Categorias relacionadas a níveis encontradas: {len(level_related)}")
                    for cat in level_related:
                        print(f"  ⭐ ID {cat['id']}: {cat['name']} - {cat['comment']}")
                else:
                    print("\n❌ Nenhuma categoria relacionada a níveis encontrada.")
                
            else:
                print(f"Erro ao buscar categorias: {response.status_code if response else 'Sem resposta'}")
        except Exception as e:
            print(f"Erro ao investigar categorias: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 2. Verificar categorias dos técnicos ativos
        print("2. CATEGORIAS DOS TÉCNICOS ATIVOS:")
        print("-" * 35)
        
        # Obter ranking de técnicos
        ranking = service.get_technician_ranking()
        
        if ranking:
            print(f"Verificando categorias dos {len(ranking)} técnicos ativos:")
            
            category_usage = {}
            techs_with_category = 0
            techs_without_category = 0
            
            for tech in ranking:
                user_id = int(tech['id'])
                tech_name = tech['name']
                
                try:
                    # Buscar dados do usuário incluindo categoria
                    response = service._make_authenticated_request(
                        'GET',
                        f"{service.glpi_url}/User/{user_id}"
                    )
                    
                    if response and response.ok:
                        user_data = response.json()
                        category_id = user_data.get('usercategories_id')
                        
                        if category_id and category_id != '0':
                            techs_with_category += 1
                            
                            # Buscar nome da categoria
                            try:
                                cat_response = service._make_authenticated_request(
                                    'GET',
                                    f"{service.glpi_url}/UserCategory/{category_id}"
                                )
                                
                                if cat_response and cat_response.ok:
                                    cat_data = cat_response.json()
                                    cat_name = cat_data.get('name', f'Categoria {category_id}')
                                    
                                    if category_id not in category_usage:
                                        category_usage[category_id] = {
                                            'name': cat_name,
                                            'count': 0,
                                            'technicians': []
                                        }
                                    
                                    category_usage[category_id]['count'] += 1
                                    category_usage[category_id]['technicians'].append({
                                        'id': user_id,
                                        'name': tech_name,
                                        'tickets': tech.get('total_tickets', 0)
                                    })
                                    
                                    print(f"  ✅ {tech_name}: Categoria {category_id} ({cat_name})")
                                else:
                                    print(f"  ⚠️  {tech_name}: Categoria {category_id} (erro ao buscar nome)")
                            except:
                                print(f"  ⚠️  {tech_name}: Categoria {category_id} (erro na consulta)")
                        else:
                            techs_without_category += 1
                            print(f"  ❌ {tech_name}: Sem categoria")
                    else:
                        print(f"  ❌ {tech_name}: Erro ao buscar dados do usuário")
                        
                except Exception as e:
                    print(f"  ❌ {tech_name}: Erro - {e}")
            
            print(f"\n📊 RESUMO DAS CATEGORIAS:")
            print(f"  Técnicos com categoria: {techs_with_category}")
            print(f"  Técnicos sem categoria: {techs_without_category}")
            print(f"  Total de técnicos: {len(ranking)}")
            
            if category_usage:
                print(f"\n📈 DISTRIBUIÇÃO POR CATEGORIA:")
                for cat_id, cat_info in sorted(category_usage.items(), key=lambda x: x[1]['count'], reverse=True):
                    print(f"\n  🏷️  Categoria {cat_id}: {cat_info['name']}")
                    print(f"     Técnicos: {cat_info['count']}")
                    
                    # Mostrar os primeiros 5 técnicos desta categoria
                    top_techs = sorted(cat_info['technicians'], key=lambda x: x['tickets'], reverse=True)[:5]
                    print(f"     Top técnicos:")
                    for tech in top_techs:
                        print(f"       - {tech['name']} ({tech['tickets']} tickets)")
        
        print("\n" + "="*80 + "\n")
        
        # 3. Análise e recomendações
        print("3. ANÁLISE E RECOMENDAÇÕES:")
        print("-" * 28)
        
        if category_usage:
            print("\n🎯 POSSIBILIDADES ENCONTRADAS:")
            
            # Verificar se as categorias podem ser mapeadas para níveis
            if len(category_usage) >= 2:
                print(f"\n✅ OPÇÃO 1: USAR CATEGORIAS EXISTENTES")
                print(f"   - {len(category_usage)} categorias em uso")
                print(f"   - Pode ser mapeado para níveis N1-N4")
                print(f"   - Requer configuração no service_levels")
                
                print(f"\n🔧 MAPEAMENTO SUGERIDO:")
                sorted_cats = sorted(category_usage.items(), key=lambda x: x[1]['count'], reverse=True)
                
                level_names = ['N1', 'N2', 'N3', 'N4']
                for i, (cat_id, cat_info) in enumerate(sorted_cats[:4]):
                    level = level_names[i] if i < len(level_names) else f'N{i+1}'
                    print(f"   {level}: Categoria {cat_id} ({cat_info['name']}) - {cat_info['count']} técnicos")
            else:
                print(f"\n⚠️  LIMITAÇÃO: Apenas {len(category_usage)} categoria(s) em uso")
                print(f"   - Insuficiente para 4 níveis (N1-N4)")
        
        print(f"\n✅ OPÇÃO 2: MANTER DISTRIBUIÇÃO POR PERFORMANCE")
        print(f"   - Solução atual funcional")
        print(f"   - Baseada em métricas objetivas")
        print(f"   - Não requer configuração adicional no GLPI")
        
        print(f"\n🏗️  OPÇÃO 3: CONFIGURAR CATEGORIAS NO GLPI")
        print(f"   - Criar categorias específicas (N1, N2, N3, N4)")
        print(f"   - Atribuir técnicos às categorias")
        print(f"   - Requer trabalho manual")
        
        print(f"\n💡 RECOMENDAÇÃO FINAL:")
        if category_usage and len(category_usage) >= 2:
            print(f"   🎯 Usar as categorias existentes com mapeamento personalizado")
            print(f"   📝 Atualizar service_levels para usar as categorias encontradas")
        else:
            print(f"   🎯 Manter a distribuição por performance")
            print(f"   📝 É a solução mais prática para o cenário atual")
        
        service.close_session()
        
    except Exception as e:
        logger.error(f"Erro na investigação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_user_categories()