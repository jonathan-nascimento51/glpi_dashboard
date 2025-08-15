#!/usr/bin/env python3
"""
Script de Exemplo - Protocolo de Mudanças Seguras

Este script demonstra como usar o protocolo de mudanças seguras
para implementar mudanças no GLPI Dashboard de forma controlada.

Autor: Sistema de Otimização GLPI Dashboard
Data: 2025-08-14
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path para importar o módulo
sys.path.append(str(Path(__file__).parent))

from safe_change_protocol import SafeChangeProtocol, ChangeType

def example_metric_change():
    """Exemplo de mudança em cálculo de métricas"""
    
    print(" Iniciando exemplo de mudança em métricas...")
    
    # Inicializar protocolo
    protocol = SafeChangeProtocol()
    
    # Criar solicitação de mudança
    change_request = protocol.create_change_request(
        title="Correção de cálculo de tickets por status",
        description="Corrigir algoritmo que estava retornando valores zerados para alguns status de tickets",
        change_type=ChangeType.METRIC_CALCULATION,
        affected_files=[
            "backend/app/services/metrics_service.py",
            "backend/app/models/ticket.py",
            "frontend/components/StatusMetricsCard.py"
        ],
        affected_metrics=[
            "tickets_by_status",
            "total_open_tickets",
            "resolution_rate"
        ],
        risk_level="HIGH",
        author="sistema_otimizacao"
    )
    
    print(f" Solicitação de mudança criada: {change_request.id}")
    
    # Fase 1: Backup
    print("\n Fase 1: Criando backup dos arquivos afetados...")
    if protocol.backup_affected_files(change_request):
        print(" Backup criado com sucesso")
    else:
        print(" Falha ao criar backup")
        return False
    
    # Fase 2: Testes obrigatórios
    print("\n Fase 2: Executando testes obrigatórios...")
    test_results = protocol.run_mandatory_tests(change_request)
    
    print(f"Status dos testes: {test_results['overall_status']}")
    for test_name, result in test_results.get('tests', {}).items():
        status_icon = "" if result.get('status') == 'PASSED' else ""
        print(f"  {status_icon} {test_name}: {result.get('status')}")
    
    if test_results['overall_status'] != 'PASSED':
        print(" Testes falharam. Mudança não pode ser aplicada.")
        return False
    
    # Fase 3: Validação de integridade
    print("\n Fase 3: Validando integridade do sistema...")
    validation_results = protocol.validate_integrity(change_request)
    
    print(f"Status da validação: {validation_results['overall_status']}")
    for validation_name, result in validation_results.get('validations', {}).items():
        status_icon = "" if result.get('status') == 'PASSED' else ""
        print(f"  {status_icon} {validation_name}: {result.get('status')}")
    
    if validation_results['overall_status'] != 'PASSED':
        print(" Validação falhou. Mudança não pode ser aplicada.")
        return False
    
    # Fase 4: Aplicar mudança
    print("\n Fase 4: Aplicando mudança...")
    if protocol.apply_change(change_request):
        print(" Mudança aplicada com sucesso")
    else:
        print(" Falha ao aplicar mudança")
        return False
    
    # Gerar relatório
    print("\n Gerando relatório da mudança...")
    report = protocol.generate_change_report(change_request)
    
    # Salvar relatório
    report_file = f"reports/change_report_{change_request.id}.md"
    os.makedirs("reports", exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f" Relatório salvo em: {report_file}")
    
    return True

def example_rollback():
    """Exemplo de rollback de mudança"""
    
    print("\n Exemplo de rollback...")
    
    protocol = SafeChangeProtocol()
    
    # Listar mudanças recentes
    history = protocol.get_change_history()
    
    if not history:
        print(" Nenhuma mudança encontrada para rollback")
        return False
    
    # Pegar a mudança mais recente
    latest_change = history[0]
    print(f" Mudança mais recente: {latest_change.get('title')}")
    
    # Simular rollback (em um cenário real, você carregaria a mudança completa)
    print("  Executando rollback...")
    print(" Rollback simulado com sucesso")
    
    return True

def show_change_history():
    """Mostra histórico de mudanças"""
    
    print("\n Histórico de Mudanças")
    print("=" * 50)
    
    protocol = SafeChangeProtocol()
    history = protocol.get_change_history()
    
    if not history:
        print(" Nenhuma mudança registrada")
        return
    
    for i, change in enumerate(history[:5], 1):  # Mostrar apenas as 5 mais recentes
        print(f"\n{i}. {change.get('title')}")
        print(f"   ID: {change.get('id')}")
        print(f"   Tipo: {change.get('change_type')}")
        print(f"   Status: {change.get('status')}")
        print(f"   Risco: {change.get('risk_level')}")
        print(f"   Data: {change.get('created_at')}")

def main():
    """Função principal"""
    
    print("  PROTOCOLO DE MUDANÇAS SEGURAS - GLPI DASHBOARD")
    print("=" * 60)
    
    try:
        # Exemplo 1: Mudança em métricas
        if example_metric_change():
            print("\n Exemplo de mudança executado com sucesso!")
        
        # Exemplo 2: Mostrar histórico
        show_change_history()
        
        # Exemplo 3: Rollback
        example_rollback()
        
        print("\n Demonstração do protocolo concluída!")
        
    except Exception as e:
        print(f" Erro durante execução: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
