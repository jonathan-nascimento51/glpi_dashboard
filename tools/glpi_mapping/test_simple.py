#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para extração de catálogos GLPI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from mapper import GLPIMapper, GLPIConfig

def test_catalog_extraction():
    """Teste simples de extração"""
    print("🚀 Testando extração de catálogos GLPI")
    print("="*50)
    
    try:
        config = GLPIConfig()
        mapper = GLPIMapper(config)
        
        # Testar cada catálogo
        for catalog_name in mapper.catalog_mappings.keys():
            print(f"\n📋 Testando catálogo: {catalog_name}")
            
            try:
                items = mapper.extract_catalog(catalog_name, limit=10)
                print(f"✅ {catalog_name}: {len(items)} itens extraídos")
                
                # Mostrar primeiro item como exemplo
                if items:
                    first_item = items[0]
                    print(f"   Exemplo: ID={first_item.id}, Nome='{first_item.name}'")
                
            except Exception as e:
                print(f"❌ {catalog_name}: Erro - {e}")
        
        # Encerrar sessão
        mapper.close_session()
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_catalog_extraction()