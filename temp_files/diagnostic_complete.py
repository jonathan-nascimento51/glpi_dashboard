#!/usr/bin/env python3
"""
Script de diagnóstico completo para identificar problemas na integração frontend-backend
Identifica problemas de CORS, configuração, dados e sugere soluções
"""

import requests
import json
import time
import subprocess
import os
from datetime import datetime
from urllib.parse import urlparse

class GLPIDashboardDiagnostic:
    def __init__(self):
        self.backend_url = 'http://localhost:5000'
        self.frontend_url = 'http://localhost:3001'
        self.api_base = f'{self.backend_url}/api'
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'issues': [],
            'recommendations': []
        }
    
    def log_test(self, test_name, status, details, issue=None, recommendation=None):
        """Registra resultado de um teste"""
        test_result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results['tests'].append(test_result)
        
        if issue:
            self.results['issues'].append({
                'test': test_name,
                'issue': issue,
                'severity': 'high' if status == 'FAILED' else 'medium'
            })
        
        if recommendation:
            self.results['recommendations'].append({
                'test': test_name,
                'recommendation': recommendation
            })
        
        # Log no console
        status_icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        
        if issue:
            print(f"   🔍 Problema: {issue}")
        if recommendation:
            print(f"   💡 Recomendação: {recommendation}")
    
    def test_backend_connectivity(self):
        """Testa conectividade com o backend"""
        print("\n🔍 Testando conectividade com o backend...")
        
        try:
            response = requests.get(f'{self.backend_url}/api/status', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        'Backend Connectivity',
                        'PASSED',
                        f'Backend respondendo corretamente (tempo: {response.elapsed.total_seconds():.2f}s)'
                    )
                    return True
                else:
                    self.log_test(
                        'Backend Connectivity',
                        'FAILED',
                        'Backend respondeu mas com success=false',
                        'Backend não está retornando dados válidos',
                        'Verificar logs do backend e configuração do GLPI'
                    )
            else:
                self.log_test(
                    'Backend Connectivity',
                    'FAILED',
                    f'Backend retornou status {response.status_code}',
                    'Backend não está respondendo corretamente',
                    'Verificar se o backend está rodando na porta 5000'
                )
        
        except requests.exceptions.ConnectionError:
            self.log_test(
                'Backend Connectivity',
                'FAILED',
                'Não foi possível conectar ao backend',
                'Backend não está rodando ou não está acessível',
                'Executar: python app.py para iniciar o backend'
            )
            return False
        
        except requests.exceptions.Timeout:
            self.log_test(
                'Backend Connectivity',
                'FAILED',
                'Timeout na conexão com o backend',
                'Backend está muito lento ou travado',
                'Verificar logs do backend e performance do servidor'
            )
            return False
        
        return False
    
    def test_frontend_connectivity(self):
        """Testa conectividade com o frontend"""
        print("\n🔍 Testando conectividade com o frontend...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                # Verificar se é uma página React válida
                content = response.text
                if 'root' in content and ('react' in content.lower() or 'vite' in content.lower()):
                    self.log_test(
                        'Frontend Connectivity',
                        'PASSED',
                        'Frontend respondendo corretamente'
                    )
                    return True
                else:
                    self.log_test(
                        'Frontend Connectivity',
                        'WARNING',
                        'Frontend respondeu mas pode não ser a aplicação React',
                        'Página pode não estar carregando corretamente',
                        'Verificar se o npm run dev está funcionando'
                    )
            else:
                self.log_test(
                    'Frontend Connectivity',
                    'FAILED',
                    f'Frontend retornou status {response.status_code}',
                    'Frontend não está respondendo corretamente',
                    'Verificar se o frontend está rodando na porta 3001'
                )
        
        except requests.exceptions.ConnectionError:
            self.log_test(
                'Frontend Connectivity',
                'FAILED',
                'Não foi possível conectar ao frontend',
                'Frontend não está rodando ou não está acessível',
                'Executar: npm run dev no diretório frontend'
            )
            return False
        
        except requests.exceptions.Timeout:
            self.log_test(
                'Frontend Connectivity',
                'FAILED',
                'Timeout na conexão com o frontend',
                'Frontend está muito lento ou travado',
                'Verificar logs do frontend e performance'
            )
            return False
        
        return False
    
    def test_api_endpoints(self):
        """Testa todos os endpoints da API"""
        print("\n🔍 Testando endpoints da API...")
        
        endpoints = {
            '/metrics': 'Métricas do Dashboard',
            '/status': 'Status do Sistema',
            '/technicians/ranking': 'Ranking de Técnicos',
            '/test': 'Endpoint de Teste'
        }
        
        all_passed = True
        
        for endpoint, description in endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(f'{self.api_base}{endpoint}', timeout=30)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        # Verificações específicas por endpoint
                        if endpoint == '/metrics':
                            if self._validate_metrics_structure(data.get('data', {})):
                                self.log_test(
                                    f'API Endpoint {endpoint}',
                                    'PASSED',
                                    f'{description} funcionando (tempo: {response_time:.0f}ms)'
                                )
                            else:
                                self.log_test(
                                    f'API Endpoint {endpoint}',
                                    'WARNING',
                                    f'{description} respondeu mas estrutura de dados inválida',
                                    'Estrutura de dados não confere com o esperado',
                                    'Verificar transformação de dados no backend'
                                )
                                all_passed = False
                        else:
                            self.log_test(
                                f'API Endpoint {endpoint}',
                                'PASSED',
                                f'{description} funcionando (tempo: {response_time:.0f}ms)'
                            )
                    else:
                        self.log_test(
                            f'API Endpoint {endpoint}',
                            'FAILED',
                            f'{description} retornou success=false',
                            'Endpoint não está retornando dados válidos',
                            'Verificar logs do backend para este endpoint'
                        )
                        all_passed = False
                else:
                    self.log_test(
                        f'API Endpoint {endpoint}',
                        'FAILED',
                        f'{description} retornou status {response.status_code}',
                        'Endpoint não está funcionando',
                        'Verificar implementação do endpoint no backend'
                    )
                    all_passed = False
            
            except Exception as e:
                self.log_test(
                    f'API Endpoint {endpoint}',
                    'FAILED',
                    f'Erro ao testar {description}: {str(e)}',
                    'Erro na comunicação com o endpoint',
                    'Verificar se o backend está funcionando corretamente'
                )
                all_passed = False
        
        return all_passed
    
    def _validate_metrics_structure(self, data):
        """Valida a estrutura dos dados de métricas"""
        required_fields = ['niveis', 'tendencias']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Verificar estrutura dos níveis
        niveis = data.get('niveis', {})
        expected_levels = ['n1', 'n2', 'n3', 'n4']
        
        for level in expected_levels:
            if level not in niveis:
                return False
            
            level_data = niveis[level]
            required_metrics = ['novos', 'pendentes', 'progresso', 'resolvidos']
            
            for metric in required_metrics:
                if metric not in level_data:
                    return False
        
        return True
    
    def test_cors_configuration(self):
        """Testa configuração de CORS"""
        print("\n🔍 Testando configuração de CORS...")
        
        try:
            # Simular requisição CORS preflight
            headers = {
                'Origin': 'http://localhost:3001',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f'{self.api_base}/metrics', headers=headers, timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                if cors_headers['Access-Control-Allow-Origin'] == '*' or 'localhost:3001' in cors_headers['Access-Control-Allow-Origin']:
                    self.log_test(
                        'CORS Configuration',
                        'PASSED',
                        'CORS configurado corretamente'
                    )
                    return True
                else:
                    self.log_test(
                        'CORS Configuration',
                        'WARNING',
                        f'CORS permite origem: {cors_headers["Access-Control-Allow-Origin"]}',
                        'CORS pode não permitir requisições do frontend',
                        'Verificar configuração de CORS no backend para incluir localhost:3001'
                    )
            else:
                self.log_test(
                    'CORS Configuration',
                    'FAILED',
                    'Headers CORS não encontrados',
                    'CORS não está configurado',
                    'Configurar CORS no backend para permitir requisições do frontend'
                )
                return False
        
        except Exception as e:
            self.log_test(
                'CORS Configuration',
                'FAILED',
                f'Erro ao testar CORS: {str(e)}',
                'Não foi possível testar CORS',
                'Verificar se o backend está respondendo a requisições OPTIONS'
            )
            return False
        
        return True
    
    def test_data_transformation(self):
        """Testa se a transformação de dados está funcionando"""
        print("\n🔍 Testando transformação de dados...")
        
        try:
            response = requests.get(f'{self.api_base}/metrics', timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    metrics_data = data['data']
                    
                    # Verificar se tem a estrutura esperada pelo frontend
                    if 'niveis' in metrics_data:
                        niveis = metrics_data['niveis']
                        
                        # Verificar se tem todos os níveis esperados
                        expected_levels = ['n1', 'n2', 'n3', 'n4']
                        missing_levels = [level for level in expected_levels if level not in niveis]
                        
                        if not missing_levels:
                            # Verificar se cada nível tem as métricas esperadas
                            all_metrics_present = True
                            expected_metrics = ['novos', 'pendentes', 'progresso', 'resolvidos']
                            
                            for level in expected_levels:
                                level_data = niveis[level]
                                missing_metrics = [metric for metric in expected_metrics if metric not in level_data]
                                
                                if missing_metrics:
                                    all_metrics_present = False
                                    break
                            
                            if all_metrics_present:
                                # Verificar se o nível 'geral' está sendo calculado (após nossa correção)
                                if 'geral' in niveis:
                                    self.log_test(
                                        'Data Transformation',
                                        'PASSED',
                                        'Transformação de dados funcionando corretamente, incluindo cálculo do nível geral'
                                    )
                                else:
                                    self.log_test(
                                        'Data Transformation',
                                        'WARNING',
                                        'Dados básicos presentes, mas nível geral não encontrado',
                                        'Frontend pode não estar calculando o nível geral corretamente',
                                        'Verificar função transformLegacyData no frontend'
                                    )
                                return True
                            else:
                                self.log_test(
                                    'Data Transformation',
                                    'FAILED',
                                    'Métricas incompletas nos níveis',
                                    'Alguns níveis não têm todas as métricas necessárias',
                                    'Verificar consultas SQL no backend'
                                )
                        else:
                            self.log_test(
                                'Data Transformation',
                                'FAILED',
                                f'Níveis ausentes: {missing_levels}',
                                'Backend não está retornando todos os níveis necessários',
                                'Verificar configuração de níveis no backend'
                            )
                    else:
                        self.log_test(
                            'Data Transformation',
                            'FAILED',
                            'Campo "niveis" não encontrado nos dados',
                            'Estrutura de dados não confere com o esperado',
                            'Verificar estrutura de resposta da API'
                        )
                else:
                    self.log_test(
                        'Data Transformation',
                        'FAILED',
                        'API não retornou dados válidos',
                        'Resposta da API está inválida',
                        'Verificar implementação do endpoint /metrics'
                    )
            else:
                self.log_test(
                    'Data Transformation',
                    'FAILED',
                    f'API retornou status {response.status_code}',
                    'Não foi possível obter dados para testar transformação',
                    'Resolver problemas de conectividade da API primeiro'
                )
        
        except Exception as e:
            self.log_test(
                'Data Transformation',
                'FAILED',
                f'Erro ao testar transformação: {str(e)}',
                'Erro durante teste de transformação de dados',
                'Verificar logs do backend e conectividade'
            )
            return False
        
        return False
    
    def test_frontend_integration(self):
        """Testa integração específica do frontend"""
        print("\n🔍 Testando integração do frontend...")
        
        # Verificar se arquivos importantes existem
        frontend_files = {
            'frontend/src/services/api.ts': 'Serviço de API',
            'frontend/src/hooks/useDashboard.ts': 'Hook do Dashboard',
            'frontend/src/types/api.ts': 'Tipos da API',
            'frontend/vite.config.ts': 'Configuração do Vite'
        }
        
        all_files_exist = True
        
        for file_path, description in frontend_files.items():
            if os.path.exists(file_path):
                self.log_test(
                    f'Frontend File {file_path}',
                    'PASSED',
                    f'{description} encontrado'
                )
            else:
                self.log_test(
                    f'Frontend File {file_path}',
                    'FAILED',
                    f'{description} não encontrado',
                    f'Arquivo {file_path} está ausente',
                    'Verificar se todos os arquivos do frontend estão presentes'
                )
                all_files_exist = False
        
        # Verificar configuração do Vite
        try:
            with open('frontend/vite.config.ts', 'r', encoding='utf-8') as f:
                vite_config = f.read()
                
                if 'proxy' in vite_config and '/api' in vite_config and '5000' in vite_config:
                    self.log_test(
                        'Vite Proxy Configuration',
                        'PASSED',
                        'Configuração de proxy do Vite está correta'
                    )
                else:
                    self.log_test(
                        'Vite Proxy Configuration',
                        'WARNING',
                        'Configuração de proxy pode estar incorreta',
                        'Proxy do Vite pode não estar redirecionando para o backend',
                        'Verificar configuração de proxy no vite.config.ts'
                    )
        except Exception as e:
            self.log_test(
                'Vite Proxy Configuration',
                'FAILED',
                f'Erro ao verificar configuração do Vite: {str(e)}',
                'Não foi possível verificar configuração do Vite',
                'Verificar se o arquivo vite.config.ts existe e está válido'
            )
        
        return all_files_exist
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos problemas encontrados"""
        print("\n💡 Gerando recomendações...")
        
        # Recomendações gerais baseadas nos problemas encontrados
        general_recommendations = [
            {
                'category': 'Prevenção de Problemas',
                'recommendations': [
                    'Implementar testes automatizados para endpoints da API',
                    'Configurar monitoramento de saúde dos serviços',
                    'Implementar logging estruturado no frontend e backend',
                    'Configurar alertas para falhas de conectividade',
                    'Implementar retry automático para requisições falhadas'
                ]
            },
            {
                'category': 'Debugging e Diagnóstico',
                'recommendations': [
                    'Adicionar mais logs detalhados no console do navegador',
                    'Implementar indicadores visuais de carregamento',
                    'Adicionar tratamento de erro mais específico',
                    'Implementar modo debug no frontend',
                    'Criar dashboard de monitoramento interno'
                ]
            },
            {
                'category': 'Performance e Confiabilidade',
                'recommendations': [
                    'Implementar cache inteligente com invalidação',
                    'Configurar timeout adequado para requisições',
                    'Implementar fallback para dados offline',
                    'Otimizar consultas do backend',
                    'Implementar compressão de dados'
                ]
            }
        ]
        
        for category_info in general_recommendations:
            print(f"\n📋 {category_info['category']}:")
            for rec in category_info['recommendations']:
                print(f"  • {rec}")
                self.results['recommendations'].append({
                    'category': category_info['category'],
                    'recommendation': rec
                })
    
    def run_full_diagnostic(self):
        """Executa diagnóstico completo"""
        print("🚀 Iniciando diagnóstico completo do GLPI Dashboard")
        print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Executar todos os testes
        tests = [
            self.test_backend_connectivity,
            self.test_frontend_connectivity,
            self.test_api_endpoints,
            self.test_cors_configuration,
            self.test_data_transformation,
            self.test_frontend_integration
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Erro durante teste: {str(e)}")
        
        # Gerar recomendações
        self.generate_recommendations()
        
        # Resumo final
        print("\n" + "="*80)
        print("📋 RESUMO DO DIAGNÓSTICO")
        print("="*80)
        
        print(f"📊 Testes executados: {len(self.results['tests'])}")
        print(f"✅ Testes aprovados: {passed_tests}/{total_tests}")
        print(f"❌ Problemas encontrados: {len(self.results['issues'])}")
        print(f"💡 Recomendações geradas: {len(self.results['recommendations'])}")
        
        if len(self.results['issues']) == 0:
            print("\n🎉 Nenhum problema crítico encontrado!")
            print("💡 Se o frontend ainda não está mostrando dados, pode ser um problema de cache do navegador.")
            print("🔄 Tente: Ctrl+F5 para recarregar sem cache")
        else:
            print("\n⚠️ Problemas encontrados que precisam ser resolvidos:")
            for issue in self.results['issues']:
                severity_icon = "🔴" if issue['severity'] == 'high' else "🟡"
                print(f"  {severity_icon} {issue['test']}: {issue['issue']}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'diagnostic_results_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados completos salvos em: {filename}")
        
        return len(self.results['issues']) == 0

def main():
    diagnostic = GLPIDashboardDiagnostic()
    success = diagnostic.run_full_diagnostic()
    
    if success:
        print("\n✅ Diagnóstico concluído com sucesso!")
        return 0
    else:
        print("\n❌ Problemas encontrados que precisam ser resolvidos.")
        return 1

if __name__ == '__main__':
    exit(main())