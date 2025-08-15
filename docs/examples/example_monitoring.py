#!/usr/bin/env python3
"""
Exemplo de Uso do Sistema de Monitoramento Proativo - GLPI Dashboard

Este script demonstra como usar o sistema de monitoramento proativo,
incluindo configuração, execução e análise de resultados.

Autor: Sistema de Otimização GLPI Dashboard
Data: 2025-01-14
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Importar sistema de monitoramento
try:
    from monitoring_system import ProactiveMonitoringSystem, AlertLevel, MetricStatus
    from config_monitoring import get_config_for_environment, validate_config
except ImportError as e:
    print(f" Erro ao importar módulos: {e}")
    print("Certifique-se de que os arquivos monitoring_system.py e config_monitoring.py estão no mesmo diretório.")
    exit(1)

async def example_basic_monitoring():
    """
    Exemplo básico de monitoramento
    """
    print(" Exemplo 1: Monitoramento Básico")
    print("=" * 50)
    
    # Criar instância do sistema
    monitoring = ProactiveMonitoringSystem()
    
    try:
        # Verificar status inicial
        status = await monitoring.get_monitoring_status()
        print(f" Status inicial: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # Executar monitoramento por 2 minutos
        print(" Executando monitoramento por 2 minutos...")
        
        # Criar task de monitoramento
        monitoring_task = asyncio.create_task(monitoring.start_monitoring())
        
        # Aguardar 2 minutos
        await asyncio.sleep(120)
        
        # Parar monitoramento
        await monitoring.stop_monitoring()
        
        # Aguardar task finalizar
        try:
            await asyncio.wait_for(monitoring_task, timeout=5)
        except asyncio.TimeoutError:
            monitoring_task.cancel()
        
        # Verificar status final
        final_status = await monitoring.get_monitoring_status()
        print(f" Status final: {json.dumps(final_status, indent=2, ensure_ascii=False)}")
        
        # Gerar relatório
        report_file = await monitoring.generate_monitoring_report()
        if report_file:
            print(f" Relatório gerado: {report_file}")
        
    except Exception as e:
        print(f" Erro no monitoramento básico: {e}")
        await monitoring.stop_monitoring()

if __name__ == "__main__":
    try:
        asyncio.run(example_basic_monitoring())
    except KeyboardInterrupt:
        print("\n Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n Erro na execução: {e}")
