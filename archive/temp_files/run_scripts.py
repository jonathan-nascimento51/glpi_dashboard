#!/usr/bin/env python3
"""
Script para executar facilmente os scripts auxiliares do projeto.
Uso: python run_scripts.py <categoria> <script>

Exemplos de uso:
  python run_scripts.py debug metrics
  python run_scripts.py debug trends
  python run_scripts.py validation frontend_trends
  python run_scripts.py validation trends_math
  python run_scripts.py tests trends
"""

import sys
import os
import subprocess
from pathlib import Path

# Mapeamento dos scripts disponíveis
SCRIPTS = {
    'analysis': {
        'check_dtic_users': 'scripts/analysis/check_dtic_users.py',
        'compare_technicians': 'scripts/analysis/compare_technicians.py',
        'extract_technicians': 'scripts/analysis/extract_all_technicians.py',
        'final_comparison': 'scripts/analysis/final_comparison.py',
        'list_groups': 'scripts/analysis/list_all_groups.py',
        'analyze_non_technicians': 'scripts/analysis/analyze_non_technicians_root.py',
        'simple_user_analysis': 'scripts/analysis/simple_user_analysis_root.py'
    },
    'debug': {
        'metrics': 'scripts/debug/debug_metrics.py',
        'trends': 'scripts/debug/debug_trends.py',
        'react_keys': 'scripts/debug/debug_react_keys.py',
        'duplicate_keys': 'scripts/debug/check_duplicate_keys.py',
        'dtic_groups': 'scripts/debug/debug_dtic_groups.py'
    },
    'validation': {
        'frontend_trends': 'scripts/validation/validate_frontend_trends.py',
        'trends_math': 'scripts/validation/validate_trends_math.py',
        'final_validation': 'scripts/validation/final_validation_report_root.py',
        'validation_fix': 'scripts/validation/validation_final_fix.py'
    },
    'tests': {
        'trends': 'scripts/tests/test_trends.py',
        'active_technicians': 'scripts/tests/test_active_technicians.py',
        'verify_endpoint': 'scripts/tests/verify_endpoint_technicians.py'
    }
}

def list_available_scripts():
    """Lista todos os scripts disponíveis."""
    print("\n📋 Scripts Disponíveis:")
    print("=" * 50)
    
    for category, scripts in SCRIPTS.items():
        print(f"\n📁 {category.upper()}:")
        for script_name, script_path in scripts.items():
            print(f"  • {script_name:<20} → {script_path}")
    
    print("\n🚀 Como usar:")
    print("  python run_scripts.py <categoria> <script>")
    print("\nExemplos:")
    print("  python run_scripts.py debug metrics")
    print("  python run_scripts.py validation frontend_trends")
    print("  python run_scripts.py tests trends")

def run_script(category: str, script_name: str):
    """Executa um script específico."""
    if category not in SCRIPTS:
        print(f"❌ Categoria '{category}' não encontrada.")
        print(f"Categorias disponíveis: {', '.join(SCRIPTS.keys())}")
        return False
    
    if script_name not in SCRIPTS[category]:
        print(f"❌ Script '{script_name}' não encontrado na categoria '{category}'.")
        print(f"Scripts disponíveis em '{category}': {', '.join(SCRIPTS[category].keys())}")
        return False
    
    script_path = SCRIPTS[category][script_name]
    
    # Verifica se o arquivo existe
    if not Path(script_path).exists():
        print(f"❌ Arquivo não encontrado: {script_path}")
        return False
    
    print(f"🚀 Executando: {script_path}")
    print("=" * 50)
    
    try:
        # Executa o script
        result = subprocess.run([sys.executable, script_path], 
                              cwd=os.getcwd(),
                              capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ Script executado com sucesso!")
            return True
        else:
            print(f"\n❌ Script falhou com código de saída: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro ao executar script: {e}")
        return False

def main():
    """Função principal."""
    if len(sys.argv) == 1:
        list_available_scripts()
        return
    
    if len(sys.argv) != 3:
        print("❌ Uso incorreto!")
        print("Uso: python run_scripts.py <categoria> <script>")
        print("\nPara ver todos os scripts disponíveis:")
        print("python run_scripts.py")
        return
    
    category = sys.argv[1].lower()
    script_name = sys.argv[2].lower()
    
    success = run_script(category, script_name)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()