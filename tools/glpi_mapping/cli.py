# -*- coding: utf-8 -*-
"""
CLI para ferramentas de mapeamento GLPI
Interface de linha de comando para extração e mapeamento de catálogos
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .mapper import GLPIMapper, GLPIConfig


app = typer.Typer(
    name="glpi-mapping",
    help="Ferramentas para mapeamento e manutenção de catálogos GLPI",
    add_completion=False
)
console = Console()


def get_glpi_config() -> GLPIConfig:
    """Obtém configuração GLPI das variáveis de ambiente"""
    base_url = os.getenv('GLPI_BASE_URL') or os.getenv('GLPI_URL')
    app_token = os.getenv('GLPI_APP_TOKEN')
    user_token = os.getenv('GLPI_USER_TOKEN')
    
    if not all([base_url, app_token, user_token]):
        console.print("[red]✗ Configuração GLPI incompleta![/red]")
        console.print("Variáveis necessárias:")
        console.print("  - GLPI_BASE_URL ou GLPI_URL")
        console.print("  - GLPI_APP_TOKEN")
        console.print("  - GLPI_USER_TOKEN")
        raise typer.Exit(1)
    
    return GLPIConfig(
        base_url=base_url.rstrip('/'),
        app_token=app_token,
        user_token=user_token
    )


@app.command()
def dump(
    base_url: Optional[str] = typer.Option(None, "--base-url", help="URL base do GLPI"),
    app_token: Optional[str] = typer.Option(None, "--app-token", help="Token da aplicação"),
    user_token: Optional[str] = typer.Option(None, "--user-token", help="Token do usuário"),
    output: Path = typer.Option(Path("./lookups"), "--out", "-o", help="Diretório de saída"),
    catalog: Optional[str] = typer.Option(None, "--catalog", "-c", help="Catálogo específico para extrair"),
    detect_levels: bool = typer.Option(False, "--detect-levels", help="Detectar níveis hierárquicos"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Limite de itens por catálogo"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Saída detalhada")
):
    """Extrai catálogos do GLPI e salva como JSON/CSV"""
    
    # Configurar logging
    import logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Configuração GLPI
        if base_url and app_token and user_token:
            config = GLPIConfig(
                base_url=base_url.rstrip('/'),
                app_token=app_token,
                user_token=user_token
            )
        else:
            config = get_glpi_config()
        
        # Criar mapper
        mapper = GLPIMapper(config)
        
        # Mostrar informações
        console.print(Panel.fit(
            f"[bold blue]GLPI Mapping Tool[/bold blue]\n"
            f"URL: {config.base_url}\n"
            f"Saída: {output.absolute()}\n"
            f"Catálogo: {catalog or 'Todos'}\n"
            f"Limite: {limit} itens por catálogo",
            title="Configuração"
        ))
        
        try:
            if catalog:
                # Extrair catálogo específico
                items = mapper.extract_catalog(catalog, limit=limit)
                
                output.mkdir(parents=True, exist_ok=True)
                
                # Salvar JSON
                json_file = output / f"{catalog}.json"
                import json
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(
                        [item.model_dump() for item in items],
                        f,
                        indent=2,
                        ensure_ascii=False
                    )
                
                # Salvar CSV
                csv_file = output / f"{catalog}.csv"
                mapper._save_as_csv(items, csv_file)
                
                console.print(f"[green]✓ {len(items)} itens extraídos de '{catalog}'[/green]")
                
                if detect_levels:
                    hierarchy = mapper.detect_hierarchy_levels(catalog)
                    console.print(f"[blue]Níveis detectados: {hierarchy['max_level']}[/blue]")
                    
                    # Salvar análise de hierarquia
                    hierarchy_file = output / f"{catalog}_hierarchy.json"
                    with open(hierarchy_file, 'w', encoding='utf-8') as f:
                        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
            
            else:
                # Extrair todos os catálogos
                results = mapper.extract_all_catalogs(output, detect_levels=detect_levels)
                
                # Mostrar resumo
                table = Table(title="Resumo da Extração")
                table.add_column("Catálogo", style="cyan")
                table.add_column("Itens", justify="right", style="green")
                
                for catalog_name, count in results.items():
                    table.add_row(catalog_name, str(count))
                
                table.add_row("[bold]TOTAL[/bold]", f"[bold]{sum(results.values())}[/bold]")
                console.print(table)
        
        finally:
            # Limpar sessão
            mapper.cleanup_session()
        
        console.print("[bold green]✓ Extração concluída com sucesso![/bold green]")
        
    except Exception as e:
        console.print(f"[red]✗ Erro durante a extração: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def list_catalogs():
    """Lista catálogos disponíveis para extração"""
    try:
        config = get_glpi_config()
        mapper = GLPIMapper(config)
        
        table = Table(title="Catálogos Disponíveis")
        table.add_column("Nome", style="cyan")
        table.add_column("Endpoint", style="yellow")
        table.add_column("Campos", style="green")
        
        for name, mapping in mapper.catalog_mappings.items():
            fields = ", ".join(mapping['fields'][:3])  # Primeiros 3 campos
            if len(mapping['fields']) > 3:
                fields += f" (+{len(mapping['fields']) - 3} mais)"
            
            table.add_row(name, mapping['endpoint'], fields)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def test_connection(
    base_url: Optional[str] = typer.Option(None, "--base-url", help="URL base do GLPI"),
    app_token: Optional[str] = typer.Option(None, "--app-token", help="Token da aplicação"),
    user_token: Optional[str] = typer.Option(None, "--user-token", help="Token do usuário")
):
    """Testa conexão com a API do GLPI"""
    try:
        # Configuração GLPI
        if base_url and app_token and user_token:
            config = GLPIConfig(
                base_url=base_url.rstrip('/'),
                app_token=app_token,
                user_token=user_token
            )
        else:
            config = get_glpi_config()
        
        console.print(f"[blue]Testando conexão com: {config.base_url}[/blue]")
        
        mapper = GLPIMapper(config)
        
        if mapper._authenticate():
            console.print("[green]✓ Conexão bem-sucedida![/green]")
            
            # Testar uma requisição simples
            data = mapper._make_request('getFullSession')
            if data:
                console.print(f"[green]✓ Sessão ativa: {data.get('session', {}).get('glpi_version', 'N/A')}[/green]")
            
            mapper.cleanup_session()
        else:
            console.print("[red]✗ Falha na conexão![/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def analyze(
    catalog: str = typer.Argument(..., help="Nome do catálogo para analisar"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="URL base do GLPI"),
    app_token: Optional[str] = typer.Option(None, "--app-token", help="Token da aplicação"),
    user_token: Optional[str] = typer.Option(None, "--user-token", help="Token do usuário"),
    limit: int = typer.Option(100, "--limit", "-l", help="Limite de itens para análise")
):
    """Analisa estrutura hierárquica de um catálogo"""
    try:
        # Configuração GLPI
        if base_url and app_token and user_token:
            config = GLPIConfig(
                base_url=base_url.rstrip('/'),
                app_token=app_token,
                user_token=user_token
            )
        else:
            config = get_glpi_config()
        
        mapper = GLPIMapper(config)
        
        try:
            hierarchy = mapper.detect_hierarchy_levels(catalog)
            
            console.print(Panel.fit(
                f"[bold blue]Análise do Catálogo: {catalog}[/bold blue]\n"
                f"Total de itens: {hierarchy['total_items']}\n"
                f"Níveis máximos: {hierarchy['max_level']}\n"
                f"Níveis encontrados: {list(hierarchy['hierarchy'].keys())}",
                title="Resumo"
            ))
            
            # Mostrar detalhes por nível
            for level, items in hierarchy['hierarchy'].items():
                table = Table(title=f"Nível {level} ({len(items)} itens)")
                table.add_column("ID", style="cyan")
                table.add_column("Nome", style="green")
                table.add_column("Parent ID", style="yellow")
                
                for item in items[:10]:  # Mostrar apenas os primeiros 10
                    table.add_row(
                        str(item['id']),
                        item['name'][:50] + ('...' if len(item['name']) > 50 else ''),
                        str(item['parent_id']) if item['parent_id'] else '-'
                    )
                
                if len(items) > 10:
                    table.add_row("...", f"(+{len(items) - 10} itens)", "...")
                
                console.print(table)
        
        finally:
            mapper.cleanup_session()
            
    except Exception as e:
        console.print(f"[red]✗ Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Mostra versão da ferramenta"""
    from . import __version__
    console.print(f"[bold blue]GLPI Mapping Tool v{__version__}[/bold blue]")


def main():
    """Ponto de entrada principal"""
    app()


if __name__ == "__main__":
    main()