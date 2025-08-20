#!/usr/bin/env python3
"""
Script principal para executar todos os testes de debug do GLPI Dashboard
Uso: python run_all_tests.py [--quick] [--verbose] [--category CATEGORY]
"""

import subprocess
import sys
import os
import argparse
import json
from datetime import datetime
from pathlib import Path

def log(message, level='INFO'):
    """Log com timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    icons = {
        'INFO': '🔍',
        'SUCCESS': '✅',
        'ERROR': '❌',
        'WARNING': '⚠️',
        'DEBUG': '🐛'
    }
    icon = icons.get(level, 'ℹ️')
    print(f"{icon} [{timestamp}] {message}")

def run_script(script_path, description, args=None, timeout=300):
    """Executa um script e retorna o resultado"""
    log(f"Executando: {description}", 'INFO')
    
    if not os.path.exists(script_path):
        log(f"Script não encontrado: {script_path}", 'ERROR')
        return False
    
    try:
        # Determina o comando baseado na extensão do arquivo
        if script_path.endswith('.py'):
            cmd = ['python', script_path]
        elif script_path.endswith('.js'):
            cmd = ['node', script_path]
        else:
            log(f"Tipo de script não suportado: {script_path}", 'ERROR')
            return False
        
        # Adiciona argumentos se fornecidos
        if args:
            cmd.extend(args)
        
        # Executa o script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode == 0:
            log(f"✅ {description} - PASSOU", 'SUCCESS')
            return True
        else:
            log(f"❌ {description} - FALHOU (código: {result.returncode})", 'ERROR')
            if result.stderr:
                log(f"Erro: {result.stderr[:200]}...", 'ERROR')
            return False
            
    except subprocess.TimeoutExpired:
        log(f"❌ {description} - TIMEOUT ({timeout}s)", 'ERROR')
        return False
    except Exception as e:
        log(f"❌ {description} - ERRO: {e}", 'ERROR')
        return False

def test_api_endpoints(quick=False):
    """Testa endpoints da API"""
    log("\n🌐 === TESTANDO API ENDPOINTS ===", 'INFO')
    
    script_path = Path(__file__).parent / 'api' / 'test_api_endpoints.py'
    args = ['--host', 'localhost', '--port', '5000']
    
    if quick:
        # Em modo rápido, testa apenas endpoints básicos
        pass
    
    return run_script(str(script_path), "Teste de API Endpoints", args)

def test_glpi_connection(quick=False):
    """Testa conexão com GLPI"""
    log("\n🔌 === TESTANDO CONEXÃO GLPI ===", 'INFO')
    
    script_path = Path(__file__).parent / 'glpi' / 'test_glpi_connection.py'
    args = []
    
    return run_script(str(script_path), "Teste de Conexão GLPI", args)

def test_database_queries(quick=False):
    """Testa queries do banco de dados"""
    log("\n🗄️  === TESTANDO BANCO DE DADOS ===", 'INFO')
    
    script_path = Path(__file__).parent / 'database' / 'test_database_queries.py'
    args = []
    
    return run_script(str(script_path), "Teste de Queries do Banco", args)

def test_frontend_components(quick=False):
    """Testa componentes do frontend"""
    log("\n🎨 === TESTANDO FRONTEND ===", 'INFO')
    
    script_path = Path(__file__).parent / 'frontend' / 'test_frontend_components.js'
    args = []
    
    return run_script(str(script_path), "Teste de Componentes Frontend", args, timeout=600)

def test_ranking_specific():
    """Testa funcionalidades específicas do ranking"""
    log("\n🏆 === TESTANDO RANKING ESPECÍFICO ===", 'INFO')
    
    ranking_scripts = list(Path(__file__).parent.glob('ranking/*.py'))
    
    if not ranking_scripts:
        log("Nenhum script de ranking encontrado", 'WARNING')
        return True
    
    results = []
    for script in ranking_scripts:
        result = run_script(str(script), f"Teste de Ranking - {script.name}")
        results.append(result)
    
    return all(results)

def generate_report(results, output_file=None):
    """Gera relatório dos testes"""
    log("\n📊 === GERANDO RELATÓRIO ===", 'INFO')
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_categories': len(results),
            'passed_categories': sum(1 for r in results.values() if r),
            'failed_categories': sum(1 for r in results.values() if not r)
        },
        'details': results,
        'recommendations': []
    }
    
    # Adiciona recomendações baseadas nos resultados
    if not results.get('api_endpoints', True):
        report['recommendations'].append("Verificar se o servidor backend está rodando na porta 5000")
    
    if not results.get('glpi_connection', True):
        report['recommendations'].append("Verificar configuração de conexão com GLPI")
    
    if not results.get('database_queries', True):
        report['recommendations'].append("Verificar integridade do banco de dados SQLite")
    
    if not results.get('frontend_components', True):
        report['recommendations'].append("Verificar dependências e build do frontend")
    
    # Salva relatório se especificado
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            log(f"Relatório salvo em: {output_file}", 'SUCCESS')
        except Exception as e:
            log(f"Erro ao salvar relatório: {e}", 'ERROR')
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Executa todos os testes de debug do GLPI Dashboard')
    parser.add_argument('--quick', action='store_true', help='Executa apenas testes rápidos')
    parser.add_argument('--verbose', '-v', action='store_true', help='Saída verbosa')
    parser.add_argument('--category', choices=['api', 'glpi', 'database', 'frontend', 'ranking'], 
                       help='Executa apenas uma categoria específica')
    parser.add_argument('--report', help='Arquivo para salvar relatório JSON')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout para cada teste (segundos)')
    
    args = parser.parse_args()
    
    log("🚀 INICIANDO TESTES DE DEBUG DO GLPI DASHBOARD", 'INFO')
    log(f"Timestamp: {datetime.now().isoformat()}", 'INFO')
    log(f"Modo: {'Rápido' if args.quick else 'Completo'}", 'INFO')
    
    if args.category:
        log(f"Categoria selecionada: {args.category}", 'INFO')
    
    # Define quais testes executar
    test_categories = {
        'api_endpoints': test_api_endpoints,
        'glpi_connection': test_glpi_connection,
        'database_queries': test_database_queries,
        'frontend_components': test_frontend_components,
        'ranking_specific': test_ranking_specific
    }
    
    # Filtra por categoria se especificado
    if args.category:
        category_map = {
            'api': ['api_endpoints'],
            'glpi': ['glpi_connection'],
            'database': ['database_queries'],
            'frontend': ['frontend_components'],
            'ranking': ['ranking_specific']
        }
        
        selected_categories = category_map.get(args.category, [])
        test_categories = {k: v for k, v in test_categories.items() if k in selected_categories}
    
    # Executa os testes
    results = {}
    
    for category_name, test_function in test_categories.items():
        try:
            if args.quick and category_name in ['frontend_components']:
                # Pula testes demorados em modo rápido
                log(f"Pulando {category_name} (modo rápido)", 'INFO')
                results[category_name] = None
                continue
            
            result = test_function(quick=args.quick)
            results[category_name] = result
            
        except KeyboardInterrupt:
            log("\n⚠️  Testes interrompidos pelo usuário", 'WARNING')
            break
        except Exception as e:
            log(f"Erro inesperado em {category_name}: {e}", 'ERROR')
            results[category_name] = False
    
    # Gera relatório
    report = generate_report(results, args.report)
    
    # Resumo final
    log("\n" + "=" * 60, 'INFO')
    log("📊 RESUMO FINAL DOS TESTES", 'INFO')
    log("=" * 60, 'INFO')
    
    for category, result in results.items():
        if result is None:
            status = "PULADO"
            icon = "⏭️"
        elif result:
            status = "PASSOU"
            icon = "✅"
        else:
            status = "FALHOU"
            icon = "❌"
        
        log(f"{icon} {category.replace('_', ' ').title()}: {status}", 'INFO')
    
    # Estatísticas
    total_tests = len([r for r in results.values() if r is not None])
    passed_tests = len([r for r in results.values() if r is True])
    
    log(f"\n🎯 Resultado Geral: {passed_tests}/{total_tests} categorias passaram", 'INFO')
    
    # Recomendações
    if report['recommendations']:
        log("\n💡 RECOMENDAÇÕES:", 'INFO')
        for i, rec in enumerate(report['recommendations'], 1):
            log(f"  {i}. {rec}", 'INFO')
    
    # Código de saída
    if passed_tests == total_tests and total_tests > 0:
        log("\n🎉 TODOS OS TESTES PASSARAM!", 'SUCCESS')
        sys.exit(0)
    else:
        log("\n⚠️  ALGUNS TESTES FALHARAM", 'WARNING')
        sys.exit(1)

if __name__ == "__main__":
    main()