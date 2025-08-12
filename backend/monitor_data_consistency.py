#!/usr/bin/env python3
"""
Script de Monitoramento Contínuo de Consistência de Dados
Dashboard GLPI

Este script pode ser executado periodicamente para monitorar
a consistência dos dados e gerar alertas automáticos.
"""

import sys
import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar o diretório backend ao path de forma segura
try:
    backend_path = os.path.dirname(os.path.abspath(__file__))
    if backend_path not in sys.path:
        sys.path.append(backend_path)
except Exception as e:
    logger.error(f"Erro ao configurar path: {e}")

class DataConsistencyMonitor:
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        try:
            # Validar URL da API
            if not isinstance(api_base_url, str) or not api_base_url.strip():
                raise ValueError("URL da API deve ser uma string não vazia")
            
            # Normalizar URL (remover barra final se existir)
            self.api_base_url = api_base_url.rstrip('/')
            self.alerts = []
            self.warnings = []
            self.timestamp = datetime.now()
            
            logger.info(f"Monitor inicializado para API: {self.api_base_url}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar monitor: {e}")
            # Fallback para configuração básica
            self.api_base_url = "http://localhost:5000"
            self.alerts = [f"Erro na inicialização: {e}"]
            self.warnings = []
            self.timestamp = datetime.now()
        
    def check_api_health(self) -> bool:
        """Verifica se a API está respondendo"""
        try:
            # Validar URL antes da requisição
            if not self.api_base_url:
                self.alerts.append("URL da API não configurada")
                return False
            
            url = f"{self.api_base_url}/api/status"
            logger.debug(f"Verificando saúde da API: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("API está saudável")
                return True
            else:
                error_msg = f"API retornou status {response.status_code}"
                self.alerts.append(error_msg)
                logger.warning(error_msg)
                return False
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout ao conectar com a API"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            return False
        except requests.exceptions.ConnectionError:
            error_msg = "Erro de conexão com a API"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Erro inesperado ao verificar API: {e}"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            return False
    
    def get_metrics_data(self) -> Dict[str, Any]:
        """Obtém dados de métricas da API"""
        try:
            # Validar URL antes da requisição
            if not self.api_base_url:
                error_msg = "URL da API não configurada"
                self.alerts.append(error_msg)
                return {}
            
            url = f"{self.api_base_url}/api/metrics"
            logger.debug(f"Obtendo métricas de: {url}")
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict):
                        error_msg = f"Dados de métricas inválidos: esperado dict, recebido {type(data)}"
                        self.alerts.append(error_msg)
                        logger.error(error_msg)
                        return {}
                    
                    logger.info("Métricas obtidas com sucesso")
                    return data
                    
                except json.JSONDecodeError as e:
                    error_msg = f"Erro ao decodificar JSON das métricas: {e}"
                    self.alerts.append(error_msg)
                    logger.error(error_msg)
                    return {}
            else:
                error_msg = f"Erro ao obter métricas: HTTP {response.status_code}"
                self.alerts.append(error_msg)
                logger.error(error_msg)
                return {}
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout ao obter métricas da API"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            return {}
        except requests.exceptions.ConnectionError:
            error_msg = "Erro de conexão ao obter métricas"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            return {}
        except Exception as e:
            error_msg = f"Erro inesperado ao obter métricas: {e}"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            return {}
    
    def check_metrics_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica consistência das métricas"""
        consistency_report = {
            "consistent": True,
            "issues": [],
            "details": {}
        }
        
        try:
            # Validar entrada
            if not isinstance(data, dict):
                error_msg = f"Dados inválidos: esperado dict, recebido {type(data)}"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.error(error_msg)
                return consistency_report
            
            if not data or 'data' not in data:
                error_msg = "Dados de métricas não encontrados"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.warning(error_msg)
                return consistency_report
            
            metrics = data['data']
            if not isinstance(metrics, dict):
                error_msg = f"Estrutura de métricas inválida: esperado dict, recebido {type(metrics)}"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.error(error_msg)
                return consistency_report
            
            # Verificar se existem dados de níveis
            if 'niveis' not in metrics:
                error_msg = "Dados de níveis não encontrados"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.warning(error_msg)
                return consistency_report
            
            niveis = metrics['niveis']
            if not isinstance(niveis, dict):
                error_msg = f"Estrutura de níveis inválida: esperado dict, recebido {type(niveis)}"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.error(error_msg)
                return consistency_report
            
            # Verificar se existe nível 'geral'
            if 'geral' not in niveis:
                error_msg = "Dados gerais não encontrados"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.warning(error_msg)
                return consistency_report
            
            geral = niveis['geral']
            if not isinstance(geral, dict):
                error_msg = f"Dados gerais inválidos: esperado dict, recebido {type(geral)}"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.error(error_msg)
                return consistency_report
            
            # Calcular totais dos níveis específicos (N1-N4)
            level_totals = {
                'novos': 0,
                'pendentes': 0,
                'progresso': 0,
                'resolvidos': 0
            }
            
            for level in ['n1', 'n2', 'n3', 'n4']:
                if level in niveis:
                    level_data = niveis[level]
                    if isinstance(level_data, dict):
                        for metric in level_totals.keys():
                            value = level_data.get(metric, 0)
                            if isinstance(value, (int, float)):
                                level_totals[metric] += int(value)
                            else:
                                logger.warning(f"Valor inválido para {level}.{metric}: {value} ({type(value)})")
                    else:
                        logger.warning(f"Dados inválidos para nível {level}: {type(level_data)}")
        
        # Verificar consistência
        tolerance = 0  # Tolerância zero para inconsistências
        
        # Verificar consistência
        tolerance = 0  # Tolerância zero para inconsistências
        
        for metric in ['novos', 'pendentes', 'progresso', 'resolvidos']:
            try:
                general_value = geral.get(metric, 0)
                if not isinstance(general_value, (int, float)):
                    logger.warning(f"Valor geral inválido para {metric}: {general_value} ({type(general_value)})")
                    general_value = 0
                else:
                    general_value = int(general_value)
                
                level_sum = level_totals[metric]
                difference = abs(general_value - level_sum)
                
                consistency_report["details"][metric] = {
                    "geral": general_value,
                    "soma_niveis": level_sum,
                    "diferenca": difference,
                    "consistente": difference <= tolerance
                }
                
                if difference > tolerance:
                    consistency_report["consistent"] = False
                    issue_msg = f"Inconsistência em '{metric}': Geral={general_value}, Soma Níveis={level_sum}, Diferença={difference}"
                    consistency_report["issues"].append(issue_msg)
                    logger.warning(issue_msg)
                    
            except Exception as e:
                error_msg = f"Erro ao verificar consistência da métrica '{metric}': {e}"
                consistency_report["consistent"] = False
                consistency_report["issues"].append(error_msg)
                logger.error(error_msg)
        
        # Log do resultado da verificação
        if consistency_report["consistent"]:
            logger.info("Verificação de consistência: PASSOU")
        else:
            logger.warning(f"Verificação de consistência: FALHOU - {len(consistency_report['issues'])} problemas encontrados")
        
        return consistency_report
        
        except Exception as e:
            error_msg = f"Erro inesperado durante verificação de consistência: {e}"
            logger.error(error_msg)
            return {
                "consistent": False,
                "issues": [error_msg],
                "details": {}
            }
    
    def check_response_times(self) -> Dict[str, Any]:
        """Verifica tempos de resposta dos endpoints"""
        endpoints = [
            "/api/status",
            "/api/metrics",
            "/api/technicians/ranking"
        ]
        
        performance_report = {
            "all_healthy": True,
            "endpoints": {}
        }
        
        try:
            # Validar URL da API
            if not self.api_base_url:
                error_msg = "URL da API não configurada para teste de performance"
                self.alerts.append(error_msg)
                logger.error(error_msg)
                performance_report["all_healthy"] = False
                return performance_report
            
            logger.info(f"Iniciando teste de performance para {len(endpoints)} endpoints")
            
            for endpoint in endpoints:
                start_time = datetime.now()
                try:
                    # Validar endpoint
                    if not isinstance(endpoint, str) or not endpoint.startswith('/'):
                        logger.warning(f"Endpoint inválido: {endpoint}")
                        continue
                    
                    url = f"{self.api_base_url}{endpoint}"
                    logger.debug(f"Testando endpoint: {url}")
                    
                    response = requests.get(url, timeout=30)
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    # Validar tempo de resposta
                    if response_time < 0:
                        logger.warning(f"Tempo de resposta inválido para {endpoint}: {response_time}ms")
                        response_time = 0
                    
                    endpoint_health = {
                        "status_code": response.status_code,
                        "response_time_ms": round(response_time, 2),
                        "healthy": response.status_code == 200 and response_time < 5000
                    }
                    
                    if not endpoint_health["healthy"]:
                        performance_report["all_healthy"] = False
                        if response.status_code != 200:
                            warning_msg = f"Endpoint {endpoint} retornou status {response.status_code}"
                            self.warnings.append(warning_msg)
                            logger.warning(warning_msg)
                        if response_time >= 5000:
                            warning_msg = f"Endpoint {endpoint} lento: {response_time:.2f}ms"
                            self.warnings.append(warning_msg)
                            logger.warning(warning_msg)
                    else:
                        logger.debug(f"Endpoint {endpoint} saudável: {response_time:.2f}ms")
                    
                    performance_report["endpoints"][endpoint] = endpoint_health
                    
                except requests.exceptions.Timeout:
                    error_msg = f"Timeout ao testar endpoint {endpoint}"
                    performance_report["all_healthy"] = False
                    performance_report["endpoints"][endpoint] = {
                        "status_code": None,
                        "response_time_ms": None,
                        "healthy": False,
                        "error": "Timeout"
                    }
                    self.alerts.append(error_msg)
                    logger.error(error_msg)
                    
                except requests.exceptions.ConnectionError:
                    error_msg = f"Erro de conexão ao testar endpoint {endpoint}"
                    performance_report["all_healthy"] = False
                    performance_report["endpoints"][endpoint] = {
                        "status_code": None,
                        "response_time_ms": None,
                        "healthy": False,
                        "error": "Connection Error"
                    }
                    self.alerts.append(error_msg)
                    logger.error(error_msg)
                    
                except Exception as e:
                    error_msg = f"Erro inesperado ao testar endpoint {endpoint}: {e}"
                    performance_report["all_healthy"] = False
                    performance_report["endpoints"][endpoint] = {
                        "status_code": None,
                        "response_time_ms": None,
                        "healthy": False,
                        "error": str(e)
                    }
                    self.alerts.append(error_msg)
                    logger.error(error_msg)
            
            # Log do resultado do teste de performance
            healthy_count = sum(1 for ep in performance_report["endpoints"].values() if ep.get("healthy", False))
            logger.info(f"Teste de performance concluído: {healthy_count}/{len(endpoints)} endpoints saudáveis")
            
        except Exception as e:
            error_msg = f"Erro crítico durante teste de performance: {e}"
            self.alerts.append(error_msg)
            logger.error(error_msg)
            performance_report["all_healthy"] = False
        
        return performance_report
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo de monitoramento"""
        try:
            print("🔍 Iniciando monitoramento de consistência de dados...")
            logger.info("Iniciando geração de relatório de monitoramento")
            
            # Verificar saúde da API
            api_healthy = self.check_api_health()
            
            if not api_healthy:
                error_report = {
                    "timestamp": self.timestamp.isoformat(),
                    "status": "CRITICAL",
                    "api_healthy": False,
                    "consistency": {"consistent": False, "issues": ["API não disponível"], "details": {}},
                    "performance": {"all_healthy": False, "endpoints": {}},
                    "alerts": self.alerts,
                    "warnings": self.warnings,
                    "summary": {
                        "total_alerts": len(self.alerts),
                        "total_warnings": len(self.warnings),
                        "data_consistent": False,
                        "performance_healthy": False
                    }
                }
                logger.error("Relatório gerado com status CRITICAL - API não disponível")
                return error_report
            
            # Obter dados de métricas
            metrics_data = self.get_metrics_data()
            
            # Verificar consistência
            consistency_report = self.check_metrics_consistency(metrics_data)
            if not isinstance(consistency_report, dict):
                logger.error(f"Relatório de consistência inválido: {type(consistency_report)}")
                consistency_report = {"consistent": False, "issues": ["Erro na verificação de consistência"], "details": {}}
            
            # Verificar performance
            performance_report = self.check_response_times()
            if not isinstance(performance_report, dict):
                logger.error(f"Relatório de performance inválido: {type(performance_report)}")
                performance_report = {"all_healthy": False, "endpoints": {}}
            
            # Determinar status geral
            if self.alerts:
                status = "CRITICAL"
            elif not consistency_report.get("consistent", False) or not performance_report.get("all_healthy", False):
                status = "WARNING"
            else:
                status = "HEALTHY"
            
            # Adicionar issues de consistência aos warnings
            if not consistency_report.get("consistent", False):
                issues = consistency_report.get("issues", [])
                if isinstance(issues, list):
                    self.warnings.extend(issues)
                else:
                    logger.warning(f"Issues de consistência inválidas: {type(issues)}")
            
            # Construir relatório final
            report = {
                "timestamp": self.timestamp.isoformat(),
                "status": status,
                "api_healthy": api_healthy,
                "consistency": consistency_report,
                "performance": performance_report,
                "alerts": self.alerts,
                "warnings": self.warnings,
                "summary": {
                    "total_alerts": len(self.alerts),
                    "total_warnings": len(self.warnings),
                    "data_consistent": consistency_report.get("consistent", False),
                    "performance_healthy": performance_report.get("all_healthy", False)
                }
            }
            
            logger.info(f"Relatório gerado com status: {status}")
            return report
            
        except Exception as e:
            error_msg = f"Erro crítico durante geração do relatório: {e}"
            logger.error(error_msg)
            
            # Relatório de emergência
            emergency_report = {
                "timestamp": self.timestamp.isoformat(),
                "status": "CRITICAL",
                "api_healthy": False,
                "consistency": {"consistent": False, "issues": [error_msg], "details": {}},
                "performance": {"all_healthy": False, "endpoints": {}},
                "alerts": self.alerts + [error_msg],
                "warnings": self.warnings,
                "summary": {
                    "total_alerts": len(self.alerts) + 1,
                    "total_warnings": len(self.warnings),
                    "data_consistent": False,
                    "performance_healthy": False
                }
            }
            
            return emergency_report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Salva relatório em arquivo JSON"""
        try:
            # Validar entrada
            if not isinstance(report, dict):
                raise ValueError(f"Relatório deve ser um dict, recebido: {type(report)}")
            
            # Gerar nome do arquivo se não fornecido
            if filename is None:
                timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
                filename = f"consistency_report_{timestamp_str}.json"
            
            # Validar nome do arquivo
            if not isinstance(filename, str) or not filename.strip():
                raise ValueError("Nome do arquivo deve ser uma string não vazia")
            
            # Garantir extensão .json
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Construir caminho do arquivo
            reports_dir = os.path.join(os.path.dirname(__file__), "reports")
            filepath = os.path.join(reports_dir, filename)
            
            # Criar diretório se não existir
            try:
                os.makedirs(reports_dir, exist_ok=True)
                logger.debug(f"Diretório de relatórios criado/verificado: {reports_dir}")
            except Exception as e:
                logger.error(f"Erro ao criar diretório de relatórios: {e}")
                raise
            
            # Salvar arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Verificar se o arquivo foi criado
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Arquivo não foi criado: {filepath}")
            
            file_size = os.path.getsize(filepath)
            logger.info(f"Relatório salvo com sucesso: {filepath} ({file_size} bytes)")
            
            return filepath
            
        except Exception as e:
            error_msg = f"Erro ao salvar relatório: {e}"
            logger.error(error_msg)
            
            # Tentar salvar em local alternativo
            try:
                fallback_filename = f"emergency_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                fallback_path = os.path.join(os.path.dirname(__file__), fallback_filename)
                
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                logger.warning(f"Relatório salvo em local alternativo: {fallback_path}")
                return fallback_path
                
            except Exception as fallback_error:
                logger.error(f"Erro ao salvar em local alternativo: {fallback_error}")
                raise Exception(f"Falha completa ao salvar relatório: {error_msg}; Fallback: {fallback_error}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Imprime resumo do relatório"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE MONITORAMENTO DE CONSISTÊNCIA")
        print("="*60)
        print(f"⏰ Timestamp: {report['timestamp']}")
        print(f"🔍 Status Geral: {report['status']}")
        print(f"🌐 API Saudável: {'✅' if report['api_healthy'] else '❌'}")
        print(f"📈 Dados Consistentes: {'✅' if report['summary']['data_consistent'] else '❌'}")
        print(f"⚡ Performance OK: {'✅' if report['summary']['performance_healthy'] else '❌'}")
        
        if report['alerts']:
            print(f"\n🚨 ALERTAS CRÍTICOS ({len(report['alerts'])})")
            for alert in report['alerts']:
                print(f"  ❌ {alert}")
        
        if report['warnings']:
            print(f"\n⚠️  AVISOS ({len(report['warnings'])})")
            for warning in report['warnings']:
                print(f"  ⚠️  {warning}")
        
        if report['consistency']['details']:
            print(f"\n📊 DETALHES DE CONSISTÊNCIA")
            for metric, details in report['consistency']['details'].items():
                status_icon = "✅" if details['consistente'] else "❌"
                print(f"  {status_icon} {metric.capitalize()}: Geral={details['geral']}, Níveis={details['soma_niveis']}, Diff={details['diferenca']}")
        
        print("\n" + "="*60)

def main():
    """Função principal"""
    monitor = DataConsistencyMonitor()
    
    try:
        # Gerar relatório
        report = monitor.generate_report()
        
        # Imprimir resumo
        monitor.print_summary(report)
        
        # Salvar relatório
        filepath = monitor.save_report(report)
        print(f"\n💾 Relatório salvo em: {filepath}")
        
        # Retornar código de saída baseado no status
        if report['status'] == 'CRITICAL':
            sys.exit(2)
        elif report['status'] == 'WARNING':
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Erro durante monitoramento: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()