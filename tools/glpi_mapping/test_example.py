#!/usr/bin/env python3
"""
Exemplo de teste e uso do módulo GLPI Mapping

Este arquivo demonstra como usar o módulo de mapeamento GLPI
programaticamente e como integrar com o dashboard.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Adiciona o diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.glpi_mapping.mapper import GLPIMapper, GLPIConfig
from backend.services.lookup_loader import get_lookup_loader


def test_glpi_connection():
    """Testa a conexão com o GLPI"""
    print("🔍 Testando conexão com GLPI...")
    
    config = GLPIConfig()
    mapper = GLPIMapper(config)
    
    try:
        # Testa autenticação
        if mapper.authenticate():
            print("✅ Conexão com GLPI estabelecida com sucesso!")
            
            # Obtém informações da sessão
            session_info = mapper.get_session_info()
            if session_info:
                print(f"📋 Usuário: {session_info.get('glpiname', 'N/A')}")
                print(f"📋 Versão GLPI: {session_info.get('glpiversion', 'N/A')}")
            
            # Testar endpoints disponíveis
            print("🔍 Testando endpoints disponíveis...")
            test_endpoints = ['User', 'Group', 'ITILCategory', 'Priority', 'Ticket']
            for endpoint in test_endpoints:
                try:
                    url = f"{mapper.config.base_url}{endpoint}?range=0-0"
                    headers = mapper._get_headers()
                    response = requests.get(url, headers=headers, timeout=10)
                    print(f"  {endpoint}: {response.status_code}")
                except Exception as e:
                    print(f"  {endpoint}: Erro - {e}")
            
            return True
        else:
            print("❌ Falha na autenticação com GLPI")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com GLPI: {e}")
        return False
    finally:
        mapper.close_session()


def test_catalog_extraction():
    """Testa a extração de catálogos"""
    print("\n📊 Testando extração de catálogos...")
    
    config = GLPIConfig()
    mapper = GLPIMapper(config)
    
    try:
        if not mapper.authenticate():
            print("❌ Falha na autenticação")
            return False
        
        # Testa extração de diferentes catálogos
        catalogs_to_test = ['users', 'groups', 'categories', 'tickets']
        
        for catalog in catalogs_to_test:
            print(f"\n🔄 Extraindo catálogo: {catalog}")
            
            try:
                items = mapper.extract_catalog(catalog, limit=5)
                if items:
                    print(f"✅ {catalog}: {len(items)} itens extraídos")
                    
                    # Mostra exemplo do primeiro item
                    if items:
                        first_item = items[0]
                        print(f"📋 Exemplo: ID={first_item.id}, Nome='{first_item.name}'")
                else:
                    print(f"⚠️ {catalog}: Nenhum dado retornado")
                    
            except Exception as e:
                print(f"❌ Erro ao extrair {catalog}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral na extração: {e}")
        return False
    finally:
        mapper.close_session()


def test_file_generation():
    """Testa a geração de arquivos de lookup"""
    print("\n💾 Testando geração de arquivos...")
    
    config = GLPIConfig()
    mapper = GLPIMapper(config)
    
    # Diretório de teste
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)
    
    try:
        if not mapper.authenticate():
            print("❌ Falha na autenticação")
            return False
        
        # Extrai e salva catálogo de grupos
        print("🔄 Extraindo e salvando catálogo de grupos...")
        
        items = mapper.extract_catalog('groups', limit=10)
        if items:
            # Salva em JSON
            json_file = test_dir / "groups.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump([item.model_dump() for item in items], f, indent=2, ensure_ascii=False)
            print(f"✅ JSON salvo: {json_file}")
            
            # Salva em CSV
            csv_file = test_dir / "groups.csv"
            mapper._save_as_csv(items, csv_file)
            print(f"✅ CSV salvo: {csv_file}")
            
            # Verifica se arquivos foram criados
            if json_file.exists() and csv_file.exists():
                print(f"📊 Tamanho JSON: {json_file.stat().st_size} bytes")
                print(f"📊 Tamanho CSV: {csv_file.stat().st_size} bytes")
                return True
            else:
                print("❌ Arquivos não foram criados")
                return False
        else:
            print("❌ Nenhum dado extraído")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração de arquivos: {e}")
        return False
    finally:
        mapper.close_session()


def test_lookup_loader_integration():
    """Testa a integração com o LookupLoader do dashboard"""
    print("\n🔗 Testando integração com LookupLoader...")
    
    try:
        # Primeiro, gera alguns dados de teste
        config = GLPIConfig()
        mapper = GLPIMapper(config)
        
        if not mapper.authenticate():
            print("❌ Falha na autenticação para gerar dados")
            return False
        
        # Extrai dados para o diretório de lookup
        print("🔄 Gerando dados de lookup...")
        lookup_dir = Path(__file__).parent.parent.parent / "backend" / "data" / "lookups"
        lookup_dir.mkdir(parents=True, exist_ok=True)
        mapper.extract_all_catalogs(lookup_dir)
        mapper.close_session()
        
        # Agora testa o loader
        loader = get_lookup_loader(lookup_dir)
        
        # Lista catálogos disponíveis
        catalogs = loader.get_available_catalogs()
        print(f"📋 Catálogos disponíveis: {catalogs}")
        
        if not catalogs:
            print("⚠️ Nenhum catálogo encontrado após extração.")
            return False
        
        # Testa carregamento de cada catálogo
        for catalog in catalogs[:2]:  # Testa apenas os primeiros 2
            print(f"\n🔄 Testando catálogo: {catalog}")
            
            try:
                # Carrega dados
                data = loader.load_catalog(catalog)
                if data:
                    count = len(data) if isinstance(data, list) else len(data.get('items', []))
                    print(f"✅ {catalog}: {count} itens carregados")
                    
                    # Testa lookup dictionary
                    lookup = loader.get_lookup_dict(catalog)
                    if lookup:
                        print(f"📋 Lookup {catalog}: {len(lookup)} mapeamentos")
                        # Mostra exemplo
                        if lookup:
                            first_key = next(iter(lookup))
                            print(f"📋 Exemplo: {first_key} -> {lookup[first_key]}")
                    
                    # Verifica frescor dos dados
                    is_fresh = loader.is_data_fresh(catalog)
                    print(f"🕐 Dados atualizados: {'Sim' if is_fresh else 'Não'}")
                    
                    # Obtém metadados
                    metadata = loader.get_extraction_metadata()
                    if metadata:
                        extraction_time = metadata.get('extraction_date')
                        print(f"📅 Última extração: {extraction_time}")
                
                else:
                    print(f"⚠️ {catalog}: Nenhum dado carregado")
                    
            except Exception as e:
                print(f"❌ Erro ao testar {catalog}: {e}")
        
        # Testa estatísticas
        print("\n📊 Testando estatísticas...")
        try:
            all_stats = loader.get_catalog_stats()
            for catalog in catalogs[:2]:
                if catalog in all_stats:
                    stats = all_stats[catalog]
                    print(f"📊 {catalog}: {stats['items_count']} itens, {stats['file_size']} bytes")
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração com LookupLoader: {e}")
        return False


def main():
    """Função principal de teste - executa todos os testes"""
    print("🚀 Iniciando testes do módulo GLPI Mapping\n")
    print("=" * 50)
    
    # Verifica variáveis de ambiente
    required_vars = ['GLPI_BASE_URL', 'GLPI_APP_TOKEN', 'GLPI_USER_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("💡 Configure as variáveis no arquivo .env")
        return False
    
    # Executa testes
    tests = [
        ("Conexão GLPI", test_glpi_connection),
        ("Extração de Catálogos", test_catalog_extraction),
        ("Geração de Arquivos", test_file_generation),
        ("Integração LookupLoader", test_lookup_loader_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print(f"\n{'='*50}")
    print("📋 RESUMO DOS TESTES")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! O módulo está funcionando corretamente.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique a configuração e logs.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)