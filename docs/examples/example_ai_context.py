#!/usr/bin/env python3`n# -*- coding: utf-8 -*-
"""
Exemplo de Uso do Sistema de AI Context

Este arquivo demonstra como usar o sistema de treinamento e otimização
do AI Context, incluindo exemplos práticos de configuração e monitoramento.

Autor: GLPI Dashboard Team
Versão: 1.0.0
Data: 2024
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Importar o sistema de AI Context
try:
    from ai_context_system import AIContextSystem, ContextType, Priority
    from config_ai_context import MCP_CONFIGS, PERFORMANCE_CONFIG
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que ai_context_system.py e config_ai_context.py estão no mesmo diretório")
    exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def exemplo_basico():
    """
    Exemplo básico de uso do sistema de AI Context.
    """
    print("\n" + "="*60)
    print("EXEMPLO 1: Uso Básico do AI Context System")
    print("="*60)
    
    # Inicializar o sistema
    system = AIContextSystem()
    
    # Obter resumo do contexto atual
    summary = await system.get_context_summary()
    print(f"\nResumo do Contexto Atual:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Simular adição de contexto manual
    from ai_context_system import ContextItem
    
    # Criar item de contexto de exemplo
    context_item = ContextItem(
        id="example_architecture",
        type=ContextType.ARCHITECTURE,
        title="Arquitetura do GLPI Dashboard",
        content="Sistema de dashboard para GLPI com FastAPI backend e Dash frontend",
        priority=Priority.HIGH,
        tags={"glpi", "dashboard", "fastapi", "dash"},
        metadata={
            "created_by": "example",
            "version": "1.0.0"
        }
    )
    
    # Adicionar ao sistema
    system.context_items[context_item.id] = context_item
    
    print(f"\nItem de contexto adicionado: {context_item.title}")
    print(f"Tipo: {context_item.type.value}")
    print(f"Prioridade: {context_item.priority.value}")
    print(f"Tags: {context_item.tags}")
    
    return system


async def exemplo_monitoramento_arquivos():
    """
    Exemplo de monitoramento de mudanças em arquivos.
    """
    print("\n" + "="*60)
    print("EXEMPLO 2: Monitoramento de Arquivos")
    print("="*60)
    
    system = AIContextSystem()
    
    # Simular processamento de arquivo
    test_file = Path("test_context_file.py")
    
    # Criar arquivo de teste
    test_content = '''
#!/usr/bin/env python3`n# -*- coding: utf-8 -*-
"""
Arquivo de teste para demonstração do AI Context.
"""

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GLPI Dashboard API")

class TicketModel(BaseModel):
    """Modelo para tickets do GLPI."""
    id: int
    title: str
    status: str
    priority: str

@app.get("/tickets")
async def get_tickets():
    """Endpoint para obter tickets."""
    return {"tickets": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # Escrever arquivo de teste
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"Arquivo de teste criado: {test_file}")
    
    # Processar arquivo
    context_type = system._determine_context_type(str(test_file))
    print(f"Tipo de contexto detectado: {context_type.value if context_type else 'Nenhum'}")
    
    if context_type:
        await system._extract_context_from_file(test_file, context_type)
        print(f"Contexto extraído do arquivo {test_file.name}")
        
        # Mostrar itens de contexto
        for item_id, item in system.context_items.items():
            if item.source_file and test_file.name in item.source_file:
                print(f"\nItem extraído:")
                print(f"  ID: {item.id}")
                print(f"  Título: {item.title}")
                print(f"  Tipo: {item.type.value}")
                print(f"  Tags: {item.tags}")
                print(f"  Dependências: {item.dependencies}")
    
    # Limpar arquivo de teste
    test_file.unlink()
    print(f"\nArquivo de teste removido: {test_file}")
    
    return system


async def exemplo_mcps():
    """
    Exemplo de configuração e monitoramento de MCPs.
    """
    print("\n" + "="*60)
    print("EXEMPLO 3: Configuração de MCPs")
    print("="*60)
    
    system = AIContextSystem()
    
    print(f"MCPs configurados: {len(system.mcp_configs)}")
    
    for mcp_name, mcp_config in system.mcp_configs.items():
        print(f"\nMCP: {mcp_name}")
        print(f"  Tipo: {mcp_config.type}")
        print(f"  Descrição: {mcp_config.description}")
        print(f"  Habilitado: {mcp_config.enabled}")
        print(f"  Auto-atualização: {mcp_config.auto_update}")
        print(f"  Intervalo: {mcp_config.update_interval}s")
        print(f"  Dependências: {mcp_config.dependencies}")
    
    # Simular atualização de MCP
    if "filesystem" in system.mcp_configs:
        mcp = system.mcp_configs["filesystem"]
        print(f"\nSimulando atualização do MCP: {mcp.name}")
        await system._update_mcp(mcp)
        print(f"MCP atualizado em: {mcp.last_update}")
    
    return system


async def exemplo_metricas():
    """
    Exemplo de geração e visualização de métricas.
    """
    print("\n" + "="*60)
    print("EXEMPLO 4: Métricas do Sistema")
    print("="*60)
    
    system = AIContextSystem()
    
    # Adicionar alguns itens de contexto para demonstração
    from ai_context_system import ContextItem
    
    items_exemplo = [
        ContextItem(
            id="code_example_1",
            type=ContextType.CODE_PATTERNS,
            title="Padrão FastAPI",
            content="Exemplo de endpoint FastAPI",
            priority=Priority.HIGH,
            tags={"fastapi", "api", "endpoint"}
        ),
        ContextItem(
            id="doc_example_1",
            type=ContextType.DOCUMENTATION,
            title="README Principal",
            content="Documentação do projeto",
            priority=Priority.MEDIUM,
            tags={"documentation", "readme"}
        ),
        ContextItem(
            id="config_example_1",
            type=ContextType.CONFIGURATION,
            title="Configuração Docker",
            content="Configuração do Docker Compose",
            priority=Priority.HIGH,
            tags={"docker", "configuration"}
        )
    ]
    
    for item in items_exemplo:
        system.context_items[item.id] = item
    
    # Gerar métricas
    await system._generate_metrics()
    
    print(f"\nMétricas Geradas:")
    print(f"  Total de itens: {system.metrics.total_items}")
    print(f"  Itens por tipo:")
    for tipo, count in system.metrics.items_by_type.items():
        print(f"    {tipo}: {count}")
    print(f"  Itens por prioridade:")
    for prioridade, count in system.metrics.items_by_priority.items():
        print(f"    {prioridade}: {count}")
    print(f"  Tamanho de armazenamento: {system.metrics.storage_size} bytes")
    print(f"  Tempo de processamento: {system.metrics.processing_time:.3f}s")
    
    return system


async def exemplo_busca_contexto():
    """
    Exemplo de busca e filtragem de contexto.
    """
    print("\n" + "="*60)
    print("EXEMPLO 5: Busca e Filtragem de Contexto")
    print("="*60)
    
    system = AIContextSystem()
    
    # Adicionar itens variados para demonstração
    from ai_context_system import ContextItem
    
    items_exemplo = [
        ContextItem(
            id="api_auth",
            type=ContextType.SECURITY,
            title="Autenticação da API",
            content="Sistema de autenticação JWT para API",
            priority=Priority.CRITICAL,
            tags={"security", "jwt", "authentication", "api"}
        ),
        ContextItem(
            id="db_performance",
            type=ContextType.PERFORMANCE,
            title="Otimização de Banco",
            content="Índices e queries otimizadas para PostgreSQL",
            priority=Priority.HIGH,
            tags={"performance", "database", "postgresql", "optimization"}
        ),
        ContextItem(
            id="test_integration",
            type=ContextType.TESTING,
            title="Testes de Integração",
            content="Suite de testes para endpoints da API",
            priority=Priority.MEDIUM,
            tags={"testing", "integration", "api", "pytest"}
        )
    ]
    
    for item in items_exemplo:
        system.context_items[item.id] = item
    
    # Buscar por tipo
    security_items = [item for item in system.context_items.values() 
                     if item.type == ContextType.SECURITY]
    print(f"\nItens de Segurança: {len(security_items)}")
    for item in security_items:
        print(f"  - {item.title} (Prioridade: {item.priority.value})")
    
    # Buscar por prioridade
    critical_items = [item for item in system.context_items.values() 
                     if item.priority == Priority.CRITICAL]
    print(f"\nItens Críticos: {len(critical_items)}")
    for item in critical_items:
        print(f"  - {item.title} (Tipo: {item.type.value})")
    
    # Buscar por tag
    api_items = [item for item in system.context_items.values() 
                if "api" in item.tags]
    print(f"\nItens relacionados à API: {len(api_items)}")
    for item in api_items:
        print(f"  - {item.title} (Tags: {item.tags})")
    
    return system


async def exemplo_exportacao():
    """
    Exemplo de exportação de contexto.
    """
    print("\n" + "="*60)
    print("EXEMPLO 6: Exportação de Contexto")
    print("="*60)
    
    system = AIContextSystem()
    
    # Adicionar alguns itens
    from ai_context_system import ContextItem
    
    item = ContextItem(
        id="export_example",
        type=ContextType.ARCHITECTURE,
        title="Exemplo para Exportação",
        content="Este é um exemplo de item de contexto para exportação",
        priority=Priority.HIGH,
        tags={"example", "export", "demo"}
    )
    
    system.context_items[item.id] = item
    
    # Salvar contexto
    await system._save_context_to_storage()
    print(f"Contexto salvo em: {system.context_storage}")
    
    # Verificar arquivos criados
    context_file = system.context_storage / "context_items.json"
    if context_file.exists():
        print(f"Arquivo de contexto criado: {context_file}")
        print(f"Tamanho: {context_file.stat().st_size} bytes")
        
        # Mostrar conteúdo (primeiras linhas)
        with open(context_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")[:10]
            print(f"\nPrimeiras linhas do arquivo:")
            for i, line in enumerate(lines, 1):
                print(f"  {i:2d}: {line}")
    
    return system


async def exemplo_monitoramento_continuo():
    """
    Exemplo de monitoramento contínuo (simulado).
    """
    print("\n" + "="*60)
    print("EXEMPLO 7: Monitoramento Contínuo (Simulado)")
    print("="*60)
    
    system = AIContextSystem()
    
    print("Iniciando monitoramento simulado por 10 segundos...")
    print("(Em produção, isso rodaria continuamente)")
    
    # Simular algumas iterações de monitoramento
    for i in range(5):
        print(f"\nIteração {i+1}/5:")
        
        # Simular verificação de arquivos modificados
        modified_files = await system._get_modified_files(datetime.now())
        print(f"  Arquivos modificados detectados: {len(modified_files)}")
        
        # Simular atualização de métricas
        await system._generate_metrics()
        print(f"  Métricas atualizadas: {system.metrics.total_items} itens")
        
        # Simular salvamento
        await system._save_context_to_storage()
        print(f"  Contexto salvo em: {system.context_storage.name}")
        
        # Aguardar antes da próxima iteração
        await asyncio.sleep(2)
    
    print("\nMonitoramento simulado concluído!")
    
    return system


async def exemplo_troubleshooting():
    """
    Exemplo de troubleshooting e validação do sistema.
    """
    print("\n" + "="*60)
    print("EXEMPLO 8: Troubleshooting e Validação")
    print("="*60)
    
    system = AIContextSystem()
    
    # Verificar configuração
    print("Verificando configuração do sistema...")
    
    # Verificar diretório de armazenamento
    if system.context_storage.exists():
        print(f" Diretório de armazenamento existe: {system.context_storage}")
    else:
        print(f" Diretório de armazenamento não existe: {system.context_storage}")
    
    # Verificar MCPs
    print(f"\nMCPs configurados: {len(system.mcp_configs)}")
    for name, mcp in system.mcp_configs.items():
        status = " Habilitado" if mcp.enabled else " Desabilitado"
        print(f"  {name}: {status}")
    
    # Verificar dependências
    try:
        import aiofiles
        print(" aiofiles disponível")
    except ImportError:
        print(" aiofiles não disponível (pip install aiofiles)")
    
    try:
        import yaml
        print(" yaml disponível")
    except ImportError:
        print(" yaml não disponível (pip install pyyaml)")
    
    # Testar funcionalidades básicas
    print("\nTestando funcionalidades básicas...")
    
    try:
        # Testar criação de item
        from ai_context_system import ContextItem
        test_item = ContextItem(
            id="test_validation",
            type=ContextType.TESTING,
            title="Teste de Validação",
            content="Item de teste para validação do sistema",
            priority=Priority.LOW,
            tags={"test", "validation"}
        )
        system.context_items[test_item.id] = test_item
        print(" Criação de item de contexto")
        
        # Testar salvamento
        await system._save_context_to_storage()
        print(" Salvamento de contexto")
        
        # Testar carregamento
        await system._load_existing_context()
        print(" Carregamento de contexto")
        
        # Testar métricas
        await system._generate_metrics()
        print(" Geração de métricas")
        
    except Exception as e:
        print(f" Erro durante teste: {e}")
    
    print("\nValidação concluída!")
    
    return system


async def main():
    """
    Função principal que executa todos os exemplos.
    """
    print(" SISTEMA DE AI CONTEXT - EXEMPLOS PRÁTICOS")
    print("=" * 80)
    
    try:
        # Executar exemplos
        await exemplo_basico()
        await exemplo_monitoramento_arquivos()
        await exemplo_mcps()
        await exemplo_metricas()
        await exemplo_busca_contexto()
        await exemplo_exportacao()
        await exemplo_monitoramento_continuo()
        await exemplo_troubleshooting()
        
        print("\n" + "="*80)
        print(" TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("="*80)
        
        print("\n PRÓXIMOS PASSOS:")
        print("1. Execute `python ai_context_system.py` para monitoramento contínuo")
        print("2. Configure os MCPs em `config_ai_context.py` conforme necessário")
        print("3. Monitore os logs em `ai_context.log`")
        print("4. Verifique o armazenamento em `ai_context_storage/`")
        print("5. Integre com seu pipeline de CI/CD")
        
    except Exception as e:
        logger.error(f"Erro durante execução dos exemplos: {e}")
        print(f"\n ERRO: {e}")
        print("\n TROUBLESHOOTING:")
        print("1. Verifique se todos os arquivos estão no mesmo diretório")
        print("2. Instale dependências: pip install aiofiles pyyaml")
        print("3. Verifique permissões de escrita no diretório")
        print("4. Execute o exemplo de troubleshooting separadamente")


if __name__ == "__main__":
    asyncio.run(main())

