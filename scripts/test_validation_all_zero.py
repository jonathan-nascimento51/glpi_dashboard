#!/usr/bin/env python3
"""
Script para testar validação com cenário all-zero.
Este script testa se a validação detecta corretamente problemas de qualidade.
"""

import requests
import sys
from pathlib import Path

# Adicionar o diretório scripts ao path para importar o módulo de validação
sys.path.append(str(Path(__file__).parent))

from validate_dashboard import (
    setup_artifacts_dir,
    check_backend_health,
    validate_data_consistency,
    generate_validation_report
)

def test_all_zero_scenario():
    """Testa cenário all-zero forçando o parâmetro."""
    print("Testando cenário all-zero...")
    
    try:
        # Fazer requisição com all_zero=true para forçar o cenário
        response = requests.get("http://localhost:8000/api/v1/health/data?all_zero=true", timeout=10.0)
        
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            return False
        
        data_health = response.json()
        
        # Simular dados do backend com o cenário all-zero
        backend_data = {
            "timestamp": "2025-08-12T13:45:00",
            "status": "ok",
            "data_health": data_health,
            "metrics": {}  # Métricas vazias para este teste
        }
        
        status = data_health.get("status", "unknown")
        all_zero = data_health.get("all_zero", False)
        quality_level = data_health.get("quality_level", "unknown")
        
        print(f"Status da resposta: {status}")
        print(f"All-zero: {all_zero}")
        print(f"Quality level: {quality_level}")
        
        # Validar consistência - deve falhar com all-zero
        validation_passed = validate_data_consistency(backend_data)
        
        if not validation_passed:
            print(" SUCESSO: Validação detectou corretamente o problema all-zero")
            return True
        else:
            print(" FALHA: Validação não detectou o problema all-zero")
            return False
            
    except Exception as e:
        print(f"Erro no teste: {e}")
        return False

def main():
    """Função principal de teste."""
    print("Testando validação com cenário all-zero")
    print("=" * 50)
    
    setup_artifacts_dir()
    
    # Testar cenário all-zero
    test_passed = test_all_zero_scenario()
    
    print("\n" + "=" * 50)
    if test_passed:
        print("TESTE PASSOU: Validação detecta corretamente problemas all-zero")
        sys.exit(0)
    else:
        print("TESTE FALHOU: Validação não detecta problemas all-zero")
        sys.exit(1)

if __name__ == "__main__":
    main()
