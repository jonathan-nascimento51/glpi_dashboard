#!/usr/bin/env python3
"""
Sistema de Monitoramento e Alertas para Dashboard GLPI

Este script monitora a integridade dos dados do dashboard e detecta inconsistências
automaticamente, gerando alertas quando necessário.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from services.glpi_service import GLPIService
from config.settings import active_config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataIntegrityMonitor:
    """Monitor de integridade de dados do dashboard GLPI"""
    
    def __init__(self):
        self.config = active_config
        self.glpi_service = GLPIService()
        self.alerts = []
        self.report_file = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def check_technician_groups_consistency(self) -> Dict[str, Any]:
        """Verifica consistência entre grupos de técnicos e mapeamento hardcoded"""
        logger.info("Verificando consistência dos grupos de técnicos...")
        
        try:
            # Obter grupos N1-N4
            groups_info = {}
            for level in ['N1', 'N2', 'N3', 'N4']:
                group_id = {'N1': 89, 'N2': 90, 'N3': 91, 'N4': 92}[level]
                group_users = self.glpi_service.get_group_users(group_id)
                groups_info[level] = {
                    'group_id': group_id,
                    'users_count': len(group_users),
                    'users': [user.get('name', 'N/A') for user in group_users]
                }
            
            # Verificar mapeamento hardcoded
            hardcoded_mapping = self.glpi_service._get_technician_level_mapping()
            
            # Detectar inconsistências
            inconsistencies = []
            
            # Verificar se há técnicos nos grupos que não estão no mapeamento
            for level, info in groups_info.items():
                if info['users_count'] > 0:
                    for user_name in info['users']:
                        if user_name not in hardcoded_mapping.get(level, []):
                            inconsistencies.append({
                                'type': 'user_in_group_not_in_mapping',
                                'level': level,
                                'user': user_name,
                                'severity': 'medium'
                            })
            
            # Verificar se há técnicos no mapeamento que não estão nos grupos
            for level, users in hardcoded_mapping.items():
                group_users = groups_info.get(level, {}).get('users', [])
                for user in users:
                    if user not in group_users:
                        inconsistencies.append({
                            'type': 'user_in_mapping_not_in_group',
                            'level': level,
                            'user': user,
                            'severity': 'low'
                        })
            
            return {
                'status': 'completed',
                'groups_info': groups_info,
                'inconsistencies': inconsistencies,
                'total_inconsistencies': len(inconsistencies)
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar consistência dos grupos: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_ranking_completeness(self) -> Dict[str, Any]:
        """Verifica se o ranking contém técnicos de todos os níveis"""
        logger.info("Verificando completude do ranking...")
        
        try:
            # Obter ranking atual
            ranking_data = self.glpi_service.get_technician_ranking()
            
            # Verificar se há técnicos em todos os níveis
            levels_present = set()
            for tech in ranking_data:
                level = tech.get('level')
                if level:
                    levels_present.add(level)
            
            expected_levels = {'N1', 'N2', 'N3', 'N4'}
            missing_levels = expected_levels - levels_present
            
            # Contar técnicos por nível
            level_counts = {}
            for level in expected_levels:
                level_counts[level] = len([t for t in ranking_data if t.get('level') == level])
            
            alerts = []
            if missing_levels:
                alerts.append({
                    'type': 'missing_levels_in_ranking',
                    'missing_levels': list(missing_levels),
                    'severity': 'high'
                })
            
            # Verificar se algum nível tem muito poucos técnicos
            for level, count in level_counts.items():
                if count == 0:
                    alerts.append({
                        'type': 'no_technicians_in_level',
                        'level': level,
                        'severity': 'high'
                    })
                elif count < 2:
                    alerts.append({
                        'type': 'few_technicians_in_level',
                        'level': level,
                        'count': count,
                        'severity': 'medium'
                    })
            
            return {
                'status': 'completed',
                'total_technicians': len(ranking_data),
                'levels_present': list(levels_present),
                'missing_levels': list(missing_levels),
                'level_counts': level_counts,
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar completude do ranking: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_api_connectivity(self) -> Dict[str, Any]:
        """Verifica conectividade com a API do GLPI"""
        logger.info("Verificando conectividade com API GLPI...")
        
        try:
            # Tentar fazer uma chamada simples para a API
            test_response = self.glpi_service.get_session_token()
            
            if test_response:
                return {
                    'status': 'connected',
                    'response_time': 'OK',
                    'api_version': getattr(self.glpi_service, 'api_version', 'unknown')
                }
            else:
                return {
                    'status': 'disconnected',
                    'error': 'Failed to get session token'
                }
                
        except Exception as e:
            logger.error(f"Erro de conectividade com API: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """Verifica se os dados estão atualizados"""
        logger.info("Verificando atualização dos dados...")
        
        try:
            # Verificar se há tickets recentes (últimas 24h)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            recent_tickets = self.glpi_service.get_tickets_by_date_range(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            alerts = []
            if len(recent_tickets) == 0:
                alerts.append({
                    'type': 'no_recent_tickets',
                    'period': '24h',
                    'severity': 'medium'
                })
            
            return {
                'status': 'completed',
                'recent_tickets_count': len(recent_tickets),
                'check_period': '24h',
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar atualização dos dados: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run_full_monitoring(self) -> Dict[str, Any]:
        """Executa monitoramento completo"""
        logger.info("Iniciando monitoramento completo...")
        
        monitoring_report = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {
                'total_alerts': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0
            }
        }
        
        # Executar todas as verificações
        checks = {
            'technician_groups_consistency': self.check_technician_groups_consistency,
            'ranking_completeness': self.check_ranking_completeness,
            'api_connectivity': self.check_api_connectivity,
            'data_freshness': self.check_data_freshness
        }
        
        for check_name, check_function in checks.items():
            logger.info(f"Executando verificação: {check_name}")
            monitoring_report['checks'][check_name] = check_function()
        
        # Consolidar alertas
        all_alerts = []
        for check_name, check_result in monitoring_report['checks'].items():
            if check_result.get('status') == 'completed':
                # Adicionar alertas específicos de cada verificação
                if 'alerts' in check_result:
                    for alert in check_result['alerts']:
                        alert['check'] = check_name
                        all_alerts.append(alert)
                
                # Adicionar inconsistências como alertas
                if 'inconsistencies' in check_result:
                    for inconsistency in check_result['inconsistencies']:
                        inconsistency['check'] = check_name
                        all_alerts.append(inconsistency)
        
        # Contar alertas por severidade
        for alert in all_alerts:
            severity = alert.get('severity', 'low')
            monitoring_report['summary']['total_alerts'] += 1
            monitoring_report['summary'][f'{severity}_severity'] += 1
        
        monitoring_report['alerts'] = all_alerts
        
        # Salvar relatório
        self.save_report(monitoring_report)
        
        logger.info(f"Monitoramento concluído. Total de alertas: {len(all_alerts)}")
        return monitoring_report
    
    def save_report(self, report: Dict[str, Any]):
        """Salva relatório de monitoramento"""
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Relatório salvo em: {self.report_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    monitor = DataIntegrityMonitor()
    report = monitor.run_full_monitoring()
    
    # Exibir resumo
    print("\n" + "="*50)
    print("RELATÓRIO DE MONITORAMENTO - DASHBOARD GLPI")
    print("="*50)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total de alertas: {report['summary']['total_alerts']}")
    print(f"  - Alta severidade: {report['summary']['high_severity']}")
    print(f"  - Média severidade: {report['summary']['medium_severity']}")
    print(f"  - Baixa severidade: {report['summary']['low_severity']}")
    
    if report['alerts']:
        print("\nALERTAS DETECTADOS:")
        for i, alert in enumerate(report['alerts'], 1):
            print(f"{i}. [{alert.get('severity', 'unknown').upper()}] {alert.get('type', 'unknown')}")
            if 'level' in alert:
                print(f"   Nível: {alert['level']}")
            if 'user' in alert:
                print(f"   Usuário: {alert['user']}")
            if 'check' in alert:
                print(f"   Verificação: {alert['check']}")
    else:
        print("\n✅ Nenhum alerta detectado. Sistema funcionando normalmente.")
    
    print(f"\nRelatório completo salvo em: {monitor.report_file}")
    print("="*50)

if __name__ == '__main__':
    main()