#!/usr/bin/env python3
"""
Script para verificação automática de problemas conhecidos
"""

import re
import os
from pathlib import Path

def check_undefined_variables():
    """Verifica variáveis não definidas em arquivos TypeScript"""
    issues = []
    
    # Verificar useDashboard.ts
    file_path = "frontend/src/hooks/useDashboard.ts"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar por currentDateRange
        if 'currentDateRange' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'currentDateRange' in line and line.strip().startswith('//'):
                    issues.append(f"⚠️  Variável comentada mas ainda em uso: {file_path}:{i}")
                    
    return issues

def check_api_calls():
    """Verifica se chamadas de API estão corretas"""
    issues = []
    
    # Verificar se getMetrics está sendo chamada sem parâmetros
    file_path = "frontend/src/hooks/useDashboard.ts"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'apiService.getMetrics(currentDateRange)' in content:
            issues.append(f"⚠️  API call com filtro de data problemático: {file_path}")
            
    return issues

if __name__ == "__main__":
    print("🔍 Verificando problemas conhecidos...")
    
    all_issues = []
    all_issues.extend(check_undefined_variables())
    all_issues.extend(check_api_calls())
    
    if all_issues:
        print("\n❌ Problemas encontrados:")
        for issue in all_issues:
            print(f"  {issue}")
    else:
        print("\n✅ Nenhum problema conhecido detectado!")