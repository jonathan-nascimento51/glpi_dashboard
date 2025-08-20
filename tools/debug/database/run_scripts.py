#!/usr/bin/env python3
"""
Script para executar facilmente os scripts auxiliares do projeto.
Uso: python run_scripts.py <categoria> <script>

Exemplos:
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
    'debug': {
        'metrics': 'scripts/debug/debug_metrics.py',
        'trends': 'scripts/debug/debug_trends.py',
        'react_keys': 'scripts/debug/debug_react_keys.py',
        'duplicate_keys': 'scripts/debug/check_duplicate_keys.py'
    },
    'validation': {
        'frontend_trends': 'scripts/validation/validate_frontend_trends.py',
        'trends_math': 'scripts/validation/validate_trends_math.py'
    },
    'tests': {
        'trends': 'scripts/tests/test_trends.py'
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