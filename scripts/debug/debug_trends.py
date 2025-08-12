#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug detalhado para investigar o cálculo de tendências
"""

import sys
sys.path.append('backend')

from backend.services.glpi_service import GLPIService
from datetime import datetime, timedelta
import json

def debug_trends_calculation():
    """Debug detalhado do cálculo de tendências"""
    print("=== DEBUG DETALHADO - CÁLCULO DE TENDÊNCIAS ===")
    
    # Inicializar o serviço GLPI
    glpi_service = GLPIService()
    
    # Calcular datas
    now = datetime.now()
    end_date_previous = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    start_date_previous = (now - timedelta(days=14)).strftime('%Y-%m-%d')
    
    print("\n=== PERÍODO ANTERIOR ===")
    print(f"Data início: {start_date_previous}")
    print(f"Data fim: {end_date_previous}")
    
    try:
        # Testar autenticação
        print("\n=== TESTE DE AUTENTICAÇÃO ===")
        if not glpi_service._ensure_authenticated():
            print("❌ ERRO: Falha na autenticação")
            return
        print("✅ Autenticação bem-sucedida")
        
        # Descobrir IDs dos campos
        print("\n=== DESCOBERTA DE CAMPOS ===")
        if not glpi_service.discover_field_ids():
            print("❌ ERRO: Falha na descoberta de campos")
            return
        print("✅ Campos descobertos")
        
        # Testar método _get_general_totals_internal para período anterior
        print("\n=== TESTE - DADOS PERÍODO ANTERIOR ===")
        previous_general = glpi_service._get_general_totals_internal(start_date_previous, end_date_previous)
        
        print(f"Dados brutos do período anterior: {json.dumps(previous_general, indent=2)}")
        
        # Calcular totais do período anterior
        previous_novos = previous_general.get("Novo", 0)
        previous_pendentes = previous_general.get("Pendente", 0)
        previous_progresso = previous_general.get("Processando (atribuído)", 0) + previous_general.get("Processando (planejado)", 0)
        previous_resolvidos = previous_general.get("Solucionado", 0) + previous_general.get("Fechado", 0)
        
        print("\n=== TOTAIS CALCULADOS - PERÍODO ANTERIOR ===")
        print(f"Novos: {previous_novos}")
        print(f"Pendentes: {previous_pendentes}")
        print(f"Progresso: {previous_progresso}")
        print(f"Resolvidos: {previous_resolvidos}")
        
        # Testar dados atuais
        print("\n=== TESTE - DADOS ATUAIS ===")
        current_general = glpi_service._get_general_totals_internal()
        
        print(f"Dados brutos atuais: {json.dumps(current_general, indent=2)}")
        
        # Calcular totais atuais
        current_novos = current_general.get("Novo", 0)
        current_pendentes = current_general.get("Pendente", 0)
        current_progresso = current_general.get("Processando (atribuído)", 0) + current_general.get("Processando (planejado)", 0)
        current_resolvidos = current_general.get("Solucionado", 0) + current_general.get("Fechado", 0)
        
        print("\n=== TOTAIS CALCULADOS - ATUAIS ===")
        print(f"Novos: {current_novos}")
        print(f"Pendentes: {current_pendentes}")
        print(f"Progresso: {current_progresso}")
        print(f"Resolvidos: {current_resolvidos}")
        
        # Simular cálculo de tendências
        print("\n=== SIMULAÇÃO CÁLCULO DE TENDÊNCIAS ===")
        
        def calculate_percentage_change(current: int, previous: int) -> str:
            print(f"  Calculando: atual={current}, anterior={previous}")
            if previous == 0:
                result = "+100%" if current > 0 else "0%"
                print(f"  Resultado (anterior=0): {result}")
                return result
            
            change = ((current - previous) / previous) * 100
            if change > 0:
                result = f"+{change:.1f}%"
            elif change < 0:
                result = f"{change:.1f}%"
            else:
                result = "0%"
            print(f"  Resultado (mudança={change:.1f}%): {result}")
            return result
        
        print("\nNovos:")
        trend_novos = calculate_percentage_change(current_novos, previous_novos)
        
        print("\nPendentes:")
        trend_pendentes = calculate_percentage_change(current_pendentes, previous_pendentes)
        
        print("\nProgresso:")
        trend_progresso = calculate_percentage_change(current_progresso, previous_progresso)
        
        print("\nResolvidos:")
        trend_resolvidos = calculate_percentage_change(current_resolvidos, previous_resolvidos)
        
        print("\n=== TENDÊNCIAS FINAIS ===")
        print(f"Novos: {trend_novos}")
        print(f"Pendentes: {trend_pendentes}")
        print(f"Progresso: {trend_progresso}")
        print(f"Resolvidos: {trend_resolvidos}")
        
        # Verificar se há dados no período anterior
        total_previous = previous_novos + previous_pendentes + previous_progresso + previous_resolvidos
        if total_previous == 0:
            print("\n⚠️  PROBLEMA IDENTIFICADO: Não há dados no período anterior!")
            print("Isso explica por que todas as tendências mostram +100%")
            print("\nPossíveis causas:")
            print("1. Não há tickets criados no período de 7-14 dias atrás")
            print("2. Problema na consulta com filtro de data")
            print("3. Formato de data incorreto na consulta")
        else:
            print(f"\n✅ Dados encontrados no período anterior (total: {total_previous})")
            
    except Exception as e:
        print(f"❌ ERRO durante debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_trends_calculation()