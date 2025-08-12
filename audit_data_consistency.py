#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de auditoria completa da consistência dos dados do dashboard GLPI
"""

import requests
import json
from datetime import datetime

def audit_metrics_consistency():
    """Audita a consistência dos dados de métricas"""
    print("=== AUDITORIA DE CONSISTÊNCIA DOS DADOS ===")
    
    try:
        # Buscar dados da API
        response = requests.get('http://localhost:5000/api/metrics')
        if response.status_code != 200:
            print(f"❌ ERRO: API retornou status {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ ERRO: API retornou success=false")
            return False
            
        metrics_data = data['data']
        
        # Verificar consistência dos níveis
        niveis = metrics_data['niveis']
        geral = niveis['geral']
        n1 = niveis['n1']
        n2 = niveis['n2']
        n3 = niveis['n3']
        n4 = niveis['n4']
        
        # Calcular soma dos níveis específicos
        soma_novos = n1['novos'] + n2['novos'] + n3['novos'] + n4['novos']
        soma_pendentes = n1['pendentes'] + n2['pendentes'] + n3['pendentes'] + n4['pendentes']
        soma_progresso = n1['progresso'] + n2['progresso'] + n3['progresso'] + n4['progresso']
        soma_resolvidos = n1['resolvidos'] + n2['resolvidos'] + n3['resolvidos'] + n4['resolvidos']
        
        print(f"\nDADOS GERAIS:")
        print(f"  Novos: {geral['novos']}")
        print(f"  Pendentes: {geral['pendentes']}")
        print(f"  Progresso: {geral['progresso']}")
        print(f"  Resolvidos: {geral['resolvidos']}")
        print(f"  Total: {geral['total']}")
        
        print(f"\nSOMA DOS NÍVEIS ESPECÍFICOS:")
        print(f"  Novos: {soma_novos}")
        print(f"  Pendentes: {soma_pendentes}")
        print(f"  Progresso: {soma_progresso}")
        print(f"  Resolvidos: {soma_resolvidos}")
        print(f"  Total: {soma_novos + soma_pendentes + soma_progresso + soma_resolvidos}")
        
        # Verificar inconsistências
        inconsistencias = []
        
        if geral['novos'] != soma_novos:
            inconsistencias.append(f"NOVOS: Geral ({geral['novos']}) != Soma níveis ({soma_novos})")
        if geral['pendentes'] != soma_pendentes:
            inconsistencias.append(f"PENDENTES: Geral ({geral['pendentes']}) != Soma níveis ({soma_pendentes})")
        if geral['progresso'] != soma_progresso:
            inconsistencias.append(f"PROGRESSO: Geral ({geral['progresso']}) != Soma níveis ({soma_progresso})")
        if geral['resolvidos'] != soma_resolvidos:
            inconsistencias.append(f"RESOLVIDOS: Geral ({geral['resolvidos']}) != Soma níveis ({soma_resolvidos})")
        
        print(f"\nINCONSISTÊNCIAS DETECTADAS:")
        if inconsistencias:
            for inc in inconsistencias:
                print(f"  ❌ {inc}")
        else:
            print("  ✅ Nenhuma inconsistência detectada nos totais")
        
        # Verificar totais por nível
        print(f"\nDETALHES POR NÍVEL:")
        nivel_inconsistencias = []
        
        for nivel_nome in ['n1', 'n2', 'n3', 'n4']:
            n = niveis[nivel_nome]
            total_calculado = n['novos'] + n['pendentes'] + n['progresso'] + n['resolvidos']
            print(f"  {nivel_nome.upper()}: novos={n['novos']}, pendentes={n['pendentes']}, progresso={n['progresso']}, resolvidos={n['resolvidos']}, total={n['total']} (calc: {total_calculado})")
            
            if n['total'] != total_calculado:
                nivel_inconsistencias.append(f"{nivel_nome.upper()}: Total informado ({n['total']}) != Total calculado ({total_calculado})")
        
        if nivel_inconsistencias:
            print(f"\nINCONSISTÊNCIAS NOS TOTAIS POR NÍVEL:")
            for inc in nivel_inconsistencias:
                print(f"  ❌ {inc}")
        else:
            print(f"\n  ✅ Todos os totais por nível estão consistentes")
        
        # Verificar tendências
        tendencias = metrics_data['tendencias']
        print(f"\nTENDÊNCIAS:")
        print(f"  Novos: {tendencias['novos']}")
        print(f"  Pendentes: {tendencias['pendentes']}")
        print(f"  Progresso: {tendencias['progresso']}")
        print(f"  Resolvidos: {tendencias['resolvidos']}")
        
        # Verificar se as tendências são válidas
        tendencia_problemas = []
        for campo, valor in tendencias.items():
            if not isinstance(valor, str):
                tendencia_problemas.append(f"{campo}: Não é string ({type(valor)})")
            elif not (valor.endswith('%') or valor == '0'):
                tendencia_problemas.append(f"{campo}: Formato inválido ({valor})")
        
        if tendencia_problemas:
            print(f"\nPROBLEMAS NAS TENDÊNCIAS:")
            for prob in tendencia_problemas:
                print(f"  ❌ {prob}")
        else:
            print(f"\n  ✅ Todas as tendências estão no formato correto")
        
        return len(inconsistencias) == 0 and len(nivel_inconsistencias) == 0 and len(tendencia_problemas) == 0
        
    except Exception as e:
        print(f"❌ ERRO durante auditoria: {e}")
        return False

def audit_system_status():
    """Audita o status do sistema"""
    print(f"\n=== AUDITORIA DO STATUS DO SISTEMA ===")
    
    try:
        response = requests.get('http://localhost:5000/api/status')
        if response.status_code != 200:
            print(f"❌ ERRO: API retornou status {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ ERRO: API retornou success=false")
            return False
            
        status_data = data['data']
        
        print(f"Status da API: {status_data.get('api', 'N/A')}")
        print(f"Status do GLPI: {status_data.get('glpi', 'N/A')}")
        print(f"Mensagem GLPI: {status_data.get('glpi_message', 'N/A')}")
        print(f"Tempo de resposta GLPI: {status_data.get('glpi_response_time', 'N/A')}ms")
        print(f"Última atualização: {status_data.get('last_update', 'N/A')}")
        print(f"Versão: {status_data.get('version', 'N/A')}")
        
        # Verificar campos obrigatórios
        campos_obrigatorios = ['api', 'glpi', 'version']
        problemas = []
        
        for campo in campos_obrigatorios:
            if campo not in status_data:
                problemas.append(f"Campo obrigatório '{campo}' ausente")
        
        if problemas:
            print(f"\nPROBLEMAS DETECTADOS:")
            for prob in problemas:
                print(f"  ❌ {prob}")
        else:
            print(f"\n  ✅ Todos os campos obrigatórios estão presentes")
        
        return len(problemas) == 0
        
    except Exception as e:
        print(f"❌ ERRO durante auditoria do status: {e}")
        return False

def audit_technician_ranking():
    """Audita o ranking de técnicos"""
    print(f"\n=== AUDITORIA DO RANKING DE TÉCNICOS ===")
    
    try:
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        if response.status_code != 200:
            print(f"❌ ERRO: API retornou status {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ ERRO: API retornou success=false")
            return False
            
        ranking_data = data['data']
        
        if not isinstance(ranking_data, list):
            print(f"❌ ERRO: Dados do ranking devem ser uma lista")
            return False
        
        print(f"Total de técnicos: {len(ranking_data)}")
        
        # Verificar estrutura dos dados
        problemas = []
        campos_obrigatorios = ['id', 'name', 'level', 'total', 'rank']
        
        for i, tecnico in enumerate(ranking_data[:5]):  # Verificar apenas os primeiros 5
            for campo in campos_obrigatorios:
                if campo not in tecnico:
                    problemas.append(f"Técnico {i+1}: Campo '{campo}' ausente")
            
            # Verificar tipos
            if 'total' in tecnico and not isinstance(tecnico['total'], (int, float)):
                problemas.append(f"Técnico {i+1}: Campo 'total' deve ser numérico")
            
            if 'rank' in tecnico and not isinstance(tecnico['rank'], int):
                problemas.append(f"Técnico {i+1}: Campo 'rank' deve ser inteiro")
        
        # Verificar ordenação por rank
        ranks = [t.get('rank', 0) for t in ranking_data]
        if ranks != sorted(ranks):
            problemas.append("Ranking não está ordenado corretamente")
        
        # Mostrar top 5
        print(f"\nTOP 5 TÉCNICOS:")
        for i, tecnico in enumerate(ranking_data[:5]):
            print(f"  {i+1}. {tecnico.get('name', 'N/A')} ({tecnico.get('level', 'N/A')}) - {tecnico.get('total', 0)} tickets")
        
        if problemas:
            print(f"\nPROBLEMAS DETECTADOS:")
            for prob in problemas:
                print(f"  ❌ {prob}")
        else:
            print(f"\n  ✅ Estrutura do ranking está correta")
        
        return len(problemas) == 0
        
    except Exception as e:
        print(f"❌ ERRO durante auditoria do ranking: {e}")
        return False

def main():
    """Função principal da auditoria"""
    print(f"🔍 AUDITORIA COMPLETA DA CONSISTÊNCIA DOS DADOS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Executar auditorias
    metrics_ok = audit_metrics_consistency()
    status_ok = audit_system_status()
    ranking_ok = audit_technician_ranking()
    
    # Resumo final
    print(f"\n=== RESUMO FINAL DA AUDITORIA ===")
    print(f"✅ Métricas consistentes: {'Sim' if metrics_ok else 'Não'}")
    print(f"✅ Status do sistema válido: {'Sim' if status_ok else 'Não'}")
    print(f"✅ Ranking de técnicos válido: {'Sim' if ranking_ok else 'Não'}")
    
    if metrics_ok and status_ok and ranking_ok:
        print(f"\n🎉 AUDITORIA COMPLETA: Todos os dados estão consistentes!")
        print(f"\nRESUMO DE QUALIDADE:")
        print(f"- Integridade dos dados: ✅ APROVADA")
        print(f"- Consistência matemática: ✅ APROVADA")
        print(f"- Estrutura da API: ✅ APROVADA")
        print(f"- Validação de tipos: ✅ APROVADA")
    else:
        print(f"\n⚠️ PROBLEMAS DETECTADOS: Verifique os logs acima")
        print(f"\nRECOMENDAÇÕES:")
        if not metrics_ok:
            print(f"- Verificar cálculos de métricas no backend")
        if not status_ok:
            print(f"- Verificar estrutura do status do sistema")
        if not ranking_ok:
            print(f"- Verificar estrutura do ranking de técnicos")

if __name__ == "__main__":
    main()