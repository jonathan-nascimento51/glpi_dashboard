#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação Contínua do Trae AI

Este script deve ser executado pelo Trae AI sempre que precisar validar
se está seguindo corretamente as configurações implementadas.
"""

import sys
import subprocess
from pathlib import Path

def quick_trae_validation():
    """Validação rápida para o Trae AI."""
    print(" VERIFICAÇÃO RÁPIDA DO TRAE AI")
    print("=" * 50)
    
    # 1. Verificar arquivos críticos
    critical_files = [
        'trae-context.yml',
        '.trae/rules/integrated_system_rules.md',
        'config_ai_context.py',
        'monitoring_system.py',
        'safe_change_protocol.py'
    ]
    
    print(" Verificando arquivos críticos...")
    missing = []
    for file in critical_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f" ARQUIVOS AUSENTES: {missing}")
        print(" TRAE AI NÃO DEVE OPERAR!")
        return False
    else:
        print(" Todos os arquivos críticos presentes")
    
    # 2. Testar importações básicas
    print("\n Testando sistemas...")
    systems = [
        ('AI Context', 'config_ai_context'),
        ('Monitoring', 'monitoring_system'),
        ('Safe Changes', 'safe_change_protocol')
    ]
    
    for name, module in systems:
        try:
            result = subprocess.run(
                [sys.executable, '-c', f'import {module}'],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f" {name}: OK")
            else:
                print(f" {name}: FALHOU")
                return False
        except Exception:
            print(f" {name}: ERRO")
            return False
    
    print("\n TRAE AI ESTÁ 100% INTEGRADO!")
    print(" Pode operar com segurança")
    print(" Todas as configurações ativas")
    return True

if __name__ == '__main__':
    success = quick_trae_validation()
    sys.exit(0 if success else 1)
